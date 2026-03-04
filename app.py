import streamlit as st
import requests
import google.generativeai as genai
import pandas as pd  # <-- NOVA BIBLIOTECA AQUI

# 1. Configuração da IA (A usar os secrets do Streamlit Cloud)
CHAVE_API_GEMINI = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=CHAVE_API_GEMINI)
modelo_ia = genai.GenerativeModel('gemini-1.5-pro')

def analisar_mercado(produto):
    url_search = "https://api.mercadolibre.com/sites/MLB/search"
    params = {"q": produto, "sort": "relevance", "limit": 5}

    # O disfarce de navegador para não ser bloqueado
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url_search, params=params, headers=headers)
    
    try:
        response = requests.get(url_search, params=params)
        resultados = response.json().get("results", [])
    except Exception as e:
        return f"Erro na pesquisa: {e}", None
        
    if not resultados:
        return "Nenhum produto encontrado.", None

    dados_para_ia = f"Produto analisado: {produto}\n\nTop 5 Anúncios:\n"
    
    # Listas para guardar os dados do gráfico
    nomes_anuncios = []
    precos_anuncios = []
    
    for i, item in enumerate(resultados, 1):
        titulo = item.get("title")
        preco = item.get("price")
        
        # Alimentar os dados do texto
        dados_para_ia += f"{i}. {titulo} - R$ {preco:.2f}\n"
        
        # Alimentar os dados do Gráfico (Usamos nomes curtos para o gráfico não ficar feio)
        nomes_anuncios.append(f"Top {i}") 
        precos_anuncios.append(preco)

    prompt = f"""
    És um especialista no Mercado Livre. Analise estes 5 anúncios:
    {dados_para_ia}
    
    Escreva um relatório rápido de viabilidade, focando no preço médio e na dificuldade de entrada. Formate a sua resposta usando Markdown (títulos, negritos e listas).
    """
    
    resposta = modelo_ia.generate_content(prompt)
    
    # --- PREPARAR OS DADOS DO GRÁFICO COM PANDAS ---
    tabela_grafico = pd.DataFrame({
        "Anúncios": nomes_anuncios,
        "Preço (R$)": precos_anuncios
    }).set_index("Anúncios")
    
    # Agora a função devolve DUAS coisas: o texto da IA e a tabela do gráfico
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
            
            # Recebe o relatório E os dados do gráfico
            relatorio, dados_grafico = analisar_mercado(produto_input)
            
            if dados_grafico is not None:
                st.success("Análise concluída com sucesso!")
                
                # --- EXIBE O GRÁFICO PRIMEIRO ---
                st.markdown("### 📈 Comparativo de Preços (Top 5)")
                st.bar_chart(dados_grafico)
                
                # --- EXIBE O RELATÓRIO DEPOIS ---
                st.markdown("### 📊 Relatório de Viabilidade da IA")
                st.info(relatorio)
            else:
                st.error(relatorio)
                
    else:
        st.warning("Por favor, digite o nome de um produto antes de analisar.")
