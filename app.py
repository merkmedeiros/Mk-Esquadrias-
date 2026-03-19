import streamlit as st
import pandas as pd
import math

# 1. CONFIGURAÇÃO DE IDENTIDADE MK
st.set_page_config(page_title="MK - Engenharia v35.0", layout="wide")

# Inicialização de Bancos de Dados (Session State)
if 'db_clientes' not in st.session_state: st.session_state.db_clientes = []
if 'db_projetos' not in st.session_state: st.session_state.db_projetos = []
if 'db_obras' not in st.session_state: st.session_state.db_obras = []

# Matriz de Custos de Vidros (Filtros por Cor e Espessura)
if 'custo_vidros' not in st.session_state:
    st.session_state.custo_vidros = {
        "Incolor": {"6mm": 120.0, "8mm": 180.0, "10mm": 220.0},
        "Verde": {"6mm": 140.0, "8mm": 210.0, "10mm": 250.0},
        "Fumê": {"6mm": 150.0, "8mm": 230.0, "10mm": 280.0},
        "Refletivo": {"6mm": 250.0, "8mm": 350.0, "10mm": 450.0}
    }

# Cadastro de Perfis (Peso e Preço por KG)
if 'custo_perfis' not in st.session_state:
    st.session_state.custo_perfis = {
        "Suprema": {"SU-001": {"peso": 0.455, "preco": 45.0}, "SU-039": {"peso": 0.580, "preco": 45.0}},
        "Gold": {"LG-028": {"peso": 0.950, "preco": 55.0}, "LG-040": {"peso": 1.100, "preco": 55.0}}
    }

# Cadastro de Acessórios (Item a Item)
if 'custo_acessorios' not in st.session_state:
    st.session_state.custo_acessorios = [
        {"item": "Roldana", "valor": 12.50},
        {"item": "Fecho/Puxador", "valor": 18.00},
        {"item": "Escova de Vedação (m)", "valor": 2.50},
        {"item": "Kit Fixação (Parafuso/Bucha)", "valor": 5.00}
    ]

