import streamlit as st
import pandas as pd
import math

# 1. CONFIGURAÇÃO DE IDENTIDADE MK
st.set_page_config(page_title="MK - Engenharia e Orçamentos", layout="wide")

# Inicialização do Banco de Dados Temporário
if 'db_clientes' not in st.session_state: st.session_state.db_clientes = []
if 'db_projetos' not in st.session_state: st.session_state.db_projetos = []
if 'db_obras' not in st.session_state: st.session_state.db_obras = []

# Tabela de Pesos Teóricos (kg/m)
if 'tab_perfis' not in st.session_state:
    st.session_state.tab_perfis = {
        "Suprema": {"SU-001": 0.455, "SU-039": 0.580, "SU-005": 0.320, "SU-225": 0.850},
        "Gold": {"LG-028": 0.950, "LG-040": 1.100, "LG-102": 0.780},
    }

# MATRIZ DE CUSTOS DE VIDROS (v30.0)
if 'custo_vidros' not in st.session_state:
    st.session_state.custo_vidros = {
        "Incolor": {"6mm": 120.0, "8mm": 180.0, "10mm": 220.0},
        "Verde": {"6mm": 140.0, "8mm": 210.0, "10mm": 250.0},
        "Fumê": {"6mm": 150.0, "8mm": 230.0, "10mm": 280.0},
        "Refletivo": {"6mm": 250.0, "8mm": 350.0, "10mm": 450.0}
    }

if 'custos_gerais' not in st.session_state:
    st.session_state.custos_gerais = {
        "preco_kg_branco": 45.0,
        "preco_kg_preto": 55.0,
        "acessorios": {"Roldana": 12.50, "Fecho": 18.00, "Escova (m)": 2.50}
    }

