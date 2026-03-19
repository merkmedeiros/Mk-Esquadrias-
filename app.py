import streamlit as st
import pandas as pd
import math

# 1. CONFIGURAÇÃO DE IDENTIDADE MK
st.set_page_config(page_title="MK - Engenharia v37.0", layout="wide")

# --- INICIALIZAÇÃO DE SEGURANÇA (Garante que as listas existam) ---
if 'db_clientes' not in st.session_state: st.session_state.db_clientes = []
if 'db_projetos' not in st.session_state: st.session_state.db_projetos = []
if 'db_obras' not in st.session_state: st.session_state.db_obras = []
if 'custo_vidros' not in st.session_state:
    st.session_state.custo_vidros = {
        "Incolor": {"6mm": 120.0, "8mm": 180.0, "10mm": 220.0},
        "Verde": {"6mm": 140.0, "8mm": 210.0, "10mm": 250.0},
        "Fumê": {"6mm": 150.0, "8mm": 230.0, "10mm": 280.0},
        "Refletivo": {"6mm": 250.0, "8mm": 350.0, "10mm": 450.0}
    }
if 'custo_perfis' not in st.session_state:
    st.session_state.custo_perfis = {
        "Suprema": {"SU-001": {"peso": 0.455, "preco": 45.0}, "SU-039": {"peso": 0.580, "preco": 45.0}},
        "Gold": {"LG-028": {"peso": 0.950, "preco": 55.0}, "LG-040": {"peso": 1.100, "preco": 55.0}}
    }
if 'custo_acessorios' not in st.session_state:
    st.session_state.custo_acessorios = [
        {"item": "Roldana", "valor": 12.50},
        {"item": "Fecho/Puxador", "valor": 18.00},
        {"item": "Escova de Vedação (m)", "valor": 2.50}
    ]