# ESTILO VISUAL MK
st.markdown("""
    <style>
    .stButton>button { font-weight: bold; width: 100%; }
    .card-projeto { border: 1px solid #1e3a8a; padding: 15px; border-radius: 8px; background: #fff; margin-bottom: 10px; }
    .section-title { color: #1e3a8a; border-bottom: 2px solid #1e3a8a; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚒️ MK - GESTÃO INDUSTRIAL v35.0")

# --- NAVEGAÇÃO POR ABAS ---
tabs = st.tabs(["📍 Cliente", "📏 Projeto", "💰 Orçamento", "🏭 Produção", "🚚 Instalação", "🚧 Gestão Obras", "⚙️ Custos"])

# --- ABA 1: CLIENTE (10 CAMPOS PRESERVADOS) ---
with tabs[0]:
    st.header("👥 Cadastro de Cliente")
    with st.form("cli_v35"):
        c1, c2 = st.columns(2)
        nome_c = c1.text_input("Nome / Razão Social")
        email_c = c2.text_input("E-mail")
        tel_c = c1.text_input("Telefone Fixo")
        wpp_c = c2.text_input("WhatsApp")
        st.divider()
        cep_c = c1.text_input("CEP")
        log_c = c2.text_input("Logradouro")
        bai_c, cid_c = st.columns(2)
        bairro_c = bai_c.text_input("Bairro")
        cidade_c = cid_c.text_input("Cidade/UF")
        ref_c = st.text_input("Ponto de Referência")
        obra_c = st.text_input("Endereço da Obra")
        if st.form_submit_button("Salvar Cliente"):
            st.session_state.db_clientes.append({"nome": nome_c, "obra": obra_c if obra_c else log_c, "wpp": wpp_c})
            st.rerun()

# --- ABA 2: PROJETO (ENGENHARIA E DETALHES POR PEÇA) ---
with tabs[1]:
    st.header("📐 Engenharia e Peças")
    col1, col2, col3 = st.columns(3)
    linha_p = col1.selectbox("Linha", list(st.session_state.custo_perfis.keys()))
    tipo_p = col2.selectbox("Tipologia", ["Janela 2fls", "Janela 4fls", "Porta Giro", "Fixo"])
    cor_p = col3.selectbox("Cor Alumínio", ["Branco", "Preto", "Bronze"])
    
    st.subheader("💎 Vidro Selecionado")
    c_vid, e_vid = st.columns(2)
    cor_v = c_vid.selectbox("Cor", list(st.session_state.custo_vidros.keys()))
    esp_v = e_vid.selectbox("Espessura", list(st.session_state.custo_vidros[cor_v].keys()))
    
    l_p, a_p, q_p = st.columns(3)
    larg = l_p.number_input("Largura (mm)", step=1); alt = a_p.number_input("Altura (mm)", step=1); qtd = q_p.number_input("Quantidade", min_value=1)
    
    pecas_detalhes = []
    for i in range(int(qtd)):
        st.write(f"**Item {i+1}:**")
        loc_col, obs_col = st.columns([1, 2])
        amb = loc_col.text_input(f"Ambiente", key=f"amb_v35_{i}")
        nota = obs_col.text_input(f"Obs. Técnica", key=f"nota_v35_{i}")
        pecas_detalhes.append({"ambiente": amb, "obs": nota})
        
    if st.button("💾 Adicionar ao Orçamento"):
        st.session_state.db_projetos.append({
            "linha": linha_p, "tipo": tipo_p, "cor": cor_p, "vidro": f"{esp_v} {cor_v}",
            "larg": larg, "alt": alt, "qtd": qtd, "detalhes": pecas_detalhes
        })
        st.success("Adicionado!")

# --- ABA 7: CUSTOS (MATRIZ DE VIDROS, PERFIS E ACESSÓRIOS) ---
with tabs[6]:
    st.header("⚙️ Configuração de Preços de Compra")
    
    # ÁREA 1: MATRIZ DE VIDROS
    st.markdown("<h3 class='section-title'>🖼️ Matriz de Vidros (R$/m²)</h3>", unsafe_allow_html=True)
    for cv, espessuras in st.session_state.custo_vidros.items():
        st.write(f"**Vidro {cv}**")
        cols = st.columns(3)
        for i, (esp, preco) in enumerate(espessuras.items()):
            st.session_state.custo_vidros[cv][esp] = cols[i].number_input(f"{esp}", value=preco, key=f"v_v35_{cv}_{esp}")

    # ÁREA 2: PERFIS DE ALUMÍNIO
    st.markdown("<h3 class='section-title'>📊 Perfis por Linha (Peso e R$/KG)</h3>", unsafe_allow_html=True)
    linha_edit = st.selectbox("Selecione a Linha para Editar Perfis", list(st.session_state.custo_perfis.keys()))
    for perf, dados in st.session_state.custo_perfis[linha_edit].items():
        col_p1, col_p2, col_p3 = st.columns([2, 1, 1])
        col_p1.write(f"**Perfil:** {perf}")
        st.session_state.custo_perfis[linha_edit][perf]["peso"] = col_p2.number_input(f"Peso (kg/m)", value=dados["peso"], key=f"p_w_{perf}", format="%.3f")
        st.session_state.custos_gerais_p = col_p3.number_input(f"Preço KG", value=dados["preco"], key=f"p_v_{perf}")

    # ÁREA 3: ACESSÓRIOS ITEM A ITEM
    st.markdown("<h3 class='section-title'>🔩 Acessórios e Ferragens (Unitário)</h3>", unsafe_allow_html=True)
    for idx, ac in enumerate(st.session_state.custo_acessorios):
        col_a1, col_a2 = st.columns([3, 1])
        col_a1.write(f"**Item:** {ac['item']}")
        st.session_state.custo_acessorios[idx]["valor"] = col_a2.number_input(f"Valor Unitário", value=ac['valor'], key=f"ac_{idx}")

# --- ABA 3: ORÇAMENTO (COM EXCLUSÃO INDIVIDUAL) ---
with tabs[2]:
    st.header("💰 Resumo do Pedido")
    if st.session_state.db_projetos:
        for idx, p in enumerate(st.session_state.db_projetos):
            col_info, col_del = st.columns([5, 1])
            col_info.markdown(f"""
            <div class='card-projeto'>
                <strong>{p['tipo']} ({p['linha']})</strong> | {p['larg']}x{p['alt']}mm<br>
                Vidro: {p['vidro']} | Qtd: {p['qtd']}
            </div>
            """, unsafe_allow_html=True)
            if col_del.button("🗑️ Apagar", key=f"del_v35_{idx}"):
                st.session_state.db_projetos.pop(idx)
                st.rerun()
    else:
        st.info("Orçamento vazio.")
