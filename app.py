import streamlit as st
import pandas as pd
import math
from datetime import datetime

# CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Serralheria ERP Pro v8.0", layout="wide")

# --- INICIALIZAÇÃO SEGURA DO ESTADO (ESTOQUE E OBRAS) ---
if 'estoque' not in st.session_state:
    st.session_state.estoque = {"Aluminio_m": 100.0, "Roldanas": 100, "Fechos": 50, "Escova_m": 200.0}
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []
if 'obras_fechadas' not in st.session_state:
    st.session_state.obras_fechadas = []

st.title("⚒️ Gestão Suprema - Corte, Estoque e Financeiro")

# --- FUNÇÃO TÉCNICA DE DESCONTOS (LINHA SUPREMA) ---
def calcular_cortes_suprema(L, H, tipo, qtd, ambiente):
    cortes = []
    # Cálculo para Janela de 2 Folhas (Padrão Suprema)
    if "2 Fls" in tipo:
        cortes.append({"Ambiente": ambiente, "Perfil": "SU-001/002 (Trilhos)", "Qtd": 2 * qtd, "Medida": L, "Corte": "90°"})
        cortes.append({"Ambiente": ambiente, "Perfil": "SU-003 (Marcos Lat)", "Qtd": 2 * qtd, "Medida": H, "Corte": "90°"})
        cortes.append({"Ambiente": ambiente, "Perfil": "SU-039/040 (Montantes)", "Qtd": 4 * qtd, "Medida": H - 45, "Corte": "90°"})
        cortes.append({"Ambiente": ambiente, "Perfil": "SU-041 (Travessas)", "Qtd": 4 * qtd, "Medida": (L + 12) / 2, "Corte": "90°"})
        v_l, v_h, v_q = (L - 110) / 2, H - 145, 2 * qtd
    elif "Porta Giro" in tipo:
        cortes.append({"Ambiente": ambiente, "Perfil": "SU-007 (Marco)", "Qtd": 3 * qtd, "Medida": "Ver Medida", "Corte": "45°"})
        cortes.append({"Ambiente": ambiente, "Perfil": "SU-023/024 (Folha)", "Qtd": 4 * qtd, "Medida": H - 35, "Corte": "45°"})
        v_l, v_h, v_q = L - 125, H - 210, 1 * qtd
    
    return cortes, v_l, v_h, v_q

# --- INTERFACE DE ABAS ---
tab_config, tab_pedido, tab_estoque, tab_obras = st.tabs([
    "🛠️ MEDIDAS E TIPOLOGIA", "🛒 ITENS DO PROJETO", "📦 ALMOXARIFADO", "📋 OBRAS FECHADAS"
])

# --- ABA 1: CONFIGURAÇÃO ---
with tab_config:
    st.header("Configuração da Peça por Ambiente")
    
    c1, c2, c3 = st.columns(3)
    cliente_nome = c1.text_input("Cliente", "Obra Nova")
    ambiente = c2.text_input("Ambiente (Ex: Cozinha)", "Sala")
    metodo_inst = c3.selectbox("Instalação", ["Com Contra-marco", "Bucha e Parafuso", "Alvenaria"])

    st.divider()
    
    col1, col2, col3 = st.columns([2,1,2])
    with col1:
        tipologia = st.selectbox("Tipologia", ["Janela Correr 2 Fls", "Porta Giro 1 Fl"])
        L = st.number_input("Largura (mm)", value=1500)
        H = st.number_input("Altura (mm)", value=1200)
        qtd = st.number_input("Quantidade", min_value=1, value=1)
    
    with col2:
        cor = st.selectbox("Cor Alumínio", ["Branco", "Preto", "Natural"])
        p_alu = st.number_input("R$/kg Alumínio", value=48.0)
    
    with col3:
        v_tipo = st.selectbox("Vidro", ["Temperado 6mm", "Temperado 8mm", "Laminado 8mm"])
        v_cor = st.selectbox("Cor Vidro", ["Incolor", "Verde", "Fumê"])
        v_ext = st.selectbox("Adicional", ["Nenhum", "Película G20", "Jateado"])

    if st.button("➕ ADICIONAR AO PROJETO", use_container_width=True):
        lista_cortes, vl, vh, vq = calcular_cortes_suprema(L, H, tipologia, qtd, ambiente)
        
        # Cálculo de consumo de alumínio (simplificado para peso)
        metros_lineares = sum([c['Qtd'] * c['Medida'] for c in lista_cortes if isinstance(c['Medida'], (int, float))]) / 1000
        
        item = {
            "Ambiente": ambiente, "Peça": tipologia, "Medida": f"{L}x{H}", "Qtd": qtd,
            "Instalação": metodo_inst, "Cortes": lista_cortes, 
            "Vidro_Pedido": f"{vq} pçs {vl:.0f}x{vh:.0f} ({v_tipo})",
            "M_Alu": metros_lineares, "Custo": (metros_lineares * 0.7 * p_alu) + 200 # Estimativa
        }
        st.session_state.carrinho.append(item)
        st.success(f"Item {ambiente} adicionado!")

