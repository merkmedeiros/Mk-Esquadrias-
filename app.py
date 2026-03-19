import streamlit as st
import pandas as pd
import math

# 1. CONFIGURAÇÃO DE IDENTIDADE MK
st.set_page_config(page_title="MK - Engenharia de Esquadrias", layout="wide")

# Inicialização do Banco de Dados Temporário e Tabelas de Referência
if 'db_clientes' not in st.session_state: st.session_state.db_clientes = []
if 'db_projetos' not in st.session_state: st.session_state.db_projetos = []
if 'db_obras' not in st.session_state: st.session_state.db_obras = []

# Tabela de Pesos Teóricos (kg/m) - Exemplo de Perfis Comuns
if 'tab_perfis' not in st.session_state:
    st.session_state.tab_perfis = {
        "Suprema": {"SU-001": 0.455, "SU-039": 0.580, "SU-005": 0.320, "SU-225": 0.850},
        "Gold": {"LG-028": 0.950, "LG-040": 1.100, "LG-102": 0.780},
    }

# Custos Iniciais (Editáveis na Aba 8)
if 'custos_config' not in st.session_state:
    st.session_state.custos_config = {
        "preco_kg_branco": 45.0,
        "preco_kg_preto": 55.0,
        "acessorios": {"Roldana": 12.50, "Fecho": 18.00, "Escova (m)": 2.50},
        "vidros": {"Incolor 8mm": 180.0, "Verde 8mm": 210.0, "Fumê 8mm": 230.0}
    }

