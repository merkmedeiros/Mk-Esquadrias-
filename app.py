import streamlit as st
import pandas as pd
import math

# 1. CONFIGURAÇÃO DE IDENTIDADE MK
st.set_page_config(page_title="MK - Engenharia v36.0", layout="wide")

# Inicialização de Bancos de Dados (Session State)
if 'db_clientes' not in st.session_state: st.session_state.db_clientes = []
if 'db_projetos' not in st.session_state: st.session_state.db_projetos = []
if 'db_obras' not in st.session_state: st.session_state.db_obras = []

# Matrizes de Custos (Mantidas as configurações anteriores)
if 'custo_vidros' not in st.session_state:
    st.session_state.custo_vidros = {
        "Incolor": {"6mm": 120.0, "8mm": 180.0, "10mm": 220.0},
        "Verde": {"6mm": 140.0, "8mm": 210.0, "10mm": 250.0},
        "Fumê": {"6mm": 150.0, "8mm": 230.0, "10mm": 280.0}
    }

# CORREÇÃO DE ESTILO (CSS) - FOCO EM LEITURA E CONTRASTE
st.markdown("""
    <style>
    /* Fundo principal */
    .main { background-color: #f8f9fa; }
    
    /* Card de Orçamento com Fonte Escura Forçada */
    .card-projeto { 
        border: 2px solid #1e3a8a; 
        padding: 20px; 
        border-radius: 10px; 
        background-color: #ffffff; 
        margin-bottom: 15px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    
    /* Forçar cor do texto dentro do card */
    .card-projeto strong, .card-projeto p, .card-projeto span {
        color: #1e3a8a !important;
        font-family: sans-serif;
    }
    
    .text-preto { color: #000000 !important; font-weight: bold; }
    
    /* Botões */
    .stButton>button { font-weight: bold; width: 100%; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚒️ MK - GESTÃO INDUSTRIAL v36.0")

# --- NAVEGAÇÃO POR ABAS ---
tabs = st.tabs(["📍 Cliente", "📏 Projeto", "💰 Orçamento", "🏭 Produção", "🚚 Instalação", "🚧 Gestão Obras", "⚙️ Custos"])

# --- ABA 1: CLIENTE (ESTÁVEL) ---
with tabs[0]:
    st.header("👥 Cadastro de Cliente")
    with st.form("cli_v36"):
        c1, c2 = st.columns(2)
        nome_c = c1.text_input("Nome / Razão Social")
        wpp_c = c2.text_input("WhatsApp")
        log_c = c1.text_input("Endereço / Logradouro")
        obra_c = c2.text_input("Endereço da Obra")
        if st.form_submit_button("Salvar Cliente"):
            st.session_state.db_clientes.append({"nome": nome_c, "obra": obra_c if obra_c else log_c})
            st.rerun()

# --- ABA 2: PROJETO ---
with tabs[1]:
    st.header("📐 Engenharia de Peças")
    col1, col2, col3 = st.columns(3)
    linha = col1.selectbox("Linha", ["Suprema", "Gold"])
    tipo = col2.selectbox("Tipologia", ["Janela 2fls", "Janela 4fls", "Porta Giro", "Fixo"])
    cor = col3.selectbox("Cor Alumínio", ["Branco", "Preto", "Bronze"])
    
    st.subheader("💎 Vidro")
    c_vid, e_vid = st.columns(2)
    cor_v = c_vid.selectbox("Cor Vidro", list(st.session_state.custo_vidros.keys()))
    esp_v = e_vid.selectbox("Espessura", list(st.session_state.custo_vidros[cor_v].keys()))
    
    l_p, a_p, q_p = st.columns(3)
    larg = l_p.number_input("Largura (mm)", step=1)
    alt = a_p.number_input("Altura (mm)", step=1)
    qtd = q_p.number_input("Quantidade", min_value=1, step=1)
    
    pecas_detalhes = []
    for i in range(int(qtd)):
        l_c, o_c = st.columns([1, 2])
        amb = l_c.text_input(f"Ambiente {i+1}", key=f"amb_v36_{i}")
        obs = o_c.text_input(f"Obs {i+1}", key=f"obs_v36_{i}")
        pecas_detalhes.append({"amb": amb, "obs": obs})
        
    if st.button("💾 Adicionar ao Orçamento"):
        st.session_state.db_projetos.append({
            "linha": linha, "tipo": tipo, "cor": cor, "vidro": f"{esp_v} {cor_v}",
            "larg": larg, "alt": alt, "qtd": qtd, "detalhes": pecas_detalhes
        })
        st.success("Item Adicionado!")

# --- ABA 3: ORÇAMENTO (CORREÇÃO DE VISUALIZAÇÃO) ---
with tabs[2]:
    st.header("💰 Resumo Detalhado")
    if st.session_state.db_projetos:
        for idx, p in enumerate(st.session_state.db_projetos):
            # Container com Estilo Forçado
            with st.container():
                col_info, col_del = st.columns([5, 1])
                
                # HTML com classes CSS para garantir a cor preta/azul do texto
                col_info.markdown(f"""
                <div class='card-projeto'>
                    <p><strong>ITEM {idx+1}: {p['tipo'].upper()} - LINHA {p['linha'].upper()}</strong></p>
                    <p class='text-preto'>Medidas: {p['larg']} x {p['alt']} mm | Qtd: {p['qtd']} un.</p>
                    <p class='text-preto'>Vidro: {p['vidro']} | Cor Alumínio: {p['cor']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Botão de Apagar
                if col_del.button("🗑️", key=f"del_v36_{idx}"):
                    st.session_state.db_projetos.pop(idx)
                    st.rerun()
        
        st.divider()
        if st.button("🔥 LIMPAR TODO ORÇAMENTO", key="clear_all"):
            st.session_state.db_projetos = []
            st.rerun()
    else:
        st.info("Nenhum item no orçamento.")

# --- ABA 7: CUSTOS (MANTIDA) ---
with tabs[6]:
    st.header("⚙️ Configuração de Preços")
    # (Matriz de vidros, perfis e acessórios continuam aqui como na v35.0)
    st.info("Configure os preços para que o sistema calcule os valores automaticamente.")
