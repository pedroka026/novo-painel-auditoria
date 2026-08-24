O código está **praticamente correto e funcional**, mas contém **duas falhas críticas de layout/HTML e sintaxe** que vão quebrar a interface do Streamlit na execução:

1. **HTML Mal Fechado na Linha do Summary (`col_summary`):**
No final do script, há duas `</div>` extras para fechar as colunas (`st.markdown('</div></div>', unsafe_allow_html=True)`). Isso vai gerar uma quebra visual ou erro de renderização porque a coluna do Streamlit não foi aberta com uma `<div>` normal do HTML, e sim com um `with col_summary:`.
2. **Perda da `<div>` do Card na Área de Resultado:**
No bloco do `col_summary`, você abre a `div` com inline CSS (`<div style="background: #111827...`), mas dependendo de como o código roda e é re-executado no Streamlit, as tags de fechamento no final da coluna acumulam e quebram a responsividade.

Aqui está a versão **totalmente corrigida e limpa**, sem conflitos de tags HTML e com a lógica de sintaxe 100% ajustada:

```python
import streamlit as st
import requests
import re
import json

# Importações condicionais para extração de anexos
try:
    import pypdf
except ImportError:
    pypdf = None

try:
    import docx
except ImportError:
    docx = None

# Configuração da página
st.set_page_config(
    page_title="Command Center - Auditoria RFI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS isolada
css_style = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');
    
    .stApp {
        background-color: #0B0F17 !important;
        color: #E2E8F0 !important;
        font-family: 'Inter', -apple-system, sans-serif;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .hero-header {
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.8) 0%, rgba(11, 15, 23, 1) 100%);
        border: 1px solid #1E293B;
        border-bottom: 2px solid #06B6D4;
        padding: 24px;
        border-radius: 12px;
        margin-bottom: 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .hero-title {
        color: #F8FAFC;
        font-size: 1.4rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .hero-subtitle {
        color: #64748B;
        font-size: 0.875rem;
        margin-top: 4px;
        font-family: 'JetBrains Mono', monospace;
    }

    .kpi-badge {
        background: rgba(6, 182, 212, 0.1);
        border: 1px solid rgba(6, 182, 212, 0.3);
        color: #38BDF8;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 600;
    }

    .card-box {
        background: #111827;
        border: 1px solid #1F2937;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 16px;
        transition: border-color 0.2s ease;
    }
    .card-box:hover {
        border-color: #374151;
    }

    .card-header {
        font-size: 0.875rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #38BDF8;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
        border-bottom: 1px solid #1F2937;
        padding-bottom: 10px;
    }

    div[data-baseweb="select"] > div {
        background-color: #1F2937 !important;
        border: 1px solid #374151 !important;
        color: #F3F4F6 !important;
        border-radius: 6px !important;
        font-size: 0.9rem !important;
    }
    div[data-baseweb="select"] > div:hover {
        border-color: #06B6D4 !important;
    }
    
    .stTextArea textarea {
        background-color: #1F2937 !important;
        border: 1px solid #374151 !important;
        color: #F3F4F6 !important;
        border-radius: 6px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.85rem !important;
    }
    .stTextArea textarea:focus {
        border-color: #06B6D4 !important;
        box-shadow: 0 0 0 1px #06B6D4 !important;
    }

    div.stButton > button:first-child {
        background: linear-gradient(135deg, #0284C7 0%, #06B6D4 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        border-radius: 8px !important;
        padding: 14px 20px !important;
        letter-spacing: 0.025em !important;
        box-shadow: 0 4px 14px rgba(6, 182, 212, 0.3) !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button:first-child:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(6, 182, 212, 0.4) !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #0F172A !important;
        border-right: 1px solid #1E293B !important;
    }
    
    .pending-item {
        background: #182234;
        border-left: 3px solid #F59E0B;
        padding: 10px 14px;
        margin-bottom: 8px;
        border-radius: 4px;
        font-size: 0.85rem;
        color: #E2E8F0;
    }
</style>
"""
st.markdown(css_style, unsafe_allow_html=True)

# Top Bar Header
st.markdown("""
<div class="hero-header">
    <div>
        <div class="hero-title">⚡ COMMAND CENTER <span style="color: #64748B; font-weight: 400;">|</span> AUDITORIA RFI</div>
        <div class="hero-subtitle">MÓDULO DE VERIFICAÇÃO TÉCNICA E LEVANTAMENTO DE PENDÊNCIAS</div>
    </div>
    <div class="kpi-badge">SYSTEM READY v2.6</div>
</div>
""", unsafe_allow_html=True)

# Helper para ler texto de arquivos anexados
def extrair_texto_arquivos(uploaded_files):
    texto_consolidado = ""
    for file in uploaded_files:
        try:
            if file.name.endswith(".pdf"):
                if pypdf:
                    pdf_reader = pypdf.PdfReader(file)
                    for page in pdf_reader.pages:
                        texto_consolidado += (page.extract_text() or "") + "\n"
                else:
                    texto_consolidado += f"\n[Arquivo PDF '{file.name}' detectado, mas biblioteca 'pypdf' não instalada]\n"
            elif file.name.endswith(".docx"):
                if docx:
                    doc = docx.Document(file)
                    for p in doc.paragraphs:
                        texto_consolidado += p.text + "\n"
                else:
                    texto_consolidado += f"\n[Arquivo DOCX '{file.name}' detectado, mas biblioteca 'python-docx' não instalada]\n"
            elif file.name.endswith(".txt"):
                texto_consolidado += file.read().decode("utf-8", errors="ignore") + "\n"
        except Exception as e:
            st.error(f"Erro ao processar arquivo {file.name}: {e}")
    return texto_consolidado

# Helper para sanitização de JSON da IA
def limpar_json_resposta(texto):
    texto = texto.strip()
    if texto.startswith("```json"):
        texto = texto[7:]
    elif texto.startswith("```"):
        texto = texto[3:]
    if texto.endswith("```"):
        texto = texto[:-3]
    return texto.strip()