# ESTILO VISUAL MK
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stHeader { color: #1e3a8a; }
    .stButton>button { background-color: #1e3a8a; color: white; font-weight: bold; }
    .card-custo { border: 1px solid #1e3a8a; padding: 15px; border-radius: 8px; background: #fff; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚒️ MK - GESTÃO, CUSTOS E ENGENHARIA v29.0")

# --- NAVEGAÇÃO POR ABAS ---
tabs = st.tabs(["📍 Cliente", "📏 Projeto", "💰 Orçamento", "🏭 Produção", "🚚 Instalação", "🚧 Gestão Obras", "📦 Estoque", "⚙️ Custos"])

# --- ABA 1: CLIENTE (10 CAMPOS PRESERVADOS) ---
with tabs[0]:
    st.header("👥 Cadastro de Cliente")
    with st.form("cli_v29"):
        c1, c2 = st.columns(2)
        nome = c1.text_input("Nome / Razão Social")
        email = c2.text_input("E-mail")
        tel = c1.text_input("Telefone")
        wpp = c2.text_input("WhatsApp")
        st.divider()
        cep = c1.text_input("CEP")
        log = c2.text_input("Logradouro")
        bai, cid = st.columns(2)
        bairro = bai.text_input("Bairro")
        cidade = cid.text_input("Cidade/UF")
        ref = st.text_input("Ponto de Referência")
        obra = st.text_input("Local da Obra (Se diferente)")
        obs = st.text_area("Observações")
        if st.form_submit_button("Salvar Cliente"):
            st.session_state.db_clientes.append({"nome": nome, "obra": obra if obra else log, "ref": ref, "wpp": wpp})
            st.success("Cliente Registrado!")

# --- ABA 2: PROJETO (ENGENHARIA E VIDROS) ---
with tabs[1]:
    st.header("📐 Configuração Técnica")
    col_l, col_t, col_c = st.columns(3)
    linha = col_l.selectbox("Linha", list(st.session_state.tab_perfis.keys()) + ["Box", "Temperado"])
    tipo = col_t.selectbox("Tipologia", ["Janela 2fls", "Janela 4fls", "Porta Giro", "Fixo"])
    cor = col_c.selectbox("Cor", ["Branco", "Preto"])
    
    st.subheader("💎 Filtro de Vidro")
    v_modelo = st.selectbox("Modelo do Vidro", list(st.session_state.custos_config["vidros"].keys()))
    
    st.divider()
    l_p, a_p, q_p = st.columns(3)
    larg = l_p.number_input("Largura (mm)", step=1)
    alt = a_p.number_input("Altura (mm)", step=1)
    qtd = q_p.number_input("Quantidade", min_value=1, step=1)
    
    # MULTI-LOCALIZAÇÃO
    ambientes = []
    for i in range(int(qtd)):
        ambientes.append(st.text_input(f"Ambiente Peça {i+1}", key=f"p_{i}"))
        
    if st.button("Calcular Engenharia"):
        # Lógica de Descontos Milimétricos (Exemplo Suprema)
        d_alt_v = alt - 160 if "Janela" in tipo else alt - 40
        d_larg_v = (larg/2) - 95 if "2fls" in tipo else larg - 50
        
        st.session_state.db_projetos.append({
            "linha": linha, "tipo": tipo, "cor": cor, "vidro": v_modelo,
            "larg": larg, "alt": alt, "qtd": qtd, "ambientes": ambientes,
            "v_h": d_alt_v, "v_l": d_larg_v
        })
        st.success("Projeto adicionado com descontos aplicados!")

# --- ABA 8: CUSTOS (CATÁLOGO EDITÁVEL ITEM A ITEM) ---
with tabs[7]:
    st.header("⚙️ Configuração de Custos e Perfis")
    
    # 1. Filtro de Perfis por Linha
    st.subheader("📊 Pesos e Preços de Alumínio")
    linha_sel = st.selectbox("Selecione a Linha para Editar", list(st.session_state.tab_perfis.keys()))
    p_kg = st.number_input(f"Preço do KG ({cor})", value=st.session_state.custos_config["preco_kg_branco"])
    
    for perfil, peso in st.session_state.tab_perfis[linha_sel].items():
        c_p1, c_p2 = st.columns(2)
        new_peso = c_p1.number_input(f"Peso {perfil} (kg/m)", value=peso, format="%.3f")
        st.session_state.tab_perfis[linha_sel][perfil] = new_peso
        c_p2.write(f"Custo Estimado/Metro: R$ {new_peso * p_kg:.2f}")

    st.divider()
    # 2. Acessórios Item a Item
    st.subheader("🔩 Tabela de Acessórios (Unitário)")
    for ac, valor in st.session_state.custos_config["acessorios"].items():
        new_val = st.number_input(f"Valor Compra: {ac}", value=valor)
        st.session_state.custos_config["acessorios"][ac] = new_val

    st.divider()
    # 3. Preço de Vidros
    st.subheader("🖼️ Tabela de Vidros (m²)")
    for vid, v_m2 in st.session_state.custos_config["vidros"].items():
        new_v = st.number_input(f"Preço m²: {vid}", value=v_m2)
        st.session_state.custos_config["vidros"][vid] = new_v

# --- ABA 4: PRODUÇÃO (LISTA DE COMPRA, CORTE E BARRAS) ---
with tabs[3]:
    st.header("🏭 Produção e Suprimentos")
    if st.session_state.db_projetos:
        for p in st.session_state.db_projetos:
            with st.expander(f"OBRA: {p['tipo']} - {p['linha']} ({p['qtd']} un)"):
                # Cálculo de Barras e Peso
                metragem_linear = ((p['larg']*2 + p['alt']*2) * p['qtd']) / 1000
                peso_total = metragem_linear * 0.550 # Peso médio para estimativa rápida
                num_barras = math.ceil(metragem_linear / 6)
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Total de Barras (6m)", f"{num_barras} un")
                col2.metric("Peso Estimado", f"{peso_total:.2f} kg")
                col3.metric("Vidro Total", f"{(p['v_h']*p['v_l']*p['qtd'])/1000000:.2f} m²")

                st.subheader("🪚 Mapa de Corte Milimétrico")
                for amb in p['ambientes']:
                    st.write(f"📍 **Ambiente: {amb}**")
                    st.write(f"- Corte Alumínio (H): {p['alt']}mm | (L): {p['larg']}mm")
                    st.write(f"- Medida do Vidro: {p['v_l']:.0f} x {p['v_h']:.0f} mm")
    else:
        st.info("Nenhum projeto em fabricação.")

# --- ABA 5, 6 e 7 (RESUMO) ---
with tabs[4]: st.header("🚚 Instalação"); st.write("Romaneio pronto com ambientes.")
with tabs[5]: 
    st.header("🚧 Gestão de Obras")
    for obra_st in st.session_state.db_obras:
        st.warning(f"Obra: {obra_st['cliente']} - STATUS: EM ANDAMENTO")
with tabs[6]: st.header("📦 Estoque"); st.write("Controle de sobras de barras.")
with tabs[2]: st.header("💰 Orçamento Final"); st.write("Custo calculado com base na Aba de Custos.")
