import streamlit as st

# 1. CONFIGURAÇÃO DE IDENTIDADE MK
st.set_page_config(page_title="MK - Engenharia v41.0", layout="wide")

# --- PERSISTÊNCIA TOTAL DE DADOS ---
if 'db_clientes' not in st.session_state: st.session_state.db_clientes = []
if 'db_projetos' not in st.session_state: st.session_state.db_projetos = []
if 'db_obras' not in st.session_state: st.session_state.db_obras = []
if 'edit_index' not in st.session_state: st.session_state.edit_index = None

# Matrizes de Custos (PRESERVADAS)
if 'custo_vidros' not in st.session_state:
    st.session_state.custo_vidros = {
        "Incolor": {"6mm": 120.0, "8mm": 180.0, "10mm": 220.0},
        "Verde": {"6mm": 140.0, "8mm": 210.0, "10mm": 250.0},
        "Fumê": {"6mm": 150.0, "8mm": 230.0, "10mm": 280.0}
    }

# --- ESTILO INDUSTRIAL MK (FONTE PRETA FORÇADA) ---
st.markdown("""
    <style>
    .main { background-color: #f4f7f9; }
    .card-mk {
        background-color: #ffffff; border: 2px solid #1e3a8a; border-left: 12px solid #1e3a8a;
        padding: 20px; border-radius: 10px; margin-bottom: 15px; box-shadow: 5px 5px 15px rgba(0,0,0,0.1);
    }
    .card-mk p, .card-mk b, .card-mk strong, .card-mk span { color: #000000 !important; font-size: 16px; }
    .stTabs [aria-selected="true"] { background-color: #1e3a8a !important; color: white !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚒️ MK - GESTÃO INDUSTRIAL v41.0")

tabs = st.tabs(["📍 CLIENTES", "📐 PROJETO", "💰 ORÇAMENTO", "🏭 PRODUÇÃO", "⚙️ CUSTOS"])

# --- ABA 1: CLIENTES (10 CAMPOS RECUPERADOS) ---
with tabs[0]:
    st.header("👥 Cadastro de Clientes")
    with st.form("f_cli_v41"):
        c1, c2 = st.columns(2)
        n = c1.text_input("Nome / Razão Social")
        em = c2.text_input("E-mail")
        t = c1.text_input("Telefone Fixo")
        w = c2.text_input("WhatsApp")
        st.divider()
        cp = c1.text_input("CEP")
        lg = c2.text_input("Logradouro")
        ba, ci = st.columns(2)
        bai = ba.text_input("Bairro")
        cid = ci.text_input("Cidade/UF")
        ref = st.text_input("Ponto de Referência")
        obr = st.text_input("Endereço da Obra")
        if st.form_submit_button("💾 SALVAR CLIENTE"):
            st.session_state.db_clientes.append({"nome": n, "obra": obr if obr else lg, "wpp": w})
            st.rerun()

# --- ABA 2: PROJETO (EDIÇÃO INTEGRADA) ---
with tabs[1]:
    idx = st.session_state.edit_index
    if idx is not None:
        st.warning(f"✏️ EDITANDO ITEM {idx + 1}")
        p_base = st.session_state.db_projetos[idx]
    else:
        st.subheader("📐 Nova Engenharia")
        p_base = {"linha": "Suprema", "tipo": "Janela 2fls", "larg": 1000, "alt": 1000, "qtd": 1, "cor": "Branco"}

    col1, col2, col3 = st.columns(3)
    lin = col1.selectbox("Linha", ["Suprema", "Gold"], index=0 if p_base['linha'] == "Suprema" else 1)
    tip = col2.selectbox("Tipologia", ["Janela 2fls", "Janela 4fls", "Porta Giro", "Fixo"], index=0)
    cor = col3.selectbox("Cor Alumínio", ["Branco", "Preto", "Bronze"], index=0)
    
    st.divider()
    l_p, a_p, q_p = st.columns(3)
    larg = l_p.number_input("Largura (mm)", value=int(p_base['larg']))
    alt = a_p.number_input("Altura (mm)", value=int(p_base['alt']))
    qtd = q_p.number_input("Quantidade", value=int(p_base['qtd']), min_value=1)
    
    st.subheader("📍 Detalhes por Peça")
    detalhes = []
    for i in range(int(qtd)):
        ca1, ca2 = st.columns([1, 2])
        amb = ca1.text_input(f"Ambiente {i+1}", key=f"amb_{i}")
        obs = ca2.text_input(f"Obs Técnica {i+1}", key=f"obs_{i}")
        detalhes.append({"amb": amb, "obs": obs})
        
    if st.button("✅ ATUALIZAR ITEM" if idx is not None else "➕ ADICIONAR AO ORÇAMENTO", use_container_width=True):
        novo_p = {"tipo": tip, "linha": lin, "cor": cor, "larg": larg, "alt": alt, "qtd": qtd, "detalhes": detalhes}
        if idx is not None:
            st.session_state.db_projetos[idx] = novo_p
            st.session_state.edit_index = None
        else:
            st.session_state.db_projetos.append(novo_p)
        st.rerun()

# --- ABA 3: ORÇAMENTO E PAGAMENTO ---
with tabs[2]:
    st.header("💰 Resumo e Checkout")
    if st.session_state.db_projetos:
        for i, p in enumerate(st.session_state.db_projetos):
            with st.container():
                c_inf, c_ed, c_del = st.columns([4, 1, 1])
                c_inf.markdown(f"""<div class='card-mk'><b>{p['tipo']}</b> | {p['larg']}x{p['alt']}mm | {p['qtd']} un. | Cor: {p['cor']}</div>""", unsafe_allow_html=True)
                if c_ed.button("✏️", key=f"ed_{i}"):
                    st.session_state.edit_index = i
                    st.rerun()
                if c_del.button("🗑️", key=f"del_{i}"):
                    st.session_state.db_projetos.pop(i)
                    st.rerun()
        
        st.divider()
        st.subheader("💳 Finalizar Pedido")
        f_pg = st.selectbox("Forma de Pagamento", ["Pix", "Cartão", "Boleto"])
        sinal = st.radio("Sinal Confirmado?", ["Pendente", "Confirmado - Liberar para Fábrica"], horizontal=True)
        
        if st.button("🚀 ENVIAR PARA PRODUÇÃO", use_container_width=True):
            if sinal == "Confirmado - Liberar para Fábrica":
                st.session_state.db_obras = st.session_state.db_projetos.copy()
                st.success("Pedido enviado!")

# --- ABA 4: PRODUÇÃO (ENGENHARIA MK) ---
with tabs[3]:
    st.header("🏭 Ordens de Produção")
    if st.session_state.db_obras:
        for p in st.session_state.db_obras:
            with st.expander(f"📋 {p['tipo']} - {p['larg']}x{p['alt']} mm"):
                st.markdown("**📐 LISTA DE CORTE ALUMÍNIO:**")
                st.write(f"- Trilho Sup/Inf: {p['larg']} mm | - Laterais: {p['alt']} mm")
                st.markdown("**💎 MEDIDA DOS VIDROS:**")
                st.write(f"- Vidro: {(p['larg']/2)+20:.0f} x {p['alt']-95:.0f} mm")
                st.markdown("**🔩 CHECK-LIST:**")
                st.write("- Roldanas, Fechos, Escovas, Parafusos e Buchas.")

# --- ABA 5: CUSTOS (MATRIZ COMPLETA) ---
with tabs[4]:
    st.header("⚙️ Configuração de Custos")
    for cor_v, espessuras in st.session_state.custo_vidros.items():
        st.write(f"**Vidro {cor_v}**")
        cols = st.columns(3)
        for i, (esp, preco) in enumerate(espessuras.items()):
            st.session_state.custo_vidros[cor_v][esp] = cols[i].number_input(f"{esp}", value=preco, key=f"v_{cor_v}_{esp}")