# Inicialização de Session State
def init_state(key, default_value):
    if key not in st.session_state:
        st.session_state[key] = default_value

# Opções Padrão
opcoes_icc = ["Não informado", "10 kA", "15 kA", "20 kA", "25 kA", "30 kA", "45 kA", "65 kA"]
opcoes_dps = ["Não informado", "Classe I", "Classe II", "Classe I + II", "Classe III", "Não terá"]
opcoes_temp = ["Não informado", "20 °C", "25 °C", "30 °C", "35 °C", "40 °C", "45 °C"]
opcoes_acesso = ["Não informado", "Por Baixo (Inferior)", "Por Cima (Superior)", "Mista (Entrada Cima / Saída Baixo)", "Mista (Entrada Baixo / Saída Cima)"]

# Sidebar - Configurações
st.sidebar.markdown("### ⚙️ MOTOR IA (GROQ)")
api_key = st.secrets.get("GROQ_API_KEY", "") if "GROQ_API_KEY" in st.secrets else ""
if not api_key:
    api_key = st.sidebar.text_input("API Key:", type="password", help="Chave para análise semântica de edital")

modelos_disponiveis = []
if api_key:
    try:
        res = requests.get("[https://api.groq.com/openai/v1/models](https://api.groq.com/openai/v1/models)", headers={"Authorization": f"Bearer {api_key}"}, timeout=3)
        if res.status_code == 200:
            data = res.json()
            modelos_disponiveis = [m["id"] for m in data.get("data", []) if any(k in m["id"] for k in ["llama", "mixtral", "gemma", "qwen"]) and "guard" not in m["id"]]
    except Exception:
        pass

if not modelos_disponiveis:
    modelos_disponiveis = ["llama-3.1-8b-instant", "llama3-70b-8192", "mixtral-8x7b-32768"]

modelo_selecionado = st.sidebar.selectbox("Modelo em Execução:", modelos_disponiveis)

# Seleção do Painel
st.markdown("<div style='margin-bottom: 8px; font-weight: 600; font-size: 0.85rem; color: #94A3B8;'>EQUIPAMENTO EM AUDITORIA</div>", unsafe_allow_html=True)
tipo_painel = st.selectbox(
    "Selecione a Tipologia:",
    [
        "CCM (Centro de Controle de Motores)",
        "QDFL (Quadro de Distribuição de Força e Luz)",
        "QGBT (Quadro Geral de Baixa Tensão)"
    ],
    label_visibility="collapsed"
)

# Opções dinâmicas conforme a tipologia
if "QDFL" in tipo_painel:
    opcoes_altura = ["1.000 mm (Padrão QDFL)", "600 mm a 800 mm", "800 mm a 1.200 mm", "1.200 mm a 1.600 mm", "Não informado"]
    opcoes_profundidade = ["300 mm (Padrão QDFL)", "200 mm a 300 mm", "300 mm a 400 mm", "400 mm a 600 mm", "Não informado"]
    opcoes_chaparia = ["Não informado", "Caixa de Sobrepor (Padrão Rittal)", "Armário de Coluna", "Padrão Fabricante"]
    opcoes_tensao = ["220V / 60Hz (Padrão)", "380V / 60Hz", "Não informado"]
