import streamlit as st
import pandas as pd
import math
from datetime import datetime

# CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Serralheria Pro v9.0", layout="wide")

# --- INICIALIZAÇÃO SEGURA DO SISTEMA ---
if 'estoque' not in st.session_state:
    # Nomes simples sem acentos para evitar o erro KeyError
    st.session_state.estoque = {"Aluminio_m": 0.0, "Roldanas_un": 0, "Fechos_un": 0, "Vidro_m2": 0.0}
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []
if 'obras_fechadas' not in st.session_state:
    st.session_state.obras_fechadas = []

st.title("⚒️ Gestão Serralheria Pro - Linha Suprema")

# --- ABAS NA ORDEM QUE VOCÊ PEDIU ---
tabs = st.tabs([
    "👤 1. DADOS DO CLIENTE", 
    "🛠️ 2. TIPOLOGIA E MEDIDAS", 
    "🛒 3. ITENS DO PROJETO", 
    "📦 4. ALMOXARIFADO", 
    "📋 5. OBRAS FECHADAS"
])

tab_cliente, tab_config, tab_pedido, tab_estoque, tab_obras = tabs

# --- ABA 1: DADOS DO CLIENTE (SOZINHA NA FRENTE) ---
with tab_cliente:
    st.header("Identificação do Cliente / Obra")
    c1, c2 = st.columns(2)
    with c1:
        st.session_state.cliente_atual = st.text_input("Nome Completo do Cliente", "Ex: João da Silva")
        st.session_state.contato_atual = st.text_input("WhatsApp / Telefone", "(00) 00000-0000")
    with c2:
        st.session_state.endereco_atual = st.text_area("Endereço da Entrega/Obra", "Rua...")
        st.session_state.status_atual = st.selectbox("Situação", ["Orçamento", "Pedido Confirmado", "Urgente"])
    
    st.info("💡 Após preencher, siga para a próxima aba para configurar as peças.")

# --- ABA 2: TIPOLOGIA E MEDIDAS (COM AMBIENTE E INSTALAÇÃO) ---
with tab_config:
    st.header("Configuração Técnica da Peça")
    
    # Linha 1: Onde e Como
    row1_1, row1_2, row1_3 = st.columns([2, 2, 1])
    ambiente = row1_1.text_input("Descrição do Ambiente", "Ex: Janela da Suíte")
    metodo_inst = row1_2.selectbox("Método de Instalação", ["Com Contra-marco", "Bucha e Parafuso", "Alvenaria Direta"])
    qtd_pecas = row1_3.number_input("Quantidade", min_value=1, value=1)

    st.divider()

    # Linha 2: Tipologia e Dimensões
    row2_1, row2_2, row2_3 = st.columns([2, 1, 1])
    tipologia = row2_1.selectbox("Tipologia (Linha Suprema)", [
        "Janela Correr 2 Fls", 
        "Janela Correr 3 Fls (Trilho Triplo)", 
        "Janela Correr 4 Fls",
        "Porta Giro 1 Fl"
    ])
    L = row2_2.number_input("Largura L (mm)", value=1500)
    H = row2_3.number_input("Altura H (mm)", value=1200)

    # Linha 3: Materiais
    row3_1, row3_2, row3_3 = st.columns(3)
    cor_alu = row3_1.selectbox("Cor Alumínio", ["Branco", "Preto", "Natural", "Bronze"])
    v_tipo = row3_2.selectbox("Tipo Vidro", ["Temperado 8mm", "Laminado 6mm", "Comum 4mm"])
    v_cor = row3_3.selectbox("Cor Vidro", ["Incolor", "Verde", "Fumê", "Refletivo"])

    # LÓGICA DE CORTES E DESCONTOS
    def calcular_engenharia(L, H, tipo, qtd):
        cortes = []
        if "2 Fls" in tipo:
            cortes = [
                {"P": "SU-001/002 (Trilhos)", "Q": 2*qtd, "M": L, "A": "90°"},
                {"P": "SU-003 (Marco Lat)", "Q": 2*qtd, "M": H, "A": "90°"},
                {"P": "SU-039/040 (Montantes)", "Q": 4*qtd, "M": H-45, "A": "90°"},
                {"P": "SU-041 (Travessas)", "Q": 4*qtd, "M": (L+12)/2, "A": "90°"}
            ]
            vl, vh = (L-110)/2, H-145
        elif "3 Fls" in tipo: # Trilho Triplo
            cortes = [
                {"P": "SU-005/006 (Trilho 3)", "Q": 2*qtd, "M": L, "A": "90°"},
                {"P": "SU-039/040", "Q": 6*qtd, "M": H-45, "A": "90°"},
                {"P": "SU-041", "Q": 6*qtd, "M": (L+106)/3, "A": "90°"}
            ]
            vl, vh = (L-60)/3, H-145
        elif "4 Fls" in tipo:
            cortes = [
                {"P": "SU-001/002", "Q": 2*qtd, "M": L, "A": "90°"},
                {"P": "SU-039/040", "Q": 8*qtd, "M": H-45, "A": "90°"},
                {"P": "SU-041", "Q": 8*qtd, "M": (L+115)/4, "A": "90°"}
            ]
            vl, vh = (L-160)/4, H-145
        else: # Porta Giro
            cortes = [{"P": "SU-007 (Marco)", "Q": 3*qtd, "M": "Calcular", "A": "45°"}]
            vl, vh = L-125, H-210
        
        return cortes, vl, vh

    if st.button("➕ ADICIONAR ITEM AO PROJETO", use_container_width=True):
        cortes_list, vl, vh = calcular_engenharia(L, H, tipologia, qtd_pecas)
        total_m_alu = sum([c['Q'] * c['M'] for c in cortes_list if isinstance(c['M'], (int, float))]) / 1000
        
        item = {
            "Ambiente": ambiente, "Peça": tipologia, "Medida": f"{L}x{H}", "Qtd": qtd_pecas,
            "Instalação": metodo_inst, "Vidro": f"{v_tipo} {v_cor} ({vl:.0f}x{vh:.0f})",
            "Custo_Estimado": (total_m_alu * 35) + (250 * qtd_pecas), # Estimativa
            "Lista_Corte": cortes_list, "Consumo_Alu": total_m_alu, "Vidro_Pedido": f"{vl:.0f}x{vh:.0f}"
        }
        st.session_state.carrinho.append(item)
        st.toast(f"✅ {ambiente} adicionado!")

