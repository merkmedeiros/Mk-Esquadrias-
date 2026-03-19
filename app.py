import streamlit as st
import pandas as pd
import math

# 1. CONFIGURAÇÃO DE IDENTIDADE MK
st.set_page_config(page_title="MK - Engenharia v31.0", layout="wide")

# Inicialização do Banco de Dados Temporário
if 'db_clientes' not in st.session_state: st.session_state.db_clientes = []
if 'db_projetos' not in st.session_state: st.session_state.db_projetos = []
if 'db_obras' not in st.session_state: st.session_state.db_obras = []

# Matriz de Custos e Pesos (v31.0)
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

if 'custos_gerais' not in st.session_state:
    st.session_state.custos_gerais = {"p_branco": 45.0, "p_preto": 55.0}

# ESTILO VISUAL MK
st.markdown("""
    <style>
    .stButton>button { background-color: #1e3a8a; color: white; font-weight: bold; width: 100%; }
    .card-projeto { border: 1px solid #1e3a8a; padding: 15px; border-radius: 8px; background: #fff; margin-bottom: 10px; }
    .obs-box { font-style: italic; color: #555; font-size: 0.9em; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚒️ MK - GESTÃO E ENGENHARIA v31.0")

# --- NAVEGAÇÃO POR ABAS ---
tabs = st.tabs(["📍 Cliente", "📏 Projeto", "💰 Orçamento", "🏭 Produção", "🚚 Instalação", "🚧 Gestão Obras", "📦 Estoque", "⚙️ Custos"])

# --- ABA 1: CLIENTE (10 CAMPOS) ---
with tabs[0]:
    st.header("👥 Cadastro de Cliente")
    with st.form("cli_v31"):
        c1, c2 = st.columns(2); nome = c1.text_input("Nome"); email = c2.text_input("E-mail")
        tel = c1.text_input("Telefone"); wpp = c2.text_input("WhatsApp")
        st.divider(); cep = c1.text_input("CEP"); log = c2.text_input("Logradouro")
        bai, cid = st.columns(2); bairro = bai.text_input("Bairro"); cidade = cid.text_input("Cidade/UF")
        ref = st.text_input("Ponto de Referência"); obra = st.text_input("Endereço da Obra")
        if st.form_submit_button("Salvar Cliente"):
            st.session_state.db_clientes.append({"nome": nome, "obra": obra if obra else log, "ref": ref, "wpp": wpp})

# --- ABA 2: PROJETO (EDIÇÃO E OBSERVAÇÕES POR PEÇA) ---
with tabs[1]:
    st.header("📐 Configuração de Projeto")
    col1, col2, col3 = st.columns(3)
    linha = col1.selectbox("Linha", list(st.session_state.tab_perfis.keys()))
    tipo = col2.selectbox("Tipologia", ["Janela 2fls", "Janela 4fls", "Porta Giro", "Fixo"])
    cor = col3.selectbox("Cor Alumínio", ["Branco", "Preto"])
    
    st.subheader("💎 Seleção de Vidro")
    c_v, e_v = st.columns(2)
    cor_vidro = c_v.selectbox("Cor Vidro", list(st.session_state.custo_vidros.keys()))
    esp_vidro = e_v.selectbox("Espessura", list(st.session_state.custo_vidros[cor_vidro].keys()))
    
    st.divider()
    l_p, a_p, q_p = st.columns(3)
    larg = l_p.number_input("Largura (mm)", step=1); alt = a_p.number_input("Altura (mm)", step=1); qtd = q_p.number_input("Quantidade", min_value=1)
    
    st.subheader("📍 Detalhes por Peça")
    pecas_info = []
    for i in range(int(qtd)):
        st.markdown(f"**Item {i+1}**")
        loc_col, obs_col = st.columns([1, 2])
        loc = loc_col.text_input(f"Ambiente", key=f"loc_{i}", placeholder="Ex: Cozinha")
        observacao = obs_col.text_input(f"Observação Técnica", key=f"obs_{i}", placeholder="Ex: Vidro com furo")
        pecas_info.append({"ambiente": loc, "nota": observacao})
        
    if st.button("💾 Adicionar Projeto"):
        # Cálculos de Vidro
        v_h = alt - 160 if "Janela" in tipo else alt - 40
        v_l = (larg/2) - 95 if "2fls" in tipo else larg - 50
        
        st.session_state.db_projetos.append({
            "id": len(st.session_state.db_projetos),
            "linha": linha, "tipo": tipo, "cor": cor, "vidro_cor": cor_vidro, "vidro_esp": esp_vidro,
            "larg": larg, "alt": alt, "qtd": qtd, "detalhes": pecas_info,
            "v_h": v_h, "v_l": v_l
        })
        st.success("Projeto adicionado!")

# --- ABA 3: ORÇAMENTO (EDITÁVEL E SALVAMENTO) ---
with tabs[2]:
    st.header("💰 Gerenciamento de Itens e Custos")
    if st.session_state.db_projetos:
        custo_acumulado = 0
        for idx, p in enumerate(st.session_state.db_projetos):
            with st.container():
                st.markdown(f"""
                <div class='card-projeto'>
                    <strong>{p['tipo']} - {p['linha']} ({p['qtd']} un)</strong><br>
                    Medida: {p['larg']}x{p['alt']}mm | Vidro: {p['vidro_esp']} {p['vidro_cor']}
                </div>
                """, unsafe_allow_html=True)
                
                # Botões de Edição/Remoção
                c_edit, c_del = st.columns([1, 1])
                if c_del.button(f"🗑️ Remover Item {idx+1}", key=f"del_{idx}"):
                    st.session_state.db_projetos.pop(idx)
                    st.rerun()
                
                if c_edit.button(f"✏️ Editar Medidas Item {idx+1}", key=f"edit_{idx}"):
                    st.warning("Para editar, altere os valores na Aba 'Projeto' e adicione novamente. Remova este item após a correção.")

        st.divider()
        margem = st.slider("Margem de Lucro (%)", 0, 200, 100)
        if st.button("🚀 Confirmar e Salvar Pedido Final"):
            st.session_state.db_obras.append({"cliente": "Novo Pedido", "data": "Hoje", "status": "A Iniciar"})
            st.success("Pedido Salvo na Gestão de Obras!")
    else:
        st.info("Nenhum projeto pendente.")

# --- ABA 4: PRODUÇÃO (EXIBIÇÃO DAS OBSERVAÇÕES) ---
with tabs[3]:
    st.header("🏭 Ordem de Fábrica")
    for p in st.session_state.db_projetos:
        st.write(f"### Peça: {p['tipo']} - {p['larg']}x{p['alt']}")
        for d in p['detalhes']:
            st.write(f"👉 **{d['ambiente']}**: {d['nota']}")

# --- ABA 8: CUSTOS (MATRIZ PRESERVADA) ---
with tabs[7]:
    st.header("⚙️ Configuração de Custos")
    with st.expander("Vidros (m²)", expanded=True):
        for cv, espessuras in st.session_state.custo_vidros.items():
            st.write(f"**{cv}**")
            cols = st.columns(3)
            for i, (esp, preco) in enumerate(espessuras.items()):
                st.session_state.custo_vidros[cv][esp] = cols[i].number_input(f"{esp}", value=preco, key=f"c_{cv}_{esp}")