# ESTILO VISUAL MK
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stHeader { color: #1e3a8a; }
    .stButton>button { background-color: #1e3a8a; color: white; font-weight: bold; }
    .card-orcamento { border: 2px solid #1e3a8a; padding: 20px; border-radius: 10px; background: #fff; margin-bottom: 20px;}
    </style>
    """, unsafe_allow_html=True)

st.title("⚒️ MK - GESTÃO INDUSTRIAL v30.0")

# --- NAVEGAÇÃO POR ABAS ---
tabs = st.tabs(["📍 Cliente", "📏 Projeto", "💰 Orçamento", "🏭 Produção", "🚚 Instalação", "🚧 Gestão Obras", "📦 Estoque", "⚙️ Custos"])

# --- ABA 1: CLIENTE (10 CAMPOS MANTIDOS) ---
with tabs[0]:
    st.header("👥 Cadastro de Cliente")
    with st.form("cli_v30"):
        c1, c2 = st.columns(2); nome = c1.text_input("Nome / Razão Social"); email = c2.text_input("E-mail")
        tel = c1.text_input("Telefone"); wpp = c2.text_input("WhatsApp")
        st.divider(); cep = c1.text_input("CEP"); log = c2.text_input("Logradouro")
        bai, cid = st.columns(2); bairro = bai.text_input("Bairro"); cidade = cid.text_input("Cidade/UF")
        ref = st.text_input("Ponto de Referência"); obra = st.text_input("Local da Obra (Se diferente)")
        obs = st.text_area("Observações")
        if st.form_submit_button("Salvar"):
            st.session_state.db_clientes.append({"nome": nome, "obra": obra if obra else log, "ref": ref, "wpp": wpp})

# --- ABA 2: PROJETO (ENGENHARIA E VIDROS) ---
with tabs[1]:
    st.header("📐 Engenharia de Peças")
    col1, col2, col3 = st.columns(3)
    linha = col1.selectbox("Linha", list(st.session_state.tab_perfis.keys()))
    tipo = col2.selectbox("Tipologia", ["Janela 2fls", "Janela 4fls", "Porta Giro", "Fixo"])
    cor = col3.selectbox("Cor Alumínio", ["Branco", "Preto"])
    
    st.subheader("💎 Seleção de Vidro")
    c_vid, e_vid = st.columns(2)
    cor_v = c_vid.selectbox("Cor do Vidro", list(st.session_state.custo_vidros.keys()))
    esp_v = e_vid.selectbox("Espessura", list(st.session_state.custo_vidros[cor_v].keys()))
    
    st.divider()
    l_p, a_p, q_p = st.columns(3)
    larg = l_p.number_input("Largura (mm)", step=1); alt = a_p.number_input("Altura (mm)", step=1); qtd = q_p.number_input("Quantidade", min_value=1)
    
    ambientes = []
    for i in range(int(qtd)): ambientes.append(st.text_input(f"Ambiente Peça {i+1}", key=f"p30_{i}"))
        
    if st.button("Configurar Projeto"):
        # Descontos de Vidro (Engenharia MK)
        v_h = alt - 160 if "Janela" in tipo else alt - 40
        v_l = (larg/2) - 95 if "2fls" in tipo else larg - 50
        
        # Puxa o custo do Vidro Selecionado
        valor_m2 = st.session_state.custo_vidros[cor_v][esp_v]
        
        st.session_state.db_projetos.append({
            "linha": linha, "tipo": tipo, "cor": cor, "vidro": f"{esp_v} {cor_v}",
            "larg": larg, "alt": alt, "qtd": qtd, "ambientes": ambientes,
            "v_h": v_h, "v_l": v_l, "custo_v_m2": valor_m2
        })
        st.success("Peça adicionada ao cálculo!")

# --- ABA 8: CUSTOS (MATRIZ DE VIDROS E ALUMÍNIO) ---
with tabs[7]:
    st.header("⚙️ Configuração de Preços de Compra")
    
    with st.expander("🖼️ MATRIZ DE PREÇOS DE VIDROS (R$/m²)", expanded=True):
        for cor_v, espessuras in st.session_state.custo_vidros.items():
            st.write(f"**Vidro {cor_v}**")
            cols = st.columns(len(espessuras))
            for i, (esp, preco) in enumerate(espessuras.items()):
                new_p = cols[i].number_input(f"{esp}", value=preco, key=f"vid_{cor_v}_{esp}")
                st.session_state.custo_vidros[cor_v][esp] = new_p

    with st.expander("📊 CUSTOS DE ALUMÍNIO E ACESSÓRIOS"):
        c1, c2 = st.columns(2)
        st.session_state.custos_gerais["preco_kg_branco"] = c1.number_input("Preço KG Branco", value=st.session_state.custos_gerais["preco_kg_branco"])
        st.session_state.custos_gerais["preco_kg_preto"] = c2.number_input("Preço KG Preto", value=st.session_state.custos_gerais["preco_kg_preto"])
        
        st.write("**Pesos de Perfis (kg/m)**")
        linha_edit = st.selectbox("Linha para editar pesos", list(st.session_state.tab_perfis.keys()))
        for p, peso in st.session_state.tab_perfis[linha_edit].items():
            new_w = st.number_input(f"Peso {p}", value=peso, format="%.3f")
            st.session_state.tab_perfis[linha_edit][p] = new_w

# --- ABA 3: ORÇAMENTO (CÁLCULO FINANCEIRO FINAL) ---
with tabs[2]:
    st.header("💰 Fechamento Financeiro")
    if st.session_state.db_projetos:
        custo_total_obra = 0
        for p in st.session_state.db_projetos:
            # Cálculo de Custo Alumínio (Peso)
            peso_est = (((p['larg']*2 + p['alt']*2) * p['qtd']) / 1000) * 0.550
            preco_al = st.session_state.custos_gerais["preco_kg_branco"] if p['cor'] == "Branco" else st.session_state.custos_gerais["preco_kg_preto"]
            custo_al = peso_est * preco_al
            
            # Cálculo de Custo Vidro
            area_v = ((p['v_h'] * p['v_l'] * p['qtd']) / 1000000)
            custo_vid = area_v * p['custo_v_m2']
            
            custo_item = custo_al + custo_vid + 50 # +50 de acessórios base
            custo_total_obra += custo_item
            
            st.markdown(f"""
            <div class='card-orcamento'>
                <h4>Peça: {p['tipo']} ({p['linha']})</h4>
                <p><b>Vidro:</b> {p['vidro']} | <b>Medidas:</b> {p['larg']}x{p['alt']}mm</p>
                <p>Custo Alumínio: R$ {custo_al:.2f} | Custo Vidro: R$ {custo_vid:.2f}</p>
            </div>
            """, unsafe_allow_html=True)
            
        st.divider()
        col_f1, col_f2 = st.columns(2)
        col_f1.metric("CUSTO TOTAL DE COMPRA", f"R$ {custo_total_obra:.2f}")
        margem = col_f2.slider("Margem de Lucro (%)", 0, 200, 100)
        preco_venda = custo_total_obra * (1 + margem/100)
        st.subheader(f"💵 PREÇO SUGERIDO DE VENDA: R$ {preco_venda:.2f}")
    else:
        st.info("Adicione projetos para calcular o orçamento.")

# --- ABA 4: PRODUÇÃO (LISTA DE COMPRA E CORTE) ---
with tabs[3]:
    st.header("🏭 Ordem de Produção")
    if st.session_state.db_projetos:
        for p in st.session_state.db_projetos:
            st.write(f"### Obra: {p['tipo']} - {p['vidro']}")
            m_linear = ((p['larg']*2 + p['alt']*2) * p['qtd']) / 1000
            st.info(f"🛒 COMPRA: {math.ceil(m_linear/6)} Barras de 6m | Vidro Total: {((p['v_h']*p['v_l']*p['qtd'])/1000000):.2f} m²")
            for amb in p['ambientes']:
                st.write(f"🪚 **Corte p/ {amb}:** L={p['larg']}mm / H={p['alt']}mm | Vidro: {p['v_l']:.0f}x{p['v_h']:.0f}mm")
