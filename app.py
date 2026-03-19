import streamlit as st
import math

# 1. CONFIGURAÇÃO DE IDENTIDADE MK
st.set_page_config(page_title="MK - Sistema Industrial", layout="wide")

# --- INICIALIZAÇÃO DE DADOS (PERSISTÊNCIA) ---
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

# --- NOVO LAYOUT CSS (DESIGN INDUSTRIAL MK) ---
st.markdown("""
    <style>
    /* Fundo e Fonte Geral */
    .main { background-color: #f4f7f9; }
    
    /* Títulos de Seção */
    .mk-title { color: #1e3a8a; font-size: 28px; font-weight: 800; border-bottom: 3px solid #1e3a8a; margin-bottom: 20px; }
    
    /* Card de Projeto Estilizado */
    .card-mk {
        background-color: #ffffff;
        border-left: 8px solid #1e3a8a;
        padding: 20px;
        border-radius: 5px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }
    
    .card-mk h4 { color: #1e3a8a; margin-top: 0; }
    .card-mk p { color: #333333 !important; font-weight: 500; margin: 5px 0; }
    
    /* Botões de Ação */
    .stButton>button {
        border-radius: 4px;
        height: 3em;
        transition: all 0.3s;
    }
    
    /* Sidebar/Menu lateral personalizado */
    [data-testid="stSidebar"] { background-color: #1e3a8a; }
    [data-testid="stSidebar"] * { color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- MENU LATERAL DE NAVEGAÇÃO ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1063/1063303.png", width=100) # Ícone de Vidraceiro
    st.title("MK SISTEMAS")
    menu = st.radio("Navegação", ["📍 Clientes", "📐 Projetos", "💰 Orçamentos", "🏭 Produção", "⚙️ Custos"])
    st.divider()
    if st.button("🔥 RESETAR TUDO"):
        st.session_state.clear()
        st.rerun()

# --- ABA: CLIENTES ---
if menu == "📍 Clientes":
    st.markdown("<div class='mk-title'>👥 Gestão de Clientes</div>", unsafe_allow_html=True)
    with st.expander("➕ CADASTRAR NOVO CLIENTE", expanded=True):
        with st.form("form_cli"):
            c1, c2 = st.columns(2)
            n = c1.text_input("Nome Completo")
            w = c2.text_input("WhatsApp")
            e = c1.text_input("E-mail")
            cp = c2.text_input("CEP")
            l = st.text_input("Endereço Completo")
            if st.form_submit_button("SALVAR CLIENTE"):
                st.session_state.db_clientes.append({"nome": n, "wpp": w, "end": l})
                st.rerun()

    for i, cli in enumerate(st.session_state.db_clientes):
        col_c, col_b = st.columns([4, 1])
        with col_c:
            st.markdown(f"""<div class='card-mk'><h4>{cli['nome']}</h4><p>📞 {cli['wpp']}</p><p>📍 {cli['end']}</p></div>""", unsafe_allow_html=True)
        if col_b.button("🗑️", key=f"del_cli_{i}"):
            st.session_state.db_clientes.pop(i)
            st.rerun()

# --- ABA: PROJETOS ---
if menu == "📐 Projetos":
    st.markdown("<div class='mk-title'>📏 Engenharia de Peças</div>", unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        linha = st.selectbox("Linha", ["Suprema", "Gold"])
        tipo = st.selectbox("Tipologia", ["Janela 2fls", "Janela 4fls", "Porta Giro", "Fixo"])
        cor = st.selectbox("Cor Alumínio", ["Branco", "Preto", "Bronze"])
    with col_b:
        cor_v = st.selectbox("Cor Vidro", list(st.session_state.custo_vidros.keys()))
        esp_v = st.selectbox("Espessura", list(st.session_state.custo_vidros[cor_v].keys()))
        qtd = st.number_input("Quantidade", min_value=1, step=1)

    l_mm = st.number_input("Largura (mm)", min_value=1)
    a_mm = st.number_input("Altura (mm)", min_value=1)
    
    st.subheader("📍 Detalhes de Instalação")
    detalhes = []
    for i in range(int(qtd)):
        c1, c2 = st.columns([1, 2])
        amb = c1.text_input(f"Ambiente {i+1}", key=f"amb_{i}")
        obs = c2.text_input(f"Obs Técnica {i+1}", key=f"obs_{i}")
        detalhes.append({"amb": amb, "obs": obs})
        
    if st.button("➕ ADICIONAR AO ORÇAMENTO", use_container_width=True):
        st.session_state.db_projetos.append({
            "tipo": tipo, "linha": linha, "medida": f"{l_mm}x{a_mm}", 
            "vidro": f"{esp_v} {cor_v}", "qtd": qtd, "detalhes": detalhes
        })
        st.success("Projeto adicionado!")

# --- ABA: ORÇAMENTOS ---
if menu == "💰 Orçamentos":
    st.markdown("<div class='mk-title'>📋 Resumo do Pedido</div>", unsafe_allow_html=True)
    if not st.session_state.db_projetos:
        st.info("Nenhum item pendente.")
    else:
        for i, p in enumerate(st.session_state.db_projetos):
            col_i, col_d = st.columns([5, 1])
            with col_i:
                st.markdown(f"""
                <div class='card-mk'>
                    <h4>{p['tipo'].upper()} - {p['qtd']} UNIDADES</h4>
                    <p><b>Medida:</b> {p['medida']} mm | <b>Linha:</b> {p['linha']}</p>
                    <p><b>Vidro:</b> {p['vidro']}</p>
                </div>
                """, unsafe_allow_html=True)
            if col_d.button("🗑️", key=f"del_p_{i}"):
                st.session_state.db_projetos.pop(i)
                st.rerun()

# --- ABA: CUSTOS ---
if menu == "⚙️ Custos":
    st.markdown("<div class='mk-title'>⚙️ Tabela de Preços</div>", unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["🖼️ Vidros", "📊 Perfis", "🔩 Acessórios"])
    
    with tab1:
        for cor_v, espessuras in st.session_state.custo_vidros.items():
            st.subheader(f"Vidro {cor_v}")
            cols = st.columns(3)
            for i, (esp, preco) in enumerate(espessuras.items()):
                st.session_state.custo_vidros[cor_v][esp] = cols[i].number_input(f"{esp}", value=preco, key=f"v_{cor_v}_{esp}")
