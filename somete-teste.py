import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
from scipy import stats
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import xgboost as xgb
from datetime import datetime
import time
import io # Mantido no topo do script para escopo global

# --- Configuração Premium da Página ---
st.set_page_config(
    page_title="Bac Bo Intelligence Pro", 
    layout="wide", 
    initial_sidebar_state="expanded",
    page_icon="🎯"
)
st.title("🎯 BAC BO PREDICTOR PRO - Sistema de Alta Precisão")

# Estilos CSS Premium
st.markdown("""
<style>
    /* Design Premium */
    .stApp {
        background: linear-gradient(135deg, #1a1b28, #26273b);
        color: #ffffff;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .stAlert {
        padding: 1.8rem;
        border-radius: 15px;
        margin-bottom: 1.8rem;
        font-size: 1.4em;
        font-weight: bold;
        text-align: center;
        box-shadow: 0 6px 12px rgba(0,0,0,0.25);
        border: 2px solid;
    }
    .alert-success { 
        background: linear-gradient(135deg, #28a745, #1e7e34);
        border-color: #0c5420;
    }
    .alert-danger { 
        background: linear-gradient(135deg, #dc3545, #bd2130);
        border-color: #8a1621;
    }
    .alert-warning { 
        background: linear-gradient(135deg, #ffc107, #e0a800);
        border-color: #b38700;
        color: #000 !important;
    }
    .stMetric {
        background: rgba(46, 47, 58, 0.7);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        border: 1px solid #3d4050;
    }
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    /* Botões premium */
    .stButton>button {
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.3s;
        border: none;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    /* Títulos */
    h1, h2, h3, h4, h5, h6 {
        color: #f0f0f0;
        text-shadow: 0 1px 3px rgba(0,0,0,0.3);
    }
    /* Abas */
    .stTabs [aria-selected="true"] {
        font-weight: bold;
        background: rgba(46, 47, 58, 0.9) !important;
    }
    .css-1aumxhk {
        background-color: rgba(38, 39, 48, 0.8) !important;
    }
    /* Melhorias na tabela */
    .dataframe th {
        background-color: #2a2b3c !important;
        color: white !important;
    }
    .dataframe tr:nth-child(even) {
        background-color: #2a2b3c !important;
    }
    .dataframe tr:nth-child(odd) {
        background-color: #1e1f2c !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Inicialização do Session State ---
if 'historico_dados' not in st.session_state:
    st.session_state.historico_dados = []
    st.session_state.padroes_detectados = []
    st.session_state.modelos_treinados = False
    st.session_state.ultimo_treinamento = None
    st.session_state.backtest_results = {}
    st.session_state.estrategia_atual = "Simples" # Isso não está sendo usado de forma ativa no código
    st.session_state.historico_recomendacoes = []

# --- Constantes Avançadas ---
JANELAS_ANALISE = [
    {"nome": "Ultra-curto", "tamanho": 8, "peso": 1.5},
    {"nome": "Curto", "tamanho": 20, "peso": 1.8},
    {"nome": "Médio", "tamanho": 50, "peso": 1.2},
    {"nome": "Longo", "tamanho": 100, "peso": 0.9}
]

# Definindo modelos com random_state para reprodutibilidade
MODELOS = {
    "XGBoost": xgb.XGBClassifier(n_estimators=150, learning_rate=0.12, max_depth=5, random_state=42, use_label_encoder=False, eval_metric='mlogloss'),
    "Random Forest": RandomForestClassifier(n_estimators=100, max_depth=7, random_state=42),
    "Neural Network": MLPClassifier(hidden_layer_sizes=(25, 15), activation='relu', max_iter=2000, random_state=42),
    "Gradient Boosting": GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42)
}

# --- Funções de Análise Avançada ---

def calcular_probabilidade_condicional(df, evento, condicao):
    try:
        total_condicao = len(df.query(condicao))
        if total_condicao == 0:
            return 0.0
        # Use query para combinar ambas as condições
        total_ambos = len(df.query(f"{condicao} and ({evento})"))
        return (total_ambos / total_condicao) * 100
    except Exception as e:
        # st.error(f"Erro em calcular_probabilidade_condicional: {e}") # Evitar muitos erros na UI
        return 0.0

def previsao_avancada(X_train, y_train, X_pred):
    probas = []
    
    # Padronizar os dados de entrada
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_pred_scaled = scaler.transform(X_pred) # Transformar X_pred com o mesmo scaler

    for nome, modelo in MODELOS.items():
        try:
            modelo.fit(X_train_scaled, y_train) # Usar dados padronizados
            proba = modelo.predict_proba(X_pred_scaled)[0] # Usar dados padronizados
            probas.append(proba)
        except Exception as e:
            # st.error(f"Erro no modelo {nome}: {str(e)}") # Evitar muitos erros na UI
            pass # Apenas ignorar o modelo que falhou
    
    if probas:
        # Calcular a média das probabilidades apenas se houver modelos bem-sucedidos
        return np.mean(probas, axis=0)
    
    # Retorno neutro se nenhum modelo conseguir prever
    # Mapear 'P', 'B', 'T' para índices 0, 1, 2 para predição
    # Como o resultado da predição pode variar a ordem das classes, 
    # é crucial garantir que a ordem das classes seja consistente.
    # MLPClassifier, RandomForestClassifier, GradientBoostingClassifier, XGBClassifier
    # geralmente retornam as probabilidades na ordem das classes aprendidas (ex: ['B', 'P', 'T'] ou ['P', 'B', 'T']).
    # Para simplicidade, assumindo que a ordem 'P', 'B', 'T' é consistente para o objetivo.
    # Ou poderíamos mapear explicitamente: classes = modelo.classes_
    # Para o propósito deste código, onde o foco é a soma dos dados, a ordem não é tão crítica,
    # mas em um sistema real, seria bom garantir.
    return np.array([0.33, 0.33, 0.34]) 

def detectar_padroes_avancados(df_completo):
    todos_padroes = []
    
    if df_completo.empty:
        return todos_padroes

    # Converter resultados para numérico para tendências se necessário para cálculos
    # Esta parte do código assume que 'Player' e 'Banker' são números.
    # A coluna 'Resultado' é categórica ('P', 'B', 'T').
    
    for janela in JANELAS_ANALISE:
        tamanho = janela["tamanho"]
        peso_janela = janela["peso"]
        
        if len(df_completo) < tamanho:
            continue
            
        df_analise = df_completo.tail(tamanho).copy()
        n = len(df_analise)
        x = np.arange(n) # Usar índices relativos à janela
        
        # 1. Análise de Tendência Avançada (somas)
        try:
            # Assegurar que 'Player' e 'Banker' são numéricos
            player_series = pd.to_numeric(df_analise["Player"], errors='coerce').dropna()
            banker_series = pd.to_numeric(df_analise["Banker"], errors='coerce').dropna()

            if len(player_series) > 1 and len(banker_series) > 1:
                player_slope, _, _, _, _ = stats.linregress(np.arange(len(player_series)), player_series)
                player_trend_strength = min(2.5, abs(player_slope) * 8)
                
                banker_slope, _, _, _, _ = stats.linregress(np.arange(len(banker_series)), banker_series)
                banker_trend_strength = min(2.5, abs(banker_slope) * 8)
                
                if player_slope > 0.15:
                    todos_padroes.append({
                        "tipo": "TENDÊNCIA", 
                        "lado": "P", 
                        "desc": f"Soma Player em alta forte ({player_slope:.2f}) - Janela {janela['nome']}",
                        "peso": player_trend_strength * peso_janela,
                        "janela": janela["nome"]
                    })
                elif player_slope < -0.15:
                    todos_padroes.append({
                        "tipo": "TENDÊNCIA", 
                        "lado": "P", 
                        "desc": f"Soma Player em queda forte ({player_slope:.2f}) - Janela {janela['nome']}",
                        "peso": player_trend_strength * peso_janela,
                        "janela": janela["nome"]
                    })
                    
                if banker_slope > 0.15:
                    todos_padroes.append({
                        "tipo": "TENDÊNCIA", 
                        "lado": "B", 
                        "desc": f"Soma Banker em alta forte ({banker_slope:.2f}) - Janela {janela['nome']}",
                        "peso": banker_trend_strength * peso_janela,
                        "janela": janela["nome"]
                    })
                elif banker_slope < -0.15:
                    todos_padroes.append({
                        "tipo": "TENDÊNCIA", 
                        "lado": "B", 
                        "desc": f"Soma Banker em queda forte ({banker_slope:.2f}) - Janela {janela['nome']}",
                        "peso": banker_trend_strength * peso_janela,
                        "janela": janela["nome"]
                    })
        except Exception as e:
            # st.warning(f"Erro na análise de tendência: {e}")
            pass
        
        # 2. Análise de Repetição Estatística
        player_counts = Counter(df_analise["Player"])
        banker_counts = Counter(df_analise["Banker"])
        
        for soma, count in player_counts.items():
            if count >= max(4, n*0.35):  # Limiares mais rigorosos
                peso = min(3.0, count * 0.6) * peso_janela
                todos_padroes.append({
                    "tipo": "REPETIÇÃO", 
                    "lado": "P", 
                    "desc": f"Soma Player {soma} repetida {count}/{n} vezes ({count/n*100:.1f}%)",
                    "peso": peso,
                    "janela": janela["nome"]
                })
                
        for soma, count in banker_counts.items():
            if count >= max(4, n*0.35):
                peso = min(3.0, count * 0.6) * peso_janela
                todos_padroes.append({
                    "tipo": "REPETIÇÃO", 
                    "lado": "B", 
                    "desc": f"Soma Banker {soma} repetida {count}/{n} vezes ({count/n*100:.1f}%)",
                    "peso": peso,
                    "janela": janela["nome"]
                })
        
        # 3. Previsão com Modelo Híbrido
        # Certifique-se de que há dados suficientes para X e y
        if n > 15: # Mínimo de dados para treino + teste + 1 para predição
            try:
                # O StandardScaler espera um array 2D
                X = df_analise[["Player", "Banker"]].values[:-1]
                y = df_analise["Resultado"].values[1:]
                X_pred = df_analise[["Player", "Banker"]].values[-1].reshape(1, -1)
                
                # Certifique-se que X_train e y_train não estão vazios
                if len(X) > 0 and len(y) > 0:
                    probas = previsao_avancada(X, y, X_pred)
                    
                    # Garantir que probas tem o formato esperado e não é apenas um placeholder
                    if probas is not None and len(probas) == 3: # P, B, T
                        max_idx = np.argmax(probas)
                        confianca = probas[max_idx]
                        
                        # Mapear o índice de volta para 'P', 'B', 'T'
                        # A ordem das classes aprendidas pelo modelo pode variar, 
                        # é mais seguro obtê-las diretamente do modelo, mas como é um ensemble
                        # e o objetivo é a maior probabilidade, podemos assumir a ordem padrão.
                        # Para ser mais robusto, você precisaria de um mapeamento de classe consistente.
                        lado_map = {0: 'P', 1: 'B', 2: 'T'} 
                        # Isso pressupõe que as classes P, B, T serão mapeadas para 0, 1, 2
                        # por padrão pelos classificadores. Isso é uma suposição que pode quebrar.
                        # Uma forma mais segura seria treinar um modelo para obter as classes.
                        # Exemplo: RandomForestClassifier().fit(X,y).classes_
                        
                        # Para este problema, vamos assumir que a ordem é 'B', 'P', 'T' ou 'P', 'B', 'T'
                        # A ordem da classe depende de como o modelo as "vê".
                        # Por exemplo, se y contém ['P', 'B', 'T'], as classes podem ser ordenadas alfabeticamente.
                        # Uma maneira de verificar isso é: `MODELOS["XGBoost"].fit(X,y).classes_`
                        # Se as classes do primeiro modelo forem {'B', 'P', 'T'}, então 0=B, 1=P, 2=T.
                        # Para simplificar aqui, vamos tentar mapear com base na suposição do problema de Bac Bo.
                        
                        # Uma solução mais robusta:
                        # Treinar um modelo temporário para obter a ordem das classes.
                        temp_model = RandomForestClassifier(random_state=42)
                        temp_model.fit(X,y)
                        classes_ordenadas = temp_model.classes_ # Ex: array(['B', 'P', 'T'], dtype=object)
                        lado_pred = classes_ordenadas[max_idx]

                        if confianca > 0.62:  # Limiar mais alto para confiança
                            todos_padroes.append({
                                "tipo": "PREVISÃO", 
                                "lado": lado_pred, 
                                "desc": f"Modelo preditivo ({janela['nome']}) sugere {lado_pred} (conf: {confianca*100:.1f}%)",
                                "peso": min(4.0, confianca * 6) * peso_janela,
                                "janela": janela["nome"]
                            })
            except Exception as e:
                # st.error(f"Erro na previsão: {str(e)}") # Evitar muitos erros na UI
                pass
    
    # 4. Análise de Probabilidade Condicional (histórico completo)
    if len(df_completo) > 100:
        try:
            # Player ganha quando soma > 8
            # `df_completo['Resultado'] == 'P'` garante que estamos pegando a coluna de resultados.
            # `Player > 8` é a condição de Player soma.
            prob = calcular_probabilidade_condicional(
                df_completo, 
                "Resultado == 'P'", 
                "Player > 8"
            )
            if prob > 58:  # Limiar mais alto
                todos_padroes.append({
                    "tipo": "PROBABILIDADE", 
                    "lado": "P", 
                    "desc": f"Prob histórica: Player ganha {prob:.1f}% quando soma Player > 8",
                    "peso": min(3.0, (prob-50)/8),
                    "janela": "Histórico"
                })
                
            # Banker ganha quando soma > 9
            prob = calcular_probabilidade_condicional(
                df_completo, 
                "Resultado == 'B'", 
                "Banker > 9"
            )
            if prob > 58:
                todos_padroes.append({
                    "tipo": "PROBABILIDADE", 
                    "lado": "B", 
                    "desc": f"Prob histórica: Banker ganha {prob:.1f}% quando soma Banker > 9",
                    "peso": min(3.0, (prob-50)/8),
                    "janela": "Histórico"
                })
                
            # Tie quando diferença pequena
            prob = calcular_probabilidade_condicional(
                df_completo, 
                "Resultado == 'T'", 
                "abs(Player - Banker) <= 1"
            )
            if prob > 15:  # Probabilidade natural ~10%
                todos_padroes.append({
                    "tipo": "PROBABILIDADE", 
                    "lado": "T", 
                    "desc": f"Prob histórica: Tie ocorre em {prob:.1f}% quando diferença de soma <=1",
                    "peso": min(3.0, prob/6),
                    "janela": "Histórico"
                })
        except Exception as e:
            # st.warning(f"Erro na análise de probabilidade condicional: {e}")
            pass
    
    # 5. Padrões de Sequência
    resultados = df_completo["Resultado"].values
    if len(resultados) > 10:
        # Detecção de sequências P-B-P-B
        padrao_alternancia_pb = 0
        for i in range(3, len(resultados)): # Começa de 3 para ter 4 elementos (i-3, i-2, i-1, i)
            if (resultados[i-3] == 'P' and resultados[i-2] == 'B' and 
                resultados[i-1] == 'P' and resultados[i] == 'B'):
                padrao_alternancia_pb += 1
        
        if padrao_alternancia_pb >= 2:
            todos_padroes.append({
                "tipo": "SEQUÊNCIA", 
                "lado": "AMBOS", 
                "desc": f"Padrão de alternância P-B-P-B detectado {padrao_alternancia_pb} vezes",
                "peso": 2.5,
                "janela": "Longo"
            })
            
        # Detecção de sequências B-P-B-P
        padrao_alternancia_bp = 0
        for i in range(3, len(resultados)): 
            if (resultados[i-3] == 'B' and resultados[i-2] == 'P' and 
                resultados[i-1] == 'B' and resultados[i] == 'P'):
                padrao_alternancia_bp += 1
        
        if padrao_alternancia_bp >= 2:
            todos_padroes.append({
                "tipo": "SEQUÊNCIA", 
                "lado": "AMBOS", 
                "desc": f"Padrão de alternância B-P-B-P detectado {padrao_alternancia_bp} vezes",
                "peso": 2.5,
                "janela": "Longo"
            })

        # Detecção de sequências de 3 ou mais iguais
        for res_type in ['P', 'B', 'T']:
            streak_count = 0
            max_res_streak = 0
            for i in range(len(resultados)):
                if resultados[i] == res_type:
                    streak_count += 1
                else:
                    max_res_streak = max(max_res_streak, streak_count)
                    streak_count = 0
            max_res_streak = max(max_res_streak, streak_count) # Para o caso da sequência ir até o final

            if max_res_streak >= 3:
                todos_padroes.append({
                    "tipo": "SEQUÊNCIA", 
                    "lado": res_type, 
                    "desc": f"Maior sequência de {res_type}s: {max_res_streak}",
                    "peso": min(3.0, max_res_streak * 0.8), # Peso baseado no tamanho da sequência
                    "janela": "Histórico"
                })

    return todos_padroes

def gerar_recomendacao(padroes):
    if not padroes:
        return "AGUARDAR", 15, "Sem padrões detectados. Aguarde mais dados.", "warning"
    
    # Agrupar padrões por lado
    scores = {"P": 0.0, "B": 0.0, "T": 0.0}
    detalhes = {"P": [], "B": [], "T": []}
    
    for padrao in padroes:
        lado = padrao["lado"]
        peso = padrao["peso"]
        
        if lado in scores:
            scores[lado] += peso
            detalhes[lado].append(f"{padrao['tipo']}: {padrao['desc']}")
        elif lado == "AMBOS":
            scores["P"] += peso/2
            scores["B"] += peso/2
            detalhes["P"].append(f"{padrao['tipo']}: {padrao['desc']}")
            detalhes["B"].append(f"{padrao['tipo']}: {padrao['desc']}")
    
    # Calcular confiança
    total_score = sum(scores.values())
    if total_score == 0:
        return "AGUARDAR", 10, "Padrões sem força significativa (total score 0).", "warning"
    
    # Normalizar scores para obter confianças percentuais
    confiancas = {lado: round((score / total_score) * 100) for lado, score in scores.items()}
    
    # Determinar recomendação com limiares mais altos
    max_lado = max(scores, key=scores.get)
    max_score = scores[max_lado]
    
    # Limiares de decisão mais rigorosos
    if max_score > 6.0:
        acao = f"APOSTAR FORTE NO {'PLAYER' if max_lado == 'P' else 'BANKER' if max_lado == 'B' else 'TIE'}"
        tipo = "success"
        conf = confiancas[max_lado]
        detalhe = f"**Convergência poderosa de padrões** ({max_score:.1f} pontos):\n- " + "\n- ".join(detalhes[max_lado])
    elif max_score > 4.0:
        acao = f"APOSTAR NO {'PLAYER' if max_lado == 'P' else 'BANKER' if max_lado == 'B' else 'TIE'}"
        tipo = "success"
        conf = confiancas[max_lado]
        detalhe = f"**Forte convergência de padrões** ({max_score:.1f} pontos):\n- " + "\n- ".join(detalhes[max_lado])
    elif max_score > 2.5:
        acao = f"CONSIDERAR {'PLAYER' if max_lado == 'P' else 'BANKER' if max_lado == 'B' else 'TIE'}"
        tipo = "warning"
        conf = confiancas[max_lado]
        detalhe = f"**Sinal moderado** ({max_score:.1f} pontos):\n- " + "\n- ".join(detalhes[max_lado])
    else:
        acao = "AGUARDAR"
        tipo = "warning"
        # Quando 'AGUARDAR', a confiança pode ser a maior confiança entre os lados, ou uma confiança baixa padrão
        # Aqui, vamos usar a confiança do lado com maior score, mesmo que não seja uma aposta forte.
        # Ou poderíamos setar um valor baixo fixo para "AGUARDAR"
        conf = confiancas[max_lado] if total_score > 0 else 10 # Retorna a confiança do lado mais forte, ou 10 se não houver scores
        detalhe = "**Sinais fracos ou conflitantes**. Aguarde confirmação:\n- " + "\n- ".join(
            [f"{lado}: {score:.1f} pts ({confiancas[lado]}%)" for lado, score in scores.items()])
    
    return acao, conf, detalhe, tipo

def estrategia_simples(df):
    """Estratégia básica baseada no último resultado"""
    if df.empty:
        return None
    ultimo = df.iloc[-1]
    if ultimo['Player'] > ultimo['Banker']:
        return 'P'
    elif ultimo['Banker'] > ultimo['Player']:
        return 'B'
    else:
        return 'T'

def estrategia_ia(df):
    """Estratégia avançada usando detecção de padrões"""
    if df.empty:
        return None
    padroes = detectar_padroes_avancados(df)
    acao, _, _, _ = gerar_recomendacao(padroes)
    
    if "PLAYER" in acao:
        return 'P'
    elif "BANKER" in acao:
        return 'B'
    elif "TIE" in acao:
        return 'T'
    else:
        return None  # Não aposta quando é AGUARDAR

def executar_backtesting(df, estrategia_func, tamanho_janela=20):
    resultados = []
    saldo = 1000 # Saldo inicial
    apostas_totais = 0
    vitorias = 0
    detalhes = []
    acoes = []
    
    # Validar se há dados suficientes para começar o backtesting
    if len(df) <= tamanho_janela:
        return {
            "saldo_final": saldo,
            "win_rate": 0,
            "retorno_percent": 0,
            "detalhes": [],
            "acoes": []
        }

    for i in range(tamanho_janela, len(df)):
        dados_janela = df.iloc[i-tamanho_janela:i]
        recomendacao = estrategia_func(dados_janela)
        
        resultado_real = df.iloc[i]['Resultado']
        
        if recomendacao is None:  # Quando estratégia recomenda AGUARDAR
            detalhes.append({
                "jogo": i,
                "aposta": "Nenhuma",
                "resultado": resultado_real,
                "ganho": 0,
                "saldo": saldo
            })
            continue
            
        apostas_totais += 1
        
        # Simulação de aposta com tamanho fixo para simplificar
        valor_aposta = 50 # Exemplo de valor fixo
        
        if recomendacao == resultado_real:
            # Recompensa para P/B é 1x, para T é 8x (aproximadamente, no Bac Bo é ~1.25:1 e 25:1)
            # Para simplificar a simulação de ganho/perda de banca:
            ganho = valor_aposta * 1 # Ganha o valor apostado
            if recomendacao == 'T':
                ganho = valor_aposta * 8 # Ganho maior para Tie
            saldo += ganho
            vitorias += 1
            
            detalhes.append({
                "jogo": i,
                "aposta": recomendacao,
                "resultado": resultado_real,
                "ganho": ganho,
                "saldo": saldo,
                "status": "Vitória"
            })
        else:
            perda = valor_aposta # Perde o valor apostado
            saldo -= perda
            
            detalhes.append({
                "jogo": i,
                "aposta": recomendacao,
                "resultado": resultado_real,
                "ganho": -perda,
                "saldo": saldo,
                "status": "Derrota"
            })
        acoes.append(recomendacao)
    
    # Calcular métricas
    win_rate = (vitorias / apostas_totais) * 100 if apostas_totais else 0
    retorno = (saldo - 1000) / 1000 * 100 if saldo != 1000 else 0 # Retorno em relação ao saldo inicial
    
    return {
        "saldo_final": saldo,
        "win_rate": win_rate,
        "retorno_percent": retorno,
        "detalhes": detalhes,
        "acoes": acoes
    }

# --- Interface Premium ---
st.markdown("""
<div style="text-align:center; margin-bottom:30px;">
    <h1 style="color:#ffc107; font-size:2.5em;">BAC BO PREDICTOR PRO</h1>
    <p style="font-size:1.2em;">Sistema de análise preditiva com algoritmos de Machine Learning</p>
</div>
""", unsafe_allow_html=True)

# --- Entrada de Dados Premium ---
with st.expander("🎮 ENTRADA DE DADOS", expanded=True):
    col1, col2, col3, col4 = st.columns([1,1,1,0.8])
    with col1:
        player_soma = st.number_input("Soma Player (2-12)", min_value=2, max_value=12, value=7, key="player_soma_input")
    with col2:
        banker_soma = st.number_input("Soma Banker (2-12)", min_value=2, max_value=12, value=7, key="banker_soma_input")
    with col3:
        resultado_op = st.selectbox("Resultado", ['P', 'B', 'T'], key="resultado_select")
    with col4:
        st.write("") # Espaço para alinhar o botão
        st.write("") 
        if st.button("➕ ADICIONAR", use_container_width=True, type="primary"):
            st.session_state.historico_dados.append((player_soma, banker_soma, resultado_op))
            st.rerun()

# --- Histórico com Visualização Premium ---
st.subheader("📜 HISTÓRICO DE RESULTADOS")
if st.session_state.historico_dados:
    df_historico = pd.DataFrame(
        st.session_state.historico_dados,
        columns=["Player", "Banker", "Resultado"]
    )
    
    # Adicionar colunas analíticas
    df_historico['Diferenca'] = abs(df_historico['Player'] - df_historico['Banker'])
    df_historico['SomaTotal'] = df_historico['Player'] + df_historico['Banker']
    df_historico['Vencedor'] = np.where(
        df_historico['Resultado'] == 'P', 'Player',
        np.where(df_historico['Resultado'] == 'B', 'Banker', 'Tie')
    )
    
    # Função para aplicar estilo à coluna 'Resultado'
    def color_resultado(val):
        color = 'blue' if val == 'P' else ('red' if val == 'B' else 'green')
        return f'color: {color}; font-weight: bold'

    st.dataframe(df_historico.tail(20).style
        .background_gradient(subset=['Player', 'Banker'], cmap='YlGnBu')
        .applymap(color_resultado, subset=['Resultado']), # Aplica a função de estilo
        use_container_width=True, height=450) # Altura ajustada
    
    # Controles do histórico
    col_hist1, col_hist2, col_hist3 = st.columns([1,1,2])
    with col_hist1:
        if st.button("🗑️ REMOVER ÚLTIMO", use_container_width=True):
            if st.session_state.historico_dados:
                st.session_state.historico_dados.pop()
                st.rerun()
    with col_hist2:
        if st.button("🧹 LIMPAR TUDO", use_container_width=True, type="secondary"):
            st.session_state.historico_dados = []
            st.session_state.padroes_detectados = []
            st.session_state.backtest_results = {} # Limpar também os resultados de backtesting
            st.rerun()
    with col_hist3:
        last = df_historico.iloc[-1] if not df_historico.empty else ""
        st.info(f"🔢 Total: {len(df_historico)} | Último: {last.get('Player', '')}-{last.get('Banker', '')}-{last.get('Resultado', '')}")
else:
    st.warning("⚠️ Nenhum dado no histórico. Adicione resultados para iniciar a análise.")

# --- Entrada em Massa Premium ---
with st.expander("📥 IMPORTAR DADOS EM MASSA", expanded=False):
    historico_input_mass = st.text_area("Cole múltiplas linhas (1 linha = Player,Banker,Resultado)", height=150)
    
    if st.button("🚀 PROCESSAR DADOS", use_container_width=True, type="primary"):
        linhas = [linha.strip() for linha in historico_input_mass.split("\n") if linha.strip()]
        novos_dados = []
        erros = []
        
        for i, linha in enumerate(linhas, 1):
            try:
                partes = [p.strip() for p in linha.split(',')]
                if len(partes) < 3:
                    erros.append(f"Linha {i}: Formato inválido (esperado: Player,Banker,Resultado)")
                    continue
                
                p = int(partes[0])
                b = int(partes[1])
                r = partes[2].upper()
                
                # Coletar todos os erros antes de adicionar
                linha_erros = []
                if not (2 <= p <= 12):
                    linha_erros.append(f"Soma Player inválida ({p}) - deve ser 2-12")
                if not (2 <= b <= 12):
                    linha_erros.append(f"Soma Banker inválida ({b}) - deve ser 2-12")
                if r not in ['P', 'B', 'T']:
                    linha_erros.append(f"Resultado inválido ({r}) - deve ser P, B ou T")
                
                if linha_erros:
                    erros.append(f"Linha {i}: {' | '.join(linha_erros)}")
                else:
                    novos_dados.append((p, b, r))
            except ValueError:
                erros.append(f"Linha {i}: Valores numéricos inválidos")
            except Exception as e:
                erros.append(f"Linha {i}: Erro de processamento - {str(e)}")
        
        # Exibir erros e adicionar dados válidos
        if novos_dados:
            st.session_state.historico_dados.extend(novos_dados)
            st.success(f"✅ {len(novos_dados)} novos registros adicionados com sucesso!")
            st.rerun() # Força a atualização da interface com os novos dados
        
        if erros:
            st.error("❌ Erros encontrados durante o processamento em massa:")
            for erro in erros:
                st.markdown(f"- {erro}") # Exibir erros com markdown para melhor formatação
    
    # Exportar dados
    if st.session_state.historico_dados:
        df_export = pd.DataFrame(st.session_state.historico_dados, 
                                 columns=["Player", "Banker", "Resultado"])
        # Converte o DataFrame para CSV e depois para bytes
        csv_bytes = df_export.to_csv(index=False).encode('utf-8')
        
        st.download_button(
            label="💾 EXPORTAR DADOS (CSV)",
            data=csv_bytes, # Passa os bytes do CSV
            file_name=f"bacbo_historico_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", # Nome do arquivo com timestamp
            mime='text/csv',
            use_container_width=True
        )

# --- ANÁLISE E RECOMENDAÇÃO ---
if st.session_state.historico_dados:
    df_analise = pd.DataFrame(
        st.session_state.historico_dados,
        columns=["Player", "Banker", "Resultado"]
    )
    
    # Adicionar colunas analíticas necessárias para a detecção de padrões se ainda não estiverem lá
    # (Elas são adicionadas no dataframe de exibição, mas a detecção de padrões usa df_completo)
    if 'Diferenca' not in df_analise.columns:
        df_analise['Diferenca'] = abs(df_analise['Player'] - df_analise['Banker'])
    if 'SomaTotal' not in df_analise.columns:
        df_analise['SomaTotal'] = df_analise['Player'] + df_analise['Banker']
    if 'Vencedor' not in df_analise.columns:
        df_analise['Vencedor'] = np.where(
            df_analise['Resultado'] == 'P', 'Player',
            np.where(df_analise['Resultado'] == 'B', 'Banker', 'Tie')
        )

    # Verifica se há dados suficientes para análise mais profunda
    if len(df_analise) >= JANELAS_ANALISE[0]['tamanho']: # Pelo menos o tamanho da menor janela
        with st.spinner("🔍 Analisando padrões e executando modelos de IA..."):
            # Detecta padrões
            st.session_state.padroes_detectados = detectar_padroes_avancados(df_analise)
            
            # Gera recomendação
            acao, conf, detalhe, tipo = gerar_recomendacao(st.session_state.padroes_detectados)
            
            # Armazena histórico de recomendações
            # Adiciona apenas se for uma nova recomendação para evitar duplicação em reruns
            if not st.session_state.historico_recomendacoes or \
               st.session_state.historico_recomendacoes[-1]['acao'] != acao or \
               st.session_state.historico_recomendacoes[-1]['confianca'] != conf: # Check simples para evitar duplicação excessiva
                st.session_state.historico_recomendacoes.append({
                    "timestamp": datetime.now(),
                    "acao": acao,
                    "confianca": conf,
                    "tipo": tipo,
                    "detalhes": detalhe
                })
            
            # Exibe recomendação
            st.markdown(f"<div class='stAlert alert-{tipo}'>{acao} (Confiança: {conf}%)</div>", unsafe_allow_html=True)
            st.markdown(f"**Detalhes da Análise:**\n{detalhe}")
            
            # Atualiza o estado dos modelos (apenas para exibição)
            st.session_state.modelos_treinados = True
            st.session_state.ultimo_treinamento = datetime.now()
            
            # Exibir padrões detectados
            st.subheader("📊 Padrões Detectados")
            if st.session_state.padroes_detectados:
                df_padroes = pd.DataFrame(st.session_state.padroes_detectados)
                # Selecionar e ordenar colunas para melhor visualização
                display_cols = ['tipo', 'lado', 'desc', 'peso', 'janela']
                st.dataframe(df_padroes[display_cols].sort_values(by='peso', ascending=False), use_container_width=True)
            else:
                st.warning("Nenhum padrão significativo detectado")
                
            # --- Visualizações Gráficas ---
            tab1, tab2, tab3 = st.tabs(["📈 Tendências", "📊 Distribuição", "🧠 Modelos"])
            
            with tab1:
                if not df_analise.empty:
                    # Gráfico de tendência das somas
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=df_analise.index, 
                        y=df_analise['Player'], 
                        name='Player',
                        line=dict(color='#1f77b4', width=3)
                    ))
                    fig.add_trace(go.Scatter(
                        x=df_analise.index, 
                        y=df_analise['Banker'], 
                        name='Banker',
                        line=dict(color='#ff7f0e', width=3)
                    ))
                    fig.update_layout(
                        title='Evolução das Somas Player vs Banker',
                        xaxis_title='Rodada',
                        yaxis_title='Soma',
                        template='plotly_dark',
                        height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Gráfico de diferenças
                    fig = px.bar(
                        df_analise, 
                        x=df_analise.index, 
                        y='Diferenca',
                        title='Diferença entre Player e Banker',
                        color='Resultado',
                        color_discrete_map={'P': '#1f77b4', 'B': '#ff7f0e', 'T': '#2ca02c'}
                    )
                    fig.update_layout(
                        template='plotly_dark',
                        height=350
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Adicione dados para visualizar tendências.")
                
            with tab2:
                if not df_analise.empty:
                    # Histograma comparativo
                    fig = px.histogram(
                        df_analise, 
                        x=['Player', 'Banker'], 
                        nbins=11, 
                        barmode='overlay',
                        opacity=0.7,
                        color_discrete_sequence=['#1f77b4', '#ff7f0e']
                    )
                    fig.update_layout(
                        title='Distribuição das Somas',
                        xaxis_title='Soma',
                        yaxis_title='Frequência',
                        template='plotly_dark',
                        height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Gráfico de pizza de resultados
                    result_counts = df_analise['Resultado'].value_counts()
                    fig = px.pie(
                        result_counts, 
                        values=result_counts.values, 
                        names=result_counts.index,
                        title='Distribuição de Resultados',
                        color=result_counts.index,
                        color_discrete_map={'P': '#1f77b4', 'B': '#ff7f0e', 'T': '#2ca02c'}
                    )
                    fig.update_layout(
                        template='plotly_dark',
                        height=350
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Adicione dados para visualizar distribuições.")
                
            with tab3:
                # Treinar e avaliar modelos
                # Mínimo de dados para split: train_size + test_size >= 2
                # Um mínimo de 50 registros é razoável para Machine Learning básico
                if len(df_analise) > 50: 
                    st.subheader("Desempenho dos Modelos")
                    
                    # Garantir que as colunas 'Player' e 'Banker' são numéricas
                    X = df_analise[["Player", "Banker"]].apply(pd.to_numeric, errors='coerce').dropna()
                    y = df_analise["Resultado"].loc[X.index] # Alinha y com X após dropna

                    if len(X) > 0 and len(y) > 0:
                        # Dividir dados de forma estratificada para manter proporções de classes
                        X_train, X_test, y_train, y_test = train_test_split(
                            X, y, test_size=0.2, random_state=42, stratify=y
                        )
                        
                        # Padronização dos dados (Importante para redes neurais)
                        scaler = StandardScaler()
                        X_train_scaled = scaler.fit_transform(X_train)
                        X_test_scaled = scaler.transform(X_test)

                        resultados_modelos = []
                        for nome, modelo in MODELOS.items():
                            try:
                                start_time = time.time()
                                modelo.fit(X_train_scaled, y_train) # Treina com dados escalados
                                y_pred = modelo.predict(X_test_scaled) # Prediz com dados escalados
                                acc = accuracy_score(y_test, y_pred)
                                resultados_modelos.append({
                                    "Modelo": nome,
                                    "Acurácia": f"{acc*100:.1f}%",
                                    "Tempo (s)": f"{time.time()-start_time:.3f}",
                                    "Status": "✅" if acc >= 0.6 else "⚠️" if acc >= 0.5 else "❌" # Múltiplos status
                                })
                            except Exception as e:
                                resultados_modelos.append({
                                    "Modelo": nome,
                                    "Acurácia": "ERRO",
                                    "Tempo (s)": "N/A",
                                    "Status": "❌"
                                })
                        
                        df_resultados = pd.DataFrame(resultados_modelos)
                        st.dataframe(df_resultados, use_container_width=True)
                        
                        # Relatório de classificação
                        if st.checkbox("Mostrar relatório detalhado do melhor modelo"):
                            # Filtra modelos que não deram erro para encontrar o melhor
                            df_valid_results = df_resultados[df_resultados['Acurácia'] != 'ERRO'].copy()
                            if not df_valid_results.empty:
                                df_valid_results['Acuracia_Num'] = df_valid_results['Acurácia'].apply(lambda x: float(x.strip('%')))
                                melhor_modelo_row = df_valid_results.loc[df_valid_results['Acuracia_Num'].idxmax()]
                                modelo_nome = melhor_modelo_row['Modelo']
                                modelo_obj = MODELOS[modelo_nome]
                                
                                # Retreinar o melhor modelo (não estritamente necessário se já treinado, mas garante)
                                modelo_obj.fit(X_train_scaled, y_train) 
                                y_pred = modelo_obj.predict(X_test_scaled)
                                
                                st.subheader(f"Relatório de Classificação - {modelo_nome}")
                                report = classification_report(y_test, y_pred, output_dict=True, zero_division=0) # zero_division para evitar warning
                                df_report = pd.DataFrame(report).transpose()
                                st.dataframe(df_report.style.highlight_max(axis=0, color='#2a8c55'))
                            else:
                                st.warning("Nenhum modelo treinado com sucesso para gerar relatório.")
                        
                        # Informação sobre atualização
                        if st.session_state.ultimo_treinamento:
                            st.caption(f"Último treinamento: {st.session_state.ultimo_treinamento.strftime('%d/%m/%Y %H:%M:%S')}")
                    else:
                        st.warning("Dados numéricos insuficientes após limpeza para treinar modelos.")
                else:
                    st.warning("Dados insuficientes para treinar modelos (mínimo 50 registros recomendados).")
            
            # --- Backtesting ---
            st.subheader("🧪 Teste de Estratégia")
            col_strat, col_size, col_run = st.columns([2, 1, 1])
            with col_strat:
                estrategia_selecionada = st.selectbox( # Renomeado para evitar conflito com 'estrategia' em outro lugar
                    "Selecione a Estratégia", 
                    ["Simples (Último Resultado)", "IA (Recomendação Inteligente)"],
                    index=0
                )
            with col_size:
                tamanho_janela_bt = st.selectbox("Janela de Análise", [20, 30, 50, 100], index=0, key="backtest_window_size")
            with col_run:
                st.write("")
                if st.button("🔁 Executar Backtesting", use_container_width=True):
                    # O backtesting precisa de mais dados para ser significativo
                    if len(df_analise) >= 100: # Mínimo 100 jogos para backtesting
                        with st.spinner("Executando simulação histórica..."):
                            # Seleciona estratégia
                            if "Simples" in estrategia_selecionada:
                                resultados = executar_backtesting(df_analise, estrategia_simples, tamanho_janela_bt)
                            else:
                                resultados = executar_backtesting(df_analise, estrategia_ia, tamanho_janela_bt)
                            
                            st.session_state.backtest_results = resultados
                            
                            # Exibir resultados
                            col1_bt, col2_bt, col3_bt = st.columns(3)
                            col1_bt.metric("Saldo Final", f"R${resultados['saldo_final']:,.2f}", 
                                        delta=f"{resultados['saldo_final']-1000:,.2f}")
                            col2_bt.metric("Win Rate", f"{resultados['win_rate']:.1f}%")
                            col3_bt.metric("Retorno", f"{resultados['retorno_percent']:.1f}%")
                            
                            # Gráfico de evolução do saldo
                            df_evolucao = pd.DataFrame(resultados['detalhes'])
                            if not df_evolucao.empty:
                                fig_bt = px.line(
                                    df_evolucao, 
                                    x='jogo', 
                                    y='saldo', 
                                    title='Evolução do Saldo no Backtesting',
                                    markers=True
                                )
                                fig_bt.update_layout(
                                    xaxis_title='Rodada',
                                    yaxis_title='Saldo (R$)',
                                    template='plotly_dark'
                                )
                                st.plotly_chart(fig_bt, use_container_width=True)
                            else:
                                st.info("Nenhum detalhe de backtesting para exibir. Verifique a janela de análise e a quantidade de dados.")
                            
                            # Análise de acertos
                            st.subheader("Análise de Desempenho")
                            if resultados['acoes']:
                                acoes_counts = pd.Series(resultados['acoes']).value_counts()
                                fig_acoes = px.bar(
                                    acoes_counts, 
                                    x=acoes_counts.index, 
                                    y=acoes_counts.values,
                                    title='Distribuição de Apostas Realizadas',
                                    labels={'x': 'Aposta', 'y': 'Quantidade'},
                                    color=acoes_counts.index,
                                    color_discrete_map={'P': '#1f77b4', 'B': '#ff7f0e', 'T': '#2ca02c'}
                                )
                                fig_acoes.update_layout(template='plotly_dark', showlegend=False)
                                st.plotly_chart(fig_acoes, use_container_width=True)
                            else:
                                st.info("Nenhuma aposta realizada durante o backtesting com a estratégia selecionada.")
                    else:
                        st.warning(f"Necessário mínimo de 100 registros para backtesting. Você tem apenas {len(df_analise)}.")
            
            # Exibir resultados de backtesting se existirem
            if st.session_state.backtest_results and st.session_state.backtest_results['saldo_final'] != 1000: # Mostra se houve execução de fato
                st.info(f"Último backtesting ({estrategia_selecionada}): "
                        f"Saldo Final R${st.session_state.backtest_results['saldo_final']:,.2f} | "
                        f"Win Rate {st.session_state.backtest_results['win_rate']:.1f}%")
            else:
                st.info("Execute o backtesting para ver os resultados aqui.")
            
            # --- Histórico de Recomendações ---
            st.subheader("🕒 Histórico de Recomendações")
            if st.session_state.historico_recomendacoes:
                # Cria uma cópia para evitar SettingWithCopyWarning
                df_recomendacoes = pd.DataFrame(st.session_state.historico_recomendacoes).copy()
                df_recomendacoes['timestamp'] = df_recomendacoes['timestamp'].dt.strftime('%H:%M:%S') # Formatar para melhor visualização
                df_recomendacoes = df_recomendacoes.sort_values('timestamp', ascending=False)
                # Ocultar a coluna 'detalhes' por padrão, ou limitar a exibição
                st.dataframe(df_recomendacoes[['timestamp', 'acao', 'confianca', 'tipo']].head(10), use_container_width=True)
            else:
                st.info("Nenhuma recomendação registrada ainda")
    else:
        st.info(f"Adicione mais dados para ativar a análise preditiva (mínimo de {JANELAS_ANALISE[0]['tamanho']} registros). Você tem apenas {len(df_analise)}.")
else:
    st.info("ℹ️ Adicione dados para ativar a análise preditiva")

# --- Rodapé ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #aaa; font-size: 0.9em; padding: 20px;">
    BAC BO PREDICTOR PRO v2.0 | Sistema de Análise Preditiva | 
    Desenvolvido com Streamlit e Machine Learning | © 2023
</div>
""", unsafe_allow_html=True)
