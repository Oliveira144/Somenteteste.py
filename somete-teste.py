import streamlit as st
import base64

# Configuração de estilo CSS
def load_css():
    css = """
    <style>
    .btn-casa {
        background-color: #ff4b4b !important;
        color: white !important;
        border: 2px solid #cc0000 !important;
        border-radius: 10px !important;
        padding: 10px 24px !important;
        font-weight: bold !important;
    }
    .btn-visitante {
        background-color: #1e90ff !important;
        color: white !important;
        border: 2px solid #0066cc !important;
        border-radius: 10px !important;
        padding: 10px 24px !important;
        font-weight: bold !important;
    }
    .btn-empate {
        background-color: #ffdd00 !important;
        color: #333 !important;
        border: 2px solid #ccaa00 !important;
        border-radius: 10px !important;
        padding: 10px 24px !important;
        font-weight: bold !important;
    }
    .btn-baralho {
        background-color: #4CAF50 !important;
        color: white !important;
        border: 2px solid #2E7D32 !important;
        border-radius: 10px !important;
        padding: 10px 24px !important;
        font-weight: bold !important;
    }
    .sugestao-box {
        background-color: #e8f5e9;
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
        border-left: 5px solid #4CAF50;
    }
    .grid-container {
        display: grid;
        grid-template-columns: repeat(9, 1fr);
        gap: 5px;
        margin-bottom: 10px;
    }
    .grid-item {
        font-size: 24px;
        text-align: center;
        padding: 10px;
        border-radius: 8px;
        background-color: #f0f2f6;
    }
    .grid-item-recente {
        box-shadow: 0 0 0 3px #ff4b4b;
    }
    .metric-card {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .alerta-box {
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        background-color: #fff8e1;
        border-left: 5px solid #ffc107;
    }
    .header-title {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Carregar CSS
load_css()

# Histórico com limite automático de 100 entradas
if "historico" not in st.session_state:
    st.session_state.historico = []

def adicionar_resultado(valor):
    if len(st.session_state.historico) >= 100:
        st.session_state.historico.pop(0)
    st.session_state.historico.append(valor)

# 🔍 Funções analíticas
def get_valores(h):
    return [r for r in h if r in ["C", "V", "E"]][-27:]

def maior_sequencia(h):
    h = get_valores(h)
    if not h:
        return 0
    max_seq = atual = 1
    for i in range(1, len(h)):
        if h[i] == h[i-1]:
            atual += 1
            max_seq = max(max_seq, atual)
        else:
            atual = 1
    return max_seq

def sequencia_final(h):
    h = get_valores(h)
    if not h:
        return 0
    atual = h[-1]
    count = 1
    for i in range(len(h)-2, -1, -1):
        if h[i] == atual:
            count += 1
        else:
            break
    return count

def alternancia(h):
    h = get_valores(h)
    if len(h) < 2:
        return 0
    return sum(1 for i in range(1, len(h)) if h[i] != h[i-1])

def eco_visual_por_linha(h):
    h = get_valores(h)
    if len(h) < 18:
        return "Poucos dados"
    ult = h[-9:]
    penult = h[-18:-9]
    return "Detectado" if ult == penult else "Não houve"

def eco_parcial_por_linha(h):
    h = get_valores(h)
    if len(h) < 18:
        return "Poucos dados"
    ult = h[-9:]
    penult = h[-18:-9]
    # CORREÇÃO APLICADA AQUI
    semelhantes = sum(1 for a, b in zip(penult, ult) 
                   if a == b or (a in ['C','V'] and b in ['C','V']))
    return f"{semelhantes}/9 semelhantes"

def dist_empates(h):
    h = get_valores(h)
    empates = [i for i, r in enumerate(h) if r == 'E']
    return empates[-1] - empates[-2] if len(empates) >= 2 else "N/A"

def blocos_espelhados(h):
    h = get_valores(h)
    cont = 0
    for i in range(len(h)-5):
        if h[i:i+3] == h[i+3:i+6][::-1]:
            cont += 1
    return cont

def alternancia_por_linha(h):
    h = get_valores(h)
    linhas = [h[i:i+9] for i in range(0, len(h), 9) if len(h[i:i+9]) >= 2]
    return [sum(1 for j in range(1, len(linha)) if linha[j] != linha[j-1]) for linha in linhas]

def tendencia_final(h):
    h = get_valores(h)
    if not h:
        return "Sem dados"
    ult = h[-9:] if len(h) >= 9 else h
    return f"{ult.count('C')}C / {ult.count('V')}V / {ult.count('E')}E"

def bolha_cor(r):
    return {
        "C": "🟥",
        "V": "🟦",
        "E": "🟨",
        "🔽": "⬇️"
    }.get(r, "⬜")

def sugestao(h):
    valores = get_valores(h)
    if not valores:
        return "Insira resultados para gerar previsão."
    ult = valores[-1] if valores else ""
    seq = sequencia_final(h)
    eco = eco_visual_por_linha(h)
    parcial = eco_parcial_por_linha(h)
    contagens = {
        "C": valores.count("C"),
        "V": valores.count("V"),
        "E": valores.count("E")
    }

    if seq >= 5 and ult in ["C", "V"]:
        cor_inversa = "V" if ult == "C" else "C"
        return f"🔁 Sequência atual de {bolha_cor(ult)} — possível reversão para {bolha_cor(cor_inversa)}"
    if ult == "E":
        return "🟨 Empate recente — instável, possível 🟥 ou 🟦"
    if eco == "Detectado" or parcial.startswith(("6", "7", "8", "9")):
        return f"🔄 Reescrita visual — repetir padrão com {bolha_cor(ult)}"
    maior = max(contagens, key=contagens.get)
    return f"📊 Tendência favorece entrada em {bolha_cor(maior)} ({maior})"

# Interface
st.set_page_config(page_title="📊 Football Studio - Estratégia", layout="wide")
st.title("📊 Football Studio - Estratégia")

# Header com botão de limpar
col_title, col_clear = st.columns([4, 1])
with col_title:
    st.header("Análise em Tempo Real")
with col_clear:
    if st.button("🧹 Limpar Histórico", use_container_width=True):
        st.session_state.historico = []
        st.rerun()

# Botões de ação
col1, col2, col3, col4 = st.columns(4)
col1.button("🟥 Casa (C)", key="btn_casa", on_click=lambda: adicionar_resultado("C"), 
           use_container_width=True, help="Registrar vitória da Casa")
col2.button("🟦 Visitante (V)", key="btn_visitante", on_click=lambda: adicionar_resultado("V"), 
           use_container_width=True, help="Registrar vitória do Visitante")
col3.button("🟨 Empate (E)", key="btn_empate", on_click=lambda: adicionar_resultado("E"), 
           use_container_width=True, help="Registrar empate")
col4.button("🔄 Novo Baralho", key="btn_baralho", on_click=lambda: adicionar_resultado("🔽"), 
           use_container_width=True, help="Iniciar novo baralho")

h = st.session_state.historico

# Sugestão de entrada
st.subheader("🎯 Sugestão de Entrada")
with st.container():
    st.markdown(f"""
    <div class="sugestao-box">
        <div style="font-size:20px; font-weight:bold;">{sugestao(h)}</div>
    </div>
    """, unsafe_allow_html=True)

# Histórico visual em grid 3x9
st.subheader("🧾 Histórico Visual (Últimas 27 Jogadas)")
valores_para_grid = get_valores(h)[-27:]  # Últimos 27 valores válidos

# Preencher com espaços vazios se necessário
while len(valores_para_grid) < 27:
    valores_para_grid.insert(0, " ")

# Dividir em 3 linhas de 9 colunas
linhas = [valores_para_grid[i:i+9] for i in range(0, 27, 9)]

# Mostrar do mais recente para o mais antigo
for idx, linha in enumerate(reversed(linhas)):
    st.markdown(f"<div class='grid-container'>", unsafe_allow_html=True)
    for j, valor in enumerate(reversed(linha)):
        # Destacar o último item
        classe_extra = "grid-item-recente" if (idx == 0 and j == 0) and valor != " " else ""
        st.markdown(f"<div class='grid-item {classe_extra}'>{bolha_cor(valor) if valor != ' ' else '⬜'}</div>", 
                    unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Painel de análise
st.subheader("📊 Análise Estratégica")
col_analise1, col_analise2 = st.columns(2)

with col_analise1:
    st.markdown("""
    <div class="metric-card">
        <h4>📈 Estatísticas Gerais</h4>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
            <div>🟥 Casa:</div>
            <div><b>{}</b></div>
            <div>🟦 Visitante:</div>
            <div><b>{}</b></div>
            <div>🟨 Empates:</div>
            <div><b>{}</b></div>
            <div>🔀 Alternância:</div>
            <div><b>{}</b></div>
        </div>
    </div>
    """.format(
        get_valores(h).count("C"),
        get_valores(h).count("V"),
        get_valores(h).count("E"),
        alternancia(h)
    ), unsafe_allow_html=True)
    
    st.markdown("""
    <div class="metric-card">
        <h4>🔄 Padrões de Repetição</h4>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
            <div>🔍 Eco Visual:</div>
            <div><b>{}</b></div>
            <div>🔎 Eco Parcial:</div>
            <div><b>{}</b></div>
            <div>🧩 Blocos Espelhados:</div>
            <div><b>{}</b></div>
        </div>
    </div>
    """.format(
        eco_visual_por_linha(h),
        eco_parcial_por_linha(h),
        blocos_espelhados(h)
    ), unsafe_allow_html=True)

with col_analise2:
    st.markdown("""
    <div class="metric-card">
        <h4>📉 Sequências Atuais</h4>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
            <div>📏 Maior Sequência:</div>
            <div><b>{}</b></div>
            <div>⏱️ Sequência Atual:</div>
            <div><b>{}</b></div>
            <div>📅 Dist. Empates:</div>
            <div><b>{}</b></div>
            <div>📊 Última Linha:</div>
            <div><b>{}</b></div>
        </div>
    </div>
    """.format(
        maior_sequencia(h),
        sequencia_final(h),
        dist_empates(h),
        tendencia_final(h)
    ), unsafe_allow_html=True)
    
    st.markdown("""
    <div class="metric-card">
        <h4>📋 Alternância por Linha</h4>
        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px;">
    """, unsafe_allow_html=True)
    
    alt_por_linha = alternancia_por_linha(h)
    if alt_por_linha:
        for i, val in enumerate(alt_por_linha[-3:]):
            st.markdown(f"<div>Linha {len(alt_por_linha)-i}:</div><div><b>{val} alter.</b></div>", unsafe_allow_html=True)
    else:
        st.markdown("<div>Dados insuficientes</div>", unsafe_allow_html=True)
    
    st.markdown("</div></div>", unsafe_allow_html=True)

# Alertas estratégicos
st.subheader("🚨 Alertas Estratégicos")
alertas = []
valores = get_valores(h)

if sequencia_final(h) >= 5 and valores and valores[-1] in ["C", "V"]:
    alertas.append("🟥 Sequência de {} - possível inversão".format(sequencia_final(h)))
if eco_visual_por_linha(h) == "Detectado":
    alertas.append("🔁 Eco visual detectado - possível repetição")
if eco_parcial_por_linha(h).startswith(("6", "7", "8", "9")):
    alertas.append("🧠 Eco parcial - padrão reescrito")
if dist_empates(h) == 1:
    alertas.append("🟨 Empates consecutivos - instabilidade")
if blocos_espelhados(h) >= 1:
    alertas.append("🧩 Bloco espelhado - reflexo estratégico")

if not alertas:
    st.info("✅ Nenhum padrão crítico identificado. Jogo dentro da normalidade estatística.")
else:
    for alerta in alertas:
        st.markdown(f'<div class="alerta-box">{alerta}</div>', unsafe_allow_html=True)
