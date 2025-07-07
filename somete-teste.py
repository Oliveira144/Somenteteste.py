import streamlit as st
import collections

# --- Definições Globais ---
SIMBOLOS_EXIBICAO = {
    'C': 'C (Casa/Azul)',
    'V': 'V (Visitante/Vermelho)',
    'E_C': 'E (Empate, prox. Casa/Azul)',
    'E_V': 'E (Empate, prox. Visitante/Vermelho)'
}

# Definições das dimensões da Road (MOVIDAS PARA CÁ PARA RESOLVER O ERRO)
NUM_LINHAS_ROAD = 3
NUM_COLUNAS_ROAD = 9

# Tamanho da janela de análise que você observa (equivalente ao 3x9 = 27 células)
TAMANHO_JANELA_ANALISE = NUM_LINHAS_ROAD * NUM_COLUNAS_ROAD
# Quantidade de resultados que você considera como "última linha" para sua análise
TAMANHO_LINHA_OBSERVACAO = NUM_COLUNAS_ROAD # Assumindo 9 resultados por "linha" visual

# --- Inicialização do Session State (CRUCIAL para Streamlit) ---
# O st.session_state é usado para persistir dados entre as interações do usuário no Streamlit
if 'historico_completo' not in st.session_state:
    st.session_state.historico_completo = collections.deque(maxlen=1000) # Capacidade maior
if 'tabela_road_interna' not in st.session_state:
    # Garante que a tabela interna seja inicializada corretamente com as dimensões
    st.session_state.tabela_road_interna = [['' for _ in range(NUM_COLUNAS_ROAD)] for _ in range(NUM_LINHAS_ROAD)]

# --- Funções Auxiliares ---

def formatar_resultado_para_exibicao(res):
    """Formata o resultado para exibição amigável."""
    if isinstance(res, tuple):
        return SIMBOLOS_EXIBICAO[f'E_{res[1]}']
    # Caso um resultado vazio ('' ) seja passado antes do histórico encher
    if res == '':
        return ''
    return SIMBOLOS_EXIBICAO[res]

def obter_cor_resultado(res):
    """Retorna a cor associada ao resultado ('Azul' ou 'Vermelho').
       Para empates, retorna a cor da 'linha' (próximo vencedor).
       Retorna None se o resultado for vazio."""
    if res == '':
        return None
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
    # Adiciona ao histórico principal do session_state
    st.session_state.historico_completo.append(resultado)
    
    # Atualiza a tabela_road_interna simulando o movimento do road
    # Move todas as células da tabela_road_interna uma posição para a esquerda
    # Isso simula o comportamento de "rolar" a tela para a esquerda quando um novo resultado entra
    for r in range(NUM_LINHAS_ROAD):
        for c in range(NUM_COLUNAS_ROAD - 1):
            st.session_state.tabela_road_interna[r][c] = st.session_state.tabela_road_interna[r][c+1]
        st.session_state.tabela_road_interna[r][NUM_COLUNAS_ROAD - 1] = '' # Limpa a última coluna

    # Adiciona o novo resultado na primeira linha da última coluna
    # Esta é a lógica simplificada para simular a entrada do novo resultado na visualização que você viu
    st.session_state.tabela_road_interna[0][NUM_COLUNAS_ROAD - 1] = resultado
    
    st.success(f"Resultado '{formatar_resultado_para_exibicao(resultado)}' adicionado ao histórico.")


# --- Funções de Análise de Padrões ---

