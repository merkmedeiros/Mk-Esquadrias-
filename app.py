import streamlit as st
import pandas as pd
import math

# CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Serralheria Pro Ultra v3.0", layout="wide")

st.title("🏭 Sistema Integrado de Gestão - Alumínio & Vidro")
st.markdown("---")

# --- BANCO DE DADOS DE ACESSÓRIOS (Dicionário Técnico) ---
def get_acessorios(tipo, qtd_folhas):
    if "Janela Correr" in tipo:
        return [
            {"Item": "Roldana de Nylon (Rolamento)", "Qtd": qtd_folhas * 2, "Un": "un"},
            {"Item": "Fecho Lateral (Janela)", "Qtd": 1 if qtd_folhas == 2 else 2, "Un": "un"},
            {"Item": "Guia de Nylon Superior", "Qtd": qtd_folhas * 2, "Un": "un"},
            {"Item": "Batedor de Borracha Lateral", "Qtd": 2, "Un": "un"},
            {"Item": "Escova de Vedação 5x5", "Qtd": "Ver aba compras", "Un": "m"},
            {"Item": "Parafuso Inox 4.2x13 (Fixação)", "Qtd": 16, "Un": "un"},
            {"Item": "Cunha de Regulagem", "Qtd": 4, "Un": "un"}
        ]
    elif "Porta Giro" in tipo:
        return [
            {"Item": "Dobradiça Suprema", "Qtd": 3, "Un": "un"},
            {"Item": "Fechadura para Giro", "Qtd": 1, "Un": "un"},
            {"Item": "Cilindro com Chave", "Qtd": 1, "Un": "un"},
            {"Item": "Puxador Tubular (Par)", "Qtd": 1, "Un": "un"},
            {"Item": "Borracha de Encosto EPDM", "Qtd": "Ver aba compras", "Un": "m"}
        ]
    return []

# --- SIDEBAR: ENTRADA DE DADOS ---
with st.sidebar:
    st.header("📐 Configurações da Peça")
    L = st.number_input("Largura do Vão (mm)", value=1500)
    H = st.number_input("Altura do Vão (mm)", value=1200)
    tipologia = st.selectbox("Tipologia", [
        "Janela Correr 2 Fls", "Janela Correr 3 Fls", "Janela Correr 4 Fls", 
        "Porta Giro 1 Fl"
    ])
    cor_perfil = st.selectbox("Cor do Alumínio", ["Branco", "Preto", "Natural", "Bronze"])
    p_alu = st.number_input("Preço kg Alumínio (R$)", value=48.0)
    p_vidro = st.number_input("Preço m2 Vidro (R$)", value=160.0)

# --- ABA DE GESTÃO E EXIBIÇÃO ---
tab_cliente, tab_orc, tab_corte, tab_vidro, tab_acessorios = st.tabs([
    "👤 CADASTRO CLIENTE", "💰 ORÇAMENTO", "🪚 CORTES & BARRAS", "💎 VIDROS", "🔩 ACESSÓRIOS"
])

with tab_cliente:
    st.subheader("Dados do Cliente e Obra")
    c1, c2 = st.columns(2)
    with c1:
        nome = st.text_input("Nome Completo", "Cliente Exemplo")
        tel = st.text_input("Telefone / WhatsApp")
        email = st.text_input("E-mail")
    with c2:
        endereco = st.text_area("Endereço da Obra")
        status = st.select_slider("Status do Orçamento", 
                                 options=["Aberto", "Em Andamento", "Finalizado"])
    st.write(f"**Resumo:** Cliente {nome} | Status: **{status}**")

# --- LÓGICA DE ENGENHARIA ---
def calcular_engenharia(L, H, tipo):
    cortes = []
    if "2 Fls" in tipo:
        cortes = [
            {"Ref": "SU-001/002", "Desc": "Trilhos", "Qtd": 2, "Corte": L, "Ang": "90°"},
            {"Ref": "SU-003", "Desc": "Marcos Lat.", "Qtd": 2, "Corte": H, "Ang": "90°"},
            {"Ref": "SU-039/040", "Desc": "Montantes", "Qtd": 4, "Corte": H-45, "Ang": "90°"},
            {"Ref": "SU-041", "Desc": "Travessas", "Qtd": 4, "Corte": (L+12)/2, "Ang": "90°"}
        ]
        v_l, v_h, v_qtd = (L-110)/2, H-145, 2
        peso = ( (L*2 + H*2 + (H-45)*4 + ((L+12)/2)*4)/1000 ) * 0.65
    elif "Porta Giro" in tipo:
        cortes = [
            {"Ref": "SU-007", "Desc": "Marco Giro", "Qtd": 2, "Corte": H, "Ang": "45°"},
            {"Ref": "SU-007", "Desc": "Marco Giro", "Qtd": 1, "Corte": L, "Ang": "45°"},
            {"Ref": "SU-023/024", "Desc": "Folha Porta", "Qtd": 4, "Corte": H-35, "Ang": "45°"}
        ]
        v_l, v_h, v_qtd = L-125, H-210, 1
        peso = ( (L*3 + H*4)/1000 ) * 0.95
    # Adicione outras aqui...
    return cortes, v_l, v_h, v_qtd, peso

cortes_lista, vl, vh, vq, peso_estimado = calcular_engenharia(L, H, tipologia)

with tab_orc:
    st.subheader("Custos de Produção")
    area_v = (vl * vh * vq) / 1_000_000
    custo_alu = peso_estimado * 1.05 * p_alu
    custo_vidro = area_v * p_vidro
    total_custo = custo_alu + custo_vidro + 180 # Estimativa acessórios
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Alumínio", f"R$ {custo_alu:.2f}")
    m2.metric("Vidro", f"R$ {custo_vidro:.2f}")
    m3.metric("TOTAL CUSTO", f"R$ {total_custo:.2f}")
    
    st.markdown(f"### **Preço Sugerido p/ Cliente: R$ {total_custo * 1.6:.2f}**")

with tab_corte:
    st.subheader("Plano de Corte e Necessidade de Barras")
    df_cortes = pd.DataFrame(cortes_lista)
    st.table(df_cortes)
    
    st.info("📊 **Resumo de Compra (Barras de 6m):**")
    for c in cortes_lista:
        total_mm = c['Qtd'] * c['Corte']
        barras = math.ceil(total_mm / 6000)
        st.write(f"- Perfil **{c['Ref']}** ({c['Desc']}): Necessário **{barras} barra(s)** de 6m.")

with tab_vidro:
    st.subheader("Medida para Têmpera")
    st.success(f"Quantidade: {vq} peça(s)")
    st.write(f"**LARGURA:** {vl:.1f} mm")
    st.write(f"**ALTURA:** {vh:.1f} mm")
    st.write(f"Área Total: {area_v:.2f} m2")

with tab_acessorios:
    st.subheader("Lista Geral de Acessórios (Sem exceção)")
    lista_ace = get_acessorios(tipologia, vq)
    df_ace = pd.DataFrame(lista_ace)
    st.table(df_ace)
    
    st.warning("⚠️ Lembre-se de conferir a cor dos componentes (Preto/Branco) de acordo com o perfil.")

