import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO MESTRA ---
st.set_page_config(page_title="ESQUADPLAN PRO v18", layout="wide")

# --- DATABASE INICIAL (PERSISTÊNCIA) ---
if 'banco_clientes' not in st.session_state: st.session_state.banco_clientes = []
if 'carrinho' not in st.session_state: st.session_state.carrinho = []
if 'obras_fechadas' not in st.session_state: st.session_state.obras_fechadas = []
if 'estoque' not in st.session_state:
    st.session_state.estoque = {
        "Alumínio Suprema (kg)": {"qtd": 0.0, "custo": 0.0},
        "Vidro Temperado (m2)": {"qtd": 0.0, "custo": 0.0},
        "Kit Box (un)": {"qtd": 0, "custo": 0.0}
    }

# --- FUNÇÕES DE ENGENHARIA (O CÉREBRO DO SISTEMA) ---
def calcular_engenharia_suprema(L, H, tipo, qtd):
    # Lógica baseada em Linha Suprema 2 Folhas
    cortes = [
        {"Perfil": "SU-001/002 (Trilhos)", "Qtd": 2 * qtd, "Medida": L, "Corte": "90°"},
        {"Perfil": "SU-003 (Laterais)", "Qtd": 2 * qtd, "Medida": H, "Corte": "90°"},
        {"Perfil": "SU-039 (Mão de Amigo)", "Qtd": 2 * qtd, "Medida": H - 45, "Corte": "90°"},
        {"Perfil": "SU-040 (Mont. Lat)", "Qtd": 2 * qtd, "Medida": H - 45, "Corte": "90°"},
        {"Perfil": "SU-041 (Travessas)", "Qtd": 4 * qtd, "Medida": (L + 12) / 2, "Corte": "90°"}
    ]
    vidro = {"L": (L - 110) / 2, "H": H - 145, "Qtd": 2 * qtd}
    materiais = [
        {"Item": "Roldanas Nylon", "Qtd": 4 * qtd},
        {"Item": "Fecho Caracol/Concha", "Qtd": 1 * qtd},
        {"Item": "Escova de Vedação (m)", "Qtd": round(((H*4)+(L*2))/1000, 2)}
    ]
    return cortes, vidro, materiais

# --- INTERFACE ---
st.title("📐 ESQUADPLAN PRO - Gestão de Engenharia")
tabs = st.tabs(["👤 CLIENTES", "📇 CRM", "🛠️ ENGENHARIA/ITENS", "📑 ORÇAMENTO", "📋 PRODUÇÃO/FINANCEIRO", "📦 ESTOQUE"])

# --- TAB 1: CADASTRO COMPLETO ---
with tabs[0]:
    st.header("Cadastro Detalhado de Cliente")
    with st.form("f_cli"):
        c1, c2, c3 = st.columns([2,1,1])
        n = c1.text_input("Nome/Razão Social")
        t = c2.text_input("WhatsApp")
        e = c3.text_input("E-mail")
        
        st.markdown("---")
        e1, e2, e3, e4 = st.columns([1, 2, 1, 1])
        cp, ru, nu, ba = e1.text_input("CEP"), e2.text_input("Rua"), e3.text_input("Nº"), e4.text_input("Bairro")
        
        cid, ent, obs = st.text_input("Cidade"), st.text_input("Endereço de Entrega"), st.text_area("Observações")
        
        if st.form_submit_button("💾 SALVAR CLIENTE"):
            if n:
                st.session_state.banco_clientes.append({
                    "Nome": n, "Tel": t, "CEP": cp, "End": f"{ru}, {nu} - {ba}", "Cid": cid, 
                    "Status": "Orçamento", "Obs": obs, "Entrega": ent, "Data": datetime.now().strftime("%d/%m/%Y")
                })
                st.success("Cliente Cadastrado!")
            else: st.error("Nome obrigatório.")

# --- TAB 2: CRM ---
with tabs[1]:
    st.header("Gestão de Status e Contatos")
    if st.session_state.banco_clientes:
        st.dataframe(pd.DataFrame(st.session_state.banco_clientes), use_container_width=True)
    else: st.info("Sem clientes.")