def analisar_padroes_football_studio():
    """
    Função principal para analisar os padrões do Football Studio com base na sua hipótese.
    """
    n = len(st.session_state.historico_completo)
    
    st.subheader("Análise de Padrões")

    if n < TAMANHO_JANELA_ANALISE: # 27 resultados para preencher a road completa
        st.warning(f"Histórico muito pequeno ({n} resultados). Precisa de pelo menos {TAMANHO_JANELA_ANALISE} para uma análise completa da 'road'.")
        st.info("Continue inserindo resultados para preencher a tabela de visualização interna.")
        return

    # Extrai a janela de análise mais recente (os últimos 27 resultados)
    # Convertemos para lista para poder fatiar, pois deque não suporta fatiamento direto de todos os elementos
    janela_analise = list(st.session_state.historico_completo)[-TAMANHO_JANELA_ANALISE:]

    # 1. Análise da "cor que some" vs. "cor que aparece"
    st.markdown("---")
    st.markdown("**1. Análise da 'Cor que Some' vs. 'Cor que Aparece':**")
    
    # O resultado que "sumiu" da visualização é o elemento que estava na posição inicial do histórico
    # antes dos 27 resultados mais recentes (se o histórico já tiver pelo menos 27 resultados).
    # Se o histórico for exatamente 27, é o primeiro elemento.
    
    # Esta lógica assume que a janela de análise é o que está "visível" no road.
    # Quando um novo resultado é adicionado, o mais antigo da janela (o primeiro) "some".
    # O resultado que "apareceu" é o mais recente.
    
    cor_que_sumiu_da_visualizacao = obter_cor_resultado(janela_analise[0]) # Primeiro elemento da janela
    cor_que_apareceu_agora = obter_cor_resultado(janela_analise[-1]) # Último elemento da janela (o mais recente)

    st.markdown(f"**Cor que 'sumiu' da visualização (mais antigo da janela):** {cor_que_sumiu_da_visualizacao}")
    st.markdown(f"**Cor que 'apareceu' (resultado mais recente na janela):** {cor_que_apareceu_agora}")

    if cor_que_sumiu_da_visualizacao == cor_que_apareceu_agora:
        st.success(f"**PADRÃO DETECTADO:** A cor ({cor_que_apareceu_agora}) que 'sumiu' do início da visualização é a mesma do resultado mais recente. (Sua Regra de Cores)")
    else:
        st.info(f"**OBS:** A cor que 'sumiu' ({cor_que_sumiu_da_visualizacao}) é diferente da cor que 'apareceu' ({cor_que_apareceu_agora}).")

    # 2. Análise de Sequências na "Última Linha" (os 9 resultados mais recentes)
    st.markdown("---")
    st.markdown("**2. Análise de Sequências na 'Última Linha' (últimos 9 resultados):**")
    
    # Pega os últimos 9 resultados do histórico completo, que representam a "última linha" visual.
    ultimos_9_resultados = list(st.session_state.historico_completo)[-TAMANHO_LINHA_OBSERVACAO:]
    
    sequencias_detectadas = []
    contagem_sequencia = 0
    cor_atual_sequencia = None
    
    if len(ultimos_9_resultados) >= 3:
        for i in range(len(ultimos_9_resultados)):
            current_res_color = obter_cor_resultado(ultimos_9_resultados[i])
            
            if current_res_color is None: # Ignora células vazias se houver (não deve acontecer com histórico cheio)
                continue

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
        # Para isso, olhamos para o resultado imediatamente posterior à "última linha" (se houver)
        # Que seria o resultado mais recente no histórico completo
        if len(st.session_state.historico_completo) > TAMANHO_LINHA_OBSERVACAO:
            ultima_sequencia_cor = sequencias_detectadas[-1].split('x ')[1].split(' ')[0] # Extrai a cor
            cor_do_proximo_resultado_apos_sequencia = obter_cor_resultado(st.session_state.historico_completo[-1])
            
            if cor_do_proximo_resultado_apos_sequencia == ultima_sequencia_cor:
                st.info(f"   **Inferência:** Após a última sequência de {ultima_sequencia_cor}, a cor parece estar 'seguindo'.")
            else:
                st.info(f"   **Inferência:** Após a última sequência de {ultima_sequencia_cor}, a cor parece estar 'virando' para {cor_do_proximo_resultado_apos_sequencia}.")
            # A lógica para "alternando" seria mais complexa, exigiria analisar 2 ou 3 resultados futuros da sequência.
            # Se você tiver uma regra específica para "alternando", me diga.
    else:
        st.info("Nenhuma sequência de 3 ou mais cores seguidas detectada na 'Última Linha' (últimos 9 resultados).")

    # 3. Análise de Comportamento dos Empates ("E")
    st.markdown("---")
    st.markdown("**3. Análise de Comportamento dos Empates (E):**")
    
    empates_na_janela = []
    # Coleta empates da janela de análise de 27 resultados
    for i, res in enumerate(janela_analise):
        if isinstance(res, tuple) and res[0] == 'E':
            empates_na_janela.append((i, res)) # (indice_na_janela, resultado_empate)

    if not empates_na_janela:
        st.info("Nenhum empate na janela de análise atual.")
    else:
        st.markdown(f"Empates encontrados na janela de análise ({len(empates_na_janela)}):")
        for idx, empate_res in empates_na_janela:
            cor_seguinte_empate = obter_cor_resultado(empate_res)
            st.text(f"  - Posição relativa na janela {idx} (0=mais antigo): Empate seguido de {cor_seguinte_empate} ({formatar_resultado_para_exibicao(empate_res)})")

        if len(empates_na_janela) >= 2:
            ultimo_empate_cor = obter_cor_resultado(empates_na_janela[-1][1])
            penultimo_empate_cor = obter_cor_resultado(empates_na_janela[-2][1])
            
            if ultimo_empate_cor == penultimo_empate_cor:
                st.success(f"**PADRÃO:** Dois últimos empates seguidos de mesma cor ({ultimo_empate_cor}).")
            else:
                st.info(f"**OBS:** Dois últimos empates seguidos de cores alternadas ({penultimo_empate_cor} -> {ultimo_empate_cor}).")

        # Regra específica "os 2 que estão colados viraram azul e os 2 vermelho viraram azul e o outro azul"
        # Esta é uma regra que você precisa formalizar com mais exemplos ou uma sequência exata.
        # Por exemplo, se significa uma sequência específica de (E_V, E_V, E_C, E_C, E_C) ou similar,
        # poderíamos buscar essa sub-sequência na 'janela_analise'.
        st.markdown("\n_Para a regra complexa de empates ('os 2 que estão colados viraram azul...'), por favor, forneça a sequência exata de resultados (E C/E V) que a caracteriza e a previsão associada._")
        
    st.markdown("---")