# --- ESTILO CSS (CORREÇÃO DE FONTE E CONTRASTE) ---
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .card-orcamento { 
        border: 2px solid #1e3a8a; 
        padding: 20px; 
        border-radius: 10px; 
        background-color: #ffffff; 
        margin-bottom: 10px;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
    }
    /* Força texto escuro em qualquer tema */
    .card-orcamento b, .card-orcamento p, .card-orcamento span, .card-orcamento strong {
        color: #000000 !important;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #ddd; border-radius: 5px; padding: 10px; }
    .stTabs [aria-selected="true"] { background-color: #1e3a8a !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚒️ MK - GESTÃO INTEGRAL v37.0")

# --- NAVEGAÇÃO POR ABAS ---
tabs = st.tabs(["📍 Cliente", "📏 Projeto", "💰 Orçamento", "🏭 Produção", "🚚 Instalação", "🚧 Gestão Obras", "⚙️ Custos"])

# --- ABA 1: CLIENTE (OS 10 CAMPOS COMPLETOS) ---
with tabs[0]:
    st.header("👥 Cadastro de Cliente")
    with st.form("form_cliente"):
        c1, c2 = st.columns(2)
        n_cli = c1.text_input("Nome / Razão Social")
        e_cli = c2.text_input("E-mail")
        t_cli = c1.text_input("Telefone Fixo")
        w_cli = c2.text_input("WhatsApp")
        st.divider()
        cp_cli = c1.text_input("CEP")
        lg_cli = c2.text_input("Logradouro")
        ba_cli, ci_cli = st.columns(2)
        bai_cli = ba_cli.text_input("Bairro")
        cid_cli = ci_cli.text_input("Cidade/UF")
        ref_cli = st.text_input("Ponto de Referência")
        ob_cli = st.text_input("Endereço da Obra (Se diferente)")
        
        if st.form_submit_button("💾 Salvar Cliente"):
            st.session_state.db_clientes.append({
                "nome": n_cli, "email": e_cli, "wpp": w_cli, "obra": ob_cli if ob_cli else lg_cli, "ref": ref_cli
            })
            st.success("Cliente salvo com sucesso!")
            st.rerun()

    st.subheader("Clientes Cadastrados")
    for i, cli in enumerate(st.session_state.db_clientes):
        col_c1, col_c2 = st.columns([5, 1])
        col_c1.info(f"👤 {cli['nome']} | 📍 {cli['obra']}")
        if col_c2.button("🗑️ Apagar", key=f"del_cli_{i}"):
            st.session_state.db_clientes.pop(i)
            st.rerun()

# --- ABA 2: PROJETO (ENGENHARIA E OBSERVAÇÃO POR PEÇA) ---
with tabs[1]:
    st.header("📐 Novo Projeto")
    col1, col2, col3 = st.columns(3)
    lin = col1.selectbox("Linha", list(st.session_state.custo_perfis.keys()))
    tip = col2.selectbox("Tipologia", ["Janela 2fls", "Janela 4fls", "Porta Giro", "Fixo"])
    cor = col3.selectbox("Cor Alumínio", ["Branco", "Preto", "Bronze"])
    
    st.subheader("💎 Vidro")
    cv, ev = st.columns(2)
    c_vid = cv.selectbox("Cor Vidro", list(st.session_state.custo_vidros.keys()))
    e_vid = ev.selectbox("Espessura", list(st.session_state.custo_vidros[c_vid].keys()))
    
    l_p, a_p, q_p = st.columns(3)
    larg = l_p.number_input("Largura (mm)", min_value=1)
    alt = a_p.number_input("Altura (mm)", min_value=1)
    qtd = q_p.number_input("Quantidade", min_value=1, step=1)
    
    st.subheader("📍 Detalhes por Ambiente")
    pecas = []
    for i in range(int(qtd)):
        ca1, ca2 = st.columns([1, 2])
        amb = ca1.text_input(f"Ambiente {i+1}", key=f"amb_v37_{i}")
        obs = ca2.text_input(f"Obs Técnica {i+1}", key=f"obs_v37_{i}")
        pecas.append({"amb": amb, "obs": obs})
        
    if st.button("➕ Adicionar Projeto"):
        st.session_state.db_projetos.append({
            "tipo": tip, "linha": lin, "cor": cor, "vidro": f"{e_vid} {c_vid}",
            "larg": larg, "alt": alt, "qtd": qtd, "detalhes": pecas
        })
        st.success("Projeto adicionado ao orçamento!")

# --- ABA 3: ORÇAMENTO (VISUALIZAÇÃO CORRIGIDA) ---
with tabs[2]:
    st.header("💰 Itens do Orçamento")
    if st.session_state.db_projetos:
        for idx, p in enumerate(st.session_state.db_projetos):
            with st.container():
                c_inf, c_btn = st.columns([5, 1])
                c_inf.markdown(f"""
                <div class='card-orcamento'>
                    <p><strong>{p['tipo'].upper()} - {p['linha'].upper()} ({p['qtd']} un)</strong></p>
                    <p><b>Medidas:</b> {p['larg']} x {p['alt']} mm</p>
                    <p><b>Vidro:</b> {p['vidro']} | <b>Alumínio:</b> {p['cor']}</p>
                </div>
                """, unsafe_allow_html=True)
                if c_btn.button("🗑️", key=f"del_item_v37_{idx}"):
                    st.session_state.db_projetos.pop(idx)
                    st.rerun()
        
        if st.button("🔥 LIMPAR TUDO", key="clear_all_v37"):
            st.session_state.db_projetos = []
            st.rerun()
    else:
        st.info("O orçamento está vazio.")

# --- ABA 7: CUSTOS (MATRIZES COMPLETAS) ---
with tabs[6]:
    st.header("⚙️ Configuração de Custos")
    
    with st.expander("🖼️ Matriz de Vidros (R$/m²)", expanded=True):
        for cor_v, espessuras in st.session_state.custo_vidros.items():
            st.write(f"**{cor_v}**")
            cols = st.columns(4)
            for i, (esp, preco) in enumerate(espessuras.items()):
                st.session_state.custo_vidros[cor_v][esp] = cols[i].number_input(f"{esp}", value=preco, key=f"v_{cor_v}_{esp}")

    with st.expander("📊 Perfis de Alumínio (Peso e Preço)"):
        l_sel = st.selectbox("Linha", list(st.session_state.custo_perfis.keys()))
        for perf, dado in st.session_state.custo_perfis[l_sel].items():
            cp1, cp2, cp3 = st.columns([2, 1, 1])
            cp1.write(f"**{perf}**")
            st.session_state.custo_perfis[l_sel][perf]["peso"] = cp2.number_input(f"Peso kg/m", value=dado["peso"], key=f"w_{perf}", format="%.3f")
            st.session_state.custo_perfis[l_sel][perf]["preco"] = cp3.number_input(f"Preço KG", value=dado["preco"], key=f"p_{perf}")

    with st.expander("🔩 Acessórios (Unitário)"):
        for i, ac in enumerate(st.session_state.custo_acessorios):
            ca1, ca2 = st.columns([3, 1])
            ca1.write(f"**{ac['item']}**")
            st.session_state.custo_acessorios[i]["valor"] = ca2.number_input("Valor R$", value=ac['valor'], key=f"ac_{i}")
