import streamlit as st
import pandas as pd
import math
from datetime import datetime

# CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Serralheria Gestão Total v7.0", layout="wide")

# --- BANCO DE DATA (ESTADOS) ---
if 'estoque' not in st.session_state:
    st.session_state.estoque = {"Alumínio (m)": 100.0, "Roldanas": 50, "Fechos": 20, "Escova (m)": 100.0}
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []
if 'obras_fechadas' not in st.session_state:
    st.session_state.obras_fechadas = []

st.title("⚒️ Sistema Integrado de Esquadrias - Linha Suprema")

# --- ABAS ---
tab_config, tab_pedido, tab_estoque, tab_obras, tab_fin = st.tabs([
    "🛠️ MEDIDAS E TIPOLOGIA", "🛒 ITENS DO PROJETO", "📦 ALMOXARIFADO", "📋 OBRAS FECHADAS", "📈 FINANCEIRO"
])

# --- ABA 1: MEDIDAS E TIPOLOGIA (CONSOLIDADA) ---
with tab_config:
    st.header("Configuração Completa da Peça")
    
    # Seção 1: Identificação e Ambiente
    with st.container():
        c1, c2, c3 = st.columns(3)
        cliente_nome = c1.text_input("Nome do Cliente/Obra", "Obra Residencial")
        ambiente = c2.text_input("Descrição do Ambiente (Ex: Cozinha, Suíte)", "Sala")
        status_venda = c3.selectbox("Status do Orçamento", ["Aberto", "Aprovado", "Em Produção"])

    st.divider()

    # Seção 2: Engenharia, Medidas e Instalação (Tudo que você pediu aqui)
    with st.container():
        col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
        
        with col1:
            tipologia = st.selectbox("Tipologia da Peça", [
                "Janela Correr 2 Fls", "Janela Correr 3 Fls", "Janela Correr 4 Fls", 
                "Porta Giro 1 Fl", "Porta Giro 2 Fls", "Maxim-ar"
            ])
            metodo_inst = st.radio("Método de Instalação", ["Bucha e Parafuso", "Com Contra-marco", "Alvenaria Direta"])
        
        with col2:
            L = st.number_input("Largura L (mm)", value=1500)
            H = st.number_input("Altura H (mm)", value=1200)
            qtd_pecas = st.number_input("Qtd de Peças Iguais", min_value=1, value=1)
            
        with col3:
            cor_alu = st.selectbox("Cor do Alumínio", ["Branco", "Preto", "Natural", "Bronze", "Amadeirado"])
            p_alu = st.number_input("Preço Alumínio (R$/kg)", value=48.0)
            
        with col4:
            # Opções de Vidro Detalhadas
            v_tipo = st.selectbox("Tipo de Vidro", ["Comum", "Temperado", "Laminado"])
            if v_tipo == "Comum":
                v_esp = st.selectbox("Espessura (mm)", [4, 6, 8, 10])
            else:
                v_esp = st.selectbox("Espessura (mm)", [6, 8, 10])
            
            v_cor = st.selectbox("Cor do Vidro", ["Incolor", "Verde", "Fumê", "Leitoso", "Refletivo"])
            v_extra = st.selectbox("Tratamento/Película", ["Nenhum", "Película G5", "Película G20", "Jateado", "Espelhada"])

    st.divider()

    # Botão de Ação Principal
    if st.button("➕ ADICIONAR ESTE ITEM AO PROJETO", use_container_width=True):
        # Lógica de Descontos Suprema
        vl, vh, vq = (L-110)/2, H-145, 2 # Exemplo 2 fls
        perimetro = ((L*2 + H*2) / 1000) * qtd_pecas
        peso_est = (perimetro * 1.8) # Estimativa kg/m linear
        
        novo_item = {
            "Ambiente": ambiente,
            "Tipologia": tipologia,
            "Medida": f"{L}x{H}",
            "Qtd": qtd_pecas,
            "Instalação": metodo_inst,
            "Vidro": f"{v_tipo} {v_esp}mm {v_cor} ({v_extra})",
            "Custo_Estimado": (peso_est * p_alu) + (180 * qtd_pecas), # 180 = Vidro+Acessórios/un
            "L": L, "H": H, "V_L": vl, "V_H": vh, "V_Q": vq,
            "Peso_Total": peso_est
        }
        st.session_state.carrinho.append(novo_item)
        st.success(f"Item '{ambiente}' adicionado com sucesso!")

