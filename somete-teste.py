import streamlit as st

# 🚀 Histórico expandido
if "historico" not in st.session_state:
    st.session_state.historico = []

def adicionar_resultado(valor):
    st.session_state.historico.append(valor)
    if len(st.session_state.historico) > 300:
        st.session_state.historico.pop(0)

# 🔍 Zona ativa: últimos 27 válidos (3 linhas)
def get_valores(h):
    return [r for r in h if r in ["C", "V", "E"]][-27:]

# 🎯 Funções preditivas com zona ativa
def maior_sequencia(h):
    h = get_valores(h)
    max_seq = atual = 1
    for i in range(1, len(h)):
        if h[i] == h[i - 1]:
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
    for i in range(len(h) - 2, -1, -1):
        if h[i] == atual:
            count += 1
        else:
            break
    return count

def alternancia(h):
    h = get_valores(h)
    return sum(1 for i in range(1, len(h)) if h[i] != h[i - 1])

def eco_visual(h):
    h = get_valores(h)
    if len(h) < 12:
        return "Poucos dados"
    return "Detectado" if h[-6:] == h[-12:-6] else "Não houve"

def eco_parcial(h):
    h = get_valores(h)
    if len(h) < 12:
        return "Poucos dados"
    anterior = h[-12:-6]
    atual = h[-6:]
    semelhantes = sum(1 for a, b in zip(anterior, atual) if a == b or (a in "CV" and b in "CV"))
    return f"{semelhantes}/6 semelhantes"

def dist_empates(h):
    h = get_valores(h)
    empates = [i for i, r in enumerate(h) if r == 'E']
    return empates[-1] - empates[-2] if len(empates) >= 2 else "N/A"

def blocos_espelhados(h):
    h = get_valores(h)
    cont = 0
    for i in range(len(h) - 5):
        if h[i:i + 3] == h[i + 3:i + 6][::-1]:
            cont += 1
    return cont

def alternancia_por_linha(h):
    h = get_valores(h)
    linhas = [h[i:i + 9] for i in range(0, len(h), 9)]
    return [sum(1 for j in range(1, len(linha)) if linha[j] != linha[j - 1]) for linha in linhas]

def tendencia_final(h):
    h = get_valores(h)
    ult = h[-5:]
    return f"{ult.count('C')}C / {ult.count('V')}V / {ult.count('E')}E"

# 🧩 Comparação posicional por linha (1×4, 2×5, 3×6)
def comparar_linhas_posicionais(h):
    linhas_validas = [r for r in h if r in ["C", "V", "E"]]
    if len(linhas_validas) < 54:
        return ["Dados insuficientes"]
    
    def linha(n):
        return linhas_validas[-(9 * n):-9 * (n - 1)]
    
    resultados = []
    for atual, espelho in [(1, 4), (2, 5), (3, 6)]:
        l1 = linha(atual)
        l2 = linha(espelho)
        iguais = sum(1 for x, y in zip(l1, l2) if x == y or (x in "CV" and y in "CV"))
        resultados.append(f"Linha {atual} × {espelho}: {iguais}/9 semelhantes")
    return resultados

# 🎯 Sugestão preditiva refinada
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
    ult = valores[-1]
    seq = sequencia_final(h)
    eco = eco_visual(h)
    parcial = eco_parcial(h)
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
    if eco == "Detectado" or parcial.startswith(("5", "6")):
        return f"🔄 Reescrita visual — repetir padrão com {bolha_cor(ult)}"
    maior = max(contagens, key=contagens.get)
    return f"📊 Tendência favorece entrada em {bolha_cor(maior)} ({maior})"

# 🧠 Interface
st.set_page_config(page_title="Football Studio – Radar Estratégico", layout="wide")
st.title("🎲 Football Studio Live — Leitura de Padrões")

# Entrada manual
col1, col2, col3, col4 = st.columns(4)
if col1.button("➕ Casa (C)"): adicionar_resultado("C")
if col2.button("➕ Visitante (V)"): adicionar_resultado("V")
if col3.button("➕ Empate (E)"): adicionar_resultado("E")
if col4.button("🗂️ Novo baralho"): adicionar_resultado("🔽")

h = st.session_state.historico

# Sugestão principal
st.subheader("🎯 Sugestão estratégica")
st.success(sugestao(h))

# Histórico visual
st.subheader("🧾 Histórico visual (27 ativos + espectador)")
h_reverso = h[::-1]
bolhas = [bolha_cor(r) for r in h_reverso]
for i in range(0, len(bolhas), 9):
    linha = bolhas[i:i + 9]
    estilo = 'font-size:24px;' if i < 27 else 'font-size:20px; opacity:0.5;'
    st.markdown("".join(f"<span style='{estilo} margin-right:4px;'>{b}</span>" for b in linha),
                unsafe_allow_html=True)

# Painel de análise
st.subheader("📊 Análise preditiva (últimos 27)")
valores = get_valores(h)
col1, col2, col3 = st.columns(3)
col1.metric("Total Casa", valores.count("C"))
col2.metric("Total Visitante", valores.count("V"))
col3.metric("Total Empates", valores.count("E"))

st.write(f"Maior sequência: **{maior_sequencia(h)}**")
st.write(f"Alternância: **{alternancia(h)}**")
st.write(f"Eco visual: **{eco_visual(h)}**")
st.write(f"Eco parcial: **{eco_parcial(h)}**")
st.write(f"Distância entre empates: **{dist_empates(h)}**")
st.write(f"Blocos espelhados: **{blocos_espelhados(h)}**")
st.write(f"Alternância por linha: **{alternancia_por_linha(h)}**")
st.write(f"Tendência final: **{tendencia_final(h)}**")

# 🔁 Comparação posicional
st.subheader("🧩 Semelhança por linha (1×4, 2×5, 3×6)")
for resultado in comparar_linhas_posicionais(h):
    st.write(resultado)

# Alertas estratégicos
st.subheader("🚨 Alertas críticos")
alertas = []
# Alertas estratégicos
st.subheader("🚨 Alertas críticos")
alertas = []
if sequencia_final(h) >= 5 and valores[-1] in ["C", "V"]:
    alerta = f"🟥 Sequência final ativa de {bolha_cor(valores[-1])} — possível reversão"
    alertas.append(alerta)

if eco_visual(h) == "Detectado":
    alertas.append("🔁 Eco visual identificado — padrão pode se repetir")

if eco_parcial(h).startswith(("4", "5", "6")):
    alertas.append("🧠 Eco parcial — padrão reescrito com semelhanças")

if dist_empates(h) == 1:
    alertas.append("🟨 Empates consecutivos — momento instável")

if blocos_espelhados(h) >= 1:
    alertas.append("🧩 Bloco espelhado — comportamento reflexivo")

comparacoes = comparar_linhas_posicionais(h)
for c in comparacoes:
    if "semelhantes" in c:
        qtd = int(c.split(":")[1].split("/")[0])
        if qtd >= 7:
            alertas.append("🧬 Reescrita por linha detectada — padrão simulando continuidade visual")

if not alertas:
    st.info("Nenhum padrão crítico identificado.")
else:
    for alerta in alertas:
        st.warning(alerta)

# Botão de limpeza
if st.button("🧹 Limpar histórico"):
    st.session_state.historico = []
    st.rerun()

if sequencia_final(h) >= 5 and valores
