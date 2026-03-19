import streamlit as st
import pandas as pd

# 1. CONFIGURAÇÃO DE IDENTIDADE MK
st.set_page_config(page_title="MK - Esquadrias & Vidros", layout="wide")

# Inicialização do Banco de Dados Temporário (Session State)
if 'db_clientes' not in st.session_state: st.session_state.db_clientes = []
if 'db_obras' not in st.session_state: st.session_state.db_obras = []
if 'custos' not in st.session_state: 
    st.session_state.custos = {"alu_b": 45.0, "alu_p": 55.0, "v8": 180.0, "v10": 220.0}

# ESTILO VISUAL MK
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stHeader { color: #1e3a8a; }
    .stButton>button { background-color: #1e3a8a; color: white; font-weight: bold; width: 100%; }
    .status-atrasado { color: #ff0000; font-weight: bold; border: 1px solid red; padding: 5px; }
    </style>
    """, unsafe_allow_html=True)

# HEADER COM NOME DA EMPRESA
st.title("⚒️ MK - SISTEMA DE GESTÃO PROFISSIONAL")
st.sidebar.markdown("### MK - LOGO")
st.sidebar.info("Espaço para Logo e Branding")

# --- NAVEGAÇÃO POR ABAS (A DIRETRIZ IMUTÁVEL) ---
tabs = st.tabs([
    "📍 Cliente", "📏 Projeto", "💰 Orçamento", "🏭 Produção", 
    "🚚 Instalação", "🚧 Gestão Obras", "📦 Estoque", "⚙️ Custos"
])

# --- ABA 1: CLIENTE (ESTRUTURA COMPLETA SOLICITADA) ---
with tabs[0]:
    st.header("👥 Cadastro Detalhado de Cliente")
    with st.form("cli_form_completo"):
        col1, col2 = st.columns(2)
        nome = col1.text_input("Nome do Cliente / Razão Social")
        email = col2.text_input("E-mail de Contato")
        
        c_tel, c_wpp = st.columns(2)
        telefone = c_tel.text_input("Telefone Fixo/Recado")
        whatsapp = c_wpp.text_input("WhatsApp Principal")
        
        st.divider()
        st.subheader("📍 Localização e Entrega")
        
        c_cep, c_log = st.columns([1, 3])
        cep = c_cep.text_input("CEP")
        logradouro = c_log.text_input("Logradouro (Rua/Avenida)")
        
        c_bairro, c_cid = st.columns(2)
        bairro = c_bairro.text_input("Bairro")
        cidade = c_cid.text_input("Cidade/UF")
        
        ponto_ref = st.text_input("Ponto de Referência (Próximo a...)")
        end_obra = st.text_input("Endereço da Obra (Se for diferente do cadastro acima)")
        
        st.divider()
        obs = st.text_area("Aba de Observações (Detalhes técnicos, horários, etc.)")
        
        if st.form_submit_button("Salvar Cadastro Completo"):
            st.session_state.db_clientes.append({
                "nome": nome, "email": email, "tel": telefone, "wpp": whatsapp,
                "cep": cep, "log": logradouro, "bairro": bairro, "cidade": cidade,
                "ref": ponto_ref, "obra": end_obra if end_obra else logradouro, "obs": obs
            })
            st.success(f"Cadastro de {nome} realizado com sucesso!")

# --- ABA 2: PROJETO (ENGENHARIA) ---
with tabs[1]:
    st.header("📐 Engenharia de Peças")
    with st.container():
        col1, col2, col3 = st.columns(3)
        linha = col1.selectbox("Linha", ["Suprema", "Gold", "Box", "Temperado", "Espelho"])
        tipo = col2.selectbox("Tipologia", ["Janela 2fls", "Porta Giro", "Fixo", "Maxim-ar", "Porta Correr"])
        cor = col3.selectbox("Cor do Alumínio", ["Branco", "Preto", "Bronze", "Natural"])
        
        col4, col5, col6 = st.columns(3)
        larg = col4.number_input("Largura (mm)", step=1)
        alt = col5.number_input("Altura (mm)", step=1)
        qtd = col6.number_input("Quantidade", min_value=1)
        
        local_p = st.text_input("Localização da Peça (Ex: Suíte, Cozinha)")
        fix = st.radio("Tipo de Fixação", ["Bucha/Parafuso", "Contra-marco"], horizontal=True)
        
        if st.button("Adicionar ao Orçamento"):
            st.toast("Peça adicionada ao cálculo!")

# --- ABA 3: ORÇAMENTO (COMERCIAL) ---
with tabs[2]:
    st.header("💰 Fechamento e Financeiro")
    st.write("### Itens do Orçamento")
    # Simulação de cálculo de custo regional da aba 8
    cor_mult = 1.15 if cor == "Preto" else 1.0
    st.info(f"Cálculo baseado no Alumínio {cor} (Acréscimo Cor: {int((cor_mult-1)*100)}%)")
    
    pag = st.selectbox("Forma de Pagamento", ["PIX", "À Vista", "Débito", "Crédito", "Parcelado"])
    if pag == "Parcelado":
        parc = st.number_input("Qtd de Parcelas", 1, 12)
        
    if st.button("📄 Gerar Contrato (PDF)"):
        st.session_state.db_obras.append({"cliente": nome, "status": "A Iniciar", "local": local_p})
        st.success("Contrato Gerado e Enviado para a Gestão de Obras!")

# --- ABA 4: PRODUÇÃO (FÁBRICA) ---
with tabs[3]:
    st.header("🏭 Produção: Plano de Corte e Vidros")
    st.subheader("💎 Área de Vidros")
    v1, v2 = st.columns(2)
    esp = v1.selectbox("Espessura", ["6mm", "8mm", "10mm"])
    c_vidro = v2.selectbox("Cor Vidro", ["Incolor", "Verde", "Fumê", "Leitoso"])
    
    st.subheader("🪚 Detalhamento de Corte (Perfis)")
    st.code(f"Exemplo: Marco Lateral | Linha: {linha} | Medida: {alt}mm | Desconto: 35mm")

# --- ABA 5: INSTALAÇÃO (CAMPO) ---
with tabs[4]:
    st.header("🚚 Romaneio de Instalação (Guia de Campo)")
    if st.session_state.db_clientes:
        c = st.session_state.db_clientes[-1]
        st.markdown(f"""
        **Cliente:** {c['nome']} | **Whats:** {c['wpp']}  
        **Endereço:** {c['log']}, {c['bairro']} - {c['cidade']}  
        **Ponto de Referência:** {c['ref']}  
        **Local da Obra:** {c['obra']}
        """)
        st.table(pd.DataFrame({"Peça": ["Exemplo"], "Medida": ["1200x1000"], "Local": [local_p]}))
    else:
        st.warning("Nenhum cliente selecionado para instalação.")

# --- ABA 6: GESTÃO DE OBRAS ---
with tabs[5]:
    st.header("🚧 Controle de Andamento Interno")
    status_opcoes = ["A Iniciar", "Em Execução", "Finalizada", "ATRASADO"]
    
    for obra in st.session_state.db_obras:
        c_ob, c_st = st.columns([3, 1])
        c_ob.write(f"**Obra:** {obra['cliente']} | Local: {obra['local']}")
        st_atual = c_st.selectbox("Status", status_opcoes, key=obra['cliente']+"_st")
        if st_atual == "ATRASADO":
            st.error("🔴 ALERTA: ESTA OBRA ESTÁ COM STATUS DE ATRASO!")
        st.divider()

# --- ABA 7: ESTOQUE ---
with tabs[6]:
    st.header("📦 Almoxarifado MK")
    st.table(pd.DataFrame({"Material": ["Perfil Suprema", "Roldana"], "Qtd": ["10 barras", "24 unid"]}))

# --- ABA 8: CONFIG. CUSTOS ---
with tabs[7]:
    st.header("⚙️ Custos Regionais (Tabela Editável)")
    with st.form("precos_form"):
        c1, c2 = st.columns(2)
        alu_b = c1.number_input("Alumínio Branco (KG)", value=st.session_state.custos["alu_b"])
        alu_p = c2.number_input("Alumínio Preto (KG)", value=st.session_state.custos["alu_p"])
        v8 = c1.number_input("Vidro 8mm (m²)", value=st.session_state.custos["v8"])
        v10 = c2.number_input("Vidro 10mm (m²)", value=st.session_state.custos["v10"])
        if st.form_submit_button("Salvar Novos Preços"):
            st.session_state.custos = {"alu_b": alu_b, "alu_p": alu_p, "v8": v8, "v10": v10}
            st.success("Tabela de preços atualizada!")
