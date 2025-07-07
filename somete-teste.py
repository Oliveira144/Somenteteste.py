import collections

# --- Definições Globais ---
SIMBOLOS_EXIBICAO = {
    'C': 'C (Casa/Azul)',
    'V': 'V (Visitante/Vermelho)',
    'E_C': 'E (Empate, prox. Casa/Azul)',
    'E_V': 'E (Empate, prox. Visitante/Vermelho)'
}

# Histórico de resultados completo
historico_completo = collections.deque(maxlen=1000) # Capacidade maior para mais dados

# Representação interna da tabela visual 3x9 do Football Studio
NUM_LINHAS_ROAD = 3
NUM_COLUNAS_ROAD = 9
# Cada célula da tabela_road_interna armazenará 'C', 'V', ('E', 'C'), ('E', 'V') ou '' (vazio)
tabela_road_interna = [['' for _ in range(NUM_COLUNAS_ROAD)] for _ in range(NUM_LINHAS_ROAD)]

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
    historico_completo.append(resultado)
    print(f"Resultado '{formatar_resultado_para_exibicao(resultado)}' adicionado ao histórico.")

    # Atualiza a tabela_road_interna simulando o movimento do road
    # Guarda o resultado que vai "sumir" da primeira posição da road ANTES de mover
    resultado_sumido_da_road = None
    if tabela_road_interna[0][0] != '': # Se a célula mais antiga da road não estiver vazia
        resultado_sumido_da_road = tabela_road_interna[0][0]

    # Move todas as células da tabela_road_interna uma posição para a esquerda
    for r in range(NUM_LINHAS_ROAD):
        for c in range(NUM_COLUNAS_ROAD - 1):
            tabela_road_interna[r][c] = tabela_road_interna[r][c+1]
        tabela_road_interna[r][NUM_COLUNAS_ROAD - 1] = '' # Limpa a última coluna

    # Adiciona o novo resultado na primeira linha da última coluna (como se fosse o início de uma nova coluna)
    # A lógica real do "Big Road" de baccarat/football studio é mais complexa,
    # ela tenta continuar na mesma coluna se o vencedor for o mesmo, e só desce ou vai para a próxima coluna se mudar.
    # Para a sua observação de "última linha" e "primeira linha" (que sempre aparece no fim da primeira linha visual),
    # esta simulação de shift é a mais adequada para capturar o "que sumiu" e "o que apareceu".

    tabela_road_interna[0][NUM_COLUNAS_ROAD - 1] = resultado # Novo resultado sempre aparece no canto superior direito do road


# --- Funções de Análise de Padrões ---

