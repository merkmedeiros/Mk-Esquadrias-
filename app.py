import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO VISUAL (CORES: AMARELO, CINZA, PRETO) ---
st.set_page_config(page_title="Esquadplan - Gestão de Esquadrias", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stApp { color: #333333; }
    /* Estilização das abas */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #e0e0e0;
        border-radius: 5px 5px 0px 0px;
        padding: 10px 20px;
        color: #000000;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffeb3b !important; /* Amarelo */
        font-weight: bold;
    }
    /* Botões */
    .stButton>button {
        background-color: #212121; /* Preto */
        color: #ffeb3b; /* Amarelo */
        border-radius: 5px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #ffeb3b;
        color: #212121;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAÇÃO ---
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []
if 'obras_fechadas' not in st.session_state:
    st.session_state.obras_fechadas = []

# --- CABEÇALHO DA EMPRESA (LOGO E DADOS) ---
with st.container():
    col_logo, col_dados = st.columns([1, 3])
    with col_logo:
        # Espaço para sua Logo - Substitua o link abaixo pela sua imagem
        st.image("https://via.placeholder.com/150x80.png?text=LOGO+AQUI", width=150)
    with col_dados:
        st.title("📐 ESQUADPLAN")
        st.caption("Sua Empresa de Esquadrias & Vidros | CNPJ: 00.000.000/0001-00 | Contato: (00) 0000-0000")

st.divider()

# --- ABAS ---
tab_cli, tab_config, tab_orc, tab_est, tab_obr = st.tabs([
    "👤 1. DADOS DO CLIENTE", 
    "🛠️ 2. TIPOLOGIA E MEDIDAS", 
    "📑 3. ORÇAMENTO (CARRINHO)", 
    "📦 4. ESTOQUE", 
    "📋 5. HISTÓRICO"
])

# --- ABA 1: DADOS DO CLIENTE DETALHADOS ---
with tab_cli:
    st.header("Ficha Cadastral do Cliente")
    
    with st.container():
        c1, c2, c3 = st.columns([2, 1, 1])
        st.session_state.cli_nome = c1.text_input("Nome Completo / Razão Social")
        st.session_state.cli_tel = c2.text_input("Telefone / WhatsApp")
        st.session_state.cli_email = c3.text_input("E-mail")

    with st.expander("📍 Endereço de Cobrança / Obra", expanded=True):
        e1, e2, e3 = st.columns([1, 2, 1])
        st.session_state.cli_cep = e1.text_input("CEP")
        st.session_state.cli_end = e2.text_input("Endereço (Rua/Av)")
        st.session_state.cli_num = e3.text_input("Número")
        
        e4, e5, e6 = st.columns([1, 1, 1])
        st.session_state.cli_comp = e4.text_input("Complemento")
        st.session_state.cli_bairro = e5.text_input("Bairro")
        st.session_state.cli_cid = e6.text_input("Cidade/UF")

    st.session_state.cli_entrega = st.text_area("Endereço de Entrega (Se diferente do cadastro)")
    st.session_state.cli_obs = st.text_area("Observações Gerais da Obra")

# --- ABA 2: TIPOLOGIA E MEDIDAS ---
with tab_config:
    st.header("Configuração de Itens")
    
    col_amb, col_inst, col_qtd = st.columns([2, 1, 1])
    amb = col_amb.text_input("Ambiente (Ex: Sacada, Quarto 01)", "Sala")
    inst = col_inst.selectbox("Tipo de Instalação", ["Contra-marco", "Bucha e Parafuso", "Kit Box", "Espelho Colado"])
    qtd = col_qtd.number_input("Quantidade", min_value=1, value=1)

    st.divider()
    
    col_t1, col_t2 = st.columns([1, 2])
    with col_t1:
        cat = st.radio("Categoria", ["Linha Suprema", "Box Temperado", "Espelhos"])
        tipo = st.selectbox("Modelo", ["Janela 2 Fls", "Janela 4 Fls", "Box Padrão", "Espelho Bisotê"])
    with col_t2:
        larg = st.number_input("Largura (mm)", value=1000)
        alt = st.number_input("Altura (mm)", value=1000)
        cor = st.selectbox("Cor Alumínio/Kit", ["Preto", "Branco", "Natural", "Bronze"])

    if st.button("➕ ADICIONAR ITEM AO ORÇAMENTO", use_container_width=True):
        cm_medida = f"{larg+44}x{alt+44}" if inst == "Contra-marco" else "N/A"
        item = {
            "Ambiente": amb, "Tipologia": f"{cat} {tipo}", "Medida": f"{larg}x{alt}",
            "Qtd": qtd, "Instalação": inst, "Contra-marco": cm_medida, "Cor": cor
        }
        st.session_state.carrinho.append(item)
        st.success(f"Item {amb} adicionado!")
        st.rerun()

# --- ABA 3: ORÇAMENTO (CARRINHO) ---
with tab_orc:
    st.header("📋 Orçamento: " + (st.session_state.get('cli_nome') if st.session_state.get('cli_nome') else "Cliente Novo"))
    
    if st.session_state.carrinho:
        df_orc = pd.DataFrame(st.session_state.carrinho)
        st.table(df_orc)
        
        st.divider()
        st.subheader("Informações do Cliente no Orçamento")
        st.text(f"Endereço: {st.session_state.get('cli_end')}, {st.session_state.get('cli_num')} - {st.session_state.get('cli_bairro')}")
        st.text(f"Observações: {st.session_state.get('cli_obs')}")

        c_o1, c_o2 = st.columns(2)
        if c_o1.button("🗑️ CANCELAR ORÇAMENTO"):
            st.session_state.carrinho = []
            st.rerun()
        if c_o2.button("🚀 FINALIZAR E SALVAR PEDIDO"):
            obra_final = {
                "Cliente": st.session_state.cli_nome,
                "Data": datetime.now().strftime("%d/%m/%Y"),
                "Itens": st.session_state.carrinho.copy(),
                "Dados_Cliente": {
                    "Tel": st.session_state.cli_tel,
                    "End": st.session_state.cli_end,
                    "Obs": st.session_state.cli_obs
                }
            }
            st.session_state.obras_fechadas.append(obra_final)
            st.session_state.carrinho = []
            st.success("Pedido registrado com sucesso!")
            st.rerun()
    else:
        st.warning("Adicione itens na aba anterior para gerar o orçamento.")

# --- ABA 4 E 5 (SIMPLIFICADAS PARA MANTER O FLUXO) ---
with tab_est:
    st.header("Estoque Esquadplan")
    st.info("Aqui você poderá ver as quantidades de perfis e vidros.")

with tab_obr:
    st.header("Histórico de Pedidos")
    for ob in st.session_state.obras_fechadas:
        with st.expander(f"Pedido: {ob['Cliente']} - {ob['Data']}"):
            st.table(pd.DataFrame(ob['Itens']))
