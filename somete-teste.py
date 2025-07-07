import streamlit as st

# Histórico com limite automático de 100 entradas
if "historico" not in st.session_state:
    st.session_state.historico = []

def adicionar_resultado(valor):
    if len(st.session_state.historico) >= 100:
        st.session_state.historico.pop(0)
    st.session_state.historico.append(valor)

# 🔍 Funções analíticas com tratamento para dados insuficientes
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
    semelhantes = sum(1 for a, b in zip(penult, ult) if a == b or (a in ['C','V'] and b in ['C','V']))
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
    ult = valores[-1]
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
st.set_page_config(page_title="Football Studio – Estratégia", layout="wide")
st.title("🎲 Football Studio Live — Leitura Estratégica")

# Entrada
col1, col2, col3, col4 = st.columns(4)
if col1.button("➕ Casa (C)"): adicionar_resultado("C")
if col2.button("➕ Visitante (V)"): adicionar_resultado("V")
if col3.button("➕ Empate (E)"): adicionar_resultado("E")
if col4.button("🗂️ Novo baralho"): adicionar_resultado("🔽")

h = st.session_state.historico

# Sugestão preditiva
st.subheader("🎯 Sugestão de entrada")
st.success(sugestao(h))

# Histórico visual com destaque até 3 linhas (27 bolhas)
st.subheader("🧾 Histórico visual (zona ativa: 3 linhas)")
if h:
    # Mostrar do mais recente para o mais antigo
    for i in range(0, len(h), 9):
        linha = h[::-1][i:i+9]  # Inverte para mostrar recentes primeiro
        estilo = 'font-size:24px;' if i < 27 else 'font-size:20px; opacity:0.5;'
        bolha_html = "".join(
            f"<span style='{estilo} margin-right:4px;'>{bolha_cor(r)}</span>" for r in linha
        )
        st.markdown(f"<div style='display:flex;'>{bolha_html}</div>", unsafe_allow_html=True)
else:
    st.caption("Nenhum resultado registrado")

# Painel de análise
st.subheader("📊 Análise dos últimos 27 jogadas")
valores = get_valores(h)
col1, col2, col3 = st.columns(3)
col1.metric("Total Casa", valores.count("C"))
col2.metric("Total Visitante", valores.count("V"))
col3.metric("Total Empates", valores.count("E") if valores else 0)

st.write(f"Maior sequência: **{maior_sequencia(h)}**")
st.write(f"Sequência atual: **{sequencia_final(h)}**")
st.write(f"Alternância total: **{alternancia(h)}**")
st.write(f"Eco visual por linha: **{eco_visual_por_linha(h)}**")
st.write(f"Eco parcial por linha: **{eco_parcial_por_linha(h)}**")
st.write(f"Distância entre empates: **{dist_empates(h)}**")
st.write(f"Blocos espelhados: **{blocos_espelhados(h)}**")

# Alternância por linha formatada
alt_por_linha = alternancia_por_linha(h)
if alt_por_linha:
    st.write("Alternância por linha:")
    for i, val in enumerate(alt_por_linha[-3:]):  # Mostra apenas últimas 3 linhas
        st.caption(f"• Linha {len(alt_por_linha)-i}: {val} alterações")
else:
    st.write("Alternância por linha: Dados insuficientes")

st.write(f"Tendência final: **{tendencia_final(h)}**")

# Alertas
st.subheader("🚨 Alerta estratégico")
alertas = []
if sequencia_final(h) >= 5 and valores and valores[-1] in ["C", "V"]:
    alertas.append(f"🟥 Sequência de {sequencia_final(h)} — possível inversão")
if eco_visual_por_linha(h) == "Detectado":
    alertas.append("🔁 Eco visual detectado — possível repetição")
if eco_parcial_por_linha(h).startswith(("6", "7", "8", "9")):
    alertas.append("🧠 Eco parcial — padrão reescrito")
if dist_empates(h) == 1:
    alertas.append("🟨 Empates consecutivos — instabilidade")
if blocos_espelhados(h) >= 1:
    alertas.append("🧩 Bloco espelhado — reflexo estratégico")

if not alertas:
    st.info("Nenhum padrão crítico identificado.")
else:
    for alerta in alertas:
        st.warning(alerta)

# Limpar
if st.button("🧹 Limpar histórico"):
    st.session_state.historico = []
    st.rerun()
