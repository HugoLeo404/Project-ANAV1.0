import streamlit as st
import pandas as pd
import plotly.express as px
import os
import time
import sys
import importlib
import pickle
import random

# ==============================================================================
# ARQUITETURA DE PERSISTÊNCIA (PASTA EXCLUSIVA DO COFRE)
# ==============================================================================
VAULT_DIR = "cofre_sessoes"
VAULT_FILE = os.path.join(VAULT_DIR, "cofre_ana_vault.pkl")

def carregar_cofre():
    if os.path.exists(VAULT_FILE):
        try:
            with open(VAULT_FILE, 'rb') as f:
                return pickle.load(f)
        except Exception:
            return {}
    return {}

def salvar_cofre(dados):
    os.makedirs(VAULT_DIR, exist_ok=True)
    with open(VAULT_FILE, 'wb') as f:
        pickle.dump(dados, f)

# ==============================================================================
# HACK CLEAN CODE: FORÇAR RECARREGAMENTO DO CORE
# ==============================================================================
for module in ['core.data_engine', 'core.ai_engine']:
    if module in sys.modules:
        importlib.reload(sys.modules[module])

try:
    from core.data_engine import extrair_base_real, otimizar_tipos_dados, identificar_outliers_detalhado, mesclar_bases_inteligente, gerar_excel_limpo
    from core.ai_engine import ativar_cerebro_ana
except ImportError as e:
    st.error(f"⚠️ ERRO CRÍTICO DE ARQUITETURA: {e}\nCertifique-se de que a pasta 'core' existe.")
    st.stop()

# ==============================================================================
# CONFIGURAÇÃO DE UI E ESTADO OPERACIONAL
# ==============================================================================
st.set_page_config(page_title="Projeto ANA - Enterprise", page_icon="📈", layout="wide", initial_sidebar_state="expanded")

