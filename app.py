import streamlit as st
import requests
import google.generativeai as genai
import pandas as pd 
from bs4 import BeautifulSoup
import urllib.parse # Ferramenta nativa para criar links de túnel

# 1. Configuração da IA
CHAVE_API_GEMINI = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=CHAVE_API_GEMINI)
modelo_ia = genai.GenerativeModel('gemini-1.5-pro')

def analisar_mercado(produto):
    # Prepara o link original do Mercado Livre
    produto_url = produto.replace(" ", "-")
    url_alvo = f"https://lista.mercadolivre.com.br/{produto_url}"
    
    # O TRUQUE MESTRE: Colocamos o link do ML dentro do túnel do AllOrigins
    url_proxy = f"https://api.allorigins.win/get?url={urllib.parse.quote(url_alvo)}"
    
    try:
        # Pedimos ao túnel para ir buscar a página
        response = requests.get(url_proxy)
        
        if response.status_code != 200:
            return "🚫 Erro no túnel de conexão. Tente novamente mais tarde.", None
            
        # O túnel devolve um pacote onde a página do ML está dentro de 'contents'
        dados_tunel = response.json()
        html_da_pagina = dados_tunel.get('contents', '')
        
        if not html_da_pagina:
            return "🚫 O Mercado Livre bloqueou até o nosso túnel! A segurança deles está extrema hoje.", None
            
        # O BeautifulSoup vai ler o código da página que o túnel trouxe
        soup = BeautifulSoup(html_da_pagina, 'html.parser')
        
        # Procuramos as "caixinhas" dos produtos na tela
        anuncios = soup.find_all('li', class_='ui-search-layout__item')
        if not anuncios:
             anuncios = soup.find_all('div', class_='ui-search-result__wrapper')
             
        if not anuncios:
            return "Nenhum produto encontrado. O visual do site mudou ou a proteção contra robôs camuflou os preços.", None
            
        dados_para_ia = f"Produto analisado: {produto}\n\nTop 5 Anúncios:\n"
        nomes_anuncios = []
        precos_anuncios = []
        
        # Pegamos os 5 primeiros anúncios da página
        for i, item in enumerate(anuncios[:5], 1):
            titulo_elem = item.find('h2')
            titulo = titulo_elem.text if titulo_elem else "Sem título"
            
            preco_elem = item.find('span', class_='andes-money-amount__fraction')
            if preco_elem:
                preco_str = preco_elem.text.replace('.', '')
                preco = float(preco_str)
            else:
                preco = 0.0
                
            dados_para_ia += f"{i}. {titulo} - R$ {preco:.2f}\n"
            nomes_anuncios.append(f"Top {i}") 
            precos_anuncios.append(preco)

    except Exception as e:
        return f"Erro na leitura dos dados: {e}", None

    prompt = f"""
    És um especialista no Mercado Livre. Analise estes 5 anúncios:
    {dados_para_ia}
    
    Escreva um relatório rápido de viabilidade, focando no preço médio e na dificuldade de entrada. Formate a sua resposta usando Markdown (títulos, negritos e listas).
    """
    
    resposta = modelo_ia.generate_content(prompt)
    
    tabela_grafico = pd.DataFrame({
        "Anúncios": nomes_anuncios,
        "Preço (R$)": precos_anuncios
    }).set_index("Anúncios")
    
    return resposta.text, tabela_grafico

# ==========================================
# 3. A INTERFACE GRÁFICA (STREAMLIT)
# ==========================================
st.set_page_config(page_title="Agente Mercado Livre", page_icon="📦", layout="centered")

st.title("📦 Agente Inteligente: Mercado Livre")
st.markdown("Descubra a viabilidade de qualquer produto em segundos usando Inteligência Artificial.")
st.divider()

produto_input = st.text_input("Qual produto deseja analisar?", placeholder="Ex: Garrafa Térmica 1L Inox")

if st.button("Analisar Mercado 🚀"):
    if produto_input:
        with st.spinner(f"A usar um túnel seguro para investigar '{produto_input}'... Isto pode levar alguns segundos."):
            
            relatorio, dados_grafico = analisar_mercado(produto_input)
            
            if dados_grafico is not None:
                st.success("Análise concluída com sucesso!")
                
                st.markdown("### 📈 Comparativo de Preços (Top 5)")
                st.bar_chart(dados_grafico)
                
                st.markdown("### 📊 Relatório de Viabilidade da IA")
                st.info(relatorio)
            else:
                st.error(relatorio)
                
    else:
        st.warning("Por favor, digite o nome de um produto antes de analisar.")
