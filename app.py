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

# Estilização Command Center - Design System Industrial Dark
st.markdown('''
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
''', unsafe_allow_html=True)

# Top Bar Header
st.markdown('''
<div class="hero-header">
    <div>
        <div class="hero-title">⚡ COMMAND CENTER <span style="color: #64748B; font-weight: 400;">|</span> AUDITORIA RFI</div>
        <div class="hero-subtitle">MÓDULO DE VERIFICAÇÃO TÉCNICA E LEVANTAMENTO DE PENDÊNCIAS</div>
    </div>
    <div class="kpi-badge">SYSTEM READY v2.6</div>
</div>
''', unsafe_allow_html=True)

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

# Inicialização de Session State para campos dinâmicos
def init_state(key, default_value):
    if key not in st.session_state:
        st.session_state[key] = default_value

# Definir opções dos seletores para validação da IA
opcoes_icc = ["Não informado", "10 kA", "15 kA", "20 kA", "25 kA", "30 kA", "45 kA", "65 kA"]
opcoes_dps = ["Não informado", "Classe I", "Classe II", "Classe I + II", "Classe III", "Não terá"]
opcoes_temp = ["Não informado", "20 °C", "25 °C", "30 °C", "35 °C", "40 °C", "45 °C"]
opcoes_acesso = ["Não informado", "Por Baixo (Inferior)", "Por Cima (Superior)", "Mista (Entrada Cima / Saída Baixo)", "Mista (Entrada Baixo / Saída Cima)"]

# Sidebar - Configurações Técnicas
st.sidebar.markdown("### ⚙️ MOTOR IA (GROQ)")
api_key = st.secrets.get("GROQ_API_KEY", "") if "GROQ_API_KEY" in st.secrets else ""
if not api_key:
    api_key = st.sidebar.text_input("API Key:", type="password", help="Chave para análise semântica de edital")

modelos_disponiveis = []
if api_key:
    try:
        res = requests.get("https://api.groq.com/openai/v1/models", headers={"Authorization": f"Bearer {api_key}"}, timeout=3)
        if res.status_code == 200:
            data = res.json()
            modelos_disponiveis = [m["id"] for m in data.get("data", []) if any(k in m["id"] for k in ["llama", "mixtral", "gemma", "qwen"]) and "guard" not in m["id"]]
    except Exception:
        pass

if not modelos_disponiveis:
    modelos_disponiveis = ["llama-3.1-8b-instant", "llama3-70b-8192", "mixtral-8x7b-32768"]

modelo_selecionado = st.sidebar.selectbox("Modelo em Execução:", modelos_disponiveis)

# Seleção de Equipamento Principal
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

st.markdown("<br>", unsafe_allow_html=True)

# Definir opções baseadas no tipo de painel
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
    else:  # CCM
        opcoes_chaparia = ["Não informado", "TS8 Rittal (Padrão CCM)", "Coluna Extraível", "Coluna Fixa", "Padrão Fabricante"]
        opcoes_tensao = ["380V / 60Hz", "440V / 60Hz", "220V / 60Hz", "Não informado"]

opcoes_largura = ["Não informado", "600 mm a 1.000 mm", "1.000 mm a 2.000 mm", "2.000 mm a 3.000 mm", "3.000 mm a 4.000 mm", "4.000 mm a 5.000 mm", "5.000 mm a 6.000 mm"]

# Inicializar estados das seleções
init_state("icc", opcoes_icc[0])
init_state("dps_classe", opcoes_dps[0])
init_state("temp_ambiente", opcoes_temp[0])
init_state("entrada_saida_cabos", opcoes_acesso[0])
init_state("altura_limite", opcoes_altura[0])
init_state("profundidade_limite", opcoes_profundidade[0])
init_state("largura_limite", opcoes_largura[0])
init_state("chaparia", opcoes_chaparia[0])
init_state("tensao_nominal", opcoes_tensao[0])

# Layout Principal Dividido
col_form, col_summary = st.columns([1.25, 0.75], gap="large")

with col_form:
    # --------------------------------------------------------------------------
    # BLOCO 1: ANÁLISE DE DOCUMENTOS E EDITAL (NO TOPO)
    # --------------------------------------------------------------------------
    st.markdown('''
    <div class="card-box">
        <div class="card-header">📄 1. Análise de Documentos & Edital</div>
    ''', unsafe_allow_html=True)
    
    anexos = st.file_uploader("Anexar Documentos / Especificações (PDF, DOCX, TXT):", type=["pdf", "docx", "txt"], accept_multiple_files=True)
    obs_adicionais = st.text_area("Texto / Trechos do Edital:", height=100, placeholder="Ex: O painel deverá conter barramentos estanhados, corrente de curto de 30 kA, acionamento via Eth/IP...", key="obs_adicionais")
    
    col_auto1, col_auto2 = st.columns([1, 1])
    with col_auto1:
        btn_auto_preencher = st.button("🤖 ANALISAR & PREENCHER SOZINHO")
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Lógica do Auto-Preenchimento via IA
    if btn_auto_preencher:
        texto_extraido_anexos = extrair_texto_arquivos(anexos) if anexos else ""
        texto_completo_para_ia = (obs_adicionais + "\n\n" + texto_extraido_anexos).strip()

        if not texto_completo_para_ia:
            st.warning("⚠️ Forneça um trecho de texto ou anexe um documento para realizar a análise.")
        elif not api_key:
            st.error("⚠️ Insira a chave da API (Groq) no menu lateral para ativar a IA.")
        else:
            with st.spinner("Analisando especificações e auto-preenchendo parâmetros..."):
                prompt_json = f"""
                Você é um assistente técnico especialista em projetos elétricos.
                Analise o texto a seguir e extraia as configurações para o painel {tipo_painel}.
                
                Texto para Análise:
                {texto_completo_para_ia[:6000]}
                
                Retorne APENAS um JSON válido (sem marcação markdown, sem ```json) com a seguinte estrutura e escolhendo estritamente uma das opções listadas:
                {{
                    "icc": "uma opção de {json.dumps(opcoes_icc)}",
                    "dps_classe": "uma opção de {json.dumps(opcoes_dps)}",
                    "temp_ambiente": "uma opção de {json.dumps(opcoes_temp)}",
                    "entrada_saida_cabos": "uma opção de {json.dumps(opcoes_acesso)}",
                    "altura_limite": "uma opção de {json.dumps(opcoes_altura)}",
                    "profundidade_limite": "uma opção de {json.dumps(opcoes_profundidade)}",
                    "largura_limite": "uma opção de {json.dumps(opcoes_largura)}",
                    "chaparia": "uma opção de {json.dumps(opcoes_chaparia)}",
                    "tensao_nominal": "uma opção de {json.dumps(opcoes_tensao)}"
                }}
                
                Se a informação não estiver no texto, atribua "Não informado".
                """
                
                try:
                    payload = {
                        "model": modelo_selecionado,
                        "messages": [{"role": "user", "content": prompt_json}],
                        "temperature": 0.1
                    }
                    
                    res = requests.post(
                        "[https://api.groq.com/openai/v1/chat/completions](https://api.groq.com/openai/v1/chat/completions)",
                        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                        json=payload,
                        timeout=20
                    )
                    
                    if res.status_code == 200:
                        conteudo_resposta = res.json()["choices"][0]["message"]["content"]
                        
                        # Limpa marcações markdown
                        conteudo_limpo = re.sub(r'
