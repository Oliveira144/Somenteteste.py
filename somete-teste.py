import streamlit as st
import pandas as pd
from collections import Counter
import json
import os

# --- Configurações Iniciais ---
# Nome do arquivo para persistir o histórico.
# ATENÇÃO: No Streamlit Community Cloud, este arquivo é volátil e pode ser resetado
# após atualizações ou reinícios do servidor. Para persistência robusta, use um DB externo.
HISTORY_FILE = 'football_studio_history.json'
LINE_LENGTH = 9 # Quantidade de resultados por linha visual
ANALYSIS_LINE_INDEX = 3 # A quarta linha (índice 3, pois contamos a partir de 0) para análise de repetição.
                        # Ex: 0 = 1ª linha, 1 = 2ª linha, 2 = 3ª linha, 3 = 4ª linha.

# --- Mapeamento de Cores ---
COLOR_MAP = {
    'R': {'name': 'Casa (Home)', 'color_hex': '#EF4444', 'text_color': 'white'}, # Vermelho
    'B': {'name': 'Visitante (Away)', 'color_hex': '#3B82F6', 'text_color': 'white'}, # Azul
    'Y': {'name': 'Empate (Draw)', 'color_hex': '#FACC15', 'text_color': 'black'} # Amarelo
}

# --- Funções de Persistência Local (via arquivo) ---
def load_history():
    """Carrega o histórico de jogos do arquivo JSON."""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                # Retorna lista vazia se o JSON estiver corrompido
                return []
    return []

def save_history(history):
    """Salva o histórico de jogos no arquivo JSON."""
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f)

# --- Funções de Análise Inteligente ---

def get_history_lines(history):
    """
    Organiza o histórico linear em blocos (linhas) para visualização e análise.
    A linha 0 é a mais recente.
    """
    lines = []
    # Inverte o histórico para que as linhas mais recentes apareçam primeiro na visualização
    reversed_history = history[::-1]
    for i in range(0, len(reversed_history), LINE_LENGTH):
        lines.append(reversed_history[i : i + LINE_LENGTH])
    return lines

def analyze_repeating_line_patterns(history, history_lines):
    """
    Analisa se uma linha específica (definida por ANALYSIS_LINE_INDEX) está se repetindo
    e tenta identificar o padrão de continuação.
    """
    suggestions = []
    
    # Verifica se há linhas suficientes para analisar a linha alvo
    if len(history_lines) <= ANALYSIS_LINE_INDEX:
        return suggestions 

    target_line = history_lines[ANALYSIS_LINE_INDEX]
    target_line_str = "".join(target_line)

    found_matches = []
    # Percorre todas as linhas no histórico (exceto a linha alvo)
    for i, current_line in enumerate(history_lines):
        if i == ANALYSIS_LINE_INDEX: 
            continue # Não compara a linha com ela mesma

        current_line_str = "".join(current_line)
        
        # Compara a linha alvo com a linha atual do loop.
        # Verifica se são idênticas ou se a linha atual é um prefixo da linha alvo.
        # Isso ajuda a pegar padrões que ainda estão sendo "formados" na linha alvo.
        if target_line_str == current_line_str:
            found_matches.append({'index_line': i, 'line_content': current_line, 'type': 'Exata'})
        elif target_line_str.startswith(current_line_str):
             found_matches.append({'index_line': i, 'line_content': current_line, 'type': 'Prefixo'})


    if found_matches:
        reason_base = f"A linha atual (índice {ANALYSIS_LINE_INDEX+1} - '{target_line_str}') foi detectada como similar a padrões anteriores."
        
        # Tenta prever a próxima cor baseada no que veio após a linha em correspondências passadas.
        potential_next_colors = Counter()
        for match in found_matches:
            # Calcular o índice no histórico ORIGINAL (não invertido) onde a linha de correspondência termina
            # history_lines[match['index_line']] corresponde ao que veio ANTES no histórico original.
            # O índice 0 em history_lines é a linha mais RECENTE.
            # Então, para um match em history_lines[i], o fim dessa linha no histórico original
            # seria: (total_de_linhas - 1 - i) * LINE_LENGTH + len(match['line_content']) - 1 (se a linha estiver completa)
            
            # Mais simples: A entrada no histórico original que corresponde ao INÍCIO da linha de match
            start_index_in_original = len(history) - ((match['index_line'] + 1) * LINE_LENGTH)
            # A entrada no histórico original que corresponde ao FIM da linha de match
            end_index_in_original = start_index_in_original + len(match['line_content']) -1
            
            # Se existe uma próxima entrada no histórico original após essa linha de correspondência
            if end_index_in_original + 1 < len(history):
                next_entry = history[end_index_in_original + 1]
                potential_next_colors[next_entry] += 1
            
        if potential_next_colors:
            most_likely_next, count = potential_next_colors.most_common(1)[0]
            total_next = sum(potential_next_colors.values())
            confidence = round((count / total_next) * 100)
            
            suggestions.append({
                'type': 'Repetição de Linha (Continuação Padrão)',
                'suggestion': most_likely_next,
                'confidence': confidence,
                'reason': f"{reason_base} Com base em ocorrências anteriores de padrões similares, a próxima cor mais comum foi **{COLOR_MAP[most_likely_next]['name']}** ({count}/{total_next} vezes)."
            })
        else: # Se não há continuação clara, sugere a cor mais comum na própria linha
            color_counts_target_line = Counter(target_line)
            if color_counts_target_line:
                most_common_color_in_line, _ = color_counts_target_line.most_common(1)[0]
                suggestions.append({
                    'type': 'Repetição de Linha (Cor Dominante)',
                    'suggestion': most_common_color_in_line,
                    'confidence': 60, # Confiança um pouco menor se não houver um "próximo" claro
                    'reason': f"{reason_base} A cor dominante nesta linha repetida é **{COLOR_MAP[most_common_color_in_line]['name']}**. Pode continuar."
                })

    return suggestions


