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

# Estilização CSS isolada para evitar erros de sintaxe
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
if
