import streamlit as st
import pandas as pd
import math

# CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Serralheria Gestão Total", layout="wide")

# --- ESTADO DO SISTEMA (SIMULANDO BANCO DE DADOS) ---
if 'financeiro' not in st.session_state:
    st.session_state.financeiro = []
if 'estoque' not in st.session_state:
    st.session_state.estoque = {"Barras 6m": 15, "Roldanas": 50, "Fechos": 20}

st.title("🚀 Serralheria Pro: Gestão, Orçamento e Produção")

# --- ABAS PRINCIPAIS ---
tab_config, tab_cliente, tab_orc, tab_corte, tab_vidro, tab_ace, tab_fin, tab_est = st.tabs([
    "🛠️ CONFIG. PEÇA", "👤 CLIENTE", "💰 ORÇAMENTO", "🪚 CORTES", "💎 VIDROS", "🔩 ACESSÓRIOS", "📈 FINANCEIRO", "📦 ESTOQUE"
])

with tab_config:
    st.header("Configuração Técnica da Esquadria")
    c1, c2, c3 = st.columns(3)
    with c1:
        tipologia = st.selectbox("Tipologia (Linha Suprema)", 
                                ["Janela Correr 2 Fls", "Janela Correr 3 Fls", "Janela Correr 4 Fls", "Porta Giro 1 Fl"])
        L = st.number_input("Largura do Vão (mm)", value=1500)
        H = st.number_input("Altura do Vão (mm)", value=1200)
    with c2:
        cor_alu = st.selectbox("Cor do Alumínio", ["Branco", "Preto", "Natural", "Bronze", "Amadeirado"])
        p_alu_kg = st.number_input("Preço Alumínio (R$/kg)", value=48.0)
    with c3:
        p_vidro_m2 = st.number_input("Preço Vidro Base (R$/m2)", value=160.0)
        mao_obra = st.number_input("Mão de Obra Fixa (R$)", value=300.0)

with tab_cliente:
    st.header("Cadastro da Obra")
    cc1, cc2 = st.columns(2)
    with cc1:
        nome_cliente = st.text_input("Nome do Cliente", "Ex: João Silva")
        contato = st.text_input("WhatsApp/Telefone")
    with cc2:
        endereco = st.text_input("Endereço da Obra")
        status_obra = st.selectbox("Status", ["Orçamento Aberto", "Aprovado", "Em Produção", "Finalizado"])

# --- LÓGICA DE ENGENHARIA ---
def calcular_esquadria(L, H, tipo):
    if "2 Fls" in tipo:
        cortes = [
            {"Ref": "SU-001/002", "D": "Trilhos", "Q": 2, "M": L, "A": "90°"},
            {"Ref": "SU-003", "D": "Marcos Lat.", "Q": 2, "M": H, "A": "90°"},
            {"Ref": "SU-039/040", "D": "Folhas Vert.", "Q": 4, "M": H-45, "A": "90°"},
            {"Ref": "SU-041", "D": "Folhas Horiz.", "Q": 4, "M": (L+12)/2, "A": "90°"}
        ]
        v_l, v_h, v_q = (L-110)/2, H-145, 2
        peso = ((L*2 + H*2 + (H-45)*4 + ((L+12)/2)*4)/1000) * 0.65
    else: # Simplificado para exemplo, pode expandir as outras
        cortes = [{"Ref": "SU-001", "D": "Perfil Geral", "Q": 4, "M": L, "A": "90°"}]
        v_l, v_h, v_q = L-100, H-100, 1
        peso = 10.0
    return cortes, v_l, v_h, v_q, peso

cortes_lista, vl, vh, vq, peso_bruto = calcular_esquadria(L, H, tipologia)

