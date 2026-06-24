import pandas as pd
import json
import re
import sys
import time
from google import genai

def _gerar_consciencia_matematica(df, col_num_uteis, col_cat):
    """NÚCLEO ESTATÍSTICO AVANÇADO"""
    insights = []
    insights.append(f"VOLUMETRIA: Base operando com {df.shape[0]} registros e {df.shape[1]} colunas.")
    try:
        if 'core.data_engine' in sys.modules:
            from core.data_engine import calcular_pareto, processar_estatistica_avancada, identificar_outliers_detalhado
        else:
            from data_engine import calcular_pareto, processar_estatistica_avancada, identificar_outliers_detalhado
            
        outliers_dict = identificar_outliers_detalhado(df, col_num_uteis)
        if outliers_dict:
            for col, dados in outliers_dict.items():
                insights.append(f"ANOMALIA DE OUTLIER [{col}]: {dados['qtd']} linhas afetadas ({dados['percentual']}% da base). Teto seguro: {dados['lim_inf']:,.2f} até {dados['lim_sup']:,.2f}.")
        
        estatisticas = processar_estatistica_avancada(df, col_num_uteis)
        if estatisticas:
            for col, dados in estatisticas.items():
                insights.append(f"MÉTRICA AVANÇADA [{col}]: Soma Total={dados['soma_total']:,.2f} | Média Geral={dados['media_aritmetica']:,.2f} | Distribuição={dados['diagnostico_assimetria']}.")
                
        pareto_dict = calcular_pareto(df, col_cat, col_num_uteis)
        if pareto_dict:
            for chave, dados in pareto_dict.items():
                insights.append(f"PARETO CRUCIAL [{chave.replace('_vs_', ' por ')}]: A elite concentra-se em: {dados['lideres_80_20']}. Topo representa {dados['concentracao_topo']:.1f}%.")
                
    except Exception as e:
        insights.append(f"AVISO DE SISTEMA: Motores analíticos inacessíveis ({str(e)}). Executando mapeamento básico.")
        for num in col_num_uteis[:3]:
            soma = df[num].sum()
            insights.append(f"MÉTRICA [{num}]: Total acumulado = {soma:,.2f}")
    return " || ".join(insights)

