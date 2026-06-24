import pandas as pd
import numpy as np
import io
import locale
import warnings

warnings.filterwarnings('ignore')

# ==============================================================================
# 1. HIGIENIZAÇÃO E INGESTÃO DE MATRIZES
# ==============================================================================
def obter_idioma_codificacao():
    try:
        idioma, codificacao = locale.getdefaultlocale()
        return idioma or 'pt_BR', codificacao or 'utf-8'
    except Exception: 
        return 'pt_BR', 'utf-8'

def limpar_textos_anomalos(df):
    """Varredura profunda para erradicar anomalias de formatação."""
    map_erros = {
        '&a0': 'ão', '&A0': 'ÃO', '&atilde;': 'ã', '&ccedil;': 'ç', 
        '&eacute;': 'é', '&iacute;': 'í', '\r': ' ', '\n': ' ', '&nbsp;': ' '
    }
    for col in df.select_dtypes(include=['object', 'string']).columns:
        df[col] = df[col].apply(lambda x: x if pd.isna(x) else str(x).strip())
        for erro, correcao in map_erros.items():
            df[col] = df[col].str.replace(erro, correcao, regex=False)
        df[col] = df[col].str.replace(r'\s+', ' ', regex=True)
    return df

def extrair_base_real(arquivo_bytes, nome_arquivo):
    """Ingestão heurística blindada com 5 camadas de descodificação."""
    _, cod_os = obter_idioma_codificacao()
    tentativas = [cod_os, 'utf-8', 'utf-8-sig', 'latin1', 'cp1252', 'iso-8859-1']
    
    try:
        if nome_arquivo.endswith(('.csv', '.txt')):
            df = None
            for cod in tentativas:
                try:
                    arquivo_bytes.seek(0)
                    df = pd.read_csv(arquivo_bytes, sep=None, engine='python', encoding=cod)
                    break
                except: 
                    continue
            
            if df is None: 
                return None, "Falha de Descodificação CSV."
                
            df = df.dropna(how='all').dropna(how='all', axis=1)
            return limpar_textos_anomalos(df), nome_arquivo
            
        elif nome_arquivo.endswith(('.xls', '.xlsx')):
            arquivo_bytes.seek(0)
            xls = pd.ExcelFile(arquivo_bytes)
            melhor_df, score_max = None, -1
            aba_vencedora = ""
            
            for aba in xls.sheet_names:
                df_temp = pd.read_excel(xls, sheet_name=aba).dropna(how='all').dropna(how='all', axis=1)
                score = df_temp.shape[0] * df_temp.shape[1]
                if score > score_max: 
                    score_max = score
                    melhor_df = df_temp
                    aba_vencedora = aba
                    
            return limpar_textos_anomalos(melhor_df), f"{nome_arquivo} [{aba_vencedora}]"
        else:
            return None, "Formato não suportado."
    except Exception as e: 
        return None, f"Erro Crítico de Ingestão: {e}"

# ==============================================================================
# 2. OTIMIZAÇÃO E BLINDAGEM DE TIPOS (Fim do Vírus 1970-01-01 e Somas de IDs)
# ==============================================================================
def otimizar_tipos_dados(df):
    """Protege datas e garante que IDs nunca sejam somados pela Inteligência."""
    df = df.copy()
    palavras_data = ['DATA', 'DATE', 'HORA', 'TIME', 'CRIACAO', 'VENCIMENTO', 'NASCIMENTO']
    palavras_id = ['ID', 'CEP', 'CÓDIGO', 'CODE', 'CPF', 'CNPJ', 'TELEFONE', 'SKU']
    
    for col in df.columns:
        col_str = str(col).upper()
        
        # Blindagem 1: Datas (Cura definitiva do formato Serial do Excel)
        if any(p in col_str for p in palavras_data):
            try:
                temp_s = df[col].dropna()
                if pd.api.types.is_numeric_dtype(temp_s) or (temp_s.astype(str).str.replace('.','', regex=False).str.isnumeric().all()):
                    temp = pd.to_datetime(df[col].astype(float), unit='D', origin='1899-12-30', errors='coerce')
                else:
                    temp = pd.to_datetime(df[col], errors='coerce')
                
                if temp.isna().sum() < (len(df) * 0.4): 
                    df[col] = temp.dt.date
            except: pass
            continue
            
        # Blindagem 2: Identificadores (Sempre forçados para texto)
        if any(p in col_str for p in palavras_id):
            df[col] = df[col].astype(str).replace(['nan', 'NaN', 'None'], 'N/A')
            continue
            
        # Blindagem 3: Conversão Numérica Agressiva
        if df[col].dtype == 'object':
            temp = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce')
            if temp.notna().sum() > (len(df) * 0.1): 
                df[col] = temp
        else:
            try: 
                df[col] = pd.to_numeric(df[col])
            except: pass
            
    return df

