import streamlit as st

# Configuração de estilo CSS
def load_css():
    css = """
    <style>
    /* Estilos gerais */
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Estilos para os botões */
    .stButton>button {
        border-radius: 10px;
        font-weight: bold;
        padding: 12px 24px;
        width: 100%;
        font-size: 16px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: scale(1.03);
        opacity: 0.9;
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
        margin-bottom: 15px;
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
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .grid-item-recente {
        box-shadow: 0 0 0 3px #ff4b4b;
        animation: pulse 1.5s infinite;
    }
    
    /* Animação para destaque */
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(255, 75, 75, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(255, 75, 75, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 75, 75, 0); }
    }
    
    /* Estilos para os cards de análise */
    .metric-card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 4px solid #4CAF50;
    }
    .metric-card h4 {
        margin-top: 0;
        color: #333;
        font-size: 16px;
    }
    .metric-card div {
        font-size: 24px;
        font-weight: bold;
        text-align: center;
        color: #1a1a1a;
    }
    
    /* Estilos para alertas */
    .alerta-box {
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        background-color: #fff8e1;
        border-left: 5px solid #ffc107;
        font-size: 16px;
    }
    
    /* Estilos para sugestão */
    .sugestao-box {
        background-color: #e8f5e9;
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
        border-left: 5px solid #4CAF50;
        font-size: 18px;
        font-weight: bold;
        text-align: center;
    }
    
    /* Melhorias gerais */
    .header-title {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
    }
    .linha-label {
        font-weight: bold;
        margin-bottom: 5px;
        font-size: 16px;
        color: #333;
    }
    .stSubheader {
        border-bottom: 2px solid #f0f2f6;
        padding-bottom: 10px;
        margin-top: 25px;
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
    return "Detectado" if ult == penult else "Não detectado"

def eco_parcial_por_linha(h):
    h = get_valores(h)
    if len(h) < 18:
        return "Poucos dados"
    ult = h[-9:]
    penult = h[-18:-9]
    semelhantes = 0
    for a, b in zip(penult, ult):
        if a == b or (a in ['C','V'] and b in ['C','V']):
            semelhantes += 1
    return f"{semelhantes}/9 semelhantes"

def dist_empates(h):
    h = get_valores(h)
    empates = [i for i, r in enumerate(h) if r == 'E']
    if len(empates) >= 2:
        distancia = empates[-1] - empates[-2]
        return f"{distancia} jogadas"
    return "N/A"

def blocos_espelhados(h):
    h = get_valores(h)
    cont = 0
    for i in range(len(h)-5):
        if h[i:i+3] == h[i+3:i+6][::-1]:
            cont += 1
    return cont

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
        return f"🔁 Sequência de {seq} {bolha_cor(ult)} - Possível reversão para {bolha_cor(cor_inversa)}"
    if ult == "E":
        return "🟨 Empate recente - Instável, possível 🟥 ou 🟦"
    if eco == "Detectado" or (isinstance(parcial, str) and parcial.startswith(("6", "7", "8", "9")):
        return f"🔄 Padrão repetido - Sugere manter {bolha_cor(ult)}"
    maior = max(contagens, key=contagens.get)
    return f"📊 Tendência favorece {bolha_cor(maior)} ({maior})"

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
        st.experimental_rerun()

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
    {sugestao(h)}
</div>
""", unsafe_allow_html=True)

# Histórico visual em grid 3x9
st.subheader("🧾 Histórico Visual (Zona Ativa: 3 Linhas)")
valores_para_grid = get_valores(h)[-27:]  # Últimos 27 valores válidos

# Preencher com espaços vazios se necessário
while len(valores_para_grid) < 27:
    valores_para_grid.insert(0, " ")  # Preencher no início para manter a ordem

# Dividir em 3 linhas de 9 colunas (Linha 1 = mais antiga, Linha 3 = mais recente)
linhas = [
    valores_para_grid[0:9],   # Linha 1 (mais antiga)
    valores_para_grid[9:18],  # Linha 2
    valores_para_grid[18:27]  # Linha 3 (mais recente)
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
        <div>{}</div>
    </div>
    """.format(get_valores(h).count("C")), unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
        <h4>🟦 Visitante</h4>
        <div>{}</div>
    </div>
    """.format(get_valores(h).count("V")), unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
        <h4>🟨 Empates</h4>
        <div>{}</div>
    </div>
    """.format(get_valores(h).count("E")), unsafe_allow_html=True)

# Outras métricas
col4, col5, col6 = st.columns(3)
with col4:
    st.markdown("""
    <div class="metric-card">
        <h4>📏 Maior Sequência</h4>
        <div>{}</div>
    </div>
    """.format(maior_sequencia(h)), unsafe_allow_html=True)

with col5:
    st.markdown("""
    <div class="metric-card">
        <h4>⏱️ Sequência Atual</h4>
        <div>{}</div>
    </div>
    """.format(sequencia_final(h)), unsafe_allow_html=True)

with col6:
    st.markdown("""
    <div class="metric-card">
        <h4>🔀 Alternância</h4>
        <div>{}</div>
    </div>
    """.format(alternancia(h)), unsafe_allow_html=True)

# Métricas adicionais
col7, col8, col9 = st.columns(3)
with col7:
    st.markdown("""
    <div class="metric-card">
        <h4>🔍 Eco Visual</h4>
        <div>{}</div>
    </div>
    """.format(eco_visual_por_linha(h)), unsafe_allow_html=True)

with col8:
    st.markdown("""
    <div class="metric-card">
        <h4>🔎 Eco Parcial</h4>
        <div>{}</div>
    </div>
    """.format(eco_parcial_por_linha(h)), unsafe_allow_html=True)

with col9:
    st.markdown("""
    <div class="metric-card">
        <h4>📊 Última Linha</h4>
        <div>{}</div>
    </div>
    """.format(tendencia_final(h)), unsafe_allow_html=True)

# Alertas estratégicos
st.subheader("🚨 Alertas Estratégicos")
alertas = []
valores = get_valores(h)

if sequencia_final(h) >= 5 and valores and valores[-1] in ["C", "V"]:
    alertas.append(f"🟥 Sequência de {sequencia_final(h)} - Possível inversão iminente")
if eco_visual_por_linha(h) == "Detectado":
    alertas.append("🔁 Eco visual detectado - Possível repetição de padrão")
if isinstance(eco_parcial_por_linha(h), str) and eco_parcial_por_linha(h).startswith(("6", "7", "8", "9")):
    alertas.append("🧠 Eco parcial - Padrão reescrito com alta similaridade")
if dist_empates(h) == 1:
    alertas.append("🟨 Empates consecutivos - Alta instabilidade no jogo")
if blocos_espelhados(h) >= 1:
    alertas.append("🧩 Bloco espelhado - Padrão reflexivo detectado")

if not alertas:
    st.info("✅ Nenhum padrão crítico identificado. Jogo dentro da normalidade estatística.")
else:
    for alerta in alertas:
        st.markdown(f'<div class="alerta-box">{alerta}</div>', unsafe_allow_html=True)

# Notas explicativas
st.markdown("""
---
**📝 Notas Explicativas:**
- **Eco Visual**: Compara a linha atual com a anterior (9 jogadas)
- **Eco Parcial**: Conta quantas jogadas são iguais ou do mesmo tipo (Casa/Visitante)
- **Blocos Espelhados**: Sequências de 3 jogadas que se repetem invertidas
- **Alternância**: Número de vezes que o resultado mudou entre jogadas consecutivas
""")