with tab_vidro:
    st.header("Especificação dos Vidros")
    v1, v2, v3 = st.columns(3)
    with v1:
        tipo_v = st.selectbox("Tipo de Vidro", ["Comum", "Temperado", "Laminado"])
        cor_v = st.selectbox("Cor do Vidro", ["Incolor", "Verde", "Fumê", "Leitoso"])
    with v2:
        if tipo_v == "Comum":
            esp_v = st.selectbox("Espessura (mm)", [4, 6, 8, 10])
        else:
            esp_v = st.selectbox("Espessura (mm)", [6, 8, 10])
    with v3:
        tratamento = st.selectbox("Acabamento Especial", ["Nenhum", "Película", "Jateado"])
        if tratamento == "Película":
            cor_pel = st.selectbox("Cor da Película", ["G5", "G20", "Espelhada", "Fosca"])

    st.success(f"**MEDIDA PARA PEDIDO:** {vq} pçs de {vl:.1f} x {vh:.1f} mm")

with tab_corte:
    st.header("Plano de Corte e Aproveitamento")
    st.table(pd.DataFrame(cortes_lista))
    
    st.subheader("📊 Aproveitamento de Barra (6000mm)")
    for c in cortes_lista:
        total_mm = c['Q*M'] if 'Q*M' in c else c['Q']*c['M']
        barras_nec = math.ceil(total_mm / 6000)
        sobra = (barras_nec * 6000) - total_mm
        st.write(f"Perfil **{c['Ref']}**: {barras_nec} barra(s). Sobra total na obra: **{sobra} mm**")

with tab_ace:
    st.header("Lista de Acessórios Completa")
    ace_list = [
        {"Item": "Roldanas", "Qtd": vq*2, "Det": "Nylon com rolamento"},
        {"Item": "Fechos Lateral", "Qtd": 1 if vq==2 else 2, "Det": "Com chave ou sem"},
        {"Item": "Guia Superior", "Qtd": vq*2, "Det": "Nylon"},
        {"Item": "Parafusos Inox", "Qtd": 20, "Det": "4.2 x 13mm"},
        {"Item": "Silicone Neutro", "Qtd": 1, "Det": "Tubo 300g"}
    ]
    st.table(pd.DataFrame(ace_list))

with tab_orc:
    st.header("Resumo Financeiro da Obra")
    area_vidro = (vl * vh * vq) / 1_000_000
    c_alu = peso_bruto * 1.05 * p_alu_kg
    c_vid = area_vidro * p_vidro_m2
    total_custo = c_alu + c_vid + 150 + mao_obra # 150 acessórios
    
    st.metric("Custo Total de Materiais", f"R$ {total_custo:.2f}")
    st.metric("Sugestão de Venda (40% Lucro)", f"R$ {total_custo * 1.4:.2f}")
    
    if st.button("Registrar como Saída no Financeiro"):
        st.session_state.financeiro.append({"Tipo": "Saída", "Desc": f"Material Obra {nome_cliente}", "Valor": total_custo})
        st.toast("Registrado!")

with tab_fin:
    st.header("Controle Financeiro (Caixa)")
    f1, f2 = st.columns(2)
    with f1:
        desc_f = st.text_input("Descrição Transação")
        val_f = st.number_input("Valor R$", value=0.0)
    with f2:
        tipo_f = st.radio("Tipo", ["Entrada", "Saída"])
        if st.button("Lançar no Caixa"):
            st.session_state.financeiro.append({"Tipo": tipo_f, "Desc": desc_f, "Valor": val_f})

    df_fin = pd.DataFrame(st.session_state.financeiro)
    if not df_fin.empty:
        st.dataframe(df_fin)
        saldo = df_fin[df_fin['Tipo'] == 'Entrada']['Valor'].sum() - df_fin[df_fin['Tipo'] == 'Saída']['Valor'].sum()
        st.subheader(f"Saldo em Caixa: R$ {saldo:.2f}")

with tab_est:
    st.header("Controle de Estoque (Almoxarifado)")
    st.write("Estoque Atual de Barras de 6m: ", st.session_state.estoque["Barras 6m"])
    nova_barra = st.number_input("Adicionar Barras compradas", value=0)
    if st.button("Atualizar Estoque"):
        st.session_state.estoque["Barras 6m"] += nova_barra
        st.success("Estoque Atualizado!")
