import streamlit as st
import pandas as pd

# 1. CONFIGURAÇÃO DE IDENTIDADE MK
st.set_page_config(page_title="MK - Esquadrias & Vidros", layout="wide")

# Inicialização do Banco de Dados Temporário (Session State)
if 'db_clientes' not in st.session_state: st.session_state.db_clientes = []
if 'db_obras' not in st.session_state: st.session_state.db_obras = []
if 'custos' not in st.session_state: 
    st.session_state.custos = {"alu_b": 45.0, "alu_p": 55.0, "v8": 180.0, "v10": 220.0}

# ESTILO VISUAL
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    h1 { color: #1e3a8a; }
    .stButton>button { background-color: #1e3a8a; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# HEADER COM NOME DA EMPRESA
st.title("⚒️ MK - SISTEMA DE GESTÃO PROFISSIONAL")
st.sidebar.header("CONFIGURAÇÃO DA LOGO")
st.sidebar.info("Espaço reservado para carregar sua Logo MK")

# --- NAVEGAÇÃO POR ABAS (A DIRETRIZ IMUTÁVEL) ---
tabs = st.tabs([
    "📍 Cliente", "📏 Projeto", "💰 Orçamento", "🏭 Produção", 
    "🚚 Instalação", "🚧 Gestão Obras", "📦 Estoque", "⚙️ Custos"
])

# --- ABA 8: CONFIG. CUSTOS (PRECISA VIR ANTES PARA O CÁLCULO) ---
with tabs[7]:
    st.header("⚙️ Tabela de Custos Regionais")
    with st.form("edit_custos"):
        c1, c2 = st.columns(2)
        alu_b = c1.number_input("Alumínio Branco (R$/KG)", value=st.session_state.custos["alu_b"])
        alu_p = c2.number_input("Alumínio Preto (R$/KG)", value=st.session_state.custos["alu_p"])
        v8 = c1.number_input("Vidro 8mm (R$/m²)", value=st.session_state.custos["v8"])
        v10 = c2.number_input("Vidro 10mm (R$/m²)", value=st.session_state.custos["v10"])
        if st.form_submit_button("Salvar Preços da Região"):
            st.session_state.custos = {"alu_b": alu_b, "alu_p": alu_p, "v8": v8, "v10": v10}
            st.success("Preços atualizados!")

# --- ABA 1: CLIENTE ---
with tabs[0]:
    st.header("👥 Cadastro de Cliente & Obra")
    with st.form("cli_form"):
        c1, c2 = st.columns(2)
        nome = c1.text_input("Nome do Cliente")
        whats = c2.text_input("WhatsApp")
        cep = c1.text_input("CEP")
        end_obra = st.text_input("Endereço Completo da Obra")
        obs = st.text_area("Observações Adicionais")
        if st.form_submit_button("Salvar Cadastro"):
            st.session_state.db_clientes.append({"nome": nome, "whats": whats, "end": end_obra})
            st.success("Cliente registrado com sucesso!")

# --- ABA 2: PROJETO ---
with tabs[1]:
    st.header("📐 Engenharia de Peças")
    with st.container():
        col1, col2, col3 = st.columns(3)
        linha = col1.selectbox("Linha", ["Suprema", "Gold", "Box", "Temperado"])
        tipo = col2.selectbox("Tipologia", ["Janela 2fls", "Porta Giro", "Fixo", "Maxim-ar"])
        cor = col3.selectbox("Cor", ["Branco", "Preto"])
        
        col4, col5, col6 = st.columns(3)
        larg = col4.number_input("Largura (mm)", step=1)
        alt = col5.number_input("Altura (mm)", step=1)
        qtd = col6.number_input("Quantidade", min_value=1)
        
        local = st.text_input("Localização (Ex: Cozinha, Suíte)")
        fix = st.radio("Fixação", ["Bucha/Parafuso", "Contra-marco"], horizontal=True)
        
        if st.button("Adicionar ao Orçamento"):
            st.toast(f"Peça {tipo} adicionada!")

# --- ABA 3: ORÇAMENTO ---
with tabs[2]:
    st.header("💰 Fechamento Comercial")
    st.write("### Itens Selecionados")
    # Simulação de cálculo baseado nos custos da aba 8
    st.info(f"Custo Base Calculado (Alu: R${st.session_state.custos['alu_b'] if cor == 'Branco' else st.session_state.custos['alu_p']})")
    
    pag = st.selectbox("Forma de Pagamento", ["PIX", "Débito", "Crédito", "À Vista", "Parcelado"])
    if st.button("📄 Gerar Contrato e Finalizar"):
        st.session_state.db_obras.append({"cliente": nome, "status": "A Iniciar", "data": "19/03/2026"})
        st.success("Contrato Gerado! Pedido enviado para Produção.")

# --- ABA 4: PRODUÇÃO ---
with tabs[3]:
    st.header("🏭 Plano de Produção & Vidros")
    st.subheader("💎 Pedido de Vidros")
    v_col1, v_col2 = st.columns(2)
    esp = v_col1.selectbox("Espessura", ["6mm", "8mm", "10mm"])
    c_vidro = v_col2.selectbox("Cor Vidro", ["Incolor", "Verde", "Fumê", "Leitoso"])
    
    st.subheader("🪚 Plano de Corte (Perfis)")
    st.code("Exemplo: SU-001 | Corte: 1145mm | Qtd: 2 | Ângulo: 45°")

# --- ABA 5: INSTALAÇÃO ---
with tabs[4]:
    st.header("🚚 Romaneio de Instalação")
    st.write(f"**Cliente:** {nome} | **Local:** {end_obra}")
    st.table(pd.DataFrame({
        "Peça": ["Janela", "Porta"], "Medida": ["1200x1000", "800x2100"], "Local": ["Cozinha", "Entrada"]
    }))

# --- ABA 6: GESTÃO DE OBRAS ---
with tabs[5]:
    st.header("🚧 Controle de Status de Obras")
    status_opcoes = ["A Iniciar", "Em Execução", "Finalizada", "ATRASADO"]
    
    # Exibição de Obras com cores para o status ATRASADO
    for obra in st.session_state.db_obras:
        col_o, col_s = st.columns([3, 1])
        col_o.write(f"**Obra:** {obra['cliente']} | Data: {obra['data']}")
        status = col_s.selectbox("Alterar Status", status_opcoes, key=obra['cliente'])
        if status == "ATRASADO": st.error("🚨 ESTA OBRA ESTÁ EM ATRASO!")
        st.divider()

# --- ABA 7: ESTOQUE ---
with tabs[6]:
    st.header("📦 Almoxarifado")
    st.table(pd.DataFrame({"Material": ["Perfil Branco", "Roldana"], "Qtd": ["20kg", "50un"]}))