else:
    opcoes_altura = ["2.000 mm (Padrão)", "1.200 mm a 1.600 mm", "1.600 mm a 2.000 mm", "2.000 mm a 2.300 mm", "Não informado"]
    opcoes_profundidade = ["600 mm (Padrão)", "400 mm a 600 mm", "600 mm a 800 mm", "800 mm a 1.000 mm", "Não informado"]
    if "QGBT" in tipo_painel:
        opcoes_chaparia = ["Não informado", "TS8 Rittal (Padrão QGBT)", "VX25 Rittal", "Forma 3b / 4b", "Padrão Fabricante"]
        opcoes_tensao = ["380V / 60Hz (Padrão)", "440V / 60Hz", "480V / 60Hz", "Não informado"]
    else:
        opcoes_chaparia = ["Não informado", "TS8 Rittal (Padrão CCM)", "Coluna Extraível", "Coluna Fixa", "Padrão Fabricante"]
        opcoes_tensao = ["380V / 60Hz", "440V / 60Hz", "220V / 60Hz", "Não informado"]

opcoes_largura = ["Não informado", "600 mm a 1.000 mm", "1.000 mm a 2.000 mm", "2.000 mm a 3.000 mm", "3.000 mm a 4.000 mm", "4.000 mm a 5.000 mm", "5.000 mm a 6.000 mm"]

# Inicializar Estados
init_state("icc", opcoes_icc[0])
init_state("dps_classe", opcoes_dps[0])
init_state("temp_ambiente", opcoes_temp[0])
init_state("entrada_saida_cabos", opcoes_acesso[0])
init_state("altura_limite", opcoes_altura[0])
init_state("profundidade_limite", opcoes_profundidade[0])
init_state("largura_limite", opcoes_largura[0])
init_state("chaparia", opcoes_chaparia[0])
init_state("tensao_nominal", opcoes_tensao[0])

# Layout de Colunas
col_form, col_summary = st.columns([1.25, 0.75], gap="large")