# --- ABA 2: ITENS DO PROJETO (ONDE FECHA A OBRA) ---
with tab_pedido:
    st.header(f"Resumo da Obra: {cliente_nome}")
    if st.session_state.carrinho:
        df_car = pd.DataFrame(st.session_state.carrinho)
        st.dataframe(df_car[["Ambiente", "Tipologia", "Medida", "Qtd", "Instalação", "Vidro"]], use_container_width=True)
        
        total_obra = df_car["Custo_Estimado"].sum()
        
        c_fin1, c_fin2 = st.columns(2)
        with c_fin1:
            st.subheader(f"Total Materiais: R$ {total_obra:.2f}")
            desconto = st.number_input("Desconto Especial (R$)", value=0.0)
            forma_pag = st.selectbox("Forma de Pagamento", ["Pix", "Dinheiro", "Cartão Crédito", "Cartão Débito", "Boleto", "Parcelado"])
            if forma_pag == "Parcelado":
                parc = st.number_input("Vezes", min_value=2, max_value=12, value=2)
        
        with c_fin2:
            valor_final = total_obra - desconto
            st.metric("VALOR FINAL DO PEDIDO", f"R$ {valor_final:.2f}")
            
        if st.button("🚀 FECHAR PEDIDO, DAR BAIXA NO ESTOQUE E GERAR CHECKLIST"):
            # Lógica de Baixa no Estoque
            total_m_alu = df_car["Peso_Total"].sum() / 0.65 # converte kg p/ metros aprox.
            st.session_state.estoque["Alumínio (m)"] -= total_m_alu
            
            obra_final = {
                "Cliente": cliente_nome,
                "Data": datetime.now().strftime("%d/%m/%Y"),
                "Valor": valor_final,
                "Pagamento": forma_pag,
                "Itens": st.session_state.carrinho.copy()
            }
            st.session_state.obras_fechadas.append(obra_final)
            st.session_state.carrinho = [] # Limpa projeto atual
            st.balloons()
            st.rerun()
    else:
        st.info("Adicione itens na primeira aba para ver o resumo aqui.")

# --- ABA 3: ESTOQUE (ALMOXARIFADO) ---
with tab_estoque:
    st.header("📦 Saldo em Estoque")
    cols = st.columns(len(st.session_state.estoque))
    for i, (item, qtd) in enumerate(st.session_state.estoque.items()):
        cols[i].metric(item, f"{qtd:.1f}")
    
    st.divider()
    st.subheader("📥 Entrada de Material")
    with st.form("entrada_estoque"):
        item_ent = st.selectbox("Item", list(st.session_state.estoque.keys()))
        qtd_ent = st.number_input("Quantidade Comprada", min_value=0.0)
        if st.form_submit_button("Registrar Compra"):
            st.session_state.estoque[item_ent] += qtd_ent
            st.rerun()

# --- ABA 4: OBRAS FECHADAS (CHECKLIST COMPLETO) ---
with tab_obras:
    if st.session_state.obras_fechadas:
        for obra in st.session_state.obras_fechadas:
            with st.expander(f"📁 {obra['Data']} - Cliente: {obra['Cliente']} | R$ {obra['Valor']:.2f}"):
                st.write(f"**Pagamento:** {obra['Pagamento']}")
                st.markdown("### 📋 Checklist de Produção e Instalação")
                df_obra = pd.DataFrame(obra['Itens'])
                st.table(df_obra[["Ambiente", "Tipologia", "Medida", "Instalação", "Vidro"]])
                st.info("⚠️ Instrução: Verificar se o contra-marco foi assentado 48h antes da instalação.")
    else:
        st.write("Nenhum histórico disponível.")
