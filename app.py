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
    .loc-box { border-left: 3px solid #1e3a8a; padding-left: 10px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# HEADER COM NOME DA EMPRESA
st.title("⚒️ MK - SISTEMA DE GESTÃO PROFISSIONAL")
st.sidebar.markdown("### MK - LOGO")
st.sidebar.info("Espaço para Logo e Branding")

# --- NAVEGAÇÃO POR ABAS ---
tabs = st.tabs([
    "📍 Cliente", "📏 Projeto", "💰 Orçamento", "🏭 Produção", 
    "🚚 Instalação", "🚧 Gestão Obras", "📦 Estoque", "⚙️ Custos"
])

# --- ABA 1: CLIENTE (10 CAMPOS SOLICITADOS) ---
with tabs[0]:
    st.header("👥 Cadastro Detalhado de Cliente")
    with st.form("cli_form_v27"):
        col1, col2 = st.columns(2)
        nome_c = col1.text_input("Nome do Cliente / Razão Social")
        email_c = col2.text_input("E-mail de Contato")
        
        c_tel, c_wpp = st.columns(2)
        tel_c = c_tel.text_input("Telefone Fixo/Recado")
        wpp_c = c_wpp.text_input("WhatsApp Principal")
        
        st.divider()
        st.subheader("📍 Localização")
        c_cep, c_log = st.columns([1, 3])
        cep_c = c_cep.text_input("CEP")
        log_c = c_log.text_input("Logradouro (Rua/Avenida)")
        
        c_bai, c_cid = st.columns(2)
        bai_c = c_bai.text_input("Bairro")
        cid_c = c_cid.text_input("Cidade/UF")
        
        ref_c = st.text_input("Ponto de Referência")
        obra_c = st.text_input("Endereço da Obra (Se for diferente)")
        
        obs_c = st.text_area("Aba de Observações")
        
        if st.form_submit_button("Salvar Cadastro"):
            st.session_state.db_clientes.append({"nome": nome_c, "wpp": wpp_c, "obra": obra_c if obra_c else log_c, "ref": ref_c})
            st.success("Cliente Salvo!")

# --- ABA 2: PROJETO (ENGENHARIA MULTINÍVEL & VIDROS) ---
with tabs[1]:
    st.header("📐 Engenharia e Configuração de Vidros")
    
    col_l, col_t, col_c = st.columns(3)
    linha_p = col_l.selectbox("Linha", ["Suprema", "Gold", "Box", "Temperado", "Espelho"])
    tipo_p = col_t.selectbox("Tipologia", ["Janela 2fls", "Janela 4fls", "Porta Giro", "Fixo", "Maxim-ar"])
    cor_p = col_c.selectbox("Cor do Alumínio", ["Branco", "Preto", "Bronze", "Natural"])
    
    st.divider()
    st.subheader("💎 Configuração do Vidro")
    col_v1, col_v2 = st.columns(2)
    vidro_esp = col_v1.selectbox("Espessura do Vidro", ["Sem Vidro", "4mm", "6mm", "8mm", "10mm", "Laminado 4+4", "Laminado 5+5"])
    vidro_cor = col_v2.selectbox("Cor/Tipo do Vidro", ["Incolor", "Verde", "Fumê", "Leitoso", "Refletivo Prata", "Refletivo Bronze"])
    
    st.divider()
    col_la, col_al, col_qt = st.columns(3)
    larg_p = col_la.number_input("Largura (mm)", step=1)
    alt_p = col_al.number_input("Altura (mm)", step=1)
    qtd_p = col_qt.number_input("Quantidade de Peças Iguais", min_value=1, step=1)
    
    # LÓGICA DE MULTI-LOCALIZAÇÃO
    st.subheader("📍 Localização dos Ambientes")
    locais_input = []
    if qtd_p > 0:
        for i in range(int(qtd_p)):
            loc = st.text_input(f"Ambiente da Peça {i+1}", placeholder=f"Ex: Quarto {i+1}", key=f"loc_{i}")
            locais_input.append(loc)
    
    fix_p = st.radio("Fixação", ["Bucha/Parafuso", "Contra-marco"], horizontal=True)
    
    if st.button("Adicionar Projeto ao Orçamento"):
        st.success(f"{qtd_p} peças de {tipo_p} configuradas com Vidro {vidro_esp} {vidro_cor}!")

# --- ABA 3: ORÇAMENTO ---
with tabs[2]:
    st.header("💰 Comercial e Financeiro")
    st.write("### Itens Selecionados")
    # Aqui o sistema puxa a localização individual para o contrato
    st.info(f"Peças para: {', '.join(locais_input) if 'locais_input' in locals() else 'Nenhum'}")
    
    pag_p = st.selectbox("Forma de Pagamento", ["PIX", "À Vista", "Débito", "Crédito", "Parcelado"])
    if st.button("🚀 Finalizar Pedido"):
        st.session_state.db_obras.append({"cliente": nome_c if 'nome_c' in locals() else "Novo", "status": "A Iniciar", "ambientes": locais_input})
        st.success("Enviado para Produção!")

# --- ABA 4: PRODUÇÃO (FOCO EM CORTE) ---
with tabs[3]:
    st.header("🏭 Fábrica: Plano de Corte de Alumínio")
    st.info("Os vidros já foram definidos no projeto e constam na ficha técnica abaixo.")
    
    st.subheader("📋 Lista de Materiais para Produção")
    if 'tipo_p' in locals():
        st.write(f"**Tipologia:** {tipo_p} | **Linha:** {linha_p} | **Vidro:** {vidro_esp} {vidro_cor}")
        st.code(f"MARCO LATERAL | Corte: {alt_p}mm | Qtd: {int(qtd_p)*2}\nMARCO SUP/INF | Corte: {larg_p}mm | Qtd: {int(qtd_p)*2}")

# --- ABA 5: INSTALAÇÃO (GUIA DE CAMPO) ---
with tabs[4]:
    st.header("🚚 Romaneio do Instalador")
    if st.session_state.db_clientes:
        c = st.session_state.db_clientes[-1]
        st.markdown(f"**Cliente:** {c['nome']} | **Ref:** {c['ref']}")
        st.markdown(f"**Local da Obra:** {c['obra']}")
        
        st.subheader("📍 Onde Instalar cada Peça:")
        for i, localizacao in enumerate(locais_input if 'locais_input' in locals() else []):
            st.markdown(f"✅ **Peça {i+1}:** {localizacao} ({tipo_p} - Vidro {vidro_esp})")
    else:
        st.warning("Cadastre um cliente primeiro.")

# --- ABA 6: GESTÃO DE OBRAS ---
with tabs[5]:
    st.header("🚧 Status das Obras")
    status_op = ["A Iniciar", "Em Execução", "Finalizada", "ATRASADO"]
    for obra in st.session_state.db_obras:
        c1, c2 = st.columns([3, 1])
        c1.write(f"**Obra:** {obra['cliente']} | Ambientes: {', '.join(obra['ambientes'])}")
        st_at = c2.selectbox("Alterar Status", status_op, key=obra['cliente']+"_geral")
        if st_at == "ATRASADO": st.error("🚨 ALERTA DE ATRASO!")
        st.divider()

# --- ABA 7: ESTOQUE ---
with tabs[6]:
    st.header("📦 Almoxarifado MK")
    st.table(pd.DataFrame({"Item": ["Perfil SU-001", "Roldana"], "Saldo": ["12 barras", "30 unid"]}))

# --- ABA 8: CUSTOS ---
with tabs[7]:
    st.header("⚙️ Tabela de Custos")
    with st.form("custos_v27"):
        c1, c2 = st.columns(2)
        alu_b = c1.number_input("Alumínio Branco (KG)", value=st.session_state.custos["alu_b"])
        alu_p = c2.number_input("Alumínio Preto (KG)", value=st.session_state.custos["alu_p"])
        if st.form_submit_button("Salvar Preços"):
            st.session_state.custos = {"alu_b": alu_b, "alu_p": alu_p}
            st.success("Custos Atualizados!")