# --- TAB 3: TIPOLOGIA & ENGENHARIA ---
with tabs[2]:
    st.header("Configuração Técnica")
    if st.session_state.banco_clientes:
        cli_ref = st.selectbox("Selecione o Cliente", [c['Nome'] for c in st.session_state.banco_clientes])
        
        r1, r2, r3 = st.columns([2, 1, 1])
        amb = r1.text_input("Ambiente", "Sala")
        tipo = r2.selectbox("Tipologia", ["Janela Suprema 2 Fls", "Box Temperado", "Espelho"])
        inst = r3.selectbox("Instalação", ["Contra-marco", "Bucha/Parafuso", "Kit Box"])
        
        l_vão = st.number_input("Largura (mm)", value=1000)
        h_vão = st.number_input("Altura (mm)", value=1000)
        p_venda = st.number_input("Preço de Venda (R$)", value=0.0)

        if st.button("➕ GERAR ENGENHARIA E ADICIONAR"):
            cortes, vidro, mats = calcular_engenharia_suprema(l_vão, h_vão, tipo, 1)
            cm = f"{l_vão+44}x{h_vão+44}" if inst == "Contra-marco" else "N/A"
            
            st.session_state.carrinho.append({
                "Cliente": cli_ref, "Ambiente": amb, "Peça": tipo, "Medida": f"{l_vão}x{h_vão}",
                "Valor": p_venda, "Cortes": cortes, "Vidro": vidro, "Checklist": mats, "CM": cm
            })
            st.success(f"Engenharia gerada para {amb}!")
    else: st.warning("Cadastre um cliente primeiro.")

# --- TAB 4: ORÇAMENTO & PAGAMENTO ---
with tabs[3]:
    st.header("📑 Orçamento e Fechamento")
    if st.session_state.carrinho:
        df_orc = pd.DataFrame(st.session_state.carrinho)
        st.table(df_orc[["Ambiente", "Peça", "Medida", "Valor"]])
        
        st.divider()
        f1, f2, f3 = st.columns(3)
        meio = f1.selectbox("Pagamento", ["Pix", "Dinheiro", "Cartão", "Boleto"])
        desc = f2.number_input("Desconto (R$)", value=0.0)
        parc = f3.number_input("Parcelas", min_value=1, value=1)
        
        total = df_orc["Valor"].sum() - desc
        st.metric("TOTAL A PAGAR", f"R$ {total:.2f}")

        if st.button("🚀 FECHAR PEDIDO E GERAR PLANOS"):
            venda = {
                "Cliente": df_orc["Cliente"].iloc[0], "Data": datetime.now().strftime("%d/%m/%Y"),
                "Itens": st.session_state.carrinho.copy(), "Total": total, "Pgto": f"{meio} {parc}x"
            }
            st.session_state.obras_fechadas.append(venda)
            st.session_state.carrinho = []
            st.success("Pedido enviado para Produção!")
            st.rerun()

# --- TAB 5: PRODUÇÃO, CHECKLIST E FINANCEIRO ---
with tabs[4]:
    st.header("📋 Ordens de Produção e Financeiro")
    for obra in st.session_state.obras_fechadas:
        with st.expander(f"📦 OBRA: {obra['Cliente']} - {obra['Data']}"):
            st.write(f"**Financeiro:** {obra['Pgto']} | **Valor:** R$ {obra['Total']:.2f}")
            
            for item in obra['Itens']:
                st.markdown(f"### 📍 {item['Ambiente']} ({item['Peça']})")
                col_c1, col_c2 = st.columns(2)
                
                with col_c1:
                    st.write("**🪚 PLANO DE CORTE (PERFIS):**")
                    st.table(pd.DataFrame(item['Cortes']))
                    st.write(f"📐 **Contra-marco:** {item['CM']}")
                
                with col_c2:
                    st.write("**💎 PEDIDO DE VIDROS:**")
                    v = item['Vidro']
                    st.warning(f"{v['Qtd']} Pçs - {v['L']:.0f} x {v['H']:.0f} mm")
                    
                    st.write("**📦 CHECKLIST DE MATERIAIS:**")
                    st.table(pd.DataFrame(item['Checklist']))
                st.divider()

# --- TAB 6: ESTOQUE ---
with tabs[5]:
    st.header("Estoque")
    st.write(st.session_state.estoque)
    if st.button("RESET GERAL"): st.session_state.clear(); st.rerun()
