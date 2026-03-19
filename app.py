import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Esquadplan - Gestão Integrada", layout="wide")

# --- INICIALIZAÇÃO DO BANCO DE DATOS ---
if 'banco_clientes' not in st.session_state:
    st.session_state.banco_clientes = []
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []
if 'vendas_fechadas' not in st.session_state:
    st.session_state.vendas_fechadas = []
if 'estoque' not in st.session_state:
    st.session_state.estoque = {
        "Alumínio (kg)": {"qtd": 0.0, "custo": 0.0},
        "Vidro (m2)": {"qtd": 0.0, "custo": 0.0},
        "Acessórios (un)": {"qtd": 0, "custo": 0.0}
    }

# --- CABEÇALHO ---
st.title("📐 ESQUADPLAN")
st.caption("Sistema Completo: Cadastro, Tipologia e Financeiro")
st.divider()

# --- ABAS ---
tab_cli, tab_crm, tab_tip, tab_orc, tab_fin, tab_est = st.tabs([
    "👤 1. CADASTRO", 
    "📇 2. GESTÃO CLIENTES", 
    "🛠️ 3. TIPOLOGIA", 
    "📑 4. ORÇAMENTO", 
    "💰 5. FINANCEIRO/HISTÓRICO",
    "📦 6. ESTOQUE"
])

# --- ABA 1: CADASTRO DE CLIENTE ---
with tab_cli:
    st.header("Novo Cadastro de Cliente")
    with st.form("form_novo_cliente"):
        c1, c2, c3 = st.columns([2, 1, 1])
        nome = c1.text_input("Nome/Razão Social")
        tel = c2.text_input("WhatsApp")
        email = c3.text_input("E-mail")
        
        e1, e2, e3, e4 = st.columns([1, 2, 1, 1])
        cep = e1.text_input("CEP")
        rua = e2.text_input("Endereço")
        num = e3.text_input("Nº")
        bairro = e4.text_input("Bairro")
        
        obs_cli = st.text_area("Observações Adicionais")
        
        if st.form_submit_button("💾 SALVAR CLIENTE"):
            if nome:
                st.session_state.banco_clientes.append({
                    "Nome": nome, "WhatsApp": tel, "Endereço": f"{rua}, {num} - {bairro}", 
                    "Status": "Em Aberto", "Cadastro": datetime.now().strftime("%d/%m/%Y")
                })
                st.success(f"Cliente {nome} cadastrado!")
            else: st.error("Nome é obrigatório.")

# --- ABA 2: CRM (GESTÃO) ---
with tab_crm:
    st.header("Banco de Dados de Contatos")
    if st.session_state.banco_clientes:
        st.dataframe(pd.DataFrame(st.session_state.banco_clientes), use_container_width=True)
    else: st.info("Sem clientes cadastrados.")

# --- ABA 3: TIPOLOGIA ---
with tab_tip:
    st.header("Adicionar Peças ao Orçamento")
    if st.session_state.banco_clientes:
        selecionado = st.selectbox("Para qual cliente é este orçamento?", [c['Nome'] for c in st.session_state.banco_clientes])
        
        col1, col2, col3 = st.columns([2, 1, 1])
        ambiente = col1.text_input("Ambiente", "Sala")
        tipo = col2.selectbox("Peça", ["Janela Suprema", "Box", "Espelho", "Porta"])
        inst = col3.selectbox("Instalação", ["Contra-marco", "Bucha/Parafuso", "Kit Box"])
        
        l = st.number_input("Largura (mm)", value=1000)
        h = st.number_input("Altura (mm)", value=1000)
        preco_item = st.number_input("Valor sugerido para esta peça (R$)", value=0.0)
        
        if st.button("➕ ADICIONAR ITEM"):
            st.session_state.carrinho.append({
                "Cliente": selecionado, "Ambiente": ambiente, "Peça": tipo, 
                "Medida": f"{l}x{h}", "Instalação": inst, "Valor": preco_item
            })
            st.toast("Item adicionado!")
    else: st.warning("Cadastre um cliente primeiro!")

# --- ABA 4: ORÇAMENTO & FECHAMENTO (AQUI VOLTOU O FINANCEIRO) ---
with tab_orc:
    st.header("🛒 Orçamento em Aberto")
    if st.session_state.carrinho:
        df_c = pd.DataFrame(st.session_state.carrinho)
        st.table(df_c)
        
        total_bruto = df_c["Valor"].sum()
        st.subheader(f"Subtotal: R$ {total_bruto:.2f}")
        
        st.divider()
        st.subheader("💳 Formas de Pagamento e Fechamento")
        
        f1, f2, f3 = st.columns(3)
        forma_pgto = f1.selectbox("Meio de Pagamento", ["Pix", "Dinheiro", "Cartão Crédito", "Cartão Débito", "Boleto", "Outros"])
        desc = f2.number_input("Desconto (R$)", value=0.0)
        parc = f3.number_input("Parcelamento (Vezes)", min_value=1, max_value=12, value=1)
        
        valor_final = total_bruto - desc
        st.metric("VALOR A COBRAR", f"R$ {valor_final:.2f}")
        
        if st.button("✅ FECHAR PEDIDO AGORA"):
            venda = {
                "Cliente": df_c["Cliente"].iloc[0],
                "Data": datetime.now().strftime("%d/%m/%Y"),
                "Itens": st.session_state.carrinho.copy(),
                "Total": valor_final,
                "Forma": forma_pgto,
                "Parcelas": parc
            }
            st.session_state.vendas_fechadas.append(venda)
            # Atualiza status no banco de clientes
            for c in st.session_state.banco_clientes:
                if c['Nome'] == venda['Cliente']: c['Status'] = "Fechado"
            
            st.session_state.carrinho = []
            st.success("Pedido fechado e enviado para o Financeiro!")
            st.rerun()
    else: st.info("Carrinho vazio.")

# --- ABA 5: FINANCEIRO & HISTÓRICO ---
with tab_fin:
    st.header("📊 Fluxo Financeiro e Obras Fechadas")
    if st.session_state.vendas_fechadas:
        for v in st.session_state.vendas_fechadas:
            with st.expander(f"💰 {v['Cliente']} | {v['Data']} | R$ {v['Total']:.2f}"):
                st.write(f"**Pagamento:** {v['Forma']} em {v['Parcelas']}x")
                st.table(pd.DataFrame(v['Itens']))
    else: st.info("Nenhuma venda realizada.")

# --- ABA 6: ESTOQUE ---
with tab_est:
    st.header("📦 Almoxarifado")
    st.write(st.session_state.estoque)