def analisar_padroes_football_studio():
    """
    Função principal para analisar os padrões do Football Studio com base na sua hipótese.
    """
    n = len(historico_completo)
    
    if n < NUM_COLUNAS_ROAD * NUM_LINHAS_ROAD: # 27 resultados para preencher a road completa
        print(f"\n--- Análise de Padrões ---")
        print(f"Histórico muito pequeno ({n} resultados). Precisa de pelo menos {NUM_COLUNAS_ROAD * NUM_LINHAS_ROAD} para uma análise completa da 'road'.")
        print("Continue inserindo resultados para preencher a tabela de visualização interna.")
        return

    print(f"\n--- Análise de Padrões do Football Studio (baseada na sua observação) ---")

    # 1. Análise da "última linha" (os 9 resultados mais recentes no road visível)
    # E como a cor que "some" se relaciona com a que "aparece" (a mais recente)

    # Coleta os resultados da "última linha" do road interno (a última coluna completa)
    # A "última linha" no seu contexto visual pode ser a coluna mais à direita, ou os últimos 9 resultados do histórico
    # que comporiam a última "fila" do road se ela estivesse cheia.
    # Vamos considerar a "última linha" como os 9 resultados mais recentes que estariam visíveis na road.
    
    # O resultado mais recente é o último no historico_completo
    # O resultado que "sumiu" seria o que foi removido da primeira posição da 'tabela_road_interna' na última atualização
    # (Este foi salvo em 'resultado_sumido_da_road' na função 'adicionar_resultado_ao_historico_e_road',
    # mas precisaríamos passá-lo ou ter um histórico de "resultados que saíram" para analisá-lo retroativamente.)

    # Para a sua regra "a cor que some está aparecendo na primeira linha":
    # Precisamos de pelo menos 27 resultados (para ter uma road "cheia") + 1 (para o que sumiu)
    if len(historico_completo) > NUM_COLUNAS_ROAD * NUM_LINHAS_ROAD:
        # Pega o resultado que "sumiu" da road interna na última atualização
        # NOTA: O 'resultado_sumido_da_road' não está sendo persistido, então vamos pegar o 28º resultado mais antigo do histórico_completo
        # que seria o primeiro a ter sido "expulso" se a road tivesse 27.
        # Isso é uma aproximação se a road não foi sempre cheia desde o início.
        
        # Para ser mais preciso, se a 'tabela_road_interna' sempre simula o visual, o resultado que sumiu é o mais antigo da visualização.
        # Mas para "a cor que some da última linha" no sentido de "sai da tela", é o mais antigo do histórico atual visível na tela.
        # E "aparece na primeira linha" é o mais recente.

        # Pega os 9 resultados mais recentes (sua "última linha" visual)
        ultimos_9_resultados_visiveis = list(historico_completo)[-NUM_COLUNAS_ROAD:]
        cores_ultimos_9 = [obter_cor_resultado(res) for res in ultimos_9_resultados_visiveis]
        
        # O resultado que "sumiu" é o que está no início da janela visível (se a road tivesse "rolado" um item para fora)
        # Se consideramos a road 3x9, o que "some" é o primeiro elemento da matriz (tabela_road_interna[0][0]) antes da rolagem.
        # Para esta versão simplificada, vamos considerar a cor do resultado que "sumiria" do histórico se ele fosse limitado
        # ao tamanho da janela de análise (27).
        
        # Vamos pegar o resultado que "sumiu" da *visualização atual* do road interno
        # O resultado que "saiu" da primeira célula da tabela interna é o tabela_road_interna[0][0] antes da nova entrada.
        # Mas como a função 'adicionar_resultado_ao_historico_e_road' já moveu, o que "sumiu" é o que estava ali antes.
        
        # Melhor abordagem para "cor que some": É a cor do resultado que foi adicionado há 27 rodadas atrás.
        if len(historico_completo) >= NUM_COLUNAS_ROAD * NUM_LINHAS_ROAD: # Se tivermos pelo menos 27 resultados
            cor_que_sumiu_da_visualizacao = obter_cor_resultado(historico_completo[-(NUM_COLUNAS_ROAD * NUM_LINHAS_ROAD)])
            cor_que_apareceu_agora = obter_cor_resultado(historico_completo[-1])

            print(f"   Cor que 'sumiu' da visualização (27 rodadas atrás): {cor_que_sumiu_da_visualizacao}")
            print(f"   Cor que 'apareceu' (resultado mais recente): {cor_que_apareceu_agora}")

            if cor_que_sumiu_da_visualizacao == cor_que_apareceu_agora:
                print(f"   PADRÃO: A cor ({cor_que_apareceu_agora}) que 'sumiu' do início da visualização é a mesma do resultado mais recente.")
            else:
                print(f"   OBS: A cor que 'sumiu' ({cor_que_sumiu_da_visualizacao}) é diferente da cor que 'apareceu' ({cor_que_apareceu_agora}).")

            # Agora, a análise da "última linha" para 3 ou mais cores seguidas:
            # Pega os últimos 9 resultados da tabela_road_interna (que representa a última coluna visual)
            # ou, para simplificar, os últimos 9 resultados do histórico_completo.
            # Vamos usar os últimos 9 do historico_completo, que é mais fácil de extrair.
            
            # Pega os 9 resultados mais recentes do histórico (que seriam a "última linha" se a tabela fosse 1x9)
            # Se você se refere à última COLUNA (onde os resultados mais recentes aparecem primeiro),
            # então precisaríamos coletar as últimas células de cada linha da tabela_road_interna.
            
            # Vamos assumir que "última linha" significa os 9 resultados mais recentes do histórico para análise de sequências.
            ultimos_9_resultados = list(historico_completo)[-NUM_COLUNAS_ROAD:]
            
            # Verifica sequências de 3 ou mais cores seguidas
            contagem_sequencia = 0
            cor_atual_sequencia = None
            
            # Para analisar "3 ou mais cores seguidas" na "última linha",
            # vamos usar os 9 resultados mais recentes do histórico_completo.
            # Se a "última linha" para você é uma coluna específica da visualização 3x9,
            # precisaríamos de uma lógica para extrair essa coluna da 'tabela_road_interna'.

            sequencias_detectadas = []
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
                
                # Checa a última sequência após o loop
                if contagem_sequencia >= 3:
                    sequencias_detectadas.append(f"{contagem_sequencia}x {cor_atual_sequencia} seguida.")

            if sequencias_detectadas:
                print("\n   Análise de Sequências na 'Última Linha' (últimos 9 resultados):")
                for seq in sequencias_detectadas:
                    print(f"     - {seq}")
                
                # Informe o que está acontecendo:
                # "a cor está x está virando na primeira linha y ou está alternando entre x e y ou seguindo"
                # Isso depende do padrão exato que você vê após a sequência.
                # Precisamos de regras mais específicas para cada caso (virando, alternando, seguindo).
                # Por exemplo: "Se 3x Azul, e o próximo resultado é Vermelho, então está virando."
                #             "Se 3x Azul, e os próximos 2 são Vermelho e Azul, então está alternando."
                
                # Exemplo hipotético de "virando", "alternando" ou "seguindo"
                if len(ultimos_9_resultados) >= 4: # Pelo menos 3 para sequencia, +1 para próximo
                    # Cor da sequência detectada (última sequência)
                    if sequencias_detectadas:
                        ultima_sequencia_cor = sequencias_detectadas[-1].split('x ')[1].split(' ')[0] # Extrai a cor
                        # Cor do próximo resultado (o que viria DEPOIS da "última linha" dos 9)
                        # Este seria o (n-9)th elemento do histórico, ou o historico_completo[-(NUM_COLUNAS_ROAD + 1)]
                        # Para ser mais preciso, é o resultado mais recente do histórico.
                        cor_proximo = obter_cor_resultado(historico_completo[-1]) # O último adicionado
                        
                        if cor_proximo == ultima_sequencia_cor:
                            print(f"   Inferência: Após a sequência de {ultima_sequencia_cor}, parece que a cor está 'seguindo'.")
                        else:
                            print(f"   Inferência: Após a sequência de {ultima_sequencia_cor}, parece que a cor está 'virando' para {cor_proximo}.")
                        # Para "alternando", precisaríamos de mais de um resultado após a sequência.
                        # Ex: Se after sequence of Blue, next two are Red, Blue.
                
            else:
                print("\n   Nenhuma sequência de 3 ou mais cores seguidas detectada na 'Última Linha' (últimos 9 resultados).")

    # 2. Análise de Comportamento dos Empates ("E")
    print("\n   Análise de Comportamento dos Empates (E):")
    
    # Pega os empates na janela de análise (27 resultados)
    empates_na_janela = []
    for i, res in enumerate(janela_analise):
        if isinstance(res, tuple) and res[0] == 'E':
            empates_na_janela.append((i, res)) # (indice_na_janela, resultado_empate)

    if not empates_na_janela:
        print("   Nenhum empate na janela de análise atual.")
    else:
        print(f"   Empates encontrados na janela de análise ({len(empates_na_analise)}):")
        for idx, empate_res in empates_na_janela:
            cor_seguinte_empate = obter_cor_resultado(empate_res)
            print(f"     - Posição relativa na janela {idx}: Empate seguido de {cor_seguinte_empate} ({formatar_resultado_para_exibicao(empate_res)})")

        # Sua regra: "o último empate se auto escreve ou na mesma cor ou em cor diferente formando ou o mesmo padrão com a mesma cor ou em parcial , o empate também se escreve ... acompanhar um emapte se reescreveu em vermelho outro em azul outro vermelho depois os 2 que estão colados viraram azul e os 2 vermelho viraram azul e o outro azul"
        # Isso ainda precisa ser traduzido em regras programáveis.
        # Exemplo hipotético de regras baseadas na sua descrição:
        if len(empates_na_janela) >= 2:
            ultimo_empate_cor = obter_cor_resultado(empates_na_janela[-1][1])
            penultimo_empate_cor = obter_cor_resultado(empates_na_janela[-2][1])
            
            if ultimo_empate_cor == penultimo_empate_cor:
                print(f"   OBS: Dois últimos empates seguidos de mesma cor ({ultimo_empate_cor}).")
                # Você poderia ter uma previsão aqui
            else:
                print(f"   OBS: Dois últimos empates seguidos de cores alternadas ({penultimo_empate_cor} -> {ultimo_empate_cor}).")
                # Previsão aqui

        # Para "os 2 que estão colados viraram azul e os 2 vermelho viraram azul e o outro azul"
        # Precisamos de mais contexto:
        # 1. Isso se refere a uma sequência de empates ou de resultados C/V?
        # 2. Onde exatamente essa sequência ocorre na janela?
        # 3. Qual é a sua previsão quando isso acontece?
        
        # Exemplo de como você formalizaria:
        # Se os últimos 4 resultados foram: E_V, E_V, E_C, E_C -> "os 2 vermelhos viraram azul"
        # Então, o que acontece? Qual é a previsão?

    print("----------------------------------------------------------\n")