# --- Interface Streamlit Principal ---

st.set_page_config(layout="wide", page_title="Analisador de Padrões Football Studio")

st.title("⚽ Analisador de Padrões Football Studio")
st.markdown("Insira os resultados e veja a análise baseada nas suas observações.")

# Colunas para entrada de dados
col1, col2 = st.columns(2)

with col1:
    st.subheader("Inserir Novo Resultado")
    entrada_usuario = st.text_input(
        "Digite o próximo resultado:",
        placeholder="Ex: C, V, E C, E V",
        key="input_resultado" # Adicionado key para gerenciar o estado do input
    )

    if st.button("Adicionar Resultado", key="btn_add_resultado"):
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
            
            # Limpa o campo de entrada após adicionar o resultado
            st.session_state.input_resultado = ""
            st.rerun() # Força uma nova execução para atualizar a interface
        else:
            st.warning("Por favor, digite um resultado.")

with col2:
    st.subheader("Ações")
    if st.button("Analisar Padrões", key="btn_analisar"):
        analisar_padroes_football_studio()

    if st.button("Mostrar Histórico Completo", key="btn_mostrar_historico"):
        if st.session_state.historico_completo:
            st.write("### Histórico Completo de Resultados:")
            historico_formatado = [formatar_resultado_para_exibicao(res) for res in st.session_state.historico_completo]
            # Exibe em colunas para melhor visualização se for muito longo
            st.write(" ".join(historico_formatado)) # Simplesmente junta tudo para visualização
            # Ou para uma exibição mais estruturada:
            # st.code(historico_formatado) # Exibe como código
        else:
            st.info("Histórico vazio. Adicione alguns resultados primeiro.")
    
    if st.button("Limpar Histórico", key="btn_limpar_historico"):
        st.session_state.historico_completo = collections.deque(maxlen=1000)
        st.session_state.tabela_road_interna = [['' for _ in range(NUM_COLUNAS_ROAD)] for _ in range(NUM_LINHAS_ROAD)]
        st.success("Histórico e tabela interna limpos.")
        st.rerun() # Reinicia o app para refletir a limpeza


# Exibir o estado atual do histórico na sidebar
st.sidebar.subheader(f"Total de Resultados no Histórico: {len(st.session_state.historico_completo)}")
if len(st.session_state.historico_completo) > 0:
    st.sidebar.markdown("Últimos resultados adicionados:")
    # Mostrar apenas os últimos 10 para não lotar a sidebar
    for res in list(st.session_state.historico_completo)[-10:]:
        st.sidebar.text(formatar_resultado_para_exibicao(res))

# Opcional: Exibir a tabela road interna (apenas para debug/visualização da lógica)
# st.markdown("### Visualização Interna do Road (para debug):")
# for linha in st.session_state.tabela_road_interna:
#    st.text(" ".join([formatar_resultado_para_exibicao(celula).ljust(15) for celula in linha]))
