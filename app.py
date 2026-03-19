import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA E ESTILO VISUAL ---
st.set_page_config(page_title="Esquadplan", layout="wide")

# CSS Simples para as cores: Amarelo, Cinza e Preto
st.markdown("""
    <style>
    /* Cor de fundo geral */
    .stApp { background-color: #FFFFFF; }
    
    /* Customização das Abas */
    button[data-baseweb="tab"] {
        color: #000000 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #FFD700 !important; /* Amarelo Ouro */
        border-radius: 5px;
        font-weight: bold;
    }
    
    /* Botões em Preto com texto Amarelo */
    .stButton>button {
        background-color: #000000;
        color: #FFD700;
        border: 1px solid #000000;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #333333;
        color: #FFD700;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAÇÃO DO ESTADO ---
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []
if 'obras_fechadas' not in st.session_state:
    st.session_state.obras_fechadas = []
if 'estoque' not in st.session_state:
    st.session_state.estoque = {
        "Perfil Aluminio (kg)": {"qtd": 0.0, "custo_unit": 0.0},
        "Vidro Temperado (m2)": {"qtd": 0.0, "custo_unit": 0.0},
        "Componentes/Kits (un)": {"qtd": 0, "custo_unit": 0.0}
    }

# --- TOPO DA PÁGINA ---
col_l, col_r = st.columns([1, 4])
with col_l:
    st.subheader("📏 ESQUADPLAN")
with col_r:
    st.write("**Dados da Empresa:** Sua Serralheria & Vidraçaria | CNPJ: 00.000.000/0001-00")
    st.write("Endereço: Sua Rua, 123 - Cidade/UF | Contato: (00) 00000-0000")

st.divider()

# --- ABAS ---
tab_cli, tab_tip, tab_orc, tab_est, tab_his = st.tabs([
    "👤 CLIENTE", "🛠️ TIPOLOGIA", "📑 ORÇAMENTO", "📦 ESTOQUE", "📋 HISTÓRICO"
])

# --- ABA 1: DADOS DO CLIENTE ---
with tab_cli:
    st.subheader("Cadastro do Cliente")
    c1, c2, c3 = st.columns([2, 1, 1])
    nome = c1.text_input("Nome/Razão Social", key="cli_nome")
    tel = c2.text_input("Telefone/WhatsApp", key="cli_tel")
    email = c3.text_input("E-mail", key="cli_email")

    st.markdown("**Endereço de Cadastro**")
    e1, e2, e3, e4 = st.columns([1, 2, 1, 1])
    cep = e1.text_input("CEP")
    rua = e2.text_input("Logradouro (Rua/Av)")
    num = e3.text_input("Nº")
    comp = e4.text_input("Comp.")

    e5, e6, e7 = st.columns([1, 1, 1])
    bairro = e5.text_input("Bairro")
    cidade = e6.text_input("Cidade")
    st.session_state.entrega = e7.text_input("Endereço de Entrega (se diferente)")
    
    st.session_state.obs = st.text_area("Observações da Obra")

# --- ABA 2: TIPOLOGIA E MEDIDAS ---
with tab_tip:
    st.subheader("Configuração das Peças")
    
    r1_1, r1_2, r1_3 = st.columns([2, 1, 1])
    ambiente = r1_1.text_input("Ambiente (Ex: Cozinha)", "Sala")
    instalacao = r1_2.selectbox("Instalação", ["Bucha/Parafuso", "Contra-marco", "Kit Box", "Colado"])
    qtd = r1_3.number_input("Quantidade", min_value=1, value=1)

    st.divider()
    
    r2_1, r2_2, r2_3, r2_4 = st.columns([2, 1, 1, 1])
    cat = r2_1.selectbox("Categoria", ["Linha Suprema", "Temperado", "Espelho", "Box"])
    largura = r2_2.number_input("Largura (mm)", value=1000)
    altura = r2_3.number_input("Altura (mm)", value=1000)
    cor = r2_4.selectbox("Cor", ["Preto", "Branco", "Natural", "Bronze"])

    if st.button("➕ ADICIONAR AO ORÇAMENTO"):
        # Cálculo básico de contra-marco
        cm = f"{largura+44}x{altura+44}" if instalacao == "Contra-marco" else "N/A"
        
        item = {
            "Ambiente": ambiente,
            "Item": f"{cat} - {cor}",
            "Medida": f"{largura}x{altura}",
            "Qtd": qtd,
            "Instalacao": instalacao,
            "Contra-marco": cm
        }
        st.session_state.carrinho.append(item)
        st.toast("Item adicionado!")

# --- ABA 3: ORÇAMENTO (CARRINHO) ---
with tab_orc:
    st.subheader(f"Orçamento para: {nome if nome else 'Novo Cliente'}")
    
    if st.session_state.carrinho:
        df_orc = pd.DataFrame(st.session_state.carrinho)
        st.table(df_orc)
        
        st.write(f"**Observações:** {st.session_state.get('obs', '')}")
        st.write(f"**Endereço de Entrega:** {st.session_state.get('entrega', 'Mesmo do cadastro')}")

        col_b1, col_b2 = st.columns(2)
        if col_b1.button("🗑️ LIMPAR TUDO"):
            st.session_state.carrinho = []
            st.rerun()
            
        if col_b2.button("🚀 SALVAR PEDIDO"):
            pedido = {
                "Cliente": nome, "Data": datetime.now().strftime("%d/%m/%Y"),
                "Itens": st.session_state.carrinho.copy()
            }
            st.session_state.obras_fechadas.append(pedido)
            st.session_state.carrinho = []
            st.success("Pedido Salvo!")
            st.rerun()
    else:
        st.info("O orçamento está vazio.")

# --- ABA 4: ESTOQUE E CUSTO ---
with tab_est:
    st.subheader("Gestão de Estoque e Preço de Compra")
    
    # Tabela de visualização de estoque
    df_est = pd.DataFrame.from_dict(st.session_state.estoque, orient='index')
    st.table(df_est)

    with st.expander("📥 Registrar Compra (Entrada de Material)"):
        it_compra = st.selectbox("Material Comprado", list(st.session_state.estoque.keys()))
        qtd_compra = st.number_input("Quantidade Comprada", min_value=0.0)
        preco_compra = st.number_input("Preço de Custo Total Pago (R$)", min_value=0.0)
        
        if st.button("Salvar Entrada"):
            unit = preco_compra / qtd_compra if qtd_compra > 0 else 0
            st.session_state.estoque[it_compra]['qtd'] += qtd_compra
            st.session_state.estoque[it_compra]['custo_unit'] = unit
            st.success("Estoque Atualizado!")
            st.rerun()
