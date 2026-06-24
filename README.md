Documentação Oficial: Projeto ANA (Versão 1.0)
Plataforma Enterprise de BI Avançado e Inteligência Neural
1. Visão Geral do Projeto
O Projeto ANA nasceu da necessidade de transformar dados brutos em
inteligência acionável de forma rápida, visual e executiva. Mais do que um simples
dashboard, a plataforma foi arquitetada para ser uma conselheira de negócios. Ela
une a força bruta da estatística e engenharia de dados com a capacidade
cognitiva de uma Inteligência Artificial de elite (a ANA), capaz de traduzir
matemática complexa em planos de ação diretos para tomadores de decisão.
O sistema foi desenhado para operar em duas frentes simultâneas:
1. Para o usuário leigo/executivo: Traduzindo dados em laudos de risco,
insights em linguagem natural e apresentações interativas.
2. Para o analista/profissional: Fornecendo um laboratório customizado
(Mini Power BI), higienização automatizada e controle total sobre as
variáveis.
2. A Jornada de Desenvolvimento
A concepção da Versão 1.0 foi um processo altamente iterativo, prático e guiado
por testes de estresse rigorosos. O desenvolvimento contou com o auxílio
estrutural e lógico do Gemini Pro, atuando como co-piloto de engenharia para
materializar a visão do projeto.
A evolução ocorreu em etapas claras de refinamento:
• Fase Alfa (Fundação): Estabelecimento da leitura de matrizes (Excel/CSV),
tratamento inicial de dados e a criação do chat básico com a IA.
• Fase Beta (Refinamento Lógico): Identificação e correção de anomalias
críticas, como o "Vírus de 1970" (conversão errônea de datas nativas do
Excel) e a trava matemática que impedia a IA de somar identificadores (IDs,
SKUs, CPFs).
• Fase Gama (Inteligência e UX): A plataforma ganhou vida. O AutoDiscovery foi implementado para gerar gráficos autonomamente. A
interface foi polida para um design Dark Mode corporativo. O sistema de
exportação de Dossiês HTML passou de um layout vertical estático para um
Slider (Apresentação de Slides) interativo e elegante.
• Fase Delta (Blindagem e Adaptação): A IA foi "destravada" de
comportamentos robotizados, ganhando multiplicadores criativos para
obedecer a comandos restritivos (ex: "apenas gráficos, sem texto").
Paralelamente, foi criado o Cofre de Sessões, um banco de dados local
que blindou o sistema contra o temido recarregamento de página (F5),
salvando o progresso da operação em tempo real.
3. Arquitetura do Sistema
O projeto foi modularizado para garantir performance e facilidade de manutenção,
dividido em três pilares principais.
3.1. Motor de Engenharia de Dados (core/data_engine.py)
Responsável por toda a "força bruta" antes da IA atuar.
• Ingestão Heurística: Descodifica múltiplos formatos e limpa caracteres
anômalos automaticamente.
• Otimização de Tipos: Força a tipagem correta de datas e blinda colunas
categóricas numéricas (como CEP e Código) para não serem distorcidas.
• Fusão Inteligente: Mescla diferentes bases de dados encontrando chaves
em comum, com um sistema de Alerta Vermelho que bloqueia a união de
matrizes incompatíveis.
• Núcleo Estatístico Avançado: Calcula autonomamente a Regra de Pareto
(80/20), identifica limites de Outliers via IQR (Intervalo Interquartil) e
diagnostica a assimetria (Skewness) das distribuições financeiras.
3.2. Cérebro Neural (core/ai_engine.py)
A consciência da ANA.
• Contexto Matemático Mapeado: A IA não "olha" apenas para a tabela, ela
recebe um dossiê técnico pré-processado pelo data_engine, o que a
impede de ter alucinações matemáticas.
• Adaptabilidade Extrema: Configurada com alta temperatura de resposta,
a ANA altera sua personalidade e formato de entrega conforme a ordem do
operador.
• Justificativa de Risco: Trava lógica que obriga a IA a provar
matematicamente o porquê de classificar uma operação como Risco Alto,
Médio ou Baixo.
• Geração Visual Dinâmica: Capacidade de gerar até 30 objetos visuais
(gráficos) formatados diretamente na interface via Plotly.
3.3. Orquestrador e Interface (analisador_big_boss.py)
O painel de controle operado pelo usuário (construído em Streamlit).
• Centro de Comando: Sidebar para upload de arquivos, inserção de chaves
de API e gestão do Cofre.
• Radar Automático: Usa o Coeficiente de Variação (CV >= 15%) para
renderizar apenas gráficos que apresentem distorções ou lideranças reais
nos negócios, ignorando dados irrelevantes ou planos.
• Mini Power BI: Laboratório com 15 geometrias visuais diferentes (Funil,
Treemap, Box Plot, Dispersão, etc.) para cruzamento manual de eixos X e Y.
• Apresentação Corporativa HTML: Compilador em tempo real que
transforma o chat, os laudos de risco e os gráficos da ANA em um arquivo
HTML contendo um Slider de apresentação com barra de rolagem
inteligente para textos densos.
4. Funcionalidades de Destaque da V1
1. Cofre de Persistência Local: Utiliza serialização (pickle) para criar uma
pasta isolada (cofre_sessoes). Permite gravar a operação, fechar a máquina
e retornar dias depois exatamente do mesmo ponto, mantendo o contexto
neural da ANA intacto.
2. Proteção Anti-Sobrescrita: Modais flutuantes centralizados que protegem
o usuário de deletar ou substituir arquivos do Cofre acidentalmente.
3. Tradutor para Leigos: Cada gráfico gerado automaticamente pelo sistema
ou pela ANA vem acompanhado de uma explicação didática do impacto
daquele cruzamento visual no mundo real dos negócios.
4. Respostas Randomizadas de Prontidão: Para evitar repetição, a interface
de chat possui um banco de 30 frases formais e variadas para solicitar o
input do usuário.
5. Auto-Clean de Memória: Ao inserir uma base de dados totalmente nova
no sistema, a matriz antiga é descartada e a memória da ANA é formatada
simultaneamente para evitar contaminação de contexto entre projetos.
5. Requisitos de Ambiente (Deploy)
Para rodar a plataforma em qualquer máquina, as seguintes dependências
precisam ser satisfeitas:
• Python 3.9+
• streamlit (Framework de Interface - Requer versão mais atualizada para
modais nativos)
• pandas e numpy (Manipulação Matemática)
• plotly (Geometria Visual e Gráficos)
• google-genai (Conexão Neural com o modelo Gemini 2.5 Flash)
• xlsxwriter (Exportação de planilhas higienizadas)
Comando de Inicialização Padrão:
Bash: streamlit run analisador_big_boss.py
