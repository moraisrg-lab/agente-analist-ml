import streamlit as st
import requests
import google.generativeai as genai
import pandas as pd 

# 1. Configurações de Chaves (Cofre)
CHAVE_API_GEMINI = st.secrets["GEMINI_API_KEY"]
ML_CLIENT_ID = st.secrets["ML_CLIENT_ID"]
ML_CLIENT_SECRET = st.secrets["ML_CLIENT_SECRET"]

genai.configure(api_key=CHAVE_API_GEMINI)

# Autodescoberta inteligente da IA
try:
    modelos_disponiveis = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    nome_do_modelo = modelos_disponiveis[0] 
    for m in modelos_disponiveis:
        if "gemini-1.5-flash" in m:
            nome_do_modelo = m
            break
    modelo_ia = genai.GenerativeModel(nome_do_modelo)
except:
    modelo_ia = genai.GenerativeModel('gemini-1.5-flash')

# 2. O Crachá Oficial: Função para pegar o Token de Acesso do ML
def obter_token_ml():
    url = "https://api.mercadolibre.com/oauth/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": ML_CLIENT_ID,
        "client_secret": ML_CLIENT_SECRET
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/x-www-form-urlencoded"
    }
    try:
        response = requests.post(url, data=payload, headers=headers)
        if response.status_code == 200:
            return response.json().get("access_token")
    except:
        pass
    return None

# 3. O Agente de Extração Real
def analisar_mercado_real(produto):
    token = obter_token_ml()
    
    if not token:
        return "🚫 Erro de Autenticação: O Mercado Livre não aceitou as chaves (ID e Secret).", None

    url_search = "https://api.mercadolibre.com/sites/MLB/search"
    params = {"q": produto, "sort": "relevance", "limit": 5}
    
    # O TRUQUE DE MESTRE: O Crachá Oficial (Token) + O Disfarce de Humano (User-Agent)
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url_search, params=params, headers=headers)
        if response.status_code != 200:
            return f"Erro na API do ML: {response.text}", None
        resultados = response.json().get("results", [])
    except Exception as e:
        return f"Erro de conexão: {e}", None
        
    if not resultados:
        return "Nenhum produto encontrado com essa descrição.", None

    dados_para_ia = f"Produto analisado: {produto}\n\nTop 5 Anúncios (DADOS REAIS):\n"
    nomes_anuncios = []
    precos_anuncios = []
    
    for i, item in enumerate(resultados, 1):
        titulo = item.get("title")
        preco = item.get("price")
        
        dados_para_ia += f"{i}. {titulo} - R$ {preco:.2f}\n"
        nomes_anuncios.append(f"Top {i}") 
        precos_anuncios.append(preco)

    prompt = f"""
    Você é um especialista em e-commerce. Analise os DADOS REAIS extraídos do Mercado Livre para o produto pesquisado:
    {dados_para_ia}
    
    Escreva um relatório de viabilidade rápido, focando no preço médio, variação de mercado e barreira de entrada. 
    Formate a sua resposta usando Markdown (títulos, negritos e listas).
    """
    
    try:
        resposta = modelo_ia.generate_content(prompt)
        texto_ia = resposta.text
    except Exception as e:
        return f"Erro ao comunicar com a IA: {e}", None
    
    tabela_grafico = pd.DataFrame({
        "Anúncios": nomes_anuncios,
        "Preço (R$)": precos_anuncios
    }).set_index("Anúncios")
    
    return texto_ia, tabela_grafico

# ==========================================
# 4. A INTERFACE GRÁFICA (STREAMLIT)
# ==========================================
st.set_page_config(page_title="Agente Mercado Livre", page_icon="📦", layout="centered")

st.title("📦 Agente Inteligente: Mercado Livre")
st.markdown("Descubra a viabilidade de qualquer produto em segundos usando Inteligência Artificial conectada à **API Oficial**.")
st.divider()

produto_input = st.text_input("Qual produto deseja analisar?", placeholder="Ex: Garrafa Térmica 1L Inox")

if st.button("Analisar Mercado 🚀"):
    if produto_input:
        with st.spinner(f"A conectar com a API oficial do Mercado Livre para analisar '{produto_input}'..."):
            
            relatorio, dados_grafico = analisar_mercado_real(produto_input)
            
            if dados_grafico is not None:
                st.success("Dados reais extraídos e analisados com sucesso!")
                
                st.markdown("### 📈 Comparativo de Preços Reais (Top 5)")
                st.bar_chart(dados_grafico)
                
                st.markdown("### 📊 Relatório Estratégico da IA")
                st.write(relatorio)
            else:
                st.error(relatorio)
    else:
        st.warning("Por favor, digite o nome de um produto antes de analisar.")