def analyze_general_patterns(history):
    """
    Função para análise de padrões mais gerais como transições e quebra de sequência,
    complementar à análise de repetição de linhas.
    """
    suggestions = []
    if len(history) < 2: # Precisa de um mínimo de resultados para certas análises
        return suggestions

    # Análise de Transições (o que vem depois da última cor)
    last_color = history[-1]
    transitions = {c: Counter() for c in COLOR_MAP.keys()}
    for i in range(len(history) - 1):
        transitions[history[i]][history[i+1]] += 1

    if last_color in transitions and transitions[last_color]:
        most_likely_next_transition, count_transition = transitions[last_color].most_common(1)[0]
        total_transitions = sum(transitions[last_color].values())
        confidence = round((count_transition / total_transitions) * 100)
        suggestions.append({
            'type': 'Transição Mais Frequente',
            'suggestion': most_likely_next_transition,
            'confidence': confidence,
            'reason': f"Após **{COLOR_MAP[last_color]['name']}**, a cor **{COLOR_MAP[most_likely_next_transition]['name']}** apareceu {count_transition} de {total_transitions} vezes no histórico."
        })

    # Análise de "Quebra de Padrão" (quando há muitas repetições da mesma cor)
    consecutive_count = 0
    if history:
        last_val = history[-1]
        for i in reversed(range(len(history))):
            if history[i] == last_val:
                consecutive_count += 1
            else:
                break
    
    if consecutive_count >= 3: # Sugere uma quebra após 3 ou mais resultados consecutivos
        opposite_colors = [c for c in COLOR_MAP.keys() if c != last_val]
        # Aqui, poderíamos adicionar lógica para escolher a "oposta" mais provável,
        # mas por simplicidade, pegamos a primeira que não seja a cor atual.
        if opposite_colors:
            suggestions.append({
                'type': 'Quebra de Sequência Longa',
                'suggestion': opposite_colors[0], 
                'confidence': 60, # Confiança média, pois não é um padrão exato
                'reason': f"Foram **{consecutive_count}** resultados consecutivos de **{COLOR_MAP[last_val]['name']}**. Há uma chance de quebra de padrão."
            })
    
    return suggestions

def calculate_stats(history):
    """Calcula estatísticas de ocorrência percentual das cores no histórico."""
    total = len(history)
    counts = Counter(history)
    stats = {
        'total': total,
        'percentages': {color: round((counts[color] / total) * 100) if total > 0 else 0 for color in COLOR_MAP.keys()},
        'counts': dict(counts)
    }
    return stats

# --- Interface Streamlit ---
st.set_page_config(layout="wide", page_title="Football Studio Analyzer Inteligente")

# Inicializa o histórico na sessão do Streamlit se ainda não existir
# Isso garante que o estado é mantido entre reruns
if 'history' not in st.session_state:
    st.session_state.history = load_history()

