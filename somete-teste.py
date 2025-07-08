import streamlit as st
import pandas as pd
from collections import Counter
import json
import os

# --- Configurações Iniciais ---
HISTORY_FILE = 'football_studio_history.json'
LINE_LENGTH = 9
ANALYSIS_LINE_INDEX = 3

# --- Mapeamento de Cores ---
COLOR_MAP = {
    'R': {'name': 'Casa (Home)', 'color_hex': '#EF4444', 'text_color': 'white'},
    'B': {'name': 'Visitante (Away)', 'color_hex': '#3B82F6', 'text_color': 'white'},
    'Y': {'name': 'Empate (Draw)', 'color_hex': '#FACC15', 'text_color': 'black'}
}

# --- Funções de Persistência Local ---
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_history(history):
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f)

# --- Funções de Análise Inteligente ---
def get_history_lines(history):
    lines = []
    reversed_history = history[::-1]
    for i in range(0, len(reversed_history), LINE_LENGTH):
        lines.append(reversed_history[i : i + LINE_LENGTH])
    return lines

def analyze_repeating_line_patterns(history, history_lines):
    suggestions = []
    
    if len(history_lines) <= ANALYSIS_LINE_INDEX:
        return suggestions 

    target_line = history_lines[ANALYSIS_LINE_INDEX]
    target_line_str = "".join(target_line)

    found_matches = []
    for i, current_line in enumerate(history_lines):
        if i == ANALYSIS_LINE_INDEX: 
            continue

        current_line_str = "".join(current_line)
        
        if target_line_str == current_line_str:
            found_matches.append({'index_line': i, 'line_content': current_line, 'type': 'Exata'})
        elif target_line_str.startswith(current_line_str):
             found_matches.append({'index_line': i, 'line_content': current_line, 'type': 'Prefixo'})

    if found_matches:
        reason_base = f"A linha atual (índice {ANALYSIS_LINE_INDEX+1} - '{target_line_str}') foi detectada como similar a padrões anteriores."
        
        potential_next_colors = Counter()
        for match in found_matches:
            start_index_in_original = len(history) - ((match['index_line'] + 1) * LINE_LENGTH)
            end_index_in_original = start_index_in_original + len(match['line_content']) -1
            
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
        else:
            color_counts_target_line = Counter(target_line)
            if color_counts_target_line:
                most_common_color_in_line, _ = color_counts_target_line.most_common(1)[0]
                suggestions.append({
                    'type': 'Repetição de Linha (Cor Dominante)',
                    'suggestion': most_common_color_in_line,
                    'confidence': 60,
                    'reason': f"{reason_base} A cor dominante nesta linha repetida é **{COLOR_MAP[most_common_color_in_line]['name']}**. Pode continuar."
                })

    return suggestions

def analyze_general_patterns(history):
    suggestions = []
    if len(history) < 2:
        return suggestions

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

    consecutive_count = 0
    if history:
        last_val = history[-1]
        for i in reversed(range(len(history))):
            if history[i] == last_val:
                consecutive_count += 1
            else:
                break
    
    if consecutive_count >= 3:
        opposite_colors = [c for c in COLOR_MAP.keys() if c != last_val]
        if opposite_colors:
            suggestions.append({
                'type': 'Quebra de Sequência Longa',
                'suggestion': opposite_colors[0], 
                'confidence': 60,
                'reason': f"Foram **{consecutive_count}** resultados consecutivos de **{COLOR_MAP[last_val]['name']}**. Há uma chance de quebra de padrão."
            })
    
    return suggestions

def calculate_stats(history):
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

