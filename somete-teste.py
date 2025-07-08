import streamlit as st
import streamlit.components.v1 as components
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

# --- Funções de Análise ---
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

# --- Interface ---
st.set_page_config(layout="wide", page_title="Football Studio Analyzer Inteligente")

# Inicialização
if 'history' not in st.session_state:
    st.session_state.history = load_history()

st.title("⚽ Football Studio - Analisador de Padrões Inteligente")
st.markdown("Analise o histórico de resultados, com foco na **identificação de padrões de linhas que se repetem**, para auxiliar nas suas decisões.")

# --- Entrada de Resultados ---
st.header("Adicionar Novo Resultado")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🔴 Casa (R)"):
        st.session_state.history.append('R')
        save_history(st.session_state.history)
        st.rerun()
with col2:
    if st.button("🔵 Visitante (B)"):
        st.session_state.history.append('B')
        save_history(st.session_state.history)
        st.rerun()
with col3:
    if st.button("🟡 Empate (Y)"):
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
        st.metric("Total de Jogos", stats['total'])
    with col_stats_2:
        st.metric("Casa", f"{stats['percentages']['R']}% ({stats['counts'].get('R',0)})")
    with col_stats_3:
        st.metric("Visitante", f"{stats['percentages']['B']}% ({stats['counts'].get('B',0)})")
    with col_stats_4:
        st.metric("Empate", f"{stats['percentages']['Y']}% ({stats['counts'].get('Y',0)})")

st.markdown("---")

# --- Histórico Corrigido ---
st.header("Histórico de Jogos (Mais Recente Primeiro)")
history_lines = get_history_lines(st.session_state.history)
if not history_lines:
    st.info("O histórico está vazio. Adicione um resultado para começar.")
else:
    for i, line in enumerate(history_lines):
        line_number = f"<strong>{i+1}</strong>" if i == ANALYSIS_LINE_INDEX else f"{i+1}"
        line_html = f"""
        <div style="display: flex; align-items: center; margin-bottom: 4px;">
            <div style='width: 30px; font-size: 0.75rem; color: gray; margin-right: 4px; font-weight: bold;'>{line_number}</div>
            <div style='display: flex; gap: 4px;'>"""
        for color in line:
            color_info = COLOR_MAP[color]
            line_html += f"""<div style='width: 36px; height: 36px; background-color: {color_info['color_hex']}; color: {color_info['text_color']}; display: flex; align-items: center; justify-content: center; border-radius: 4px; font-weight: bold;'>{color}</div>"""
        for _ in range(LINE_LENGTH - len(line)):
            line_html += """<div style='width: 36px; height: 36px; background-color: #E5E7EB; color: #9CA3AF; display: flex; align-items: center; justify-content: center; border-radius: 4px; font-weight: bold;'>-</div>"""
        line_html += "</div></div>"
        components.html(line_html, height=60, scrolling=False)

    st.caption(f"A análise está focada na linha {ANALYSIS_LINE_INDEX + 1} (contando da mais recente para a mais antiga).")

st.markdown("---")

# --- Sugestões Inteligentes ---
st.header("Sugestões de Entrada Inteligentes")
all_suggestions = analyze_repeating_line_patterns(st.session_state.history, history_lines)
all_suggestions.extend(analyze_general_patterns(st.session_state.history))

if not all_suggestions:
    st.info("Adicione mais resultados para ativar as sugestões.")
else:
    for suggestion in all_suggestions:
        color_info = COLOR_MAP[suggestion['suggestion']]
        st.success(f"""
        ✅ **{suggestion['type']}**  
        🎯 **Sugestão**: {color_info['name']} ({suggestion['suggestion']})  
        📊 Confiança: {suggestion['confidence']}%  
        🧠 {suggestion['reason']}
        """)

st.markdown("---")

# --- Botão de Limpar Histórico ---
if st.button("🗑️ Limpar Histórico"):
    st.session_state.history = []
    save_history([])
    st.rerun()

st.caption("Desenvolvido por Helio Oliveira - Análise Inteligente para Football Studio 🎯")
