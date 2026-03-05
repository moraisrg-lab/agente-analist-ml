import streamlit as st
import google.generativeai as genai
import pandas as pd 
import random

# 1. Configuração da IA
CHAVE_API_GEMINI = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=CHAVE_API_GEMINI)

# -------------------------------------------------------------------
# A SOLUÇÃO INTELIGENTE: AUTODESCOBERTA DE MODELOS
# O código vai perguntar ao Google quais modelos a sua chave tem 
# acesso e vai selecionar o melhor automaticamente!
# -------------------------------------------------------------------
try:
    # Pede a lista de todos os modelos que escrevem textos
    modelos_disponiveis = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    
    # Procura pelo Flash ou Pro, se não achar, pega o primeiro da lista
    nome_do_modelo = modelos_disponiveis[0] 
    for m in modelos_disponiveis:
        if "gemini-1.5-flash" in m:
            nome_do_modelo = m
            break
        elif "gemini-1.0-pro" in m:
            nome_do_modelo = m
            
    modelo_ia = genai.GenerativeModel(nome_do_modelo)
except Exception as e:
    # Se falhar, usa um modelo de segurança
    modelo_ia = genai.GenerativeModel('gemini-1.5-flash')

def analisar_mercado_simulado(produto):
    # SIMULADOR: Criando dados fictícios para contornar o bloqueio do ML
    preco_base = random.uniform(50.0, 300.0) 
    
    resultados_simulados = [
        {"title": f"{produto} - Original (Mais Vendido)", "price": preco_base * 1.1},
        {"title": f"{produto} - Padrão Nacional", "price": preco_base * 0.9},
        {"title": f"{produto} - Importado Premium", "price": preco_base * 1.5},
        {"title": f"{produto} - Edição Básica", "price": preco_base * 0.7},
        {"title": f"{produto} - Kit Completo", "price": preco_base * 1.8},
    ]

    dados_para_ia = f"Produto analisado: {produto}\n\nTop 5 Anúncios (CENÁRIO SIMULADO):\n"
    nomes_anuncios = []
    precos_anuncios = []
    
    for i, item in enumerate(resultados_simulados, 1):
        titulo = item["title"]
        preco = item["price"]
        
        dados_para_ia += f"{i}. {titulo} - R$ {preco:.2f}\n"
        nomes_anuncios.append(f"Top {i}") 
        precos_anuncios.append(preco)

    prompt = f"""
    Você é um especialista em e-commerce. Eu gerei um cenário de mercado simulado com 5 anúncios para o produto pesquisado:
    {dados_para_ia}
    
    Escreva um relatório de viabilidade rápido, focando no preço médio, na variação (do mais barato ao mais caro) e sugerindo uma estratégia de entrada. 
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
# 3. A INTERFACE GRÁFICA (STREAMLIT)
# ==========================================
st.set_page_config(page_title="Agente Mercado Livre", page_icon="📦", layout="centered")

st.title("📦 Agente Inteligente: Mercado Livre")
st.markdown("Descubra a viabilidade de qualquer produto em segundos usando Inteligência Artificial.")

st.info("⚠️ **Modo Simulador Ativo:** Devido às políticas de segurança do Mercado Livre, este agente está gerando cenários de mercado simulados para demonstrar a capacidade de análise da Inteligência Artificial.")

st.divider()

produto_input = st.text_input("Qual produto deseja analisar?", placeholder="Ex: Garrafa Térmica 1L Inox")

if st.button("Analisar Mercado 🚀"):
    if produto_input:
        with st.spinner(f"A criar cenário simulado para '{produto_input}' e a ligar o cérebro da IA..."):
            
            relatorio, dados_grafico = analisar_mercado_simulado(produto_input)
            
            if dados_grafico is not None:
                st.success("Análise de cenário concluída!")
                
                st.markdown("### 📈 Comparativo de Preços (Simulação)")
                st.bar_chart(dados_grafico)
                
                st.markdown("### 📊 Relatório de Viabilidade da IA")
                st.write(relatorio)
            else:
                st.error(relatorio)
                
    else:
        st.warning("Por favor, digite o nome de um produto antes de analisar.")
