import streamlit as st
import pandas as pd

# CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Serralheria Pro v1.0", layout="wide", page_icon="🛠️")

# --- ESTILIZAÇÃO CSS ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_index=True)

# --- CABEÇALHO ---
st.title("🛠️ Gestão de Esquadrias - Linha Suprema")
st.markdown("---")

# --- ENTRADA DE DADOS (SIDEBAR) ---
with st.sidebar:
    st.header("👤 Dados do Cliente")
    cliente = st.text_input("Nome do Cliente/Obra", "Nova Obra")
    
    st.header("📐 Dimensões do Vão")
    L = st.number_input("Largura (mm)", min_value=100, value=1500, step=1)
    H = st.number_input("Altura (mm)", min_value=100, value=1200, step=1)
    
    st.header("⚙️ Especificações")
    tipologia = st.selectbox("Tipologia", [
        "Janela Correr 2 Fls", 
        "Janela Correr 3 Fls (Triplo)", 
        "Janela Correr 4 Fls",
        "Porta Giro 1 Fl",
        "Porta Giro 2 Fls"
    ])
    cor = st.selectbox("Cor do Alumínio", ["Branco", "Preto", "Bronze", "Natural"])
    vidro_tipo = st.selectbox("Tipo de Vidro", ["Incolor", "Fumê", "Verde", "Refletivo"])
    vidro_esp = st.selectbox("Espessura Vidro (mm)", [4, 6, 8, 10])

    st.header("💰 Tabela de Preços")
    p_alu = st.number_input("Preço Alumínio (R$/kg)", value=48.0)
    p_vidro = st.number_input("Preço Vidro (R$/m2)", value=160.0)

# --- LÓGICA DE CÁLCULO (ENGENHARIA) ---
def realizar_calculos(L, H, tipologia):
    res = {}
    # Regras de Desconto Suprema
    if "Janela Correr 2 Fls" in tipologia:
        res['c_travessa'] = (L + 12) / 2
        res['c_montante'] = H - 45
        res['v_largura'] = (L - 110) / 2
        res['v_altura'] = H - 145
        res['v_qtd'] = 2
        res['peso_estimado'] = ((L*2 + H*2 + (H-45)*4 + (res['c_travessa'])*4)/1000) * 0.65
        res['acessorios'] = [("Roldana Simples", 4), ("Fecho Lateral", 1), ("Guia Nylon", 4), ("Escova 5x5 (m)", (H*4+L*2)/1000)]

    elif "Janela Correr 4 Fls" in tipologia:
        res['c_travessa'] = (L + 115) / 4
        res['c_montante'] = H - 45
        res['v_largura'] = (L - 160) / 4
        res['v_altura'] = H - 145
        res['v_qtd'] = 4
        res['peso_estimado'] = ((L*2 + H*2 + (H-45)*8 + (res['c_travessa'])*8)/1000) * 0.68
        res['acessorios'] = [("Roldana Simples", 8), ("Fecho Central", 1), ("Guia Nylon", 8), ("Escova 5x5 (m)", (H*8+L*2)/1000)]

    elif "Porta Giro 1 Fl" in tipologia:
        res['c_travessa'] = L - 68
        res['c_montante'] = H - 35
        res['v_largura'] = L - 125
        res['v_altura'] = H - 210
        res['v_qtd'] = 1
        res['peso_estimado'] = ((L*2 + H*2 + (res['c_travessa'])*2 + (res['c_montante'])*2)/1000) * 0.85
        res['acessorios'] = [("Dobradiça", 3), ("Fechadura Giro", 1), ("Borracha batedor (m)", (H*2+L)/1000)]
    
    # Adicionais padrão para as outras se não selecionadas
    else:
        res = {'c_travessa': 0, 'c_montante': 0, 'v_largura': 0, 'v_altura': 0, 'v_qtd': 0, 'peso_estimado': 0, 'acessorios': []}
        
    return res

dados = realizar_calculos(L, H, tipologia)

# --- INTERFACE PRINCIPAL (ABAS) ---
tab_orc, tab_corte, tab_vidro, tab_inst = st.tabs(["💰 ORÇAMENTO", "🪚 LISTA DE CORTE", "💎 VIDROS & ACESSÓRIOS", "📋 INSTALAÇÃO"])

with tab_orc:
    st.subheader(f"Cliente: {cliente}")
    area_v = (dados['v_largura'] * dados['v_altura'] * dados['v_qtd']) / 1_000_000
    custo_alu = (dados['peso_estimado'] * 1.05) * p_alu # 5% perca
    custo_vidro = area_v * p_vidro
    total = custo_alu + custo_vidro + 100 # +100 kit fixo
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Peso Total (c/ perca)", f"{dados['peso_estimado']*1.05:.2f} kg")
    c2.metric("Custo Material", f"R$ {total:.2f}")
    c3.metric("Sugestão de Venda", f"R$ {total*1.5:.2f}")

with tab_corte:
    st.subheader("Lista de Alumínio (Cortes)")
    df_corte = pd.DataFrame([
        {"Perfil": "Marcos Horizontais", "Qtd": 2, "Medida (mm)": L, "Corte": "90°"},
        {"Perfil": "Marcos Verticais", "Qtd": 2, "Medida (mm)": H, "Corte": "90°"},
        {"Perfil": "Montantes Folha", "Qtd": dados['v_qtd']*2, "Medida (mm)": dados['c_montante'], "Corte": "90°"},
        {"Perfil": "Travessas Folha", "Qtd": dados['v_qtd']*2, "Medida (mm)": dados['c_travessa'], "Corte": "90°"}
    ])
    st.table(df_corte)
    st.info(f"💡 Dica: Estime {(dados['peso_estimado']/5):.0f} barras de 6m para este projeto.")

with tab_vidro:
    col_v, col_a = st.columns(2)
    with col_v:
        st.subheader("Pedido de Vidro")
        st.info(f"{dados['v_qtd']} pçs - {vidro_tipo} {vidro_esp}mm")
        st.success(f"MEDIDA: {dados['v_largura']:.1f} x {dados['v_altura']:.1f} mm")
    with col_a:
        st.subheader("Acessórios")
        for item, qtd in dados['acessorios']:
            st.write(f"✅ {item}: **{qtd:.1f}**")

with tab_inst:
    st.subheader("Checklist de Instalação")
    st.checkbox("Prumo e Nível do vão conferidos?")
    st.checkbox("Vedação externa com silicone realizada?")
    st.checkbox("Roldanas reguladas e folhas correndo soltas?")
    st.checkbox("Fechos alinhados e travando corretamente?")
    st.button("Salvar Relatório")
