import streamlit as st
import requests
import google.generativeai as genai
import pandas as pd 

# 1. Configuração da IA 
CHAVE_API_GEMINI = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=CHAVE_API_GEMINI)
modelo_ia = genai.GenerativeModel('gemini-1.5-pro')

def analisar_mercado(produto):
    url_search = "https://api.mercadolibre.com/sites/MLB/search"
    params = {"q": produto, "sort": "relevance", "limit": 5}
    
    # Novo disfarce: Fingir ser uma ferramenta oficial de testes de API (Postman)
    headers = {
        "Accept": "application/json",
        "User-Agent": "PostmanRuntime/7.36.1"
    }
    
    try:
        response = requests.get(url_search, params=params, headers=headers)
        
        # AVISO DE BLOQUEIO: Se o ML barrar a pesquisa, agora ele vai avisar na tela!
        if response.status_code != 200:
            return f"🚫 Bloqueio do Mercado Livre (Erro {response.status_code}): O servidor barrou a nossa entrada. Mensagem do ML: {response.text}", None
            
        resultados = response.json().get("results", [])
    except Exception as e:
        return f"Erro na conexão: {e}", None
        
    if not resultados:
        return "Nenhum produto encontrado. Tente um termo menos específico.", None

    dados_para_ia = f"Produto analisado: {produto}\n\nTop 5 Anúncios:\n"
    
    nomes_anuncios = []
    precos_anuncios = []
    
    for i, item in enumerate(resultados, 1):
        titulo = item.get("title")
        preco = item.get("price")
        
        dados_para_ia += f"{i}. {titulo} - R$ {preco:.2f}\n"
        nomes_anuncios.append(f"Top {i}") 
        precos_anuncios.append(preco)

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
                st.error(relatorio) # Agora a caixa vermelha mostrará o erro exato do ML
                
    else:
        st.warning("Por favor, digite o nome de um produto antes de analisar.")