def ativar_cerebro_ana(api_key, df, historico, pergunta_atual, nome_chefe):
    """
    Cérebro ANA com Proteção de Insights e Desativação de Sirene de Risco.
    """
    client = genai.Client(api_key=api_key)
    
    col_num_todas = df.select_dtypes(include=['number']).columns.tolist()
    palavras_proibidas_num = ['ID', 'CEP', 'CÓDIGO', 'CODE', 'CPF', 'CNPJ', 'SKU', 'TELEFONE']
    col_num_uteis = [c for c in col_num_todas if not any(x in str(c).upper() for x in palavras_proibidas_num)]
    if not col_num_uteis: col_num_uteis = col_num_todas 
    
    palavras_proibidas_cat = ['DATA', 'DATE', 'HORA', 'TIME', 'CRIACAO', 'VENCIMENTO', 'NASCIMENTO']
    col_cat = [c for c in df.columns if c not in col_num_todas and not pd.api.types.is_datetime64_any_dtype(df[c]) and not any(x in str(c).upper() for x in palavras_proibidas_cat)]
    
    consciencia_matematica = _gerar_consciencia_matematica(df, col_num_uteis, col_cat)
    contexto_conversa = "\n".join([f"{m['role'].upper()}: {m['texto']}" for m in historico[-6:]])
    
    if not nome_chefe or nome_chefe.strip() == "" or nome_chefe.strip() == "Prezado(a)":
        nome_chefe = "Prezado(a)"
        regra_tratamento = "Dirija-se ao usuário como 'Prezado(a)' mantendo um tom profissional, respeitoso e analítico."
    else:
        regra_tratamento = f"NUNCA utilize saudações robóticas. Fale diretamente com {nome_chefe} com um tom executivo, imponente e direto."
    
    prompt_base = f"""VOCÊ É A ANA: Uma Inteligência Artificial de Dados Ultra-Avançada, Altamente Adaptável e Estratégica.
SEU COMANDANTE É: {nome_chefe}.

DIRETRIZES DE LIBERDADE E ADAPTAÇÃO (SISTEMA DESBLOQUEADO):
1. ADAPTABILIDADE ABSOLUTA: Se o usuário pedir "sem painel tático", "sem introdução" ou "apenas gráficos", você DEVE deixar 'saudacao_tática', 'veredito_operacional', 'justificativa_risco' e 'recomendacao_acao' EXATAMENTE VAZIOS (""). Além disso, o 'nivel_risco' DEVE ser estritamente "N/A" para desligar a sirene de alerta.
2. PROTEÇÃO DE INSIGHTS: NUNCA apague o 'insight_estrategico' dos relatórios visuais a menos que o usuário peça expressamente "sem insights" ou "gráficos crus". Se ele apenas não quiser o texto principal/introdutório, você DEVE gerar os gráficos e PREENCHER os insights de cada um deles de forma brilhante.
3. JUSTIFICATIVA DE RISCO OBRIGATÓRIA: Se você gerar o painel tático e definir um nível de risco (ALTO, MÉDIO, BAIXO), explique com dados o porquê na 'justificativa_risco'.
4. VOLUME DINÂMICO: Se o usuário pedir um número específico de gráficos (ex: 15 gráficos), gere EXATAMENTE esse número cruzando variáveis diferentes.
5. PERSONALIDADE CAMALEÔNICA: {regra_tratamento}
6. REGRA MATEMÁTICA: É ESTRITAMENTE PROIBIDO fazer somas ou médias sobre identificadores estruturais (IDs, Códigos, SKUs).

COLUNAS E DADOS DA MATRIZ:
- Métricas Reais: {col_num_uteis}
- Categorias Reais: {col_cat}

VERDADES ESTATÍSTICAS REAIS DA BASE DE DADOS (Baseie sua análise nestes fatos):
{consciencia_matematica}

ORDEM ATUAL DO COMANDANTE: "{pergunta_atual}"
MEMÓRIA DA CONVERSA:
{contexto_conversa}

RETORNE ESTRITAMENTE ESTE JSON:
{{
    "painel_executivo": {{
        "saudacao_tática": "Cumprimento. (Deixe VAZIO se ordenado sem introdução/painel)",
        "veredito_operacional": "Texto dinâmico. (Deixe VAZIO se ordenado sem introdução/painel)",
        "nivel_risco": "ALTO", // Opções exatas: ALTO, MÉDIO, BAIXO ou "N/A" se for para ocultar o painel.
        "justificativa_risco": "Explicação direta. (Deixe VAZIO se ordenado sem introdução/painel)",
        "recomendacao_acao": "Ação. (Deixe VAZIO se ordenado sem introdução/painel)"
    }},
    "relatorios_visuais": [
        {{
            "titulo": "Título Único e Estratégico",
            "insight_estrategico": "Texto profundo explicando o gráfico para o negócio. (VAZIO apenas se exigido 'sem insights').",
            "gerar_grafico": true,
            "tipo_grafico": "bar", // Opções: bar, pie, line
            "eixo_x": "Coluna categórica válida",
            "eixo_y": "Coluna numérica válida"
        }}
    ],
    "gerar_apresentacao_html": true
}}"""

    max_retries = 3
    for tentativa in range(max_retries):
        try:
            resposta = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt_base,
                config={
                    'response_mime_type': 'application/json',
                    'temperature': 0.65 
                }
            )
            
            texto_bruto = resposta.text.replace('\n', ' ').strip()
            match = re.search(r'\{.*\}', texto_bruto, re.DOTALL)
            
            if match:
                return json.loads(match.group(0))
            else:
                return json.loads(resposta.text)
                
        except Exception as e:
            if "503" in str(e) and tentativa < max_retries - 1:
                time.sleep(2.5) 
                continue
                
            return {
                "painel_executivo": {
                    "saudacao_tática": "Instabilidade Neural.",
                    "veredito_operacional": f"O sistema enfrentou uma ruptura. Detalhes: {str(e)}",
                    "nivel_risco": "CRÍTICO",
                    "justificativa_risco": "Falha de conexão com os servidores.",
                    "recomendacao_acao": "Verifique a API."
                },
                "relatorios_visuais": [],
                "gerar_apresentacao_html": False
            }