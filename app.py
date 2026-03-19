import streamlit as st
import pandas as pd
import math

# CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Serralheria Gestão Pro v4.0", layout="wide")

# --- INICIALIZAÇÃO DO BANCO DE DADOS TEMPORÁRIO ---
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []
if 'obras_fechadas' not in st.session_state:
    st.session_state.obras_fechadas = []
if 'financeiro' not in st.session_state:
    st.session_state.financeiro = []

st.title("⚒️ Serralheria Pro: Gestão de Pedidos e Obras")

# --- ABAS ---
tabs = st.tabs([
    "🛠️ CONFIG. PEÇA", "🛒 ITENS DO PEDIDO", "📦 OBRAS FECHADAS", 
    "🪚 CORTES GERAIS", "💎 VIDROS", "🔩 ACESSÓRIOS", "📈 FINANCEIRO"
])

tab_config, tab_pedido, tab_fechadas, tab_corte, tab_vidro, tab_ace, tab_fin = tabs

# --- ABA 1: CONFIGURAÇÃO (AGORA COM BOTÃO ADICIONAR) ---
with tab_config:
    st.header("Configurar Nova Peça")
    
    with st.expander("👤 Dados do Cliente", expanded=True):
        c_nome = st.text_input("Nome do Cliente", "Obra João")
        c_end = st.text_input("Endereço")

    col1, col2, col3 = st.columns(3)
    with col1:
        tipologia = st.selectbox("Tipologia", ["Janela Correr 2 Fls", "Janela Correr 4 Fls", "Porta Giro 1 Fl"])
        L = st.number_input("Largura (mm)", value=1500)
        H = st.number_input("Altura (mm)", value=1200)
    with col2:
        qtd_pecas = st.number_input("Quantidade de peças iguais", min_value=1, value=1)
        cor_alu = st.selectbox("Cor Alumínio", ["Branco", "Preto", "Natural", "Bronze"])
        p_alu = st.number_input("Preço Alumínio (R$/kg)", value=48.0)
    with col3:
        tipo_v = st.selectbox("Tipo Vidro", ["Temperado 6mm", "Temperado 8mm", "Comum 6mm", "Laminado 8mm"])
        cor_v = st.selectbox("Cor Vidro", ["Incolor", "Verde", "Fumê"])
        p_vidro = st.number_input("Preço Vidro (R$/m2)", value=160.0)

    # Lógica de Cálculo Interna para o Carrinho
    def calcular_unitario(L, H, tipo):
        if "2 Fls" in tipo:
            v_l, v_h = (L-110)/2, H-145
            peso = ((L*2 + H*2 + (H-45)*4 + ((L+12)/2)*4)/1000) * 0.65
        else: # Porta Giro
            v_l, v_h = L-125, H-210
            peso = ((L*2 + H*4)/1000) * 0.95
        return v_l, v_h, peso

    if st.button("➕ ADICIONAR ITEM AO PROJETO"):
        vl, vh, peso_u = calcular_unitario(L, H, tipologia)
        area_v = (vl * vh) / 1_000_000
        custo_item = (peso_u * p_alu) + (area_v * p_vidro) + 100 # +100 kit
        
        novo_item = {
            "Descrição": f"{tipologia} {cor_alu}",
            "Medida": f"{L}x{H}",
            "Qtd": qtd_pecas,
            "Peso Total": peso_u * qtd_pecas,
            "Vidro": f"{tipo_v} {cor_v} ({vl:.0f}x{vh:.0f})",
            "Custo Total": custo_item * qtd_pecas,
            "L": L, "H": H, "Tipo": tipologia, "V_L": vl, "V_H": vh
        }
        st.session_state.carrinho.append(novo_item)
        st.success("Item adicionado com sucesso!")

# --- ABA 2: ITENS DO PEDIDO (VISUALIZAR E FECHAR) ---
with tab_pedido:
    st.header(f"Itens Selecionados para: {c_nome}")
    if st.session_state.carrinho:
        df_car = pd.DataFrame(st.session_state.carrinho)
        st.table(df_car[["Descrição", "Medida", "Qtd", "Vidro", "Custo Total"]])
        
        total_pedido = df_car["Custo Total"].sum()
        st.subheader(f"VALOR TOTAL DO PEDIDO: R$ {total_pedido:.2f}")
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            if st.button("💾 FECHAR E SALVAR OBRA"):
                obra_finalizada = {
                    "Cliente": c_nome,
                    "Total": total_pedido,
                    "Itens": st.session_state.carrinho.copy()
                }
                st.session_state.obras_fechadas.append(obra_finalizada)
                st.session_state.carrinho = [] # Limpa carrinho
                st.rerun()
        with col_f2:
            st.button("📄 GERAR PDF (Simular)")
    else:
        st.info("Nenhum item adicionado ainda.")

# --- ABA 3: OBRAS FECHADAS ---
with tab_fechadas:
    st.header("Histórico de Obras Fechadas")
    if st.session_state.obras_fechadas:
        for i, obra in enumerate(st.session_state.obras_fechadas):
            with st.expander(f"Obra: {obra['Cliente']} - Total: R$ {obra['Total']:.2f}"):
                st.write("Itens desta obra:")
                st.table(pd.DataFrame(obra['Itens'])[["Descrição", "Medida", "Qtd"]])
    else:
        st.write("Nenhuma obra fechada no sistema.")

# --- ABA 4: CORTES GERAIS (SOMA TUDO DO CARRINHO) ---
with tab_corte:
    if st.session_state.carrinho:
        st.header("Lista de Corte Consolidada")
        for item in st.session_state.carrinho:
            st.subheader(f"Item: {item['Descrição']} ({item['Qtd']} pçs)")
            # Aqui entraria a tabela de corte multiplicada pela Qtd
            st.write(f"- Cortar {item['Qtd'] * 2} Trilhos de {item['L']} mm")
            st.write(f"- Cortar {item['Qtd'] * 2} Marcos Laterais de {item['H']} mm")
    else:
        st.write("Adicione itens para ver o plano de corte.")

# --- ABA 7: FINANCEIRO ---
with tab_fin:
    st.header("Resumo Financeiro")
    total_receber = sum([o['Total'] for o in st.session_state.obras_fechadas])
    st.metric("Total em Obras Fechadas", f"R$ {total_receber:.2f}")
