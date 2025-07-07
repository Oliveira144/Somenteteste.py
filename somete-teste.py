import streamlit as st

# Configuração de estilo CSS
def load_css():
    css = """
    <style>
    /* Estilos para os botões */
    .stButton>button {
        border-radius: 10px;
        font-weight: bold;
        padding: 10px 24px;
        width: 100%;
    }
    .btn-casa {
        background-color: #ff4b4b !important;
        color: white !important;
        border: 2px solid #cc0000 !important;
    }
    .btn-visitante {
        background-color: #1e90ff !important;
        color: white !important;
        border: 2px solid #0066cc !important;
    }
    .btn-empate {
        background-color: #ffdd00 !important;
        color: #333 !important;
        border: 2px solid #ccaa00 !important;
    }
    .btn-baralho {
        background-color: #4CAF50 !important;
        color: white !important;
        border: 2px solid #2E7D32 !important;
    }
    
    /* Estilos para o grid de histórico */
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
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 50px;
    }
    .grid-item-recente {
        box-shadow: 0 0 0 3px #ff4b4b;
    }
    
    /* Estilos para os cards de análise */
    .metric-card {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Estilos para alertas */
    .alerta-box {
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        background-color: #fff8e1;
        border-left: 5px solid #ffc107;
    }
    
    /* Estilos para sugestão */
    .sugestao-box {
        background-color: #e8f5e9;
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
        border-left: 5px solid #4CAF50;
    }
    
    /* Melhorias gerais */
    .header-title {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .linha-label {
        font-weight: bold;
        margin-bottom: 5px;
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

# CORREÇÃO APLICADA AQUI - SINTAXE CORRIGIDA
def eco_parcial_por_linha(h):
    h = get_valores(h)
    if len(h) < 18:
        return "Poucos dados"
    ult = h[-9:]
    penult = h[-18:-9]
    semelhantes = sum(1 for a, b in zip(penult, ult) 
                   if a == b or (a in ['C','V'] and b in ['C','V']) else 0
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
    if eco == "Detectado" or (isinstance(parcial, str) and parcial.startswith(("6", "7", "8", "9"))):
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
with col1:
    st.button("🟥 Casa (C)", key="btn_casa", on_click=lambda: adicionar_resultado("C"), 
              use_container_width=True, help="Registrar vitória da Casa")
with col2:
    st.button("🟦 Visitante (V)", key="btn_visitante", on_click=lambda: adicionar_resultado("V"), 
              use_container_width=True, help="Registrar vitória do Visitante")
with col3:
    st.button("🟨 Empate (E)", key="btn_empate", on_click=lambda: adicionar_resultado("E"), 
              use_container_width=True, help="Registrar empate")
with col4:
    st.button("🔄 Novo Baralho", key="btn_baralho", on_click=lambda: adicionar_resultado("🔽"), 
              use_container_width=True, help="Iniciar novo baralho")

h = st.session_state.historico

# Sugestão de entrada
st.subheader("🎯 Sugestão de Entrada")
st.markdown(f"""
<div class="sugestao-box">
    <div style="font-size:20px; font-weight:bold;">{sugestao(h)}</div>
</div>
""", unsafe_allow_html=True)

# Histórico visual em grid 3x9 - CORREÇÃO COMPLETA
st.subheader("🧾 Histórico Visual (Zona Ativa: 3 Linhas)")
valores_para_grid = get_valores(h)[-27:]  # Últimos 27 valores válidos

# Preencher com espaços vazios se necessário
while len(valores_para_grid) < 27:
    valores_para_grid.insert(0, " ")  # Preencher no início para manter a ordem

# Dividir em 3 linhas de 9 colunas (Linha 1 = mais antiga, Linha 3 = mais recente)
linhas = [
    valores_para_grid[0:9],   # Linha 1 (mais antiga)
    valores_para_grid[9:18],   # Linha 2
    valores_para_grid[18:27]   # Linha 3 (mais recente)
]

# Exibir as 3 linhas
for i, linha in enumerate(linhas):
    linha_num = i + 1
    st.markdown(f"<div class='linha-label'>Linha {linha_num}</div>", unsafe_allow_html=True)
    st.markdown("<div class='grid-container'>", unsafe_allow_html=True)
    
    for j, valor in enumerate(linha):
        # Destacar o último item da última linha
        destaque = (i == 2 and j == 8) and valor != " "
        classe = "grid-item grid-item-recente" if destaque else "grid-item"
        st.markdown(f"<div class='{classe}'>{bolha_cor(valor)}</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# Painel de análise
st.subheader("📊 Análise dos Últimos 27 Jogadas")

# Criar cards para os totais
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    <div class="metric-card">
        <h4>🟥 Casa</h4>
        <div style="font-size:24px; text-align:center; font-weight:bold;">{}</div>
    </div>
    """.format(get_valores(h).count("C")), unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
        <h4>🟦 Visitante</h4>
        <div style="font-size:24px; text-align:center; font-weight:bold;">{}</div>
    </div>
    """.format(get_valores(h).count("V")), unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
        <h4>🟨 Empates</h4>
        <div style="font-size:24px; text-align:center; font-weight:bold;">{}</div>
    </div>
    """.format(get_valores(h).count("E")), unsafe_allow_html=True)

# Outras métricas
st.markdown("""
<div class="metric-card">
    <h4>📏 Maior Sequência</h4>
    <div style="font-size:20px; text-align:center; font-weight:bold;">{}</div>
</div>
""".format(maior_sequencia(h)), unsafe_allow_html=True)

st.markdown("""
<div class="metric-card">
    <h4>⏱️ Sequência Atual</h4>
    <div style="font-size:20px; text-align:center; font-weight:bold;">{}</div>
</div>
""".format(sequencia_final(h)), unsafe_allow_html=True)

st.markdown("""
<div class="metric-card">
    <h4>🔀 Alternância</h4>
    <div style="font-size:20px; text-align:center; font-weight:bold;">{}</div>
</div>
""".format(alternancia(h)), unsafe_allow_html=True)

# Alertas estratégicos
st.subheader("🚨 Alertas Estratégicos")
alertas = []
valores = get_valores(h)

if sequencia_final(h) >= 5 and valores and valores[-1] in ["C", "V"]:
    alertas.append("🟥 Sequência de {} - possível inversão".format(sequencia_final(h)))
if eco_visual_por_linha(h) == "Detectado":
    alertas.append("🔁 Eco visual detectado - possível repetição")
if isinstance(eco_parcial_por_linha(h), str) and eco_parcial_por_linha(h).startswith(("6", "7", "8", "9")):
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
