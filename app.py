import streamlit as st
import pandas as pd
import math
from datetime import datetime

# CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Serralheria & Vidraçaria Pro v10", layout="wide")

# --- BANCO DE DADOS INICIAL ---
if 'estoque' not in st.session_state:
    st.session_state.estoque = {
        "Aluminio_m": {"qtd": 0.0, "custo": 0.0},
        "Roldanas_un": {"qtd": 0, "custo": 0.0},
        "Fechos_un": {"qtd": 0, "custo": 0.0},
        "Kit_Box_un": {"qtd": 0, "custo": 0.0},
        "Espelho_m2": {"qtd": 0.0, "custo": 0.0}
    }
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []
if 'obras_fechadas' not in st.session_state:
    st.session_state.obras_fechadas = []

st.title("⚒️ Serralheria & Vidraçaria Pro v10")

# --- ABAS ---
tabs = st.tabs(["👤 CLIENTE", "🛠️ TIPOLOGIA/MEDIDAS", "🛒 PROJETO", "📦 ESTOQUE & CUSTOS", "📋 OBRAS"])
tab_cli, tab_config, tab_ped, tab_est, tab_obr = tabs

# --- ABA 1: CLIENTE ---
with tab_cli:
    st.header("Dados do Cliente")
    c1, c2 = st.columns(2)
    st.session_state.cliente = c1.text_input("Nome", "Cliente Padrão")
    st.session_state.obra_ref = c2.text_input("Ref. Obra", "Residencial")

# --- ABA 2: TIPOLOGIA E MEDIDAS ---
with tab_config:
    st.header("Configuração da Peça / Item")
    
    # Campo de Ambiente e Instalação
    col_a1, col_a2, col_a3 = st.columns(3)
    ambiente = col_a1.text_input("Ambiente", "Sala")
    metodo = col_a2.selectbox("Instalação", ["Contra-marco", "Bucha/Parafuso", "Colado (Espelho)", "Kit Box"])
    qtd = col_a3.number_input("Quantidade", min_value=1, value=1)

    st.divider()
    
    # Seleção de Tipologia com "Fotos" (Tags de Imagem)
    t1, t2 = st.columns([1, 2])
    with t1:
        categoria = st.radio("Categoria", ["Linha Suprema", "Vidro Temperado/Box", "Espelhos"])
        
        if categoria == "Linha Suprema":
            tipo = st.selectbox("Modelo", ["Janela 2 Fls", "Janela 4 Fls", "Porta Giro"])
            
        elif categoria == "Vidro Temperado/Box":
            tipo = st.selectbox("Modelo", ["Box Padrão Reta", "Box Canto L", "Fixo Temperado"])
            
        else:
            tipo = st.selectbox("Modelo", ["Espelho Simples", "Espelho Bisotê", "Espelho com Led"])
            

    with t2:
        L = st.number_input("Largura (mm)", value=1000)
        H = st.number_input("Altura (mm)", value=1000)
        cor = st.selectbox("Cor Alumínio/Kit", ["Branco", "Preto", "Fosco", "Cromado"])

    # Lógica de Contra-marco e Engenharia
    def calcular_tudo(L, H, tipo, cat):
        cortes = []
        cm_l, cm_h = 0, 0
        if cat == "Linha Suprema":
            cm_l, cm_h = L + 44, H + 44 # Medida externa do contra-marco
            cortes = [{"P": "SU-001", "M": L, "Q": 2}, {"P": "SU-039", "M": H-45, "Q": 4}]
        elif "Box" in tipo:
            cortes = [{"P": "Trilho Superior", "M": L, "Q": 1}, {"P": "U de Fixação", "M": H, "Q": 2}]
        
        return cortes, cm_l, cm_h

    if st.button("➕ ADICIONAR AO PROJETO", use_container_width=True):
        cortes, cml, cmh = calcular_tudo(L, H, tipo, categoria)
        item = {
            "Ambiente": ambiente, "Item": f"{tipo} ({cor})", "Medida": f"{L}x{H}",
            "Instalacao": metodo, "Qtd": qtd, "Cortes": cortes,
            "CM": f"{cml}x{cmh}" if metodo == "Contra-marco" else "N/A"
        }
        st.session_state.carrinho.append(item)
        st.success("Adicionado!")

# --- ABA 4: ESTOQUE E PREÇO DE CUSTO ---
with tab_est:
    st.header("📦 Gestão de Compras e Estoque")
    
    # Exibição com Preço de Custo
    for k, v in st.session_state.estoque.items():
        c1, c2, c3 = st.columns([2,1,1])
        c1.write(f"**{k}**")
        c2.metric("Qtd", v['qtd'])
        c3.metric("Custo Médio", f"R$ {v['custo']:.2f}")

    st.divider()
    st.subheader("🛒 Registrar Entrada (Compra)")
    with st.form("add_est"):
        it = st.selectbox("Item Comprado", list(st.session_state.estoque.keys()))
        q_comprada = st.number_input("Quantidade", min_value=0.0)
        p_pago = st.number_input("Preço Total Pago (R$)", min_value=0.0)
        if st.form_submit_button("Salvar Compra"):
            # Atualiza média de custo e quantidade
            novo_custo = p_pago / q_comprada if q_comprada > 0 else 0
            st.session_state.estoque[it]['qtd'] += q_comprada
            st.session_state.estoque[it]['custo'] = novo_custo
            st.rerun()

    if st.button("🚨 ZERAR TODO ESTOQUE"):
        for k in st.session_state.estoque:
            st.session_state.estoque[k]['qtd'] = 0.0
        st.rerun()

# --- ABA 5: OBRAS E CHECKLIST ---
with tab_obr:
    for obra in st.session_state.obras_fechadas:
        with st.expander(f"Obra: {obra['Cliente']}"):
            for item in obra['Itens']:
                st.write(f"📍 **{item['Ambiente']}**")
                if item['CM'] != "N/A":
                    st.warning(f"📐 MEDIDA DO CONTRA-MARCO: {item['CM']} mm")
                st.table(pd.DataFrame(item['Cortes']))