# Injeção de CSS personalizado
st.markdown("""
<style>
    .stApp {
        background-color: #f0f2f6;
        color: #333;
    }
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 1200px;
    }
    h1, h2, h3 {
        color: #1a202c;
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
    .stButton button[data-testid="stButton-primary"]:nth-of-type(1) {
        background-color: #EF4444; border: none; color: white;
    }
    .stButton button[data-testid="stButton-primary"]:nth-of-type(1):hover { background-color: #DC2626; }
    .stButton button[data-testid="stButton-primary"]:nth-of-type(2) {
        background-color: #3B82F6; border: none; color: white;
    }
    .stButton button[data-testid="stButton-primary"]:nth-of-type(2):hover { background-color: #2563EB; }
    .stButton button[data-testid="stButton-primary"]:nth-of-type(3) {
        background-color: #FACC15; border: none; color: black;
    }
    .stButton button[data-testid="stButton-primary"]:nth-of-type(3):hover { background-color: #EAB308; }
    .color-box-container {
        display: flex;
        gap: 4px;
        margin-bottom: 4px;
        align-items: center;
        flex-wrap: nowrap;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        padding-bottom: 5px;
    }
    .color-box {
        width: 36px;
        min-width: 36px;
        height: 36px;
        border-radius: 4px;
        border: 2px solid #D1D5DB;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 0.875rem;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        flex-shrink: 0;
    }
    .line-number-box {
        width: 30px;
        min-width: 30px;
        font-size: 0.75rem;
        color: gray;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        margin-right: 4px;
        font-weight: bold;
    }
    .suggestion-box {
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid;
        margin-bottom: 0.75rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    .confidence-high { border-color: #22C55E; background-color: #ECFDF5; }
    .confidence-medium { border-color: #FBBF24; background-color: #FFFBEB; }
    .confidence-low { border-color: #EF4444; background-color: #FEF2F2; }
</style>
""", unsafe_allow_html=True)

# Inicialização do estado da sessão
if 'history' not in st.session_state:
    st.session_state.history = load_history()

st.title("⚽ Football Studio - Analisador de Padrões Inteligente")
st.markdown("Analise o histórico de resultados, com foco na **identificação de padrões de linhas que se repetem**, para auxiliar nas suas decisões.")

# --- Seção de Adição de Resultado ---
st.header("Adicionar Novo Resultado")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔴 Casa (R)", key="add_R"):
        st.session_state.history.append('R')
        save_history(st.session_state.history)
        st.rerun()

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
        # Geração dinâmica do HTML para cada linha
        line_html = f"""
        <div style="display: flex; align-items: center; margin-bottom: 4px;">
            <div class="line-number-box">
                {f"<strong>{i+1}</strong>" if i == ANALYSIS_LINE_INDEX else i+1}
            </div>
            <div class="color-box-container">
        """
        
        # Adiciona as caixas coloridas para cada resultado
        for color in line:
            color_info = COLOR_MAP[color]
            line_html += f"""
                <div class="color-box" style="background-color: {color_info['color_hex']}; color: {color_info['text_color']};">
                    {color}
                </div>
            """
        
        # Preenche com caixas vazias se a linha não estiver completa
        for _ in range(LINE_LENGTH - len(line)):
            line_html += """
                <div class="color-box" style="background-color: #E5E7EB; color: #9CA3AF;">-</div>
            """
        
        line_html += """
            </div>
        </div>
        """
        
        st.markdown(line_html, unsafe_allow_html=True)
    
    st.caption(f"A **análise de repetição de linha** está focada na **linha {ANALYSIS_LINE_INDEX + 1}** (contando a partir da mais recente no histórico).")

st.markdown("---")

# --- Sugestões Inteligentes ---
st.header("Sugestões de Entrada Inteligentes")

all_suggestions = []
line_repetition_suggestions = analyze_repeating_line_patterns(st.session_state.history, history_lines)
all_suggestions.extend(line_repetition_suggestions)
general_pattern_suggestions = analyze_general_patterns(st.session_state.history)
all_suggestions.extend(general_pattern_suggestions)

if not all_suggestions:
    st.info("Adicione mais resultados ao histórico para que a IA possa analisar e gerar sugestões. A análise de 'repetição de linha' precisa de um histórico mais longo para identificar padrões.")
else:
    for suggestion in all_suggestions:
        color_info = COLOR_MAP[suggestion['suggestion']]
        
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
if st.button("🗑️ Limpar Histórico", key="clear_history_btn"):
    st.session_state.history = []
    save_history([])
    st.rerun()

st.caption("Desenvolvido por seu Engenheiro de Computação para análise de padrões em Football Studio.")
