import streamlit as st
import pandas as pd
import math

# 1. CONFIGURAÇÃO DE IDENTIDADE MK
st.set_page_config(page_title="MK - Engenharia v32.0", layout="wide")

# Inicialização do Banco de Dados Temporário (Session State)
if 'db_clientes' not in st.session_state: st.session_state.db_clientes = []
if 'db_projetos' not in st.session_state: st.session_state.db_projetos = []
if 'db_obras' not in st.session_state: st.session_state.db_obras = []

# Matriz de Custos e Pesos
if 'tab_perfis' not in st.session_state:
    st.session_state.tab_perfis = {
        "Suprema": {"SU-001": 0.455, "SU-039": 0.580, "SU-005": 0.320},
        "Gold": {"LG-028": 0.950, "LG-040": 1.100}
    }

if 'custo_vidros' not in st.session_state:
    st.session_state.custo_vidros = {
        "Incolor": {"6mm": 120.0, "8mm": 180.0, "10mm": 220.0},
        "Verde": {"6mm": 140.0, "8mm": 210.0, "10mm": 250.0},
        "Fumê": {"6mm": 150.0, "8mm": 230.0, "10mm": 280.0}
    }

# ESTILO VISUAL MK
st.markdown("""
    <style>
    .stButton>button { font-weight: bold; width: 100%; }
    .btn-delete { background-color: #ff4b4b !important; color: white !important; }
    .card-projeto { border: 1px solid #1e3a8a; padding: 15px; border-radius: 8px; background: #fff; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚒️ MK - GESTÃO TOTAL v32.0")

# --- NAVEGAÇÃO POR ABAS ---
tabs = st.tabs(["📍 Cliente", "📏 Projeto", "💰 Orçamento", "🏭 Produção", "🚚 Instalação", "🚧 Gestão Obras", "⚙️ Custos"])

# --- ABA 1: CLIENTE (COM EXCLUSÃO) ---
with tabs[0]:
    st.header("👥 Cadastro de Cliente")
    with st.form("cli_v32"):
        c1, c2 = st.columns(2); nome = c1.text_input("Nome"); email = c2.text_input("E-mail")
        tel = c1.text_input("Telefone"); wpp = c2.text_input("WhatsApp")
        st.divider(); cep = c1.text_input("CEP"); log = c2.text_input("Logradouro")
        ref = st.text_input("Ponto de Referência"); obra = st.text_input("Endereço da Obra")
        if st.form_submit_button("Salvar Cliente"):
            st.session_state.db_clientes.append({"id": len(st.session_state.db_clientes), "nome": nome, "obra": obra if obra else log})

    st.subheader("Lista de Clientes")
    for i, cli in enumerate(st.session_state.db_clientes):
        col_c1, col_c2 = st.columns([4, 1])
        col_c1.write(f"👤 {cli['nome']} - {cli['obra']}")
        if col_c2.button(f"🗑️ Apagar", key=f"del_cli_{i}"):
            st.session_state.db_clientes.pop(i)
            st.rerun()

    if st.button("🔥 APAGAR TODOS OS CLIENTES", key="clear_all_cli"):
        st.session_state.db_clientes = []
        st.rerun()

# --- ABA 2: PROJETO ---
with tabs[1]:
    st.header("📐 Configuração de Projeto")
    col1, col2, col3 = st.columns(3)
    linha = col1.selectbox("Linha", list(st.session_state.tab_perfis.keys()))
    tipo = col2.selectbox("Tipologia", ["Janela 2fls", "Janela 4fls", "Porta Giro", "Fixo"])
    cor = col3.selectbox("Cor Alumínio", ["Branco", "Preto"])
    
    st.subheader("💎 Vidro")
    c_v, e_v = st.columns(2)
    cor_vidro = c_v.selectbox("Cor Vidro", list(st.session_state.custo_vidros.keys()))
    esp_vidro = e_v.selectbox("Espessura", list(st.session_state.custo_vidros[cor_vidro].keys()))
    
    l_p, a_p, q_p = st.columns(3)
    larg = l_p.number_input("Largura (mm)", step=1); alt = a_p.number_input("Altura (mm)", step=1); qtd = q_p.number_input("Quantidade", min_value=1)
    
    st.subheader("📍 Detalhes e Observações")
    pecas_info = []
    for i in range(int(qtd)):
        l_c, o_c = st.columns([1, 2])
        loc = l_c.text_input(f"Ambiente {i+1}", key=f"loc_{i}")
        obs_p = o_c.text_input(f"Obs Técnica {i+1}", key=f"obs_{i}")
        pecas_info.append({"ambiente": loc, "nota": obs_p})
        
    if st.button("💾 Adicionar ao Orçamento"):
        st.session_state.db_projetos.append({
            "linha": linha, "tipo": tipo, "cor": cor, "vidro_cor": cor_vidro, "vidro_esp": esp_vidro,
            "larg": larg, "alt": alt, "qtd": qtd, "detalhes": pecas_info
        })
        st.success("Adicionado!")

# --- ABA 3: ORÇAMENTO (EXCLUSÃO UNITÁRIA E TOTAL) ---
with tabs[2]:
    st.header("💰 Gerenciar Orçamento")
    if st.session_state.db_projetos:
        for idx, p in enumerate(st.session_state.db_projetos):
            with st.container():