# Injeção de CSS personalizado para estilização (Tailwind-like)
st.markdown("""
<style>
    .stApp {
        background-color: #f0f2f6; /* Cor de fundo geral */
        color: #333;
    }
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 1200px; /* Limita a largura do conteúdo */
    }
    h1, h2, h3 {
        color: #1a202c; /* Cores de título mais escuras */
    }
    .stButton>button {
        width: 100%;
        padding: 1rem 0;
        border-radius: 0.5rem;
        font-weight: bold;
        font-size: 1.1rem;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        transition: background-color 0.2s ease-in-out;
    }
    /* Estilos específicos para os botões de resultado */
    .stButton button[data-testid="stButton-primary"]:nth-of-type(1) { /* Botão Casa */
        background-color: #EF4444; border: none; color: white;
    }
    .stButton button[data-testid="stButton-primary"]:nth-of-type(1):hover { background-color: #DC2626; }

    .stButton button[data-testid="stButton-primary"]:nth-of-type(2) { /* Botão Visitante */
        background-color: #3B82F6; border: none; color: white;
    }
    .stButton button[data-testid="stButton-primary"]:nth-of-type(2):hover { background-color: #2563EB; }

    .stButton button[data-testid="stButton-primary"]:nth-of-type(3) { /* Botão Empate */
        background-color: #FACC15; border: none; color: black;
    }
    .stButton button[data-testid="stButton-primary"]:nth-of-type(3):hover { background-color: #EAB308; }

    .color-box {
        width: 40px;
        height: 40px;
        border-radius: 4px;
        border: 2px solid #D1D5DB; /* lightgray-300 */
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 0.875rem; /* text-sm */
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05); /* Pequena sombra */
    }
    .suggestion-box {
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid;
        margin-bottom: 0.75rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06); /* Sombra mais pronunciada */
    }
    .confidence-high { border-color: #22C55E; background-color: #ECFDF5; } /* green-500, green-50 */
    .confidence-medium { border-color: #FBBF24; background-color: #FFFBEB; } /* yellow-500, yellow-50 */
    .confidence-low { border-color: #EF4444; background-color: #FEF2F2; } /* red-500, red-50 */
</style>
""", unsafe_allow_html=True)

st.title("⚽ Football Studio - Analisador de Padrões Inteligente")
st.markdown("Analise o histórico de resultados, com foco na **identificação de padrões de linhas que se repetem**, para auxiliar nas suas decisões.")

# --- Seção de Adição de Resultado ---
st.header("Adicionar Novo Resultado")
col1, col2, col3 = st.columns(3)

# Botões de adição de resultado
with col1:
    if st.button("🔴 Casa (R)", key="add_R"):
        st.session_state.history.append('R')
        save_history(st.session_state.history)
        st.rerun() # Recarrega a página para atualizar as análises

with col2:
    if st.button("🔵 Visitante (B)", key="add_B"):
        st.session_state.history.append('B')
        save_history(st.session_state.history)
        st.rerun()

with col3:
    if st.button("🟡 Empate (Y)", key="add_Y"):
        st.session_state.history.append('Y')
        save_history(st.session_state.history)
        st.rerun()

st.markdown("---")

# --- Estatísticas ---
st.header("Estatísticas Atuais")
stats = calculate_stats(st.session_state.history)

if stats['total'] == 0:
    st.info("Adicione resultados para ver as estatísticas de ocorrência.")
