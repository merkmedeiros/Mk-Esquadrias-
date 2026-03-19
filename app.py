import streamlit as st
import pandas as pd

# CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Serralheria Pro v1.0", layout="wide")

st.title("🛠️ Gestão de Esquadrias - Linha Suprema")
st.markdown("---")

# --- ENTRADA DE DADOS (SIDEBAR) ---
with st.sidebar:
    st.header("👤 Dados do Cliente")
    cliente = st.text_input("Nome do Cliente/Obra", "Nova Obra")
    
    st.header("📐 Dimensões do Vão")
    L = st.number_input("Largura (mm)", min_value=100, value=1500)
    H = st.number_input("Altura (mm)", min_value=100, value=1200)
    
    st.header("⚙️ Especificações")
    tipologia = st.selectbox("Tipologia", [
        "Janela Correr 2 Fls", 
        "Janela Correr 4 Fls",
        "Porta Giro 1 Fl"
    ])
    p_alu = st.number_input("Preço Alumínio (R$/kg)", value=48.0)
    p_vidro = st.number_input("Preço Vidro (R$/m2)", value=160.0)

# --- LÓGICA DE CÁLCULO ---
def realizar_calculos(L, H, tipologia):
    res = {}
    if "Janela Correr 2 Fls" in tipologia:
        res['c_travessa'] = (L + 12) / 2
        res['c_montante'] = H - 45
        res['v_largura'] = (L - 110) / 2
        res['v_altura'] = H - 145
        res['v_qtd'] = 2
        res['peso'] = ((L*2 + H*2 + (H-45)*4 + (res['c_travessa'])*4)/1000) * 0.65
    elif "Janela Correr 4 Fls" in tipologia:
        res['c_travessa'] = (L + 115) / 4
        res['c_montante'] = H - 45
        res['v_largura'] = (L - 160) / 4
        res['v_altura'] = H - 145
        res['v_qtd'] = 4
        res['peso'] = ((L*2 + H*2 + (H-45)*8 + (res['c_travessa'])*8)/1000) * 0.68
    else: # Porta Giro
        res['c_travessa'] = L - 68
        res['c_montante'] = H - 35
        res['v_largura'] = L - 125
        res['v_altura'] = H - 210
        res['v_qtd'] = 1
        res['peso'] = ((L*2 + H*2 + (res['c_travessa'])*2 + (res['c_montante'])*2)/1000) * 0.85
    return res

dados = realizar_calculos(L, H, tipologia)

# --- EXIBIÇÃO ---
t1, t2, t3 = st.tabs(["💰 Orçamento", "🪚 Cortes", "💎 Vidros"])

with t1:
    custo_total = (dados['peso'] * 1.05 * p_alu) + ((dados['v_largura'] * dados['v_altura'] * dados['v_qtd'] / 1000000) * p_vidro) + 100
    st.metric("Custo Estimado", f"R$ {custo_total:.2f}")
    st.write(f"**Peso Total:** {dados['peso']*1.05:.2f} kg")

with t2:
    st.write(f"**Travessas:** {dados['c_travessa']:.1f} mm")
    st.write(f"**Montantes:** {dados['c_montante']:.1f} mm")

with t3:
    st.success(f"Vidro: {dados['v_qtd']} pçs de {dados['v_largura']:.1f} x {dados['v_altura']:.1f} mm")
