import streamlit as st
import pandas as pd

# CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Mestre das Esquadrias v2.0", layout="wide")

st.title("🛠️ Sistema de Gestão de Esquadrias - Linha Suprema")
st.markdown("---")

# --- SIDEBAR: ENTRADA DE DADOS ---
with st.sidebar:
    st.header("👤 Obra / Cliente")
    cliente = st.text_input("Nome do Cliente", "Obra Exemplo")
    
    st.header("📐 Medidas do Vão")
    L = st.number_input("Largura (mm)", min_value=100, value=1500)
    H = st.number_input("Altura (mm)", min_value=100, value=1200)
    
    st.header("⚙️ Configurações")
    tipologia = st.selectbox("Tipologia", [
        "Janela Correr 2 Fls", 
        "Janela Correr 3 Fls (Triplo)",
        "Janela Correr 4 Fls",
        "Porta Giro 1 Fl"
    ])
    
    cor = st.selectbox("Cor do Alumínio", ["Natural", "Branco", "Preto", "Bronze"])
    # Ajuste de preço por cor
    acrescimo_cor = 1.0 if cor == "Natural" else 1.15 # 15% a mais para cores
    
    p_alu_base = st.number_input("Preço Alumínio Base (R$/kg)", value=45.0)
    p_alu = p_alu_base * acrescimo_cor
    p_vidro = st.number_input("Preço Vidro (R$/m2)", value=150.0)

# --- FUNÇÃO DE CÁLCULO DE ENGENHARIA ---
def calcular(L, H, tipo):
    res = {}
    if "2 Fls" in tipo:
        res = {'trav': (L+12)/2, 'mont': H-45, 'v_l': (L-110)/2, 'v_h': H-145, 'qtd': 2, 'peso_m': 0.65}
    elif "3 Fls" in tipo:
        res = {'trav': (L+106)/3, 'mont': H-45, 'v_l': (L-60)/3, 'v_h': H-145, 'qtd': 3, 'peso_m': 0.72}
    elif "4 Fls" in tipo:
        res = {'trav': (L+115)/4, 'mont': H-45, 'v_l': (L-160)/4, 'v_h': H-145, 'qtd': 4, 'peso_m': 0.68}
    else: # Porta Giro
        res = {'trav': L-68, 'mont': H-35, 'v_l': L-125, 'v_h': H-210, 'qtd': 1, 'peso_m': 0.85}
    
    # Cálculo de Peso e Barras
    metragem_total = (L*2 + H*2 + (res['mont']*res['qtd']*2) + (res['trav']*res['qtd']*2)) / 1000
    res['peso_total'] = metragem_total * res['peso_m']
    res['barras'] = (metragem_total / 6) + 0.5 # Estimativa com sobra
    return res

dados = calcular(L, H, tipologia)
area_vidro = (dados['v_l'] * dados['v_h'] * dados['qtd']) / 1_000_000

# --- INTERFACE DE ABAS ---
tab_orc, tab_corte, tab_vidro, tab_check = st.tabs(["💰 Orçamento", "🪚 Plano de Corte", "💎 Vidros & Ferragens", "✅ Checklist"])

with tab_orc:
    col1, col2, col3 = st.columns(3)
    custo_alu = dados['peso_total'] * 1.05 * p_alu
    custo_vidro = area_vidro * p_vidro
    total = custo_alu + custo_vidro + 120 # +120 kit acessórios
    
    col1.metric("Peso Alumínio", f"{dados['peso_total']*1.05:.2f} kg")
    col2.metric("Custo Total", f"R$ {total:.2f}")
    col3.metric("Preço de Venda (Sug.)", f"R$ {total*1.6:.2f}") # Markup 60%
    
    st.write(f"**Resumo:** Alumínio {cor} para o cliente **{cliente}**.")

with tab_corte:
    st.subheader("Lista de Peças para Cortar")
    lista = [
        {"Peça": "Trilhos (Superior/Inferior)", "Qtd": 2, "Medida (mm)": L},
        {"Peça": "Marcos Laterais", "Qtd": 2, "Medida (mm)": H},
        {"Peça": "Montantes da Folha", "Qtd": dados['qtd']*2, "Medida (mm)": dados['mont']},
        {"Peça": "Travessas da Folha", "Qtd": dados['qtd']*2, "Medida (mm)": dados['trav']}
    ]
    st.table(pd.DataFrame(lista))
    st.warning(f"📦 **Estoque:** Você vai precisar de aproximadamente **{int(dados['barras'])+1} barras** de 6 metros.")

with tab_vidro:
    st.info(f"**Pedido para a Vidraçaria:**")
    st.write(f"Quantidade: {dados['qtd']} peças")
    st.write(f"Medida: **{dados['v_l']:.1f} x {dados['v_h']:.1f} mm**")
    st.write(f"**Acessórios:** Roldanas ({dados['qtd']*2} un), Escova Vedação, Fechos.")

with tab_check:
    st.subheader("Instalação e Qualidade")
    st.checkbox("Vão está no prumo e nível?")
    st.checkbox(" Silicone aplicado nos cantos e parafusos?")
    st.checkbox("Folhas correndo sem esforço?")
    st.checkbox("Vidros limpos e sem riscos?")
    if st.button("Finalizar Ordem de Serviço"):
        st.balloons()
        st.success("Dados salvos com sucesso!")
