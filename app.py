import streamlit as st
import requests
import google.generativeai as genai
import pandas as pd 
from bs4 import BeautifulSoup # A nossa nova ferramenta "Hacker"

# 1. Configuração da IA
CHAVE_API_GEMINI = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=CHAVE_API_GEMINI)
modelo_ia = genai.GenerativeModel('gemini-1.5-pro')

def analisar_mercado(produto):
    # Formata o texto para a URL do site visual do Mercado Livre
    produto_url = produto.replace(" ", "-")
    url_search = f"https://lista.mercadolivre.com.br/{produto_url}"
    
    # O nosso disfarce de navegador humano
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9",
        "Referer": "https://www.mercadolivre.com.br/"
    }
    
    try:
        # Em vez de pedir à API, vamos carregar a página web visual inteira
        response = requests.get(url_search, headers=headers)
        
        if response.status_code != 200:
            return f"🚫 Bloqueio do servidor (Erro {response.status_code}): O Mercado Livre barrou o IP da nuvem.", None
            
        # O BeautifulSoup vai ler o código HTML da página
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Procuramos as "caixinhas" dos produtos na tela
        anuncios = soup.find_all('li', class_='ui-search-layout__item')
        if not anuncios:
             anuncios = soup.find_all('div', class_='ui-search-result__wrapper')
             
        if not anuncios:
            return "Nenhum produto encontrado. A página mudou o visual ou a nuvem foi detectada.", None
            
        dados_para_ia = f"Produto analisado: {produto}\n\nTop 5 Anúncios:\n"
        nomes_anuncios = []
        precos_anuncios = []
        
        # Pegamos os 5 primeiros que apareceram na tela
        for i, item in enumerate(anuncios[:5], 1):
            titulo_elem = item.find('h2')
            titulo = titulo_elem.text if titulo_elem else "Sem título"
            
            preco_elem = item.find('span', class_='andes-money-amount__fraction')
            if preco_elem:
                preco_str = preco_elem.text.replace('.', '') # Remove o ponto de milhar
                preco = float(preco_str)
            else:
                preco = 0.0
                
            dados_para_ia += f"{i}. {titulo} - R$ {preco:.2f}\n"
            nomes_anuncios.append(f"Top {i}") 
            precos_anuncios.append(preco)

    except Exception as e:
        return f"Erro na leitura: {e}", None

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
        with st.spinner(f"A investigar os concorrentes de '{produto_input}' e a consultar a IA..."):
            
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