if os.path.exists("assets/style.css"):
    with open("assets/style.css", "r", encoding="utf-8") as f: 
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        .ana-branding { background: linear-gradient(135deg, #1e1e2f, #0f172a); padding: 20px; border-radius: 10px; margin-bottom: 25px; border-left: 5px solid #3b82f6; }
        .titulo-ana { font-size: 2.5rem; font-weight: bold; color: #ffffff; margin: 0; }
        .subtitulo { color: #94a3b8; margin: 5px 0 0 0; font-size: 1rem; }
        .ana-message-box { background-color: #1e293b; padding: 20px; border-radius: 8px; border-left: 4px solid #3b82f6; margin-bottom: 15px; }
        .badge-alto { background-color: #ef4444; color: white; padding: 3px 8px; border-radius: 4px; font-weight: bold; }
        .badge-medio { background-color: #f59e0b; color: white; padding: 3px 8px; border-radius: 4px; font-weight: bold; }
        .badge-baixo { background-color: #10b981; color: white; padding: 3px 8px; border-radius: 4px; font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="ana-branding"><p class="titulo-ana">✨ Projeto ANA</p><p class="subtitulo">Plataforma Enterprise de BI Avançado e Inteligência Neural</p></div>', unsafe_allow_html=True)

if "mensagens" not in st.session_state: st.session_state.mensagens = []
if "cofre_conversas" not in st.session_state: st.session_state.cofre_conversas = carregar_cofre()
if "last_uploader_state" not in st.session_state: st.session_state.last_uploader_state = []
if "df_base" not in st.session_state: st.session_state.df_base = None
if "ui_msgs" not in st.session_state: st.session_state.ui_msgs = []
if "sessao_ativa" not in st.session_state: st.session_state.sessao_ativa = None
if "confirmar_sobrescrita" not in st.session_state: st.session_state.confirmar_sobrescrita = None
if "deletar_alvo" not in st.session_state: st.session_state.deletar_alvo = None

# ==============================================================================
# MODAIS FLUTUANTES (EXCLUSÃO E SOBRESCRITA)
# ==============================================================================
if hasattr(st, 'dialog'):
    @st.dialog("⚠️ Confirmar Exclusão")
    def modal_exclusao():
        st.error(f"Você está prestes a deletar permanentemente a sessão: **{st.session_state.deletar_alvo}**")
        st.markdown("Esta ação apagará a matriz, o histórico neural e os relatórios desta operação. Deseja prosseguir?")
        c1, c2 = st.columns(2)
        if c1.button("✔️ Sim, Excluir", use_container_width=True, type="primary"):
            alvo = st.session_state.deletar_alvo
            if alvo in st.session_state.cofre_conversas:
                del st.session_state.cofre_conversas[alvo]
            if st.session_state.sessao_ativa == alvo:
                st.session_state.sessao_ativa = None
                st.session_state.mensagens = []
                st.session_state.df_base = None
            salvar_cofre(st.session_state.cofre_conversas)
            st.session_state.deletar_alvo = None
            st.rerun()
        if c2.button("❌ Cancelar", use_container_width=True):
            st.session_state.deletar_alvo = None
            st.rerun()

    @st.dialog("⚠️ Substituir Arquivo")
    def modal_sobrescrita():
        alvo = st.session_state.confirmar_sobrescrita
        st.warning(f"Já existe um arquivo salvo no cofre com o nome **'{alvo}'**.")
        st.markdown("Deseja substituir o arquivo antigo por esta nova gravação?")
        c1, c2 = st.columns(2)
        if c1.button("✔️ Sim, Substituir", use_container_width=True, type="primary"):
            st.session_state.cofre_conversas[alvo] = {
                "mensagens": list(st.session_state.mensagens), 
                "df": st.session_state.df_base.copy() if st.session_state.df_base is not None else None
            }
            st.session_state.sessao_ativa = alvo
            st.session_state.confirmar_sobrescrita = None
            salvar_cofre(st.session_state.cofre_conversas)
            st.rerun()
        if c2.button("❌ Cancelar", use_container_width=True):
            st.session_state.confirmar_sobrescrita = None
            st.rerun()

    if st.session_state.deletar_alvo: modal_exclusao()
    if st.session_state.confirmar_sobrescrita: modal_sobrescrita()

# ==============================================================================
# SIDEBAR: CENTRO DE COMANDO E COFRE DE SESSÕES
# ==============================================================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/8653/8653200.png", width=70)
    st.header("Centro de Comando")
    
    nome_usuario_input = st.text_input("👤 Identificação do Operador:", value="", placeholder="Deixe vazio para 'Prezado(a)'...")
    nome_comando = nome_usuario_input.strip() if nome_usuario_input.strip() else "Prezado(a)"
    
    api_key = st.text_input("🔑 Chave API Gemini:", type="password")
    st.divider()
    
    st.markdown("### 📂 Ingestão de Dados")
    arquivos_up = st.file_uploader("Arraste bases (.csv, .xlsx):", type=['xlsx', 'csv'], accept_multiple_files=True)
    
    st.divider()
    st.subheader("🗄️ Cofre")
    
    nome_conversa = st.text_input("Nome da Sessão:", value=st.session_state.sessao_ativa if st.session_state.sessao_ativa else "")
    
    if st.button("💾 Gravar Operação", use_container_width=True):
        if nome_conversa:
            if nome_conversa in st.session_state.cofre_conversas and nome_conversa != st.session_state.sessao_ativa:
                st.session_state.confirmar_sobrescrita = nome_conversa
                st.rerun()
            else:
                st.session_state.cofre_conversas[nome_conversa] = {
                    "mensagens": list(st.session_state.mensagens), 
                    "df": st.session_state.df_base.copy() if st.session_state.df_base is not None else None
                }
                st.session_state.sessao_ativa = nome_conversa
                st.session_state.confirmar_sobrescrita = None
                salvar_cofre(st.session_state.cofre_conversas)
                st.toast(f"Sessão '{nome_conversa}' blindada no Cofre!", icon="✅")
        else:
            st.warning("Dê um nome para a sessão antes de gravar.")

    st.markdown("---")
    st.markdown("### 📜 Histórico de Sessões")
    
    if st.session_state.cofre_conversas:
        for sessao in list(st.session_state.cofre_conversas.keys()):
            marcacao_ativa = "🟢 " if st.session_state.sessao_ativa == sessao else ""
            
            with st.container(border=True):
                c_nome, c_btn, c_dots = st.columns([5, 4, 1.5], vertical_alignment="center")
                
                with c_nome:
                    st.markdown(f"**{marcacao_ativa}{sessao}**")
                
                with c_btn:
                    if st.button("📂 Abrir", key=f"load_{sessao}", use_container_width=True):
                        st.session_state.mensagens = list(st.session_state.cofre_conversas[sessao]["mensagens"])
                        st.session_state.df_base = st.session_state.cofre_conversas[sessao]["df"]
                        st.session_state.sessao_ativa = sessao
                        st.rerun()
                
                with c_dots:
                    with st.popover("⋮", use_container_width=True):
                        if st.button("🗑️ Apagar", key=f"pre_del_{sessao}", use_container_width=True):
                            st.session_state.deletar_alvo = sessao
                            st.rerun()
    else:
        st.caption("Nenhuma sessão arquivada.")

# ==============================================================================
# PIPELINE ETL AUTOMÁTICO COM LIMPEZA DE MEMÓRIA NEURAL
# ==============================================================================
estado_atual = [(f.name, f.size) for f in arquivos_up] if arquivos_up else []
if estado_atual != st.session_state.last_uploader_state:
    st.session_state.last_uploader_state = estado_atual
    st.session_state.df_base = None
    st.session_state.ui_msgs = []
    
    st.session_state.mensagens = [] 
    st.session_state.sessao_ativa = None 
    
    if arquivos_up:
        with st.spinner("Refinando matrizes..."):
            conteudos_vistos = set()
            for arquivo in arquivos_up:
                cb = arquivo.getvalue()
                if cb in conteudos_vistos: continue
                conteudos_vistos.add(cb)
                
                df_temp, n_res = extrair_base_real(arquivo, arquivo.name)
                
                if df_temp is None:
                    st.session_state.ui_msgs.append(("error", f"❌ Erro na leitura de: '{arquivo.name}'."))
                    continue
                    
                df_temp = otimizar_tipos_dados(df_temp)
                
                if st.session_state.df_base is None:
                    st.session_state.df_base = df_temp
                    st.session_state.ui_msgs.append(("success", f"✅ Matriz Alfa Estabelecida."))
                else:
                    st.session_state.df_base, msg_fusao = mesclar_bases_inteligente(st.session_state.df_base, df_temp, arquivo.name)
                    st.session_state.ui_msgs.append(msg_fusao)

for tipo, msg in st.session_state.get("ui_msgs", []):
    if tipo == "success": st.success(msg)
    elif tipo == "error": st.error(msg)
    else: st.info(msg)

# ==============================================================================
# TOP-LEVEL: BASE HIGIENIZADA E KPIs 
# ==============================================================================
if st.session_state.df_base is not None:
    df = st.session_state.df_base
    
    col_num_todas = df.select_dtypes(include=['number']).columns.tolist()
    pal_proibidas_num = ['ID', 'CEP', 'CÓDIGO', 'CODE', 'CPF', 'CNPJ', 'SKU', 'TELEFONE']
    col_num_uteis = [c for c in col_num_todas if not any(x in str(c).upper() for x in pal_proibidas_num)] or col_num_todas
    
    pal_proibidas_cat = ['DATA', 'DATE', 'HORA', 'TIME', 'CRIACAO', 'VENCIMENTO', 'NASCIMENTO']
    col_cat = [c for c in df.columns if c not in col_num_todas and not pd.api.types.is_datetime64_any_dtype(df[c]) and not any(x in str(c).upper() for x in pal_proibidas_cat)]

    outliers_dados = identificar_outliers_detalhado(df, col_num_uteis) if col_num_uteis else {}
    total_outliers = sum([dados['qtd'] for dados in outliers_dados.values()]) if outliers_dados else 0

    st.markdown("### 🗃️ Base Higienizada e Volumetria")
    
    m1, m2, m3 = st.columns(3)
    with m1: st.metric("Volume de Linhas", f"{len(df):,}")
    with m2: st.metric("Vetores (Colunas)", len(df.columns))
    with m3: st.metric("Gargalos (Outliers)", f"{total_outliers:,}", delta="Exposição" if total_outliers > 0 else "Limpa", delta_color="inverse" if total_outliers > 0 else "normal")
    
    st.dataframe(df, use_container_width=True, height=250)
    col_dl1, _ = st.columns([1, 4])
    with col_dl1:
        st.download_button("📥 Descarregar Matriz Limpa (.xlsx)", gerar_excel_limpo(df), "Matriz_Tratada.xlsx", use_container_width=True)

    st.divider()

    # ==============================================================================
    # PAINEL DE BI E AUTO-DISCOVERY
    # ==============================================================================
    st.markdown("### 🎛️ Análise Operacional e Insights Automáticos")
    tab_saude, tab_smart, tab_pro = st.tabs(["📊 Radar Automático", "📚 Matrizes Auxiliares", "🛠️ Mini Power BI"])

    with tab_saude:
        if total_outliers > 0:
            st.error(f"🚨 **Dossiê de Anomalias:** {total_outliers} anomalias encontradas.")
            for col_anomala, dados_anom in outliers_dados.items():
                with st.expander(f"🔍 Anomalia em: '{col_anomala}'"): 
                    st.dataframe(dados_anom['amostra'], use_container_width=True)
            st.divider()

        if col_num_uteis and col_cat:
            categorias_limpas = sorted([c for c in col_cat if 1 < df[c].nunique() <= 50], key=lambda x: df[x].nunique())
            
            graficos_a_renderizar = []
            for cat in categorias_limpas:
                for num in col_num_uteis:
                    agrupado = df.groupby(cat)[num].sum()
                    if agrupado.sum() == 0 or len(agrupado) <= 1: 
                        continue
                    cv = agrupado.std() / (agrupado.mean() + 1e-9)
                    if cv >= 0.15: 
                        graficos_a_renderizar.append((cat, num, cv))
            
            graficos_a_renderizar.sort(key=lambda x: x[2], reverse=True)
            graficos_a_renderizar = graficos_a_renderizar[:30]
            qtd_graficos = len(graficos_a_renderizar)
            
            if qtd_graficos > 0:
                st.success(f"🤖 O motor estatístico avaliou a base e identificou a necessidade exata de **{qtd_graficos}** visualizações estratégicas com variações relevantes.")
                cols = st.columns(2)
                for idx, (cat, num, cv) in enumerate(graficos_a_renderizar):
                    col_alvo = cols[idx % 2]
                    with col_alvo:
                        with st.container(border=True):
                            df_g = df.groupby(cat)[num].sum().reset_index()
                            
                            if idx % 2 == 0:
                                df_g = df_g.nlargest(10, num).sort_values(num, ascending=True) 
                                fig = px.bar(df_g, y=cat, x=num, orientation='h', title=f"Liderança de Valor: {num} vs {cat}", text_auto='.2s', color=num, color_continuous_scale="Blues")
                                fig.update_layout(template="plotly_dark", margin=dict(t=40, b=10, l=10, r=10), height=300)
                                st.plotly_chart(fig, use_container_width=True)
                                st.markdown(f"<div style='background-color: #1e293b; padding: 10px; border-radius: 6px; border-left: 3px solid #3b82f6;'><p style='font-size:0.85rem; color:#94a3b8; margin:0;'><b>💡 Tradução para leigos:</b> Visualiza a contribuição de <b>{num}</b> por cada <b>{cat}</b>. A discrepância visível prova a importância de focar na maior barra.</p></div>", unsafe_allow_html=True)
                            else:
                                df_g = df_g.nlargest(7, num) 
                                fig = px.pie(df_g, names=cat, values=num, hole=0.4, title=f"Monopólio Categórico: {num} em {cat}", color_discrete_sequence=px.colors.qualitative.Bold)
                                fig.update_layout(template="plotly_dark", margin=dict(t=40, b=10, l=10, r=10), height=300)
                                st.plotly_chart(fig, use_container_width=True)
                                st.markdown(f"<div style='background-color: #1e293b; padding: 10px; border-radius: 6px; border-left: 3px solid #10b981;'><p style='font-size:0.85rem; color:#94a3b8; margin:0;'><b>💡 Tradução para leigos:</b> A fatia dominante representa a dependência de mercado. Se a categoria líder cair, todo o sistema sofre.</p></div>", unsafe_allow_html=True)
            else:
                st.info("A matriz de dados é muito homogênea. Nenhuma anomalia de variação foi identificada para gerar insights automáticos.")

    with tab_smart:
        if col_num_uteis and col_cat:
            cats_validas = [c for c in col_cat if 1 < df[c].nunique() <= 100]
            if cats_validas:
                abas_tabelas = st.tabs([f"Por {c}" for c in cats_validas[:15]])
                for i, cat in enumerate(cats_validas[:15]):
                    with abas_tabelas[i]:
                        st.dataframe(df.groupby(cat)[col_num_uteis].sum().reset_index().style.format({col: "{:,.2f}" for col in col_num_uteis}), use_container_width=True, hide_index=True)

    with tab_pro:
        st.markdown("#### 🛠️ Laboratório Customizado (Mini Power BI)")
        c_x, c_y, c_f = st.columns(3)
        padrao_x = col_cat[0] if col_cat else df.columns[0]
        padrao_y = col_num_uteis[0] if col_num_uteis else df.columns[0]
        
        with c_x: ex = st.selectbox("Eixo X (Dimensão/Eixo):", df.columns, index=df.columns.get_loc(padrao_x))
        with c_y: ey = st.selectbox("Eixo Y (Métrica/Eixo):", df.columns, index=df.columns.get_loc(padrao_y))
        
        opcoes_grafico = [
            "Automático (Recomendado)", "Barras Horizontais", "Barras Verticais",
            "Linhas de Tendência", "Área", "Rosca Dinâmica", "Pizza Tradicional",
            "Dispersão Relacional", "Dispersão (Bolhas)", "Histograma",
            "Box Plot", "Violino", "Treemap", "Funil", "Mapa de Calor (Densidade)"
        ]
        
        with c_f: formato = st.selectbox("Geometria Visual:", opcoes_grafico)

        try:
            tipo_escolhido = formato
            graficos_brutos = ["Dispersão Relacional", "Dispersão (Bolhas)", "Histograma", "Box Plot", "Violino", "Mapa de Calor (Densidade)"]
            df_agrupado = df.groupby(ex)[ey].sum().reset_index() if formato not in graficos_brutos else df
            
            if formato == "Automático (Recomendado)":
                if df_agrupado[ex].nunique() <= 6: tipo_escolhido = "Rosca Dinâmica"
                elif pd.api.types.is_numeric_dtype(df_agrupado[ex]): tipo_escolhido = "Linhas de Tendência"
                else: tipo_escolhido = "Barras Horizontais"

            if tipo_escolhido == "Barras Horizontais": fig_man = px.bar(df_agrupado.nlargest(15, ey).sort_values(ey), y=ex, x=ey, orientation='h', text_auto='.2s', color=ey, color_continuous_scale="Purples", title=f"Top 15 {ey} por {ex}")
            elif tipo_escolhido == "Barras Verticais": fig_man = px.bar(df_agrupado.nlargest(15, ey), x=ex, y=ey, text_auto='.2s', color=ey, color_continuous_scale="Blues", title=f"Top 15 {ey} por {ex}")
            elif tipo_escolhido == "Linhas de Tendência": fig_man = px.line(df_agrupado.sort_values(ex), x=ex, y=ey, markers=True, title=f"Evolução/Tendência de {ey} em {ex}")
            elif tipo_escolhido == "Área": fig_man = px.area(df_agrupado.sort_values(ex), x=ex, y=ey, title=f"Volume de Área: {ey} em {ex}")
            elif tipo_escolhido == "Rosca Dinâmica": fig_man = px.pie(df_agrupado.nlargest(10, ey), names=ex, values=ey, hole=0.45, title=f"Participação: {ey} em {ex}")
            elif tipo_escolhido == "Pizza Tradicional": fig_man = px.pie(df_agrupado.nlargest(10, ey), names=ex, values=ey, title=f"Distribuição: {ey} em {ex}")
            elif tipo_escolhido == "Dispersão Relacional": fig_man = px.scatter(df, x=ex, y=ey, color=ex, opacity=0.7, title=f"Dispersão Pura: {ey} x {ex}")
            elif tipo_escolhido == "Dispersão (Bolhas)":
                size_col = ey if pd.api.types.is_numeric_dtype(df[ey]) else None
                fig_man = px.scatter(df, x=ex, y=ey, size=size_col, color=ex, opacity=0.7, title=f"Bolhas: {ey} x {ex}")
            elif tipo_escolhido == "Histograma": fig_man = px.histogram(df, x=ex, y=ey, color=ex, title=f"Distribuição/Frequência de {ey} por {ex}")
            elif tipo_escolhido == "Box Plot": fig_man = px.box(df, x=ex, y=ey, color=ex, title=f"Box Plot (Variação e Outliers): {ey} em {ex}")
            elif tipo_escolhido == "Violino": fig_man = px.violin(df, x=ex, y=ey, color=ex, box=True, title=f"Distribuição Violino de {ey} por {ex}")
            elif tipo_escolhido == "Treemap":
                df_tree = df_agrupado[df_agrupado[ey] > 0] 
                fig_man = px.treemap(df_tree.nlargest(30, ey), path=[ex], values=ey, title=f"Mapa Hierárquico (Treemap): {ey} por {ex}")
            elif tipo_escolhido == "Funil": fig_man = px.funnel(df_agrupado.nlargest(10, ey).sort_values(ey, ascending=False), x=ey, y=ex, title=f"Gráfico de Funil: {ey} por {ex}")
            elif tipo_escolhido == "Mapa de Calor (Densidade)": fig_man = px.density_heatmap(df, x=ex, y=ey, title=f"Mapa de Calor (Densidade): {ey} x {ex}", color_continuous_scale="Viridis")
                
            fig_man.update_layout(template="plotly_dark", margin=dict(t=50, b=20))
            st.plotly_chart(fig_man, use_container_width=True)
        except Exception as e: 
            st.error(f"Conflito Matemático na Geometria dos Eixos selecionados. ({e})")

# ==============================================================================
# CONSOLE NEURAL DA ANA E GERAÇÃO DE SLIDES HTML
# ==============================================================================
st.divider()
st.markdown('<p class="titulo-ana" style="font-size: 2.2rem;">🧠 Inteligência ANA</p>', unsafe_allow_html=True)

if api_key:
    for idx, msg in enumerate(st.session_state.mensagens):
        if msg["role"] == "ana":
            if msg.get('saudacao', '').strip() != "" or msg.get('texto', '').strip() != "":
                with st.chat_message("ana", avatar="✨"):
                    st.markdown(f"<div class='ana-message-box'><b>🎙️ {msg.get('saudacao', 'Diretriz:')}</b><br><br>{msg['texto']}</div>", unsafe_allow_html=True)
            
            if msg.get("graficos_dados"):
                with st.chat_message("ana", avatar="✨"):
                    for i, g_data in enumerate(msg["graficos_dados"]):
                        if g_data.get("figura"):
                            st.plotly_chart(g_data["figura"], use_container_width=True, key=f"hist_g_{idx}_{i}")
                            if g_data.get('explicacao', '').strip() != "":
                                st.markdown(f"<div style='padding: 15px; border-left: 4px solid #3b82f6; background: rgba(30, 41, 59, 0.9); margin-bottom: 25px; border-radius: 0 8px 8px 0;'><b>🔥 Insight:</b> {g_data['explicacao']}</div>", unsafe_allow_html=True)
                    if msg.get("download_html"): 
                        st.download_button("📥 Baixar Apresentação (HTML)", msg["download_html"], f"Apresentacao_ANA_V{idx}.html", "text/html", key=f"dl_{idx}")
        else:
            with st.chat_message("user", avatar="👨‍💼"):
                st.markdown(f"**{nome_comando}:** {msg['texto']}")

    # Banco de Frases Táticas Randomizadas
    placeholders_ana = [
        "Insira o Comando Tático, {nome}...",
        "Aguardando diretrizes operacionais, {nome}...",
        "Qual o próximo alvo analítico, {nome}?",
        "Sistemas prontos. Defina a estratégia, {nome}.",
        "Insira os parâmetros de extração, {nome}.",
        "Console neural ativo. Aguardando ordens, {nome}.",
        "Para onde devemos direcionar o foco, {nome}?",
        "Pronta para processamento profundo. Comande, {nome}.",
        "Defina o vetor de análise, {nome}.",
        "Qual a próxima manobra estratégica, {nome}?",
        "Aguardando instruções de varredura, {nome}.",
        "Insira a variável de interesse, {nome}.",
        "Mapeamento pronto. Informe o alvo, {nome}.",
        "Qual o foco da próxima auditoria de dados, {nome}?",
        "Aguardando parâmetros de cruzamento, {nome}.",
        "Sistemas em repouso. Aguardando ativação, {nome}.",
        "Estabeleça as prioridades de análise, {nome}.",
        "Insira a diretriz de mineração, {nome}.",
        "Pronta para desfragmentar novos dados. Comande, {nome}.",
        "Qual o próximo quadrante a ser investigado, {nome}?",
        "Defina o escopo da próxima operação, {nome}.",
        "Aguardando coordenadas para análise preditiva, {nome}.",
        "Insira o protocolo de contingência, {nome}.",
        "Qual métrica devemos isolar agora, {nome}?",
        "Sistemas de inteligência aguardando input, {nome}.",
        "Informe o alvo da próxima prospecção, {nome}.",
        "Aguardando o próximo comando executivo, {nome}.",
        "Defina a pauta da próxima extração neural, {nome}.",
        "Qual o objetivo da próxima varredura tática, {nome}?",
        "Insira os parâmetros de inteligência, {nome}."
    ]
    
    placeholder_atual = random.choice(placeholders_ana).format(nome=nome_comando)

    if pergunta := st.chat_input(placeholder_atual):
        st.session_state.mensagens.append({"role": "user", "texto": pergunta})
        if st.session_state.sessao_ativa:
            st.session_state.cofre_conversas[st.session_state.sessao_ativa]["mensagens"] = list(st.session_state.mensagens)
            salvar_cofre(st.session_state.cofre_conversas)
        st.rerun()

    if st.session_state.mensagens and st.session_state.mensagens[-1]["role"] == "user":
        if st.session_state.df_base is None:
            st.error("Ação Abortada: A matriz de dados ainda não foi inserida no sistema.")
            st.session_state.mensagens.pop()
            st.stop()
            
        with st.chat_message("ana", avatar="✨"):
            with st.spinner("Compilando Apresentação Executiva em Tempo Real..."):
                try:
                    pergunta_atual = st.session_state.mensagens[-1]["texto"]
                    r_json = ativar_cerebro_ana(api_key, st.session_state.df_base, st.session_state.mensagens, pergunta_atual, nome_comando)

                    painel = r_json.get("painel_executivo", {})
                    saudacao = painel.get("saudacao_tática", "")
                    
                    veredito_bruto = painel.get("veredito_operacional", "")
                    veredito = veredito_bruto.replace('\n', '<br>') if veredito_bruto else ""
                    
                    risco = str(painel.get("nivel_risco", "N/A")).upper()
                    justificativa_risco = painel.get("justificativa_risco", "").replace('\n', '<br>')
                    acao = painel.get("recomendacao_acao", "")
                    
                    relatorios = r_json.get("relatorios_visuais", [])
                    gerar_html = r_json.get("gerar_apresentacao_html", False)
                    
                    badge_risco = f"<span class='badge-baixo'>{risco}</span>"
                    if risco in ["ALTO", "CRÍTICO"]: badge_risco = f"<span class='badge-alto'>{risco}</span>"
                    elif risco == "MÉDIO": badge_risco = f"<span class='badge-medio'>{risco}</span>"
                    
                    texto_final = f"{veredito}" if veredito else ""
                    if risco != "N/A" and risco != "":
                        texto_final += f"<br><br><b>🚨 Grau de Risco:</b> {badge_risco}"
                        if justificativa_risco: 
                            texto_final += f"<br><b>🔍 Base do Risco:</b> {justificativa_risco}"
                    if acao: 
                        texto_final += f"<br><b>🎯 Manobra Imediata:</b> <u>{acao}</u>"
                    
                    if texto_final.strip() != "" or saudacao.strip() != "":
                        st.markdown(f"<div class='ana-message-box'><b>🎙️ {saudacao}</b><br><br>{texto_final}</div>", unsafe_allow_html=True)
                    
                    lista_graficos = []
                    
                    html_content = f"""
                    <!DOCTYPE html>
                    <html lang="pt">
                    <head>
                        <meta charset="UTF-8">
                        <title>Apresentação Executiva - ANA</title>
                        <script src="https://cdn.plot.ly/plotly-2.24.1.min.js"></script>
                        <style>
                            body, html {{ margin: 0; padding: 0; width: 100vw; height: 100vh; overflow: hidden; font-family: 'Segoe UI', Arial, sans-serif; background-color: #0f172a; color: #f8fafc; }}
                            .slider-container {{ display: flex; width: 100vw; height: 100vh; transition: transform 0.6s ease-in-out; }}
                            .slide {{ min-width: 100vw; height: 100vh; display: flex; justify-content: center; align-items: center; padding: 40px; box-sizing: border-box; }}
                            
                            .card {{ background: #1e293b; padding: 50px; border-radius: 16px; border-left: 8px solid #3b82f6; max-width: 1000px; width: 100%; max-height: 85vh; overflow-y: auto; box-shadow: 0 20px 40px rgba(0,0,0,0.4); }}
                            .card::-webkit-scrollbar {{ width: 8px; }}
                            .card::-webkit-scrollbar-track {{ background: rgba(0,0,0,0.1); border-radius: 4px; }}
                            .card::-webkit-scrollbar-thumb {{ background: #3b82f6; border-radius: 4px; }}
                            
                            .card-red {{ border-left-color: #ef4444; }}
                            h1 {{ font-size: 3rem; margin: 0 0 10px 0; color: #ffffff; }}
                            h2 {{ font-size: 2rem; color: #60a5fa; margin-top: 0; }}
                            p {{ font-size: 1.2rem; line-height: 1.7; color: #cbd5e1; }}
                            .badge {{ background: #ef4444; color: white; padding: 5px 12px; border-radius: 6px; font-weight: bold; font-size: 1rem; }}
                            
                            .nav-btn {{ position: fixed; top: 50%; transform: translateY(-50%); background: rgba(30, 41, 59, 0.4); color: rgba(255,255,255,0.3); border: 2px solid rgba(255,255,255,0.1); width: 50px; height: 50px; cursor: pointer; border-radius: 50%; font-size: 20px; z-index: 1000; transition: all 0.3s; display: flex; align-items: center; justify-content: center; backdrop-filter: blur(5px); }}
                            .nav-btn:hover {{ background: rgba(59, 130, 246, 0.9); color: white; border-color: #3b82f6; box-shadow: 0 0 15px rgba(59, 130, 246, 0.5); }}
                            #btn-prev {{ left: 20px; display: none; }}
                            #btn-next {{ right: 20px; }}
                            
                            .indicator {{ position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); font-size: 1rem; color: #64748b; letter-spacing: 2px; font-weight: bold; }}
                            .plot-container {{ width: 100%; height: 500px; margin-top: 20px; }}
                        </style>
                    </head>
                    <body>
                        <button id="btn-prev" class="nav-btn" onclick="moveSlide(-1)">&#10094;</button>
                        <button id="btn-next" class="nav-btn" onclick="moveSlide(1)">&#10095;</button>
                        <div class="indicator" id="slide-indicator">1 / 1</div>
                        
                        <div class="slider-container" id="slider">
                            <div class="slide">
                                <div class="card">
                                    <h1>📊 Apresentação Corporativa - ANA</h1>
                                    <p style="font-size: 1.4rem; color: #94a3b8;">Gerado exclusivamente para: <b>{nome_comando}</b></p>
                                    <hr style="border:0; border-top: 1px solid #334155; margin: 30px 0;">
                                    <p>Utilize as setas do teclado ( ◀ ▶ ) para navegar pelas análises executivas.</p>
                                </div>
                            </div>
                    """
                    
                    for hist_msg in st.session_state.mensagens[:-1]:
                        if hist_msg["role"] == "ana": 
                            txt_hist_br = hist_msg.get('texto', '').replace('\n', '<br>')
                            if txt_hist_br.strip() != "":
                                html_content += f"""
                                <div class="slide">
                                    <div class="card card-red">
                                        <h2>🎙️ {hist_msg.get('saudacao', 'Pronunciamento')}</h2>
                                        <p>{txt_hist_br}</p>
                                    </div>
                                </div>"""

                    if veredito.strip() != "" or (risco != "N/A" and risco != ""):
                        bloco_risco_html = ""
                        if risco != "N/A" and risco != "":
                            bloco_risco_html = f"""<div style="background: #0f172a; padding: 20px; border-radius: 8px; margin-top: 20px;"><p style="margin:0;"><b>Risco de Mercado:</b> <span class="badge">{risco}</span></p>"""
                            if justificativa_risco: 
                                bloco_risco_html += f"""<p style="margin: 10px 0 0 0; color:#94a3b8;"><b>Justificativa:</b> {justificativa_risco}</p>"""
                            if acao: 
                                bloco_risco_html += f"""<p style="margin: 10px 0 0 0;"><b>Manobra:</b> {acao}</p>"""
                            bloco_risco_html += "</div>"
                            
                        html_content += f"""
                        <div class="slide">
                            <div class="card card-red">
                                <h2>🎙️ {saudacao}</h2>
                                <p>{veredito}</p>
                                {bloco_risco_html}
                            </div>
                        </div>"""
                    
                    for i, rel in enumerate(relatorios):
                        tit = rel.get("titulo", "Análise Visual")
                        insight = rel.get("insight_estrategico", "")
                        insight_br_html = insight.replace('\n', '<br>')
                        
                        st.markdown(f"#### 📊 {tit}")
                        if rel.get("gerar_grafico"):
                            t = str(rel.get("tipo_grafico", "bar")).lower()
                            cx, cy = rel.get("eixo_x"), rel.get("eixo_y")
                            if cx in df.columns and cy in df.columns:
                                df_g = df.groupby(cx)[cy].sum().reset_index()
                                fig = None
                                paleta = ['#3b82f6', '#60a5fa', '#1d4ed8', '#1e3a8a']
                                
                                if t in ['bar', 'barras']: 
                                    fig = px.bar(df_g.nlargest(10, cy).sort_values(cy, ascending=True), y=cx, x=cy, orientation='h', color_discrete_sequence=paleta)
                                elif t in ['pie', 'pizza']: 
                                    fig = px.pie(df_g.nlargest(7, cy), names=cx, values=cy, hole=0.4, color_discrete_sequence=paleta)
                                elif t in ['line', 'linhas']: 
                                    fig = px.line(df_g.sort_values(cx), x=cx, y=cy, markers=True)
                                
                                if fig:
                                    fig.update_layout(template="plotly_dark", margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                                    st.plotly_chart(fig, use_container_width=True, key=f"din_g_{len(st.session_state.mensagens)}_{i}")
                                    
                                    if insight_br_html.strip() != "": 
                                        st.markdown(f"<div style='padding: 15px; border-left: 4px solid #3b82f6; background: rgba(30, 41, 59, 0.9); margin-bottom: 25px; border-radius: 0 8px 8px 0;'><b>🔥 Insight:</b> {insight_br_html}</div>", unsafe_allow_html=True)
                                    
                                    lista_graficos.append({"figura": fig, "explicacao": insight_br_html})
                                    
                                    plot_html = fig.to_html(full_html=False, include_plotlyjs=False)
                                    insight_html_tag = f'<p style="font-size: 1rem; color: #94a3b8; background: #0f172a; padding: 15px; border-radius: 6px; border-left: 3px solid #3b82f6;">{insight_br_html}</p>' if insight_br_html.strip() != "" else ""
                                    
                                    html_content += f"""
                                    <div class="slide">
                                        <div class="card" style="max-width: 1200px; padding: 30px;">
                                            <h2 style="margin-bottom: 5px;">{tit}</h2>
                                            {insight_html_tag}
                                            <div class="plot-container">{plot_html}</div>
                                        </div>
                                    </div>"""
                        
                    html_content += """
                        </div>
                        <script>
                            let currentSlide = 0; 
                            const slides = document.querySelectorAll('.slide'); 
                            const slider = document.getElementById('slider'); 
                            const indicator = document.getElementById('slide-indicator'); 
                            const btnPrev = document.getElementById('btn-prev'); 
                            const btnNext = document.getElementById('btn-next');
                            
                            function updateUI() { 
                                slider.style.transform = `translateX(-${currentSlide * 100}vw)`; 
                                indicator.innerText = `${currentSlide + 1} / ${slides.length}`; 
                                btnPrev.style.display = currentSlide === 0 ? 'none' : 'flex'; 
                                btnNext.style.display = currentSlide === slides.length - 1 ? 'none' : 'flex'; 
                            }
                            
                            function moveSlide(dir) { 
                                currentSlide += dir; 
                                if(currentSlide < 0) currentSlide = 0; 
                                if(currentSlide >= slides.length) currentSlide = slides.length - 1; 
                                updateUI(); 
                            }
                            
                            document.addEventListener('keydown', (e) => { 
                                if(e.key === 'ArrowRight') moveSlide(1); 
                                if(e.key === 'ArrowLeft') moveSlide(-1); 
                            }); 
                            
                            updateUI();
                        </script>
                    </body>
                    </html>
                    """
                    
                    html_dl = html_content if gerar_html else None
                    if html_dl: 
                        st.download_button("📥 Baixar Apresentação Corporativa", html_dl, "Apresentacao_Dinamica_ANA.html", "text/html", key=f"dl_new_{len(st.session_state.mensagens)}")
                    
                    st.session_state.mensagens.append({"role": "ana", "saudacao": saudacao, "texto": texto_final, "graficos_dados": lista_graficos, "download_html": html_dl})
                    
                    if st.session_state.sessao_ativa:
                        st.session_state.cofre_conversas[st.session_state.sessao_ativa]["mensagens"] = list(st.session_state.mensagens)
                        salvar_cofre(st.session_state.cofre_conversas)
                        
                    st.rerun()

                except Exception as e:
                    st.error(f"⚠️ Instabilidade de Núcleo: {e}")
                    if st.button("🔄 Abortar Comando"):
                        st.session_state.mensagens.pop()
                        st.rerun()
else:
    st.warning("⚠️ Insira a Chave de Acesso para acordar a Inteligência Artificial da ANA.")