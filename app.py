import streamlit as st
import pandas as pd
import math

# 1. CONFIGURAÇÃO DE IDENTIDADE MK
st.set_page_config(page_title="MK - Engenharia v33.0", layout="wide")

# Inicialização do Banco de Dados Temporário
if 'db_clientes' not in st.session_state: st.session_state.db_clientes = []
if 'db_projetos' not in st.session_state: st.session_state.db_projetos = []
if 'db_obras' not in st.session_state: st.session_state.db_obras = []
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
    .card-projeto { border: 1px solid #1e3a8a; padding: 15px; border-radius: 8px; background: #fff; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚒️ MK - GESTÃO TOTAL v33.0")

# --- NAVEGAÇÃO POR ABAS ---
tabs = st.tabs(["📍 Cliente", "📏 Projeto", "💰 Orçamento", "🏭 Produção", "🚚 Instalação", "🚧 Gestão Obras", "⚙️ Custos"])

# --- ABA 1: CLIENTE ---
with tabs[0]:
    st.header("👥 Cadastro de Cliente")
    with st.form("cli_v33"):
        c1, c2 = st.columns(2)
        nome = c1.text_input("Nome")
        tel = c2.text_input("WhatsApp")
        cep = c1.text_input("CEP")
        log = c2.text_input("Logradouro")
        if st.form_submit_button("Salvar Cliente"):
            st.session_state.db_clientes.append({"nome": nome, "obra": log})
            st.rerun()

    st.subheader("Lista de Clientes")
    for i, cli in enumerate(st.session_state.db_clientes):
        col_c1, col_c2 = st.columns([4, 1])
        col_c1.write(f"👤 {cli['nome']} - {cli['obra']}")
        if col_c2.button(f"🗑️ Apagar", key=f"btn_cli_del_{i}"):
            st.session_state.db_clientes.pop(i)
            st.rerun()

# --- ABA 2: PROJETO ---
with tabs[1]:
    st.header("📐 Novo Projeto")
    c1, c2, c3 = st.columns(3)
    tipo = c1.selectbox("Tipologia", ["Janela 2fls", "Janela 4fls", "Porta Giro", "Fixo"])
    larg = c2.number_input("Largura (mm)", min_value=0)
    alt = c3.number_input("Altura (mm)", min_value=0)
    qtd = st.number_input("Quantidade de Peças", min_value=1, step=1)
    
    st.subheader("📍 Ambientes e Observações")
    pecas_info = []
    for i in range(int(qtd)):
        l_c, o_c = st.columns([1, 2])
        loc = l_c.text_input(f"Ambiente {i+1}", key=f"loc_input_{i}")
        obs_p = o_c.text_input(f"Obs {i+1}", key=f"obs_input_{i}")
        pecas_info.append({"ambiente": loc, "nota": obs_p})
        
    if st.button("💾 Adicionar Projeto"):
        st.session_state.db_projetos.append({
            "tipo": tipo, "larg": larg, "alt": alt, "qtd": qtd, "detalhes": pecas_info
        })
        st.success("Adicionado!")

# --- ABA 3: ORÇAMENTO (ONDE ESTAVA O ERRO) ---
with tabs[2]:
    st.header("💰 Itens do Orçamento")
    # Limpeza total
    if st.button("🔥 LIMPAR TODO O ORÇAMENTO", key="btn_clear_orc"):
        st.session_state.db_projetos = []
        st.rerun()
    
    st.divider()
    
    # Exclusão unitária corrigida
    if st.session_state.db_projetos:
        for idx, p in enumerate(st.session_state.db_projetos):
            with st.container():
                col_info, col_btn = st.columns([5, 1])
                col_info.markdown(f"""
                <div class='card-projeto'>
                    <strong>{p['tipo']}</strong> | {p['larg']}x{p['alt']}mm | {p['qtd']} unidades
                </div>
                """, unsafe_allow_html=True)
                
                # A chave (key) agora é baseada no índice e no tipo para nunca repetir
                if col_btn.button("🗑️ Apagar", key=f"btn_del_item_{idx}_{p['tipo']}"):
                    st.session_state.db_projetos.pop(idx)
                    st.rerun()
    else:
        st.info("Nenhum item no orçamento.")

# --- ABA 6: GESTÃO OBRAS ---
with tabs[5]:
    st.header("🚧 Controle de Obras")
    if st.button("🔥 LIMPAR TODAS AS OBRAS", key="btn_clear_obras"):
        st.session_state.db_obras = []
        st.rerun()
        
    for i, obra in enumerate(st.session_state.db_obras):
        c_o1, c_o2 = st.columns([4, 1])
        c_o1.write(f"🏗️ {obra['cliente']}")
        if c_o2.button("🗑️ Excluir", key=f"btn_obra_del_{i}"):
            st.session_state.db_obras.pop(i)
            st.rerun()