with col_form:
    st.markdown('<div class="card-box"><div class="card-header">📄 1. Análise de Documentos & Edital</div>', unsafe_allow_html=True)
    anexos = st.file_uploader("Anexar Documentos / Especificações (PDF, DOCX, TXT):", type=["pdf", "docx", "txt"], accept_multiple_files=True)
    obs_adicionais = st.text_area("Texto / Trechos do Edital:", height=100, placeholder="Ex: O painel deverá conter barramentos estanhados, corrente de curto de 30 kA...", key="obs_adicionais")
    btn_auto_preencher = st.button("🤖 ANALISAR & PREENCHER SOZINHO")
    st.markdown('</div>', unsafe_allow_html=True)

    if btn_auto_preencher:
        texto_extraido_anexos = extrair_texto_arquivos(anexos) if anexos else ""
        texto_completo_para_ia = (obs_adicionais + "\n\n" + texto_extraido_anexos).strip()

        if not texto_completo_para_ia:
            st.warning("⚠️ Forneça um trecho de texto ou anexe um documento.")
        elif not api_key:
            st.error("⚠️ Insira a chave da API (Groq) na barra lateral.")
        else:
            with st.spinner("Analisando especificações com IA..."):
                prompt_json = f"""
                Analise o texto a seguir e extraia as configurações para o painel {tipo_painel}.
                Texto: {texto_completo_para_ia[:6000]}
                Retorne APENAS um JSON válido com estas chaves:
                - icc: {json.dumps(opcoes_icc)}
                - dps_classe: {json.dumps(opcoes_dps)}
                - temp_ambiente: {json.dumps(opcoes_temp)}
                - entrada_saida_cabos: {json.dumps(opcoes_acesso)}
                - altura_limite: {json.dumps(opcoes_altura)}
                - profundidade_limite: {json.dumps(opcoes_profundidade)}
                - largura_limite: {json.dumps(opcoes_largura)}
                - chaparia: {json.dumps(opcoes_chaparia)}
                - tensao_nominal: {json.dumps(opcoes_tensao)}
                Se não achar, coloque "Não informado".
                """
                try:
                    res = requests.post(
                        "[https://api.groq.com/openai/v1/chat/completions](https://api.groq.com/openai/v1/chat/completions)",
                        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                        json={"model": modelo_selecionado, "messages": [{"role": "user", "content": prompt_json}], "temperature": 0.1},
                        timeout=20
                    )
                    if res.status_code == 200:
                        conteudo = limpar_json_resposta(res.json()["choices"][0]["message"]["content"])
                        dados = json.loads(conteudo)
                        for k, v in dados.items():
                            if k in st.session_state:
                                st.session_state[k] = v
                        st.success("✅ Formulário atualizado!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Erro ao processar: {e}")

    st.markdown('<div class="card-box"><div class="card-header">📐 2. Parâmetros Construtivos & Elétricos Gerais</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.selectbox("Corrente Curto (Icc):", opcoes_icc, key="icc")
        st.selectbox("Classe DPS:", opcoes_dps, key="dps_classe")
        st.selectbox("Temp. Ambiente Máxima:", opcoes_temp, key="temp_ambiente")
    with c2:
        st.selectbox("Acesso Cabos:", opcoes_acesso, key="entrada_saida_cabos")
        st.selectbox("Limite Altura:", opcoes_altura, key="altura_limite")
        st.selectbox("Limite Profundidade:", opcoes_profundidade, key="profundidade_limite")
    
    c3, c4 = st.columns(2)
    with c3:
        st.selectbox("Limite Largura:", opcoes_largura, key="largura_limite")
    with c4:
        st.selectbox("Invólucro / Chaparia:", opcoes_chaparia, key="chaparia")
        st.selectbox("Tensão Nominal:", opcoes_tensao, key="tensao_nominal")
    st.markdown('</div>', unsafe_allow_html=True)

    # Bloco 3 Específico
    if "CCM" in tipo_painel:
        st.markdown('<div class="card-box"><div class="card-header">⚙️ 3. Especificações do CCM</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.selectbox("Total Partidas:", ["Não informado", "1 a 5 partidas", "5 a 10 partidas", "10 a 20 partidas", "Mais de 20"], key="quantitativo_partidas")
            st.selectbox("Partida Predominante:", ["Não informado", "Partida Direta", "Inversor de Frequência", "Soft-Starter"], key="tipo_partida")
            st.selectbox("CLP / E/S Remota:", ["Não informado", "ControlLogix", "CompactLogix", "Flex I/O", "Point I/O", "Não terá"], key="clp_es")
        with c2:
            st.selectbox("Potência Motores:", ["Não informado", "Definido no Texto de Observações"], key="potencia_motores")
            st.selectbox("Categoria NR-12:", ["Não informado", "Categoria 1", "Categoria 2", "Categoria 3", "Categoria 4"], key="categoria_seguranca")
            st.selectbox("Volume I/O:", ["Não informado", "Informado"], key="quantitativo_io")
        st.selectbox("Modo Acionamento:", ["Não informado", "Local (Botoeiras)", "Remoto (Via CLP/Rede)", "Misto"], key="modo_acionamento")
        st.selectbox("Topologia da Rede:", ["Não informado", "Anel (DLR / MRP)", "Estrela", "Barramento"], key="topologia_rede")
        st.selectbox("Protocolo Comunicação:", ["Não informado", "EtherNet/IP", "PROFINET", "Modbus TCP"], key="protocolo_comunicacao")
        st.markdown('</div>', unsafe_allow_html=True)

    elif "QDFL" in tipo_painel:
        st.markdown('<div class="card-box"><div class="card-header">💡 3. Especificações do QDFL</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.selectbox("Qtd de Circuitos:", ["Não informado", "1 a 10 circuitos", "10 a 20 circuitos", "Mais de 20"], key="qdfl_cargas")
            st.selectbox("Corrente Disjuntores:", ["Não informado", "Especificado nas Observações"], key="qdfl_corrente_disjuntores")
            st.selectbox("Aplicação de IDR (DR):", ["Não informado", "Sim (Geral)", "Sim (Apenas em Cargas Específicas)", "Não terá"], key="qdfl_idr")
        with c2:
            st.selectbox("Cargas com IDR:", ["Não informado", "Detalhado nas Observações", "Todas as Iluminações/Tomadas"], key="qdfl_idr_detalhe")
            st.selectbox("Acionamentos na Porta:", ["Não informado", "Chaves Comutadoras", "Botoeiras", "Apenas Disjuntores Internos"], key="qdfl_acionamento")
        st.markdown('</div>', unsafe_allow_html=True)

    elif "QGBT" in tipo_painel:
        st.markdown('<div class="card-box"><div class="card-header">🔌 3. Especificações do QGBT</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.selectbox("Disjuntor Geral:", ["Não informado", "Aberto (ACB) Extraível", "Aberto (ACB) Fixo", "Caixa Moldada (MCCB)"], key="qgbt_disjuntor_geral")
            st.selectbox("Corrente Nominal (In):", ["Não informado", "Até 800A", "1000A a 1600A", "2000A a 3200A", "Acima de 4000A"], key="qgbt_corrente_geral")
            st.selectbox("Tratamento Barramento:", ["Não informado", "Cobre Eletrolítico Nu", "Cobre Prateado", "Cobre Estanhado"], key="qgbt_barramento")
        with c2:
            st.selectbox("Forma Separação (IEC 61439):", ["Não informado", "Forma 1", "Forma 2b", "Forma 3b", "Forma 4b"], key="qgbt_forma_separacao")
            st.selectbox("Multimedidor de Porta:", ["Não informado", "Multimedidor Digital na Porta", "Não terá"], key="qgbt_medicao")
            st.selectbox("Correção Fator de Potência:", ["Não informado", "Integrado ao QGBT", "Painel Separado", "Não terá"], key="qgbt_recomposição_fp")
        st.markdown('</div>', unsafe_allow_html=True)

with col_summary:
    st.markdown(f"""
    <div style="background: #111827; border: 1px solid #1F2937; border-radius: 10px; padding: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
            <span style="font-size: 0.9rem; font-weight: 700; color: #F3F4F6;">PAINEL DE CONSOLIDAÇÃO</span>
            <span style="background: #0284C7; color: #FFF; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 600;">{tipo_painel.split(' ')[0]}</span>
        </div>
    """, unsafe_allow_html=True)

    btn_processar = st.button("RUN AUDIT / GERAR RFI ➔")

    if btn_processar:
        pendencias = []

        if st.session_state.get("icc") == "Não informado": pendencias.append("Qual é a corrente de curto-circuito (Icc em kA)?")
        if st.session_state.get("dps_classe") == "Não informado": pendencias.append("Qual é a classe de proteção do DPS exigida?")
        if st.session_state.get("temp_ambiente") == "Não informado": pendencias.append("Qual é a temperatura ambiente máxima no local?")
        if st.session_state.get("entrada_saida_cabos") == "Não informado": pendencias.append("Qual a direção de entrada e saída dos cabos?")
        if st.session_state.get("altura_limite") == "Não informado": pendencias.append("Qual é o limite de altura disponível?")
        if st.session_state.get("profundidade_limite") == "Não informado": pendencias.append("Qual é o limite de profundidade disponível?")
        if st.session_state.get("largura_limite") == "Não informado": pendencias.append("Qual é o limite de largura disponível?")
        if st.session_state.get("chaparia") == "Não informado": pendencias.append("Qual é o padrão de invólucro / chaparia?")
        if st.session_state.get("tensao_nominal") == "Não informado": pendencias.append("Qual é a tensão nominal e frequência?")

        if "CCM" in tipo_painel:
            if st.session_state.get("quantitativo_partidas") == "Não informado": pendencias.append("Qual o quantitativo total de partidas do CCM?")
            if st.session_state.get("tipo_partida") == "Não informado": pendencias.append("Qual o tipo de partida exigido?")
            if st.session_state.get("potencia_motores") == "Não informado": pendencias.append("Qual a potência (kW/cv) dos motores?")
            if st.session_state.get("categoria_seguranca") == "Não informado": pendencias.append("Qual a Categoria de Segurança NR-12?")
            if st.session_state.get("modo_acionamento") == "Não informado": pendencias.append("Como será o acionamento dos motores?")
            if st.session_state.get("clp_es") == "Não informado": pendencias.append("Qual o modelo do CLP ou E/S Remota?")
            if st.session_state.get("quantitativo_io") == "Não informado": pendencias.append("Qual o quantitativo de I/O?")
            if st.session_state.get("topologia_rede") == "Não informado": pendencias.append("Qual a topologia da rede de comunicação?")
            if st.session_state.get("protocolo_comunicacao") == "Não informado": pendencias.append("Qual o protocolo de comunicação?")

        elif "QDFL" in tipo_painel:
            if st.session_state.get("qdfl_cargas") == "Não informado": pendencias.append("Qual a quantidade de cargas do QDFL?")
            if st.session_state.get("qdfl_corrente_disjuntores") == "Não informado": pendencias.append("Qual a corrente nominal dos disjuntores?")
            if st.session_state.get("qdfl_idr") == "Não informado": pendencias.append("Será necessária proteção residual IDR?")
            if st.session_state.get("qdfl_idr") == "Sim (Apenas em Cargas Específicas)" and st.session_state.get("qdfl_idr_detalhe") == "Não informado":
                pendencias.append("Em quais saídas específicas é obrigatório IDR?")
            if st.session_state.get("qdfl_acionamento") == "Não informado": pendencias.append("Haverá comandos na porta?")

        elif "QGBT" in tipo_painel:
            if st.session_state.get("qgbt_disjuntor_geral") == "Não informado": pendencias.append("Qual o tipo do disjuntor geral de entrada?")
            if st.session_state.get("qgbt_corrente_geral") == "Não informado": pendencias.append("Qual a corrente nominal geral (In) do QGBT?")
            if st.session_state.get("qgbt_barramento") == "Não informado": pendencias.append("Qual o tratamento do barramento?")
            if st.session_state.get("qgbt_forma_separacao") == "Não informado": pendencias.append("Qual a Forma de Separação Interna (IEC 61439)?")
            if st.session_state.get("qgbt_medicao") == "Não informado": pendencias.append("Qual o modelo de multimedidor na porta?")
            if st.session_state.get("qgbt_recomposição_fp") == "Não informado": pendencias.append("Deverá possuir banco de capacitores integrado?")

        duvidas_extras = []
        texto_anexos_geral = extrair_texto_arquivos(anexos) if anexos else ""
        texto_consolidado = (obs_adicionais + "\n" + texto_anexos_geral).strip()

        if texto_consolidado and api_key:
            system_prompt = (
                f"Você é um engenheiro orçamentista de painéis elétricos especializado em {tipo_painel}. "
                "Crie perguntas técnicas em Português sobre pontos não esclarecidos. "
                "Responda APENAS em tópicos com perguntas diretas iniciando por 'Qual', 'Quais', 'Há' ou 'É'."
            )
            try:
                res = requests.post(
                    "[https://api.groq.com/openai/v1/chat/completions](https://api.groq.com/openai/v1/chat/completions)",
                    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                    json={
                        "model": modelo_selecionado,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": texto_consolidado[:6000]}
                        ],
                        "temperature": 0.0
                    },
                    timeout=10
                )
                if res.status_code == 200:
                    texto_ia = res.json()["choices"][0]["message"]["content"]
                    padrao_ptbr = re.compile(r'^\s*[\*\-]?\s*(Qual|Quais|Como|Há|É|Existe|Deve)\b.*\?$', re.IGNORECASE)
                    for linha in texto_ia.split('\n'):
                        linha_limpa = linha.strip()
                        if padrao_ptbr.match(linha_limpa):
                            pergunta_formatada = re.sub(r'^[\*\-\d\.\s]+', '', linha_limpa)
                            duvidas_extras.append(pergunta_formatada)
            except Exception as e:
                st.error(f"Erro LLM: {e}")

        todas_duvidas = list(dict.fromkeys(pendencias + duvidas_extras))

        st.markdown("<br>", unsafe_allow_html=True)
        if todas_duvidas:
            st.markdown(f"""
            <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid #F59E0B; padding: 10px 14px; border-radius: 6px; font-size: 0.8rem; color: #FBBF24; font-family: 'JetBrains Mono', monospace; margin-bottom: 12px;">
                ⚠️ {len(todas_duvidas)} PENDÊNCIA(S) DETECTADA(S)
            </div>
            """, unsafe_allow_html=True)

            texto_relatorio = f"RFI - LEVANTAMENTO DE DÚVIDAS TÉCNICAS ({tipo_painel.split(' ')[0]})\n\n"
            for idx, d in enumerate(todas_duvidas, 1):
                st.markdown(f'<div class="pending-item"><b>{idx}.</b> {d}</div>', unsafe_allow_html=True)
                texto_relatorio += f"{idx}. {d}\n"

            st.markdown("<br>", unsafe_allow_html=True)
            st.download_button(
                label="📥 EXPORTAR RELATÓRIO (.TXT)",
                data=texto_relatorio,
                file_name=f"rfi_duvidas_{tipo_painel.split(' ')[0].lower()}.txt",
                mime="text/plain"
            )
        else:
            st.markdown("""
            <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid #10B981; padding: 12px; border-radius: 6px; font-size: 0.85rem; color: #34D399; text-align: center;">
                ✓ NENHUMA PENDÊNCIA ENCONTRADA
            </div>
            """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

```
