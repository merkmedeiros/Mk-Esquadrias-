import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Esquadplan - Gestão Profissional", layout="wide")

# --- INICIALIZAÇÃO DO BANCO DE DADOS ---
if 'banco_clientes' not in st.session_state:
    st.session_state.banco_clientes = [] # Lista permanente de contatos
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []
if 'obras_fechadas' not in st.session_state:
    st.session_state.obras_fechadas = []

# --- CABEÇALHO ---
st.title("📐 ESQUADPLAN")
st.caption("Sistema de Gestão de Esquadrias e Vidros")
st.divider()

# --- ABAS ---
tabs = st.tabs([
    "👤 CADASTRO", 
    "📇 GESTÃO DE CLIENTES (CRM)", 
    "🛠️ TIPOLOGIA", 
    "📑 ORÇAMENTO", 
    "📦 ESTOQUE"
])
tab_cli, tab_crm, tab_tip, tab_orc, tab_est = tabs

# --- ABA 1: CADASTRO DE CLIENTE ---
with tab_cli:
    st.header("Novo Cadastro")
    with st.form("form_cliente"):
        c1, c2, c3 = st.columns([2, 1, 1])
        nome = c1.text_input("Nome/Razão Social")
        tel = c2.text_input("Telefone/WhatsApp")
        email = c3.text_input("E-mail")

        st.markdown("---")
        e1, e2, e3, e4 = st.columns([1, 2, 1, 1])
        cep = e1.text_input("CEP")
        rua = e2.text_input("Rua/Avenida")
        num = e3.text_input("Nº")
        comp = e4.text_input("Complemento")

        e5, e6, e7 = st.columns([1, 1, 1])
        bairro = e5.text_input("Bairro")
        cidade = e6.text_input("Cidade")
        status = e7.selectbox("Status Inicial", ["Orçamento", "Fechado", "Em Aberto", "Em Andamento"])
        
        obs = st.text_area("Observações para contatos futuros")
        
        btn_salvar = st.form_submit_button("💾 SALVAR/ADICIONAR CLIENTE")
        
        if btn_salvar:
            if nome:
                novo_cli = {
                    "Data Cadastro": datetime.now().strftime("%d/%m/%Y"),
                    "Nome": nome, "WhatsApp": tel, "E-mail": email,
                    "CEP": cep, "Endereço": f"{rua}, {num} - {bairro}",
                    "Cidade": cidade, "Status": status, "OBS": obs
                }
                st.session_state.banco_clientes.append(novo_cli)
                st.success(f"Cliente {nome} salvo com sucesso no banco de dados!")
            else:
                st.error("Por favor, preencha pelo menos o nome do cliente.")

# --- ABA 2: GESTÃO DE CLIENTES (CRM) ---
with tab_crm:
    st.header("Banco de Dados de Contatos")
    if st.session_state.banco_clientes:
        df_clientes = pd.DataFrame(st.session_state.banco_clientes)
        
        # Filtros para contatos futuros
        f1, f2 = st.columns(2)
        filtro_status = f1.multiselect("Filtrar por Status", ["Orçamento", "Fechado", "Em Aberto", "Em Andamento"], default=["Orçamento", "Em Aberto"])
        
        df_filtrado = df_clientes[df_clientes['Status'].isin(filtro_status)]
        
        st.dataframe(df_filtrado, use_container_width=True)
        
        st.write(f"Total de clientes na base: {len(df_clientes)}")
    else:
        st.info("Nenhum cliente cadastrado ainda.")

# --- ABA 3: TIPOLOGIA (SIMPLIFICADA) ---
with tab_tip:
    st.header("Configuração da Peça")
    # Selecionar cliente já cadastrado
    if st.session_state.banco_clientes:
        lista_nomes = [c['Nome'] for c in st.session_state.banco_clientes]
        cliente_selecionado = st.selectbox("Selecione o Cliente do Orçamento", lista_nomes)
    
    r1, r2 = st.columns(2)
    amb = r1.text_input("Ambiente", "Sala")
    tipo = r2.selectbox("Modelo", ["Janela Suprema", "Box Temperado", "Espelho"])
    
    larg = st.number_input("Largura (mm)", value=1000)
    alt = st.number_input("Altura (mm)", value=1000)
    
    if st.button("➕ ADICIONAR AO ORÇAMENTO ATUAL"):
        item = {"Cliente": cliente_selecionado, "Ambiente": amb, "Peça": tipo, "Medida": f"{larg}x{alt}"}
        st.session_state.carrinho.append(item)
        st.success("Item adicionado ao carrinho!")

# --- ABA 4: ORÇAMENTO (CARRINHO) ---
with tab_orc:
    st.header("Orçamento Atual")
    if st.session_state.carrinho:
        st.table(pd.DataFrame(st.session_state.carrinho))
        if st.button("🗑️ LIMPAR CARRINHO"):
            st.session_state.carrinho = []
            st.rerun()
    else:
        st.warning("Carrinho vazio.")

# --- ABA 5: ESTOQUE (SIMPLIFICADA) ---
with tab_est:
    st.header("Estoque")
    st.write("Controle de insumos e preços de custo.")
