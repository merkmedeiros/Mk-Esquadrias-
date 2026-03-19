import streamlit as st
import pandas as pd
import math
from datetime import datetime

# CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Serralheria ERP Pro v5.0", layout="wide")

# --- BANCO DE DADOS EM MEMÓRIA ---
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []
if 'obras_fechadas' not in st.session_state:
    st.session_state.obras_fechadas = []

st.title("🏭 Sistema Integrado de Esquadrias - Gestão 360°")

# --- FUNÇÕES DE ENGENHARIA ---
def get_detalhes_producao(item):
    """Retorna checklist de materiais baseado na tipologia"""
    L, H, Qtd = item['L'], item['H'], item['Qtd']
    if "2 Fls" in item['Tipo']:
        materiais = [
            {"Categoria": "Alumínio", "Ref": "SU-001/002", "Qtd": 2 * Qtd, "Medida": L, "Corte": "90°"},
            {"Categoria": "Alumínio", "Ref": "SU-003", "Qtd": 2 * Qtd, "Medida": H, "Corte": "90°"},
            {"Categoria": "Alumínio", "Ref": "SU-039/040", "Qtd": 4 * Qtd, "Medida": H-45, "Corte": "90°"},
            {"Categoria": "Acessório", "Ref": "Roldana", "Qtd": 2 * Qtd, "Medida": "-", "Corte": "-"},
            {"Categoria": "Acessório", "Ref": "Escova 5x5", "Qtd": 1, "Medida": "Rolo", "Corte": "-"},
            {"Categoria": "Vidro", "Ref": item['Vidro'], "Qtd": 2 * Qtd, "Medida": f"{item['V_L']}x{item['V_H']}", "Corte": "Reto"}
        ]
    else: # Exemplo simplificado para outras
        materiais = [{"Categoria": "Geral", "Ref": "Ver Manual", "Qtd": 1, "Medida": "-", "Corte": "-"}]
    return materiais

# --- INTERFACE DE ABAS ---
tab_config, tab_pedido, tab_pagamento, tab_obras, tab_financeiro = st.tabs([
    "🛠️ 1. CONFIGURAR PEÇA", "🛒 2. ITENS & PROJETO", "💳 3. PAGAMENTO", "📦 4. OBRAS FECHADAS", "📈 5. FLUXO CAIXA"
])

# --- ABA 1: CONFIGURAÇÃO ---
with tab_config:
    st.header("Configuração da Esquadria")
    with st.expander("👤 Identificação do Projeto", expanded=True):
        cliente = st.text_input("Nome do Cliente/Obra", "Residência Silva")
        contato = st.text_input("WhatsApp")

    c1, c2, c3 = st.columns(3)
    with c1:
        tipo = st.selectbox("Tipologia", ["Janela Correr 2 Fls", "Porta Giro 1 Fl", "Janela Maxim-ar"])
        L = st.number_input("Largura Vão (mm)", value=1000)
        H = st.number_input("Altura Vão (mm)", value=1000)
    with c2:
        qtd = st.number_input("Quantidade", min_value=1, value=1)
        cor_alu = st.selectbox("Cor Alumínio", ["Branco", "Preto", "Bronze"])
    with c3:
        vidro_tipo = st.selectbox("Vidro", ["Temperado 8mm", "Laminado 6mm", "Comum 4mm"])
        vidro_cor = st.selectbox("Cor Vidro", ["Incolor", "Verde", "Fumê", "Leitoso"])
        acabamento = st.radio("Acabamento", ["Liso", "Película G20", "Jateado"])

    if st.button("➕ ADICIONAR AO PROJETO"):
        # Cálculos de folga (Exemplo Suprema)
        vl, vh = (L-110)/2, H-145
        custo_est = (L*H/1000000) * 450 # Estimativa base R$ 450/m2
        
        item = {
            "ID": len(st.session_state.carrinho) + 1,
            "Tipo": tipo, "L": L, "H": H, "Qtd": qtd,
            "Vidro": f"{vidro_tipo} {vidro_cor}", "Acab": acabamento,
            "V_L": vl, "V_H": vh, "Custo": custo_est * qtd
        }
        st.session_state.carrinho.append(item)
        st.toast("Item Adicionado!")