# --- ABA 3: ITENS DO PROJETO (ORÇAMENTO E FECHAMENTO) ---
with tab_pedido:
    st.header(f"Resumo da Obra: {st.session_state.get('cliente_atual', 'Sem Nome')}")
    if st.session_state.carrinho:
        df_itens = pd.DataFrame(st.session_state.carrinho)
        st.dataframe(df_itens[["Ambiente", "Peça", "Medida", "Qtd", "Instalação", "Vidro"]], use_container_width=True)
        
        total = df_itens["Custo_Estimado"].sum()
        st.metric("Total Materiais", f"R$ {total:.2f}")

        # FINANCEIRO
        f1, f2 = st.columns(2)
        forma = f1.selectbox("Pagamento", ["Pix", "Dinheiro", "Cartão Débito", "Cartão Crédito", "Parcelado"])
        desc = f2.number_input("Desconto (R$)", value=0.0)

        if st.button("🚀 FECHAR PEDIDO (BAIXA NO ESTOQUE)"):
            # BAIXA SEGURA
            total_alu_obra = df_itens["Consumo_Alu"].sum()
            st.session_state.estoque["Aluminio_m"] -= total_alu_obra
            
            obra_final = {
                "Cliente": st.session_state.cliente_atual, "Data": datetime.now().strftime("%d/%m/%Y"),
                "Valor": total - desc, "Itens": st.session_state.carrinho.copy()
            }
            st.session_state.obras_fechadas.append(obra_final)
            st.session_state.carrinho = []
            st.success("Obra finalizada e enviada para o histórico!")
            st.rerun()
    else:
        st.info("Nenhum item configurado.")

# --- ABA 4: ALMOXARIFADO (ESTOQUE) ---
with tab_estoque:
    st.header("📦 Controle de Materiais")
    col_e1, col_e2, col_e3 = st.columns(3)
    col_e1.metric("Alumínio (m)", f"{st.session_state.estoque['Aluminio_m']:.1f}")
    col_e2.metric("Roldanas", st.session_state.estoque['Roldanas_un'])
    col_e3.metric("Fechos", st.session_state.estoque['Fechos_un'])

    with st.expander("📥 Registrar Entrada de Compra"):
        item_c = st.selectbox("Item", list(st.session_state.estoque.keys()))
        qtd_c = st.number_input("Qtd", min_value=0.0)
        if st.button("Salvar Compra"):
            st.session_state.estoque[item_c] += qtd_c
            st.rerun()

# --- ABA 5: OBRAS FECHADAS (CHECKLIST COMPLETO) ---
with tab_obras:
    for obra in st.session_state.obras_fechadas:
        with st.expander(f"📁 {obra['Data']} - {obra['Cliente']} - R$ {obra['Valor']:.2f}"):
            st.markdown("### 📜 PLANILHA DE PRODUÇÃO")
            for item in obra['Itens']:
                st.write(f"📍 **{item['Ambiente']}** - {item['Peça']} ({item['Medida']})")
                st.write(f"🔹 *Instalação:* {item['Instalação']} | *Vidro:* {item['Vidro']}")
                st.write("**Cortes:**")
                st.dataframe(pd.DataFrame(item['Lista_Corte']), use_container_width=True)
                st.divider()