# --- Loop Principal ---
if __name__ == "__main__":
    print("Bem-vindo ao Analisador de Padrões do Football Studio!")
    print("Este sistema tentará identificar padrões com base nas suas observações.")
    print("--- Comandos ---")
    print("  'C': Casa (Azul)")
    print("  'V': Visitante (Vermelho)")
    print("  'E C': Empate (linha azul, próximo Casa)")
    print("  'E V': Empate (linha vermelha, próximo Visitante)")
    print("  'analisar': Executa a análise dos padrões.")
    print("  'historico': Exibe o histórico completo de resultados.")
    print("  'sair': Encerra o programa.")
    print("------------------\n")

    while True:
        entrada = input("Insira o próximo resultado ou comando: ").strip().upper()

        if entrada == 'SAIR':
            break
        elif entrada == 'ANALISAR':
            analisar_padroes_football_studio()
        elif entrada == 'HISTORICO':
            print(f"\nHistórico Completo ({len(historico_completo)} resultados):")
            # Exibe o histórico completo
            print([formatar_resultado_para_exibicao(res) for res in historico_completo])
            print("-------------------------------------------\n")
        elif entrada in ['C', 'V']:
            adicionar_resultado_ao_historico_e_road(entrada)
        elif entrada.startswith('E '):
            partes = entrada.split()
            if len(partes) == 2 and partes[0] == 'E' and partes[1] in ['C', 'V']:
                adicionar_resultado_ao_historico_e_road(('E', partes[1]))
            else:
                print("Entrada inválida para Empate. Use 'E C' ou 'E V'.")
        else:
            print("Comando ou entrada de resultado inválida. Tente novamente.")

    print("Analisador encerrado.")