# ==============================================================================
# 3. MOTORES MATEMÁTICOS E ESTATÍSTICOS
# ==============================================================================
def calcular_pareto(df, colunas_cat, colunas_num):
    """Identifica a regra 80/20 de dominância na base."""
    if not colunas_cat or not colunas_num: return {}
    pareto_data = {}
    
    for cat in colunas_cat[:3]:
        for num in colunas_num[:2]:
            agrupado = df.groupby(cat)[num].sum().sort_values(ascending=False)
            if agrupado.empty or agrupado.sum() == 0: continue
            
            acumulado = agrupado.cumsum() / agrupado.sum()
            elite = acumulado[acumulado <= 0.8].index.tolist()
            if not elite: elite = [agrupado.index[0]]
            
            pareto_data[f"{cat}_vs_{num}"] = {
                "lideres_80_20": elite[:5],
                "concentracao_topo": float(agrupado.iloc[0] / agrupado.sum() * 100)
            }
    return pareto_data

def processar_estatistica_avancada(df, colunas_num):
    """Avalia o coeficiente de Assimetria (Skewness) para achar gargalos invisíveis."""
    report = {}
    for col in colunas_num:
        serie = df[col].dropna()
        if len(serie) < 5: continue
        
        soma = float(serie.sum())
        media = float(serie.mean())
        std = float(serie.std())
        skew = float(serie.skew())
        
        report[col] = {
            "soma_total": soma, 
            "media_aritmetica": media, 
            "desvio_padrao": std, 
            "assimetria": skew,
            "diagnostico_assimetria": "Altamente concentrado em pequenos" if skew > 1 else "Concentrado em gigantes" if skew < -1 else "Distribuição normalizada"
        }
    return report

def identificar_outliers_detalhado(df, colunas_num):
    """Isola falhas operacionais usando o cálculo IQR (Intervalo Interquartil)."""
    relatorio = {}
    for col in colunas_num:
        serie = df[col].dropna()
        if len(serie) < 5: continue
        
        Q1, Q3 = serie.quantile(0.25), serie.quantile(0.75)
        IQR = Q3 - Q1
        if IQR == 0: continue
        
        limite_inf, limite_sup = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR
        outliers = df[(df[col] < limite_inf) | (df[col] > limite_sup)]
        
        if not outliers.empty: 
            relatorio[col] = {
                'qtd': len(outliers), 
                'percentual': round((len(outliers) / len(df)) * 100, 2), 
                'lim_inf': limite_inf, 
                'lim_sup': limite_sup, 
                'amostra': outliers.head(100)
            }
    return relatorio

# ==============================================================================
# 4. MOTOR DE FUSÃO E EXPORTAÇÃO
# ==============================================================================
def mesclar_bases_inteligente(df_base, df_novo, nome_novo):
    """IA de Fusão com Alerta de Segurança Vermelho para Matrizes Incompatíveis."""
    col_base, col_novo = set(df_base.columns), set(df_novo.columns)
    intersecao = list(col_base.intersection(col_novo))
    taxa_similaridade = len(intersecao) / max(len(col_base), 1)
    
    try:
        if taxa_similaridade > 0.6:
            df_final = pd.concat([df_base, df_novo], ignore_index=True)
            return df_final.drop_duplicates(), ("success", f"🔗 Matriz Concatenada: '{nome_novo}' anexado à base.")
        elif len(intersecao) > 0:
            for col in intersecao:
                df_base[col] = df_base[col].astype(str)
                df_novo[col] = df_novo[col].astype(str)
            df_final = pd.merge(df_base, df_novo, on=intersecao, how='outer')
            return df_final.drop_duplicates(), ("info", f"🧩 Matrizes Cruzadas usando chaves em comum: {intersecao}.")
        else:
            return df_base, ("error", f"🚫 Operação Rejeitada: '{nome_novo}' não possui relação (chaves em comum) com a base principal.")
    except Exception as e: 
        return df_base, ("error", f"⚠️ Falha Crítica de Fusão: {e}")

def gerar_excel_limpo(df):
    """Exportador de Alta Fidelidade visual."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Matriz_ANA')
        worksheet = writer.sheets['Matriz_ANA']
        
        formato_cab = writer.book.add_format({
            'bold': True, 'bg_color': '#0f172a', 'font_color': 'white', 
            'border': 1, 'text_wrap': True, 'valign': 'vcenter'
        })
        
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, formato_cab)
            worksheet.set_column(col_num, col_num, max(len(str(value)) + 2, 12))
            
        worksheet.freeze_panes(1, 0)
    return output.getvalue()