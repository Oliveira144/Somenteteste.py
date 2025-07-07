import streamlit as st
import collections

# --- Definições Globais ---
SIMBOLOS_EXIBICAO = {
    'C': 'C (Casa/Azul)',
    'V': 'V (Visitante/Vermelho)',
    'E_C': 'E (Empate, prox. Casa/Azul)',
    'E_V': 'E (Empate, prox. Visitante/Vermelho)'
}

# Tamanho da janela de análise que você observa (equivalente ao 3x9 = 27 células)
TAMANHO_JANELA_ANALISE = 27
# Quantidade de resultados que você considera como "última linha" para sua análise
TAMANHO_LINHA_OBSERVACAO = 9

# --- Inicialização do Session State (CRUCIAL para Streamlit) ---
if 'historico_completo' not in st.session_state:
    st.session_state.historico_completo = collections.deque(maxlen=1000) # Capacidade maior
if 'tabela_road_interna' not in st.session_state:
    st.session_state.tabela_road_interna = [['' for _ in range(NUM_COLUNAS_ROAD)] for _ in range(NUM_LINHAS_ROAD)]

# --- Funções Auxiliares ---

def formatar_resultado_para_exibicao(res):
    """Formata o resultado para exibição amigável."""
    if isinstance(res, tuple):
        return SIMBOLOS_EXIBICAO[f'E_{res[1]}']
    return SIMBOLOS_EXIBICAO[res]

def obter_cor_resultado(res):
    """Retorna a cor associada ao resultado ('Azul' ou 'Vermelho').
       Para empates, retorna a cor da 'linha' (próximo vencedor)."""
    if isinstance(res, tuple): # Empate
        return 'Azul' if res[1] == 'C' else 'Vermelho'
    return 'Azul' if res == 'C' else 'Vermelho'

def get_vencedor_real(res):
    """Retorna 'C' ou 'V' para o resultado, tratando empates pelo próximo vencedor."""
    if isinstance(res, tuple): # Empate
        return res[1] # Retorna 'C' ou 'V' que o seguiu
    return res # Retorna 'C' ou 'V' diretamente

def adicionar_resultado_ao_historico_e_road(resultado):
    """
    Adiciona um novo resultado ao histórico completo e atualiza a tabela interna do road.
    Este é o ponto de entrada para novos resultados.
    """
    # Guarda o resultado que vai "sumir" da primeira posição da road ANTES de mover
    # Isso é apenas para análise posterior, não afeta a adição do resultado agora.
    
    # Move todas as células da tabela_road_interna uma posição para a esquerda
    for r in range(NUM_LINHAS_ROAD):
        for c in range(NUM_COLUNAS_ROAD - 1):
            st.session_state.tabela_road_interna[r][c] = st.session_state.tabela_road_interna[r][c+1]
        st.session_state.tabela_road_interna[r][NUM_COLUNAS_ROAD - 1] = '' # Limpa a última coluna

    # Adiciona o novo resultado na primeira linha da última coluna (como se fosse o início de uma nova coluna)
    st.session_state.tabela_road_interna[0][NUM_COLUNAS_ROAD - 1] = resultado
    
    # Adiciona ao histórico principal do session_state
    st.session_state.historico_completo.append(resultado)
    st.success(f"Resultado '{formatar_resultado_para_exibicao(resultado)}' adicionado ao histórico.")


# --- Funções de Análise de Padrões ---

def analisar_padroes_football_studio():
    """
    Função principal para analisar os padrões do Football Studio com base na sua hipótese.
    """
    n = len(st.session_state.historico_completo)
    
    st.subheader("Análise de Padrões")

    if n < NUM_COLUNAS_ROAD * NUM_LINHAS_ROAD: # 27 resultados para preencher a road completa
        st.warning(f"Histórico muito pequeno ({n} resultados). Precisa de pelo menos {NUM_COLUNAS_ROAD * NUM_LINHAS_ROAD} para uma análise completa da 'road'.")
        st.info("Continue inserindo resultados para preencher a tabela de visualização interna.")
        return

    # Extrai a janela de análise mais recente (os últimos 27 resultados)
    janela_analise = list(st.session_state.historico_completo)[-NUM_COLUNAS_ROAD * NUM_LINHAS_ROAD:]

    # 1. Análise da "cor que some" vs. "cor que aparece"
    if len(st.session_state.historico_completo) >= NUM_COLUNAS_ROAD * NUM_LINHAS_ROAD:
        # O resultado que "sumiu" da visualização é o elemento que estava na posição inicial do histórico
        # antes dos 27 resultados mais recentes.
        cor_que_sumiu_da_visualizacao = obter_cor_resultado(st.session_state.historico_completo[-(NUM_COLUNAS_ROAD * NUM_LINHAS_ROAD)])
        # A cor que "apareceu" é a do resultado mais recente
        cor_que_apareceu_agora = obter_cor_resultado(st.session_state.historico_completo[-1])

        st.markdown(f"**Cor que 'sumiu' da visualização (resultado mais antigo da janela de {TAMANHO_JANELA_ANALISE}):** {cor_que_sumiu_da_visualizacao}")
        st.markdown(f"**Cor que 'apareceu' (resultado mais recente):** {cor_que_apareceu_agora}")

        if cor_que_sumiu_da_visualizacao == cor_que_apareceu_agora:
            st.success(f"**PADRÃO DETECTADO:** A cor ({cor_que_apareceu_agora}) que 'sumiu' do início da visualização é a mesma do resultado mais recente. (Sua Regra de Cores)")
        else:
            st.info(f"**OBS:** A cor que 'sumiu' ({cor_que_sumiu_da_visualizacao}) é diferente da cor que 'apareceu' ({cor_que_apareceu_agora}).")

    # 2. Análise de Sequências na "Última Linha" (os 9 resultados mais recentes)
    st.markdown("\n**Análise de Sequências na 'Última Linha' (últimos 9 resultados):**")
    ultimos_9_resultados = list(st.session_state.historico_completo)[-NUM_COLUNAS_ROAD:]
    
    sequencias_detectadas = []
    contagem_sequencia = 0
    cor_atual_sequencia = None
    
    if len(ultimos_9_resultados) >= 3:
        for i in range(len(ultimos_9_resultados)):
            current_res_color = obter_cor_resultado(ultimos_9_resultados[i])
            
            if current_res_color == cor_atual_sequencia:
                contagem_sequencia += 1
            else:
                if contagem_sequencia >= 3:
                    sequencias_detectadas.append(f"{contagem_sequencia}x {cor_atual_sequencia} seguida.")
                cor_atual_sequencia = current_res_color
                contagem_sequencia = 1
        
        if contagem_sequencia >= 3: # Checa a última sequência após o loop
            sequencias_detectadas.append(f"{contagem_sequencia}x {cor_atual_sequencia} seguida.")

    if sequencias_detectadas:
        for seq in sequencias_detectadas:
            st.success(f"- {seq}")
        
        # Inferência de "virando", "alternando", "seguindo"
        if len(st.session_state.historico_completo) > NUM_COLUNAS_ROAD: # Precisa de resultados após os 9 para inferir
            ultima_sequencia_cor = sequencias_detectadas[-1].split('x ')[1].split(' ')[0] # Extrai a cor
            
            # Pega o resultado imediatamente após a sequência (que é o último adicionado)
            cor_proximo = obter_cor_resultado(st.session_state.historico_completo[-1])
            
            if cor_proximo == ultima_sequencia_cor:
                st.info(f"   **Inferência:** Após a sequência de {ultima_sequencia_cor}, parece que a cor está 'seguindo'.")
            else:
                st.info(f"   **Inferência:** Após a sequência de {ultima_sequencia_cor}, parece que a cor está 'virando' para {cor_proximo}.")
            # Para "alternando", precisaríamos de mais complexidade, como analisar os 2-3 próximos resultados.
            # Se você tiver uma regra específica para "alternando", me diga.
    else:
        st.info("Nenhuma sequência de 3 ou mais cores seguidas detectada na 'Última Linha' (últimos 9 resultados).")

    # 3. Análise de Comportamento dos Empates ("E")
    st.markdown("\n**Análise de Comportamento dos Empates (E):**")
    
    empates_na_janela = []
    for i, res in enumerate(janela_analise):
        if isinstance(res, tuple) and res[0] == 'E':
            empates_na_janela.append((i, res)) # (indice_na_janela, resultado_empate)

    if not empates_na_janela:
        st.info("Nenhum empate na janela de análise atual.")
    else:
        st.markdown(f"Empates encontrados na janela de análise ({len(empates_na_janela)}):")
        for idx, empate_res in empates_na_janela:
            cor_seguinte_empate = obter_cor_resultado(empate_res)
            st.text(f"  - Posição relativa na janela {idx}: Empate seguido de {cor_seguinte_empate} ({formatar_resultado_para_exibicao(empate_res)})")

        if len(empates_na_janela) >= 2:
            ultimo_empate_cor = obter_cor_resultado(empates_na_janela[-1][1])
            penultimo_empate_cor = obter_cor_resultado(empates_na_janela[-2][1])
            
            if ultimo_empate_cor == penultimo_empate_cor:
                st.success(f"**PADRÃO:** Dois últimos empates seguidos de mesma cor ({ultimo_empate_cor}).")
            else:
                st.info(f"**OBS:** Dois últimos empates seguidos de cores alternadas ({penultimo_empate_cor} -> {ultimo_empate_cor}).")

        # Regra específica "os 2 que estão colados viraram azul e os 2 vermelho viraram azul e o outro azul"
        # Isso precisa ser mais formalizado. Se você tiver a sequência exata de C/V/E que gera isso,
        # podemos tentar detectar.
        # Exemplo: Verificar se nos últimos 5 resultados, há: E_V, E_V, E_C, E_C, C
        # OU: E_V, E_V, E_C, E_C, E_C
        # Precisa da sequência exata e da previsão.
        
    st.markdown("---")


# --- Interface Streamlit ---

st.set_page_config(layout="wide", page_title="Analisador de Padrões Football Studio")

st.title("⚽ Analisador de Padrões Football Studio")
st.markdown("Insira os resultados e veja a análise baseada nas suas observações.")

# Colunas para entrada de dados
col1, col2 = st.columns(2)

with col1:
    st.subheader("Inserir Novo Resultado")
    entrada_usuario = st.text_input(
        "Digite o próximo resultado:",
        placeholder="Ex: C, V, E C, E V"
    )

    if st.button("Adicionar Resultado"):
        if entrada_usuario:
            entrada_formatada = entrada_usuario.strip().upper()
            if entrada_formatada in ['C', 'V']:
                adicionar_resultado_ao_historico_e_road(entrada_formatada)
            elif entrada_formatada.startswith('E '):
                partes = entrada_formatada.split()
                if len(partes) == 2 and partes[0] == 'E' and partes[1] in ['C', 'V']:
                    adicionar_resultado_ao_historico_e_road(('E', partes[1]))
                else:
                    st.error("Entrada inválida para Empate. Use 'E C' ou 'E V'.")
            else:
                st.error("Entrada inválida. Use 'C', 'V', 'E C' ou 'E V'.")
        else:
            st.warning("Por favor, digite um resultado.")

with col2:
    st.subheader("Ações")
    if st.button("Analisar Padrões"):
        analisar_padroes_football_studio()

    if st.button("Mostrar Histórico Completo"):
        if st.session_state.historico_completo:
            st.write("### Histórico Completo de Resultados:")
            # Exibe o histórico de forma mais legível
            historico_formatado = [formatar_resultado_para_exibicao(res) for res in st.session_state.historico_completo]
            st.code(historico_formatado)
        else:
            st.info("Histórico vazio. Adicione alguns resultados primeiro.")
    
    if st.button("Limpar Histórico"):
        st.session_state.historico_completo = collections.deque(maxlen=1000)
        st.session_state.tabela_road_interna = [['' for _ in range(NUM_COLUNAS_ROAD)] for _ in range(NUM_LINHAS_ROAD)]
        st.success("Histórico e tabela interna limpos.")
        st.rerun() # Reinicia o app para refletir a limpeza

# Exibir o estado atual do histórico na sidebar ou em algum lugar fixo
st.sidebar.subheader(f"Total no Histórico: {len(st.session_state.historico_completo)}")
if len(st.session_state.historico_completo) > 0:
    st.sidebar.markdown("Últimos resultados:")
    # Mostrar apenas os últimos 10 para não lotar a sidebar
    for res in list(st.session_state.historico_completo)[-10:]:
        st.sidebar.text(formatar_resultado_para_exibicao(res))
