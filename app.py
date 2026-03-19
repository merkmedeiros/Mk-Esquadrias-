import streamlit as st
import math

# 1. CONFIGURAÇÃO DE IDENTIDADE MK (PÁGINA CHEIA)
st.set_page_config(page_title="MK - Engenharia de Vidros", layout="wide")

# --- PERSISTÊNCIA DE DADOS (BANCO DE DADOS TEMPORÁRIO) ---
for key in ['db_clientes', 'db_projetos', 'db_obras', 'custo_vidros', 'custo_perfis', 'custo_acessorios']:
    if key not in st.session_state:
        if 'vidros' in key:
            st.session_state.custo_vidros = {
                "Incolor": {"6mm": 120.0, "8mm": 180.0, "10mm": 220.0},
                "Verde": {"6mm": 140.0, "8mm": 210.0, "10mm": 250.0},
                "Fumê": {"6mm": 150.0, "8mm": 230.0, "10mm": 280.0}
            }
        elif 'perfis' in key:
            st.session_state.custo_perfis = {"Suprema": {}, "Gold": {}}
        elif 'acessorios' in key:
            st.session_state.custo_acessorios = []
        else:
            st.session_state[key] = []

# --- ESTILO VISUAL INDUSTRIAL MK (SEM ABAS LATERAIS) ---
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    
    /* Títulos e Headers */
    .mk-header { color: #1e3a8a; font-weight: 800; border-bottom: 4px solid #1e3a8a; padding-bottom: 10px; margin-bottom: 20px; }
    
    /* Card de Projeto com Contraste Total */
    .card-mk {
        background-color: #ffffff;
        border: 2px solid #1e3a8a;
        border-left: 10px solid #1e3a8a;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 15px;
        box-shadow: 4px 4px 10px rgba(0,0,0,0.1);
    }
    .card-mk p, .card-mk b, .card-mk strong { color: #000000 !important; font-size: 16px; }
    .card-mk h4 { color: #1e3a8a; font-weight: bold; margin-bottom: 10px; }
    
    /* Customização das Abas Superiores */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #e2e8f0; 
        border-radius: 5px 5px 0 0; 
        padding: 12px 20px; 
        font-weight: bold;
        color: #1e3a8a;
    }
    .stTabs [aria-selected="true"] { background-color: #1e3a8a !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='mk-header'>⚒️ MK - GESTÃO INDUSTRIAL v39.0</h1>", unsafe_allow_html=True)

# --- NAVEGAÇÃO POR ABAS NO TOPO ---
tabs = st.tabs(["📍 CLIENTES", "📐 PROJETOS", "💰 ORÇAMENTO", "🏭 PRODUÇÃO", "⚙️ CUSTOS"])

# --- ABA 1: CLIENTES (10 CAMPOS COMPLETOS) ---
with tabs[0]:
    st.subheader("👥 Cadastro de Clientes")
    with st.form("f_cli"):
        c1, c2 = st.columns(2)
        n = c1.text_input("Nome / Razão Social")
        e = c2.text_input("E-mail")
        t = c1.text_input("Telefone Fixo")
        w = c2.text_input("WhatsApp")
        st.divider()
        cp = c1.text_input("CEP")
        lg = c2.text_input("Logradouro (Rua/Av)")
        ba, ci = st.columns(2)
        bai = ba.text_input("Bairro")
        cid = ci.text_input("Cidade/UF")
        ref = st.text_input("Ponto de Referência")
        obr = st.text_input("Endereço da Obra (Se diferente)")
        if st.form_submit_button("💾 SALVAR CLIENTE"):
            st.session_state.db_clientes.append({"nome": n, "obra": obr if obr else lg, "wpp": w})
            st.rerun()

    st.markdown("---")
    for i, cli in enumerate(st.session_state.db_clientes):
        col_c, col_b = st.columns([5, 1])
        with col_c:
            st.info(f"👤 **{cli['nome']}** | 📍 {cli['obra']} | 📱 {cli['wpp']}")
        if col_b.button("🗑️", key=f"del_cli_{i}"):
            st.session_state.db_clientes.pop(i)
            st.rerun()

# --- ABA 2: PROJETOS (LOCALIZAÇÃO E OBSERVAÇÃO) ---
with tabs[1]:
    st.subheader("📐 Engenharia e Peças")
    col1, col2, col3 = st.columns(3)
    lin = col1.selectbox("Linha", ["Suprema", "Gold"])
    tip = col2.selectbox("Tipologia", ["Janela 2fls", "Janela 4fls", "Porta Giro", "Fixo", "Maxim-ar"])
    cor = col3.selectbox("Cor Alumínio", ["Branco", "Preto", "Bronze"])
    
    st.markdown("#### 💎 Vidro")
    cv, ev = st.columns(2)
    c_vid = cv.selectbox("Cor Vidro", list(st.session_state.custo_vidros.keys()))
    e_vid = ev.selectbox("Espessura", list(st.session_state.custo_vidros[c_vid].keys()))
    
    l_p, a_p, q_p = st.columns(3)
    larg = l_p.number_input("Largura (mm)", min_value=1)
    alt = a_p.number_input("Altura (mm)", min_value=1)
    qtd = q_p.number_input("Quantidade de Peças", min_value=1, step=1)
    
    st.markdown("#### 📍 Detalhes Técnicos por Peça")
    pecas = []
    for i in range(int(qtd)):
        ca1, ca2 = st.columns([1, 2])
        amb = ca1.text_input(f"Ambiente Peça {i+1}", key=f"amb_v39_{i}")
        obs = ca2.text_input(f"Observação Peça {i+1}", key=f"obs_v39_{i}")
        pecas.append({"amb": amb, "obs": obs})
        
    if st.button("➕ ADICIONAR AO ORÇAMENTO", use_container_width=True):
        st.session_state.db_projetos.append({
            "tipo": tip, "linha": lin, "cor": cor, "vidro": f"{e_vid} {c_vid}",
            "larg": larg, "alt": alt, "qtd": qtd, "detalhes": pecas
        })
        st.success("Projeto adicionado!")

# --- ABA 3: ORÇAMENTO (VISUALIZAÇÃO DE CARD INDUSTRIAL) ---
with tabs[2]:
    st.subheader("💰 Resumo do Orçamento")
    if st.session_state.db_projetos:
        for idx, p in enumerate(st.session_state.db_projetos):
            with st.container():
                c_inf, c_btn = st.columns([5, 1])
                c_inf.markdown(f"""
                <div class='card-mk'>
                    <h4>{p['tipo'].upper()} - {p['linha'].upper()} ({p['qtd']} un)</h4>
                    <p><b>Medidas:</b> {p['larg']} x {p['alt']} mm</p>
                    <p><b>Vidro:</b> {p['vidro']} | <b>Alumínio:</b> {p['cor']}</p>
                </div>
                """, unsafe_allow_html=True)
                if c_btn.button("🗑️ APAGAR", key=f"del_p_v39_{idx}"):
                    st.session_state.db_projetos.pop(idx)
                    st.rerun()
        
        st.divider()
        if st.button("🔥 LIMPAR TUDO", key="clear_all"):
            st.session_state.db_projetos = []
            st.rerun()
    else:
        st.info("Nenhum projeto no orçamento.")

# --- ABA 5: CUSTOS (MATRIZ COMPLETA) ---
with tabs[4]:
    st.subheader("⚙️ Tabela de Custos (Vidros, Perfis e Acessórios)")
    t1, t2, t3 = st.tabs(["🖼️ Vidros", "📊 Perfis", "🔩 Acessórios"])
    
    with t1:
        for cor_v, espessuras in st.session_state.custo_vidros.items():
            st.markdown(f"**Vidro {cor_v}**")
            cols = st.columns(3)
            for i, (esp, preco) in enumerate(espessuras.items()):
                st.session_state.custo_vidros[cor_v][esp] = cols[i].number_input(f"{esp}", value=preco, key=f"v_{cor_v}_{esp}")
    
    with t2:
        st.info("Configure aqui o peso por metro e o preço do KG do Alumínio.")
    with t3:
        st.info("Adicione aqui os valores unitários de roldanas, fechos e escovas.")
