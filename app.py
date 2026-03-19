import streamlit as st
import pandas as pd
import math

# 1. CONFIGURAÇÃO DE IDENTIDADE MK
st.set_page_config(page_title="MK - Esquadrias & Vidros", layout="wide")

# Inicialização do Banco de Dados Temporário
if 'db_clientes' not in st.session_state: st.session_state.db_clientes = []
if 'db_projetos' not in st.session_state: st.session_state.db_projetos = []
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
    .card-engenharia { border: 1px solid #ddd; padding: 15px; border-radius: 8px; margin-bottom: 10px; background: #fff; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚒️ MK - SISTEMA DE GESTÃO E ENGENHARIA v28.0")

# --- NAVEGAÇÃO POR ABAS ---
tabs = st.tabs([
    "📍 Cliente", "📏 Projeto", "💰 Orçamento", "🏭 Produção", 
    "🚚 Instalação", "🚧 Gestão Obras", "📦 Estoque", "⚙️ Custos"
])

# --- ABA 1: CLIENTE (10 CAMPOS) ---
with tabs[0]:
    st.header("👥 Cadastro Detalhado")
    with st.form("cli_form_v28"):
        col1, col2 = st.columns(2)
        nome_c = col1.text_input("Nome / Razão Social")
        email_c = col2.text_input("E-mail")
        c_tel, c_wpp = st.columns(2)
        tel_c = c_tel.text_input("Telefone")
        wpp_c = c_wpp.text_input("WhatsApp")
        
        st.divider()
        c_cep, c_log = st.columns([1, 3])
        cep_c = c_cep.text_input("CEP")
        log_c = c_log.text_input("Logradouro")
        c_bai, c_cid = st.columns(2)
        bai_c = c_bai.text_input("Bairro")
        cid_c = c_cid.text_input("Cidade/UF")
        
        ref_c = st.text_input("Ponto de Referência")
        obra_c = st.text_input("Endereço da Obra (Se diferente)")
        obs_c = st.text_area("Observações")
        
        if st.form_submit_button("Salvar Cadastro"):
            st.session_state.db_clientes.append({"nome": nome_c, "wpp": wpp_c, "obra": obra_c if obra_c else log_c, "ref": ref_c})
            st.success("Cliente Salvo!")

# --- ABA 2: PROJETO (ENGENHARIA & LOCALIZAÇÃO INDIVIDUAL) ---
with tabs[1]:
    st.header("📐 Engenharia de Peças e Vidros")
    col_l, col_t, col_c = st.columns(3)
    linha_p = col_l.selectbox("Linha", ["Suprema", "Gold", "Box", "Temperado"])
    tipo_p = col_t.selectbox("Tipologia", ["Janela 2fls", "Porta Giro", "Fixo", "Maxim-ar"])
    cor_p = col_c.selectbox("Cor do Alumínio", ["Branco", "Preto"])
    
    st.divider()
    st.subheader("💎 Configuração do Vidro")
    v_col1, v_col2 = st.columns(2)
    vid_esp = v_col1.selectbox("Espessura", ["6mm", "8mm", "10mm", "4+4mm"])
    vid_cor = v_col2.selectbox("Cor Vidro", ["Incolor", "Verde", "Fumê", "Refletivo"])
    
    st.divider()
    l_p, a_p, q_p = st.columns(3)
    larg = l_p.number_input("Largura (mm)", step=1)
    alt = a_p.number_input("Altura (mm)", step=1)
    qtd = q_p.number_input("Quantidade", min_value=1, step=1)
    
    st.subheader("📍 Localização por Peça")
    ambientes = []
    for i in range(int(qtd)):
        ambientes.append(st.text_input(f"Ambiente da Peça {i+1}", key=f"amb_{i}"))
        
    if st.button("Configurar para Produção"):
        projeto = {
            "linha": linha_p, "tipo": tipo_p, "cor": cor_p,
            "vidro": f"{vid_esp} {vid_cor}", "larg": larg, "alt": alt, "qtd": qtd,
            "ambientes": ambientes
        }
        st.session_state.db_projetos.append(projeto)
        st.success("Engenharia processada!")

# --- ABA 4: PRODUÇÃO (CÁLCULOS DE CORTE, COMPRA E ACESSÓRIOS) ---
with tabs[3]:
    st.header("🏭 Inteligência de Produção e Suprimentos")
    
    if st.session_state.db_projetos:
        for p in st.session_state.db_projetos:
            with st.expander(f"PROJETO: {p['tipo']} - {p['linha']} ({p['qtd']} un)"):
                
                # 1. LISTA DE COMPRA (BARRAS)
                st.subheader("📦 LISTA PARA COMPRA")
                col_c1, col_c2 = st.columns(2)
                # Cálculo simplificado de barras (6m)
                perimetro_total = ((p['larg']*2 + p['alt']*2) * p['qtd']) / 1000
                barras = math.ceil(perimetro_total / 6)
                col_c1.metric("Perfil Principal (6m)", f"{barras} Barras")
                col_c2.metric("Vidro Total", f"{(p['larg']*p['alt']*p['qtd'])/1000000:.2f} m²")
                
                # ACESSÓRIOS
                st.write("**Acessórios Necessários:**")
                if "Janela" in p['tipo']:
                    st.write(f"- Roldanas: {int(p['qtd'])*2} un | - Fechos: {int(p['qtd'])} un | - Escova: {perimetro_total:.1f} m")
                
                st.divider()
                
                # 2. MAPA DE FABRICAÇÃO (CORTE)
                st.subheader("🪚 MAPA DE FABRICAÇÃO (CORTE)")
                for idx, amb in enumerate(p['ambientes']):
                    st.markdown(f"**Peça {idx+1}: {amb}**")
                    # Exemplo de folgas técnicas (Suprema)
                    st.write(f"👉 Cortar Batentes: {p['alt']}mm (2 un) | 👉 Cortar Trilhos: {p['larg']}mm (2 un)")
                    st.write(f"👉 Vidro p/ este ambiente: {p['larg']/2 - 35:.0f} x {p['alt'] - 80:.0f} mm")
    else:
        st.info("Adicione um projeto para gerar as listas de fabricação.")

# --- ABA 3: ORÇAMENTO ---
with tabs[2]:
    st.header("💰 Comercial")
    if st.session_state.db_projetos:
        st.table(pd.DataFrame(st.session_state.db_projetos))
        if st.button("Finalizar e Enviar para Obras"):
            st.session_state.db_obras.append({"cliente": nome_c if 'nome_c' in locals() else "Novo", "status": "A Iniciar"})
            st.success("Pedido finalizado!")

# --- ABA 5: INSTALAÇÃO ---
with tabs[4]:
    st.header("🚚 Romaneio de Campo")
    if st.session_state.db_clientes:
        c = st.session_state.db_clientes[-1]
        st.write(f"**Cliente:** {c['nome']} | **Obra:** {c['obra']} | **Ref:** {c['ref']}")
        if st.session_state.db_projetos:
            for p in st.session_state.db_projetos:
                for amb in p['ambientes']:
                    st.write(f"✅ Instalar {p['tipo']} em: **{amb}** (Vidro: {p['vidro']})")

# --- ABA 6: GESTÃO OBRAS ---
with tabs[5]:
    st.header("🚧 Controle de Obras")
    status_op = ["A Iniciar", "Em Execução", "Finalizada", "ATRASADO"]
    for obra in st.session_state.db_obras:
        c1, c2 = st.columns([3, 1])
        c1.write(f"**Obra:** {obra['cliente']}")
        st_at = c2.selectbox("Status", status_op, key=obra['cliente'])
        if st_at == "ATRASADO": st.error("🚨 ATRASO DETECTADO")

# --- ABA 7: ESTOQUE & 8: CUSTOS (MANTIDOS) ---
with tabs[6]: st.header("📦 Estoque de Barras"); st.write("Saldo: 45 barras alumínio branco.")
with tabs[7]:
    st.header("⚙️ Custos Regionais")
    st.number_input("Alumínio Branco (KG)", value=st.session_state.custos["alu_b"])
    if st.button("Salvar Custos"): st.success("Atualizado!")