else:
    # Exibição das estatísticas em colunas com cores personalizadas
    col_stats_1, col_stats_2, col_stats_3, col_stats_4 = st.columns(4)
    with col_stats_1:
        st.markdown(f"""
        <div style="background-color: #60A5FA; color: white; padding: 1rem; border-radius: 0.5rem;">
            <div style="font-size: 0.875rem; opacity: 0.9;">Total de Jogos</div>
            <div style="font-size: 1.8rem; font-weight: bold;">{stats['total']}</div>
        </div>
        """, unsafe_allow_html=True)
    with col_stats_2:
        st.markdown(f"""
        <div style="background-color: {COLOR_MAP['R']['color_hex']}; color: white; padding: 1rem; border-radius: 0.5rem;">
            <div style="font-size: 0.875rem; opacity: 0.9;">Casa (Home)</div>
            <div style="font-size: 1.5rem; font-weight: bold;">{stats['percentages']['R']}%</div>
            <div style="font-size: 0.875rem; opacity: 0.9;">({stats['counts'].get('R', 0)} jogos)</div>
        </div>
        """, unsafe_allow_html=True)
    with col_stats_3:
        st.markdown(f"""
        <div style="background-color: {COLOR_MAP['B']['color_hex']}; color: white; padding: 1rem; border-radius: 0.5rem;">
            <div style="font-size: 0.875rem; opacity: 0.9;">Visitante (Away)</div>
            <div style="font-size: 1.5rem; font-weight: bold;">{stats['percentages']['B']}%</div>
            <div style="font-size: 0.875rem; opacity: 0.9;">({stats['counts'].get('B', 0)} jogos)</div>
        </div>
        """, unsafe_allow_html=True)
    with col_stats_4:
        st.markdown(f"""
        <div style="background-color: {COLOR_MAP['Y']['color_hex']}; color: {COLOR_MAP['Y']['text_color']}; padding: 1rem; border-radius: 0.5rem;">
            <div style="font-size: 0.875rem; opacity: 0.9;">Empate (Draw)</div>
            <div style="font-size: 1.5rem; font-weight: bold;">{stats['percentages']['Y']}%</div>
            <div style="font-size: 0.875rem; opacity: 0.9;">({stats['counts'].get('Y', 0)} jogos)</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# --- Histórico Visual ---
st.header("Histórico de Jogos (Mais Recente Primeiro)")

history_lines = get_history_lines(st.session_state.history)

if not history_lines:
    st.info("O histórico está vazio. Adicione um resultado para começar a análise visual e de padrões.")
else:
    for i, line in enumerate(history_lines):
        # O primeiro elemento da coluna é para o número da linha
        cols = st.columns([0.05] + [1] * LINE_LENGTH) 
        
        # Número da linha (i+1 para começar do 1, e marcamos a linha de análise)
        line_label = f"{i+1}"
        if i == ANALYSIS_LINE_INDEX:
            line_label = f"**{i+1}**" # Destaca a linha de análise
        cols[0].markdown(f"<div style='font-size: 0.75rem; color: gray; width: 30px; display: flex; align-items: center; justify-content: center;'>{line_label}</div>", unsafe_allow_html=True)
        
        for j, color in enumerate(line):
            color_info = COLOR_MAP[color]
            cols[j+1].markdown(f"""
            <div class="color-box" style="background-color: {color_info['color_hex']}; color: {color_info['text_color']};">
                {color}
            </div>
            """, unsafe_allow_html=True)
        
        # Preencher espaços vazios com caixas cinzas se a linha não estiver completa
        for j in range(len(line), LINE_LENGTH):
            cols[j+1].markdown("""
            <div class="color-box" style="background-color: #E5E7EB; color: #9CA3AF;">-</div>
            """, unsafe_allow_html=True)
    
    st.caption(f"A **análise de repetição de linha** está focada na **linha {ANALYSIS_LINE_INDEX + 1}** (contando a partir da mais recente no histórico).")

st.markdown("---")

# --- Sugestões Inteligentes ---
st.header("Sugestões de Entrada Inteligentes")

all_suggestions = []

# 1. Análise de Repetição de Linha (principal foco e a nova inteligência)
line_repetition_suggestions = analyze_repeating_line_patterns(st.session_state.history, history_lines)
all_suggestions.extend(line_repetition_suggestions)

# 2. Análise de Padrões Gerais (complementar)
general_pattern_suggestions = analyze_general_patterns(st.session_state.history)
all_suggestions.extend(general_pattern_suggestions)

if not all_suggestions:
    st.info("Adicione mais resultados ao histórico para que a IA possa analisar e gerar sugestões. A análise de 'repetição de linha' precisa de um histórico mais longo para identificar padrões.")
else:
    for suggestion in all_suggestions:
        color_info = COLOR_MAP[suggestion['suggestion']]
        
        # Determina a classe CSS da caixa de sugestão com base na confiança
        confidence_class = "confidence-low"
        if suggestion['confidence'] >= 70:
            confidence_class = "confidence-high"
        elif suggestion['confidence'] >= 50:
            confidence_class = "confidence-medium"

        st.markdown(f"""
        <div class="suggestion-box {confidence_class}">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <span style="font-weight: bold; color: #1F2937;">{suggestion['type']}</span>
                <span style="font-size: 0.875rem; background-color: #E5E7EB; padding: 0.25rem 0.5rem; border-radius: 0.25rem;">
                    {suggestion['confidence']}% confiança
                </span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.75rem;">
                <div class="color-box" style="background-color: {color_info['color_hex']}; color: {color_info['text_color']};">
                    {suggestion['suggestion']}
                </div>
                <span style="font-weight: 500; color: #374151;">
                    Próxima sug. → **{color_info['name']}**
                </span>
            </div>
            <div style="font-size: 0.875rem; color: #4B5563; margin-top: 0.5rem;">
                {suggestion['reason']}
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# --- Botão de Limpar Histórico ---
# Adiciona uma chave única para o botão, como boa prática no Streamlit
if st.button("🗑️ Limpar Histórico", key="clear_history_btn"):
    st.session_state.history = []
    save_history([]) # Garante que o arquivo também seja limpo
    st.rerun() # Recarrega a página para refletir o histórico limpo

st.caption("Desenvolvido por seu Engenheiro de Computação para análise de padrões em Football Studio.")