# --- ABA 2: PROJETO ATUAL ---
with tab_pedido:
    if st.session_state.carrinho:
        st.header(f"Projeto: {cliente_nome}")
        df_car = pd.DataFrame(st.session_state.carrinho)
        st.table(df_car[["Ambiente", "Peça", "Medida", "Qtd", "Instalação"]])
        
        total_obra = df_car["Custo"].sum()
        st.subheader(f"Total Materiais: R$ {total_obra:.2f}")
        
        # Financeiro
        pag = st.selectbox("Forma de Pagamento", ["Pix", "Dinheiro", "Cartão 1x", "Cartão Parcelado"])
        
        if st.button("🚀 FINALIZAR OBRA E GERAR LISTA DE CORTE"):
            # Baixa no estoque segura
            total_consumo = df_car["M_Alu"].sum()
            st.session_state.estoque["Aluminio_m"] -= total_consumo
            
            obra = {
                "Cliente": cliente_nome, "Data": datetime.now().strftime("%d/%m/%Y"),
                "Itens": st.session_state.carrinho.copy(), "Valor": total_obra, "Pgto": pag
            }
            st.session_state.obras_fechadas.append(obra)
            st.session_state.carrinho = []
            st.rerun()
    else:
        st.info("Adicione itens na primeira aba.")

# --- ABA 3: ESTOQUE ---
with tab_estoque:
    st.header("📦 Almoxarifado Central")
    c1, c2, c3 = st.columns(3)
    c1.metric("Alumínio Disponível", f"{st.session_state.estoque['Aluminio_m']:.1f} m")
    c2.metric("Roldanas", st.session_state.estoque['Roldanas'])
    c3.metric("Fechos", st.session_state.estoque['Fechos'])
    
    st.divider()
    with st.form("compra"):
        st.subheader("🛒 Registrar Compra de Material")
        it = st.selectbox("Item", list(st.session_state.estoque.keys()))
        val = st.number_input("Quantidade", min_value=0.0)
        if st.form_submit_button("Adicionar ao Estoque"):
            st.session_state.estoque[it] += val
            st.rerun()

# --- ABA 4: OBRAS FECHADAS (CHECKLIST DE CORTE POR AMBIENTE) ---
with tab_obras:
    for obra in st.session_state.obras_fechadas:
        with st.expander(f"📁 {obra['Data']} - {obra['Cliente']} - R$ {obra['Valor']:.2f}"):
            st.markdown("### 🪚 PLANILHA DE CORTE POR AMBIENTE")
            todas_pecas_corte = []
            for item in obra['Itens']:
                todas_pecas_corte.extend(item['Cortes'])
            
            df_corte_final = pd.DataFrame(todas_pecas_corte)
            st.dataframe(df_corte_final, use_container_width=True)
            
            st.markdown("### 💎 PEDIDO DE VIDROS")
            for item in obra['Itens']:
                st.write(f"- **{item['Ambiente']}**: {item['Vidro_Pedido']}")