# --- ABA 2: ITENS & PROJETO ---
with tab_pedido:
    if st.session_state.carrinho:
        st.header("Resumo do Projeto")
        df_itens = pd.DataFrame(st.session_state.carrinho)
        st.table(df_itens[["Tipo", "L", "H", "Qtd", "Vidro", "Custo"]])
        
        total_bruto = df_itens["Custo"].sum()
        st.subheader(f"Subtotal: R$ {total_bruto:.2f}")
    else:
        st.info("Adicione peças na aba anterior.")

# --- ABA 3: PAGAMENTO ---
with tab_pagamento:
    if st.session_state.carrinho:
        st.header("Condições de Pagamento")
        total_obra = sum(i['Custo'] for i in st.session_state.carrinho)
        
        p1, p2 = st.columns(2)
        with p1:
            metodo = st.selectbox("Forma de Pagamento", ["Pix", "Dinheiro", "Cartão Crédito", "Cartão Débito", "Boleto"])
            desconto = st.number_input("Desconto (R$)", value=0.0)
            acrescimo = st.number_input("Acréscimo/Taxas (R$)", value=0.0)
        with p2:
            parcelas = st.number_input("Número de Parcelas", min_value=1, max_value=12, value=1)
            valor_final = total_obra - desconto + acrescimo
            st.metric("VALOR FINAL", f"R$ {valor_final:.2f}")
            if parcelas > 1:
                st.write(f"Valor da Parcela: {parcelas}x de R$ {valor_final/parcelas:.2f}")

        if st.button("✅ FECHAR PEDIDO & GERAR CHECKLIST"):
            checklist_geral = []
            for item in st.session_state.carrinho:
                checklist_geral.extend(get_detalhes_producao(item))
            
            obra_fechada = {
                "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "Cliente": cliente,
                "Valor": valor_final,
                "Pagamento": f"{metodo} ({parcelas}x)",
                "Itens": st.session_state.carrinho.copy(),
                "Checklist": checklist_geral
            }
            st.session_state.obras_fechadas.append(obra_fechada)
            st.session_state.carrinho = []
            st.success("Pedido Fechado! Vá para a aba 'Obras Fechadas' para ver o Checklist.")
    else:
        st.error("Adicione itens ao projeto primeiro.")

# --- ABA 4: OBRAS FECHADAS (CHECKLIST COMPLETO) ---
with tab_obras:
    st.header("Gerenciamento de Obras")
    for idx, obra in enumerate(st.session_state.obras_fechadas):
        with st.expander(f"📦 OBRA: {obra['Cliente']} | {obra['Data']} | R$ {obra['Valor']:.2f}"):
            st.write(f"**Forma de Pagamento:** {obra['Pagamento']}")
            
            # --- SEÇÃO COMPRAS E CORTE ---
            st.subheader("📋 CHECKLIST DE PRODUÇÃO")
            df_check = pd.DataFrame(obra['Checklist'])
            
            st.markdown("### 🛒 1. Lista de Compras (Perfis e Acessórios)")
            st.dataframe(df_check[df_check['Categoria'] != 'Vidro'], use_container_width=True)
            
            st.markdown("### 💎 2. Pedido de Vidros")
            st.dataframe(df_check[df_check['Categoria'] == 'Vidro'], use_container_width=True)
            
            st.markdown("### 🪚 3. Guia de Corte e Montagem")
            for item in obra['Itens']:
                st.info(f"Peça {item['Tipo']}: Cortar perfis conforme lista acima. Montar com {item['Acab']}.")
            
            st.button(f"📄 Exportar PDF (Obra {idx})", key=f"btn_{idx}")
