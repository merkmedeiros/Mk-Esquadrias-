import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA (PADRÃO ORIGINAL) ---
st.set_page_config(page_title="Esquadplan", layout="wide")

# --- INICIALIZAÇÃO DO ESTADO ---
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []
if 'obras_fechadas' not in st.session_state:
    st.session_state.obras_fechadas = []
if 'estoque' not in st.session_state:
    st.session_state.estoque = {
        "Perfil Aluminio (kg)": {"qtd": 0.0, "custo_unit": 0.0},
        "Vidro Temperado (m2)": {"qtd": 0.0, "custo_unit": 0.0},
        "Componentes/Kits (un)": {"qtd": 0, "custo_unit": 0.0}
    }

# --- CABEÇALHO ---
col_logo, col_info = st.columns([1, 4])
with col_logo:
    st.subheader("📏 ESQUADPLAN")
with col_info:
    st.write("**Dados da Empresa:** Sua Serralheria & Vidraçaria | Contato: (00) 00000-0000")
    st.write("Endereço: Sua Rua, 123 - Cidade/UF")

st.divider()

# --- ABAS ---
tabs = st.tabs(["👤 CLIENTE", "🛠️ TIPOLOGIA", "📑 ORÇAMENTO", "📦 ESTOQUE", "📋 HISTÓRICO"])
tab_cli, tab_tip, tab_orc, tab_est, tab_his = tabs

# --- ABA 1: DADOS DO CLIENTE ---
with tab_cli:
    st.header("Ficha do Cliente")
    c1, c2, c3 = st.columns([2, 1, 1])
    st.session_state.nome_cli = c1.text_input("Nome/Razão Social")
    st.session_state.tel_cli = c2.text_input("Telefone/WhatsApp")
    st.session_state.email_cli = c3.text_input("E-mail")

    st.markdown("### Endereço de Cadastro")
    e1, e2, e3, e4 = st.columns([1, 2, 1, 1])
    st.session_state.cep = e1.text_input("CEP")
    st.session_state.rua = e2.text_input("Rua/Avenida")
    st.session_state.num = e3.text_input("Nº")
    st.session_state.comp = e4.text_input("Complemento")

    e5, e6, e7 = st.columns([1, 1, 1])
    st.session_state.bairro = e5.text_input("Bairro")
    st.session_state.cidade = e6.text_input("Cidade")
    st.session_state.entrega = e7.text_input("Endereço de Entrega (Diferente)")
    
    st.session_state.obs = st.text_area("Observações Gerais")

# --- ABA 2: TIPOLOGIA E MEDIDAS ---
with tab_tip:
    st.header("Configuração da Peça")
    
    r1, r2, r3 = st.columns([2, 1, 1])
    amb = r1.text_input("Ambiente", "Cozinha")
    inst = r2.selectbox("Instalação", ["Bucha/Parafuso", "Contra-marco", "Kit Box", "Colado"])
    qtd = r3.number_input("Quantidade", min_value=1, value=1)

    st.divider()
    
    col_a, col_b = st.columns([1, 1])
    with col_a:
        cat = st.radio("Categoria", ["Linha Suprema", "Temperado/Box", "Espelhos"])
        if cat == "Linha Suprema":
            tipo = st.selectbox("Modelo", ["Janela 2 Fls", "Janela 4 Fls", "Porta Giro", "Maxim-ar"])
            
        elif cat == "Temperado/Box":
            tipo = st.selectbox("Modelo", ["Box Padrão", "Box de Canto", "Fixo + Correr"])
            
        else:
            tipo = st.selectbox("Modelo", ["Espelho 4mm", "Espelho Bisotê"])
            

    with col_b:
        larg = st.number_input("Largura (mm)", value=1000)
        alt = st.number_input("Altura (mm)", value=1000)
        cor = st.selectbox("Cor", ["Preto", "Branco", "Natural", "Bronze"])

    if st.button("➕ ADICIONAR AO ORÇAMENTO", use_container_width=True):
        cm = f"{larg+44}x{alt+44}" if inst == "Contra-marco" else "N/A"
        item = {
            "Ambiente": amb, "Item": f"{cat} - {tipo}", "Medida": f"{larg}x{alt}",
            "Qtd": qtd, "Instalação": inst, "Contra-marco": cm, "Cor": cor
        }
        st.session_state.carrinho.append(item)
        st.toast(f"Item {amb} adicionado!")

# --- ABA 3: ORÇAMENTO (CARRINHO) ---
with tab_orc:
    st.header(f"Orçamento: {st.session_state.get('nome_cli', 'Novo Cliente')}")
    
    if st.session_state.carrinho:
        df_orc = pd.DataFrame(st.session_state.carrinho)
        st.table(df_orc)
        
        st.info(f"**Obs:** {st.session_state.get('obs', 'Nenhuma')}")
        
        c_b1, c_b2 = st.columns(2)
        if c_b1.button("🗑️ LIMPAR TUDO"):
            st.session_state.carrinho = []
            st.rerun()
        if c_b2.button("💾 SALVAR PEDIDO"):
            obra = {
                "Cliente": st.session_state.nome_cli, "Data": datetime.now().strftime("%d/%m/%Y"),
                "Itens": st.session_state.carrinho.copy()
            }
            st.session_state.obras_fechadas.append(obra)
            st.session_state.carrinho = []
            st.success("Pedido registrado!")
            st.rerun()
    else:
        st.warning("Carrinho vazio.")

# --- ABA 4: ESTOQUE ---
with tab_est:
    st.header("Estoque e Custos")
    df_est = pd.DataFrame.from_dict(st.session_state.estoque, orient='index')
    st.table(df_est)

    with st.expander("📥 Registrar Compra"):
        item_c = st.selectbox("Material", list(st.session_state.estoque.keys()))
        qtd_c = st.number_input("Quantidade", min_value=0.0)
        preco_c = st.number_input("Preço de Custo Total (R$)", min_value=0.0)
        if st.button("Salvar Entrada"):
            unit = preco_c / qtd_c if qtd_c > 0 else 0
            st.session_state.estoque[item_c]['qtd'] += qtd_c
            st.session_state.estoque[item_c]['custo_unit'] = unit
            st.rerun()

# --- ABA 5: HISTÓRICO ---
with tab_his:
    st.header("Histórico de Obras")
    for ob in st.session_state.obras_fechadas:
        with st.expander(f"Cliente: {ob['Cliente']} - {ob['Data']}"):
            st.table(pd.DataFrame(ob['Itens']))
