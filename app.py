import streamlit as st
import pandas as pd
import math
from datetime import datetime

# CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Serralheria Control v6.0", layout="wide")

# --- INICIALIZAÇÃO DO BANCO DE DADOS (SESSION STATE) ---
if 'estoque' not in st.session_state:
    st.session_state.estoque = {
        "Barras Alumínio (m)": 0.0,
        "Roldanas (un)": 0,
        "Fechos (un)": 0,
        "Escova Vedação (m)": 0.0,
        "Silicone (tubos)": 0
    }
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []
if 'obras_fechadas' not in st.session_state:
    st.session_state.obras_fechadas = []
if 'historico_estoque' not in st.session_state:
    st.session_state.historico_estoque = []

st.title("🏗️ Serralheria Pro 6.0 - Gestão de Estoque & Produção")

# --- FUNÇÕES DE AUXÍLIO ---
def registrar_estoque(item, qtd, tipo="Entrada"):
    if tipo == "Entrada":
        st.session_state.estoque[item] += qtd
    else:
        st.session_state.estoque[item] -= qtd
    st.session_state.historico_estoque.append({
        "Data": datetime.now().strftime("%d/%m %H:%M"),
        "Tipo": tipo, "Item": item, "Qtd": qtd
    })

# --- ABAS ---
tab_config, tab_pedido, tab_estoque, tab_obras, tab_fin = st.tabs([
    "🛠️ CONFIG. PEÇA", "🛒 PROJETO ATUAL", "📦 ESTOQUE/ALMOXARIFADO", "📋 OBRAS CONCLUÍDAS", "📈 FINANCEIRO"
])

# --- ABA 1: CONFIGURAÇÃO ---
with tab_config:
    st.header("Nova Esquadria")
    with st.expander("📍 Localização e Instalação", expanded=True):
        c1, c2, c3 = st.columns(3)
        ambiente = c1.text_input("Ambiente (Ex: Cozinha, Quarto 1)", "Sala")
        metodo_inst = c2.selectbox("Método de Instalação", ["Bucha e Parafuso", "Com Contra-marco", "Alvenaria Direta"])
        cliente = c3.text_input("Cliente/Obra", "Nova Obra")

    with st.expander("📐 Medidas e Tipologia"):
        col1, col2, col3 = st.columns(3)
        tipo = col1.selectbox("Tipologia", ["Janela Correr 2 Fls", "Janela Correr 4 Fls", "Porta Giro 1 Fl"])
        L = col1.number_input("Largura (mm)", value=1200)
        H = col1.number_input("Altura (mm)", value=1000)
        qtd = col2.number_input("Quantidade de Peças", min_value=1, value=1)
        cor = col2.selectbox("Cor Alumínio", ["Branco", "Preto", "Natural"])
        v_tipo = col3.selectbox("Vidro", ["Temperado 8mm", "Laminado 6mm"])
        v_cor = col3.selectbox("Cor Vidro", ["Incolor", "Fumê"])

    if st.button("➕ ADICIONAR AO PROJETO"):
        # Cálculos de materiais para baixa de estoque posterior
        perimetro = ((L*2 + H*2) / 1000) * qtd
        folhas = 2 if "2 Fls" in tipo else 4
        
        item_projeto = {
            "Ambiente": ambiente,
            "Peça": f"{tipo} ({cor})",
            "Medida": f"{L}x{H}",
            "Instalação": metodo_inst,
            "Qtd": qtd,
            "Custo_Est": (L*H/1000000) * 550 * qtd,
            # Dados para baixa automática:
            "m_alu": (perimetro * 1.5), # Estimativa de metros lineares de perfis
            "roldanas": folhas * qtd,
            "escova": perimetro * 2
        }
        st.session_state.carrinho.append(item_projeto)
        st.success(f"Item para {ambiente} adicionado!")

# --- ABA 2: PROJETO ATUAL & BAIXA ---
with tab_pedido:
    if st.session_state.carrinho:
        st.header("Itens do Orçamento")
        df_c = pd.DataFrame(st.session_state.carrinho)
        st.table(df_c[["Ambiente", "Peça", "Medida", "Instalação", "Qtd"]])
        
        total_obra = df_c["Custo_Est"].sum()
        st.subheader(f"Total Estimado: R$ {total_obra:.2f}")
        
        if st.button("🚀 FECHAR PEDIDO E DAR BAIXA NO ESTOQUE"):
            for item in st.session_state.carrinho:
                registrar_estoque("Barras Alumínio (m)", item['m_alu'], "Saída")
                registrar_estoque("Roldanas (un)", item['roldanas'], "Saída")
                registrar_estoque("Escova Vedação (m)", item['escova'], "Saída")
            
            st.session_state.obras_fechadas.append({
                "Cliente": cliente, "Data": datetime.now().strftime("%d/%m/%Y"),
                "Itens": st.session_state.carrinho.copy(), "Valor": total_obra
            })
            st.session_state.carrinho = []
            st.balloons()
            st.rerun()
    else:
        st.info("O projeto está vazio.")

# --- ABA 3: ESTOQUE/ALMOXARIFADO ---
with tab_estoque:
    st.header("📦 Controle de Almoxarifado")
    
    # Exibição dos cards de estoque
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Alumínio (m)", f"{st.session_state.estoque['Barras Alumínio (m)']:.1f}m")
    c2.metric("Roldanas", st.session_state.estoque['Roldanas (un)'])
    c3.metric("Fechos", st.session_state.estoque['Fechos (un)'])
    c4.metric("Escova (m)", f"{st.session_state.estoque['Escova Vedação (m)']:.1f}m")

    with st.expander("📥 Entrada Manual de Material (Compra)"):
        col_e1, col_e2 = st.columns(2)
        item_add = col_e1.selectbox("Item Comprado", list(st.session_state.estoque.keys()))
        qtd_add = col_e2.number_input("Quantidade Adquirida", min_value=0.0)
        if st.button("Confirmar Entrada"):
            registrar_estoque(item_add, qtd_add, "Entrada")
            st.success("Estoque Atualizado!")
            st.rerun()

    st.subheader("📜 Histórico de Movimentação")
    st.dataframe(pd.DataFrame(st.session_state.historico_estoque), use_container_width=True)

# --- ABA 4: OBRAS CONCLUÍDAS ---
with tab_obras:
    for obra in st.session_state.obras_fechadas:
        with st.expander(f"Obra: {obra['Cliente']} - {obra['Data']}"):
            st.write("**Lista de Ambientes e Instalação:**")
            st.table(pd.DataFrame(obra['Itens'])[["Ambiente", "Peça", "Medida", "Instalação"]])
