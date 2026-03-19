import streamlit as st
import pandas as pd
import math

# 1. CONFIGURAÇÃO DE IDENTIDADE MK
st.set_page_config(page_title="MK - Engenharia v34.0", layout="wide")

# Inicialização de todos os Bancos de Dados (Session State)
if 'db_clientes' not in st.session_state: st.session_state.db_clientes = []
if 'db_projetos' not in st.session_state: st.session_state.db_projetos = []
if 'db_obras' not in st.session_state: st.session_state.db_obras = []

# Matriz de Custos de Vidros (6mm, 8mm, 10mm)
if 'custo_vidros' not in st.session_state:
    st.session_state.custo_vidros = {
        "Incolor": {"6mm": 120.0, "8mm": 180.0, "10mm": 220.0},
        "Verde": {"6mm": 140.0, "8mm": 210.0, "10mm": 250.0},
        "Fumê": {"6mm": 150.0, "8mm": 230.0, "10mm": 280.0},
        "Refletivo": {"6mm": 250.0, "8mm": 350.0, "10mm": 450.0}
    }

# Tabela de Pesos Teóricos Alumínio
if 'tab_perfis' not in st.session_state:
    st.session_state.tab_perfis = {
        "Suprema": {"SU-001": 0.455, "SU-039": 0.580, "SU-005": 0.320},
        "Gold": {"LG-028": 0.950, "LG-040": 1.100}
    }

# ESTILO VISUAL MK
st.markdown("""
    <style>
    .stButton>button { font-weight: bold; width: 100%; }
    .card-projeto { border: 1px solid #1e3a8a; padding: 15px; border-radius: 8px; background: #fff; margin-bottom: 10px; }
    .status-atrasado { color: red; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚒️ MK - GESTÃO INDUSTRIAL v34.0")

# --- NAVEGAÇÃO POR ABAS ---
tabs = st.tabs(["📍 Cliente", "📏 Projeto", "💰 Orçamento", "🏭 Produção", "🚚 Instalação", "🚧 Gestão Obras", "⚙️ Custos"])

# --- ABA 1: CLIENTE (RECUPERADO OS 10 CAMPOS) ---
with tabs[0]:
    st.header("👥 Cadastro Detalhado de Cliente")
    with st.form("cli_v34"):
        c1, c2 = st.columns(2)
        nome_c = c1.text_input("Nome / Razão Social")
        email_c = c2.text_input("E-mail")
        tel_c = c1.text_input("Telefone Fixo")
        wpp_c = c2.text_input("WhatsApp")
        st.divider()
        cep_c = c1.text_input("CEP")
        log_c = c2.text_input("Logradouro (Rua/Av)")
        bai_c, cid_c = st.columns(2)
        bairro_c = bai_c.text_input("Bairro")
        cidade_c = cid_c.text_input("Cidade/UF")
        ref_c = st.text_input("Ponto de Referência")
        obra_c = st.text_input("Endereço da Obra (Se diferente)")
        obs_c = st.text_area("Observações Gerais")
        if st.form_submit_button("Salvar Cliente"):
            st.session_state.db_clientes.append({"nome": nome_c, "obra": obra_c if obra_c else log_c, "wpp": wpp_c})
            st.rerun()

    st.subheader("Lista de Clientes Cadastrados")
    for i, cli in enumerate(st.session_state.db_clientes):
        col_c1, col_c2 = st.columns([5, 1])
        col_c1.info(f"👤 {cli['nome']} | 📍 {cli['obra']}")
        if col_c2.button("🗑️ Apagar", key=f"del_cli_{i}"):
            st.session_state.db_clientes.pop(i)
            st.rerun()

# --- ABA 2: PROJETO (RECUPERADO LOCALIZAÇÃO E OBS POR PEÇA) ---
with tabs[1]:
    st.header("📐 Engenharia e Tipologias")
    col1, col2, col3 = st.columns(3)
    linha_p = col1.selectbox("Linha", list(st.session_state.tab_perfis.keys()))
    tipo_p = col2.selectbox("Tipologia", ["Janela 2fls", "Janela 4fls", "Porta Giro", "Fixo", "Maxim-ar"])
    cor_p = col3.selectbox("Cor Alumínio", ["Branco", "Preto", "Bronze"])
    
    st.subheader("💎 Configuração do Vidro")
    c_vid, e_vid = st.columns(2)
    cor_v = c_vid.selectbox("Cor do Vidro", list(st.session_state.custo_vidros.keys()))
    esp_v = e_vid.selectbox("Espessura", list(st.session_state.custo_vidros[cor_v].keys()))
    
    st.divider()
    l_p, a_p, q_p = st.columns(3)
    larg = l_p.number_input("Largura (mm)", step=1)
    alt = a_p.number_input("Altura (mm)", step=1)
    qtd = q_p.number_input("Quantidade de Peças", min_value=1, step=1)
    
    st.subheader("📍 Detalhes de Cada Peça")
    pecas_detalhes = []
    for i in range(int(qtd)):
        st.write(f"**Item {i+1}:**")
        loc_col, obs_col = st.columns([1, 2])
        amb = loc_col.text_input(f"Ambiente", key=f"amb_v34_{i}", placeholder="Ex: Suíte")
        nota = obs_col.text_input(f"Obs. Técnica", key=f"nota_v34_{i}", placeholder="Ex: Vidro com furo")
        pecas_detalhes.append({"ambiente": amb, "obs": nota})
        
    if st.button("💾 Adicionar ao Orçamento"):
        st.session_state.db_projetos.append({
            "linha": linha_p, "tipo": tipo_p, "cor": cor_p, "vidro": f"{esp_v} {cor_v}",
            "larg": larg, "alt": alt, "qtd": qtd, "detalhes": pecas_detalhes,
            "v_m2": st.session_state.custo_vidros[cor_v][esp_v]
        })
        st.success("Projeto adicionado com sucesso!")

# --- ABA 3: ORÇAMENTO (EDITÁVEL E COM EXCLUSÃO CORRIGIDA) ---
with tabs[2]:
    st.header("💰 Gerenciamento de Orçamento")
    if st.button("🔥 LIMPAR TODO O ORÇAMENTO", key="clear_orc_v34"):
        st.session_state.db_projetos = []
        st.rerun()

    if st.session_state.db_projetos:
        for idx, p in enumerate(st.session_state.db_projetos):
            with st.container():
                col_info, col_btn = st.columns([5, 1])
                col_info.markdown(f"""
                <div class='card-projeto'>
                    <strong>{p['tipo']} ({p['linha']})</strong> | {p['larg']}x{p['alt']}mm | {p['qtd']} un.<br>
                    Vidro: {p['vidro']}
                </div>
                """, unsafe_allow_html=True)
                
                if col_btn.button("🗑️ Apagar", key=f"del_item_v34_{idx}"):
                    st.session_state.db_projetos.pop(idx)
                    st.rerun()
    else:
        st.info("Nenhum item adicionado.")

# --- ABA 7: CUSTOS (MATRIZ DE VIDROS COMPLETA) ---
with tabs[6]:
    st.header("⚙️ Configuração de Preços (Custo de Compra)")
    with st.expander("🖼️ MATRIZ DE VIDROS (R$/m²)", expanded=True):
        for cv, espessuras in st.session_state.custo_vidros.items():
            st.write(f"**Vidro {cv}**")
            cols = st.columns(3)
            for i, (esp, preco) in enumerate(espessuras.items()):
                st.session_state.custo_vidros[cv][esp] = cols[i].number_input(f"{esp}", value=preco, key=f"mat_v34_{cv}_{esp}")
