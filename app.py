import streamlit as st
import pandas as pd

# 1. CONFIGURAÇÃO MK - PÁGINA CHEIA
st.set_page_config(page_title="MK - Engenharia v40.0", layout="wide")

# --- PERSISTÊNCIA E ESTADOS ---
for key in ['db_clientes', 'db_projetos', 'db_obras', 'custo_vidros', 'edit_index']:
    if key not in st.session_state:
        if 'vidros' in key:
            st.session_state.custo_vidros = {"Incolor": {"6mm": 120.0, "8mm": 180.0}, "Verde": {"6mm": 140.0, "8mm": 210.0}}
        elif 'edit_index' in key: st.session_state.edit_index = None
        else: st.session_state[key] = []

# --- ESTILO INDUSTRIAL REFORÇADO ---
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .mk-header { color: #1e3a8a; font-weight: 800; border-bottom: 4px solid #1e3a8a; padding-bottom: 10px; }
    .card-mk {
        background-color: #ffffff; border: 2px solid #1e3a8a; border-left: 10px solid #1e3a8a;
        padding: 20px; border-radius: 8px; margin-bottom: 15px; box-shadow: 4px 4px 10px rgba(0,0,0,0.1);
    }
    .card-mk p, .card-mk b { color: #000000 !important; }
    .stTabs [aria-selected="true"] { background-color: #1e3a8a !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='mk-header'>⚒️ MK - GESTÃO INDUSTRIAL v40.0</h1>", unsafe_allow_html=True)

tabs = st.tabs(["📍 CLIENTES", "📐 PROJETO/EDIÇÃO", "💰 ORÇAMENTO", "🏭 LISTA DE CORTE", "⚙️ CUSTOS"])

# --- ABA 1: CLIENTES ---
with tabs[0]:
    st.subheader("👥 Cadastro de Clientes")
    with st.form("f_cli"):
        c1, c2 = st.columns(2)
        n = c1.text_input("Nome / Razão Social")
        w = c2.text_input("WhatsApp")
        lg = st.text_input("Endereço Completo")
        if st.form_submit_button("💾 SALVAR CLIENTE"):
            st.session_state.db_clientes.append({"nome": n, "obra": lg, "wpp": w})
            st.rerun()

# --- ABA 2: PROJETO E EDIÇÃO ---
with tabs[1]:
    if st.session_state.edit_index is not None:
        st.warning(f"⚠️ EDITANDO ITEM {st.session_state.edit_index + 1}")
        item_edit = st.session_state.db_projetos[st.session_state.edit_index]
    else:
        st.subheader("📐 Nova Peça")
        item_edit = {"linha": "Suprema", "tipo": "Janela 2fls", "larg": 1000, "alt": 1000, "qtd": 1}

    col1, col2, col3 = st.columns(3)
    lin = col1.selectbox("Linha", ["Suprema", "Gold"], index=0 if item_edit['linha'] == "Suprema" else 1)
    tip = col2.selectbox("Tipologia", ["Janela 2fls", "Janela 4fls", "Porta Giro", "Fixo"], index=0)
    larg = col1.number_input("Largura (mm)", value=int(item_edit.get('larg', 1000)))
    alt = col2.number_input("Altura (mm)", value=int(item_edit.get('alt', 1000)))
    qtd = col3.number_input("Quantidade", value=int(item_edit.get('qtd', 1)), min_value=1)
    
    if st.button("💾 SALVAR PROJETO / ATUALIZAR" if st.session_state.edit_index is not None else "➕ ADICIONAR AO ORÇAMENTO", use_container_width=True):
        novo_p = {"tipo": tip, "linha": lin, "larg": larg, "alt": alt, "qtd": qtd}
        if st.session_state.edit_index is not None:
            st.session_state.db_projetos[st.session_state.edit_index] = novo_p
            st.session_state.edit_index = None # Limpa o modo edição
        else:
            st.session_state.db_projetos.append(novo_p)
        st.success("Sucesso! Verifique a aba Orçamento.")
        st.rerun()

# --- ABA 3: ORÇAMENTO E PAGAMENTO ---
with tabs[2]:
    st.subheader("💰 Resumo e Pagamento")
    if st.session_state.db_projetos:
        for idx, p in enumerate(st.session_state.db_projetos):
            c_inf, c_ed, c_del = st.columns([4, 1, 1])
            c_inf.markdown(f"<div class='card-mk'><b>{p['tipo']}</b> | {p['larg']}x{p['alt']}mm | {p['qtd']} un.</div>", unsafe_allow_html=True)
            
            if c_ed.button("✏️ EDITAR", key=f"ed_{idx}"):
                st.session_state.edit_index = idx
                st.rerun()
            if c_del.button("🗑️ APAGAR", key=f"del_{idx}"):
                st.session_state.db_projetos.pop(idx)
                st.rerun()
        
        st.divider()
        st.subheader("💳 Detalhes do Pagamento")
        pg_col1, pg_col2 = st.columns(2)
        forma_pg = pg_col1.selectbox("Forma de Pagamento", ["Pix (5% desc)", "Cartão 12x", "Entrada + Boleto"])
        status_sinal = pg_col2.radio("Sinal Recebido?", ["Não", "Sim - Liberar Produção"])
        
        if st.button("🚀 CONFIRMAR PEDIDO E GERAR LISTAS", use_container_width=True):
            if status_sinal == "Sim - Liberar Produção":
                st.session_state.db_obras = st.session_state.db_projetos.copy()
                st.balloons()
                st.success("Pedido enviado para a PRODUÇÃO!")
    else:
        st.info("Adicione projetos para ver o orçamento.")

# --- ABA 4: PRODUÇÃO (LISTA DE CORTE E CHECK-LIST) ---
with tabs[3]:
    st.subheader("🏭 Ordem de Fábrica")
    if not st.session_state.db_obras:
        st.warning("Aguardando confirmação de pagamento no Orçamento.")
    else:
        for p in st.session_state.db_obras:
            with st.expander(f"📋 {p['tipo']} - {p['larg']}x{p['alt']} mm", expanded=True):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**📐 Lista de Corte (Alumínio):**")
                    if "Janela 2fls" in p['tipo']:
                        st.write(f"- Trilho Superior: {p['larg']} mm (1 un)")
                        st.write(f"- Trilho Inferior: {p['larg']} mm (1 un)")
                        st.write(f"- Montante Lateral: {p['alt']} mm (2 un)")
                        st.write(f"- Mão de Amigo: {p['alt'] - 45} mm (2 un)")
                with c2:
                    st.markdown("**💎 Plano de Vidros:**")
                    v_l = (p['larg'] / 2) + 20
                    v_a = p['alt'] - 95
                    st.write(f"- Vidro: {v_l:.0f} x {v_a:.0f} mm ({p['qtd'] * 2} peças)")
                
                st.markdown("**🔩 Check-list de Materiais:**")
                st.write(f"✅ Roldanas (4 un/peça) | ✅ Fecho Central | ✅ Escova de Vedação: {(p['alt']*4 + p['larg']*2)/1000:.1f} metros")

# --- ABA 5: CUSTOS ---
with tabs[4]:
    st.subheader("⚙️ Configuração")
    st.info("Preços de m² de vidros e acessórios para cálculo automático.")
