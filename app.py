import streamlit as st
import requests
import json
import os
import pypdf

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

    div.stButton > button:first-child {
        background: linear-gradient(135deg, #0284C7 0%, #06B6D4 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        border-radius: 8px !important;
        padding: 12px 20px !important;
        width: 100%;
    }

    div[data-testid="stFileUploader"] {
        background-color: #1F2937 !important;
        border: 1px dashed #374151 !important;
        border-radius: 8px !important;
        padding: 10px !important;
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
        <div class="hero-subtitle">MÓDULO DE VERIFICAÇÃO TÉCNICA E AUTO-PREENCHIMENTO VIA IA</div>
    </div>
    <div class="kpi-badge">SYSTEM READY</div>
</div>
''', unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# GERENCIAMENTO SEGURO DA CHAVE DA API GROQ
# ------------------------------------------------------------------------------
api_key = ""

# 1. Tenta carregar dos Secrets do Streamlit Cloud (sem travar se não existir)
try:
    if "GROQ_API_KEY" in st.secrets:
        api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    pass

# 2. Tenta carregar de variável de ambiente
if not api_key:
    api_key = os.environ.get("GROQ_API_KEY", "")

# 3. Configurações na Barra Lateral
st.sidebar.markdown("### ⚙️ MOTOR IA (GROQ)")

if not api_key:
    api_key = st.sidebar.text_input("Cole a chave Groq (gsk_...):", type="password")
    if not api_key:
        st.sidebar.warning("⚠️ Insira a chave da API para habilitar a IA.")
else:
    st.sidebar.success("✓ Chave da API configurada com segurança!")

modelo_selecionado = st.sidebar.selectbox(
    "Modelo em Execução:", 
    [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768"
    ]
)

# Dicionários de opções para o formulário
OPCOES_ICC = ["Não informado", "10 kA", "15 kA", "20 kA", "25 kA", "30 kA", "45 kA", "65 kA"]
OPCOES_DPS = ["Não informado", "Classe I", "Classe II", "Classe I + II", "Classe III", "Não terá"]
OPCOES_TEMP = ["Não informado", "20 °C", "25 °C", "30 °C", "35 °C", "40 °C", "45 °C"]
OPCOES_ACESSOCABOS = ["Não informado", "Por Baixo (Inferior)", "Por Cima (Superior)", "Mista (Entrada Cima / Saída Baixo)", "Mista (Entrada Baixo / Saída Cima)"]

# Inicializar estados de sessão
def inicializar_campos():
    for key in ["icc", "dps", "temp", "acessocabos"]:
        if key not in st.session_state:
            st.session_state[key] = "Não informado"

inicializar_campos()

# 1. SELEÇÃO DE EQUIPAMENTO PRINCIPAL
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

# 2. UPLOAD E PROCESSAMENTO DE DOCUMENTAÇÃO/EDITAL
st.markdown("<div style='margin-top: 12px; margin-bottom: 8px; font-weight: 600; font-size: 0.85rem; color: #94A3B8;'>📎 ANEXAR ESPECIFICAÇÃO / EDITAL (PDF OU TXT)</div>", unsafe_allow_html=True)
arquivo_anexado = st.file_uploader("Arraste ou selecione o arquivo do edital:", type=["pdf", "txt"], label_visibility="collapsed")

texto_arquivo = ""
if arquivo_anexado is not None:
    try:
        if arquivo_anexado.name.endswith(".pdf"):
            reader = pypdf.PdfReader(arquivo_anexado)
            for page in reader.pages:
                texto_arquivo += page.extract_text() or ""
        elif arquivo_anexado.name.endswith(".txt"):
            texto_arquivo = arquivo_anexado.read().decode("utf-8")
            
        st.success(f"✓ Arquivo '{arquivo_anexado.name}' carregado!")
        
        # BOTÃO PARA EXTRAÇÃO E PREENCHIMENTO AUTOMÁTICO
        if st.button("🤖 ANALISAR DOCUMENTAÇÃO E PREENCHER CAMPOS AUTOMATICAMENTE"):
            if not api_key:
                st.error("Insira uma chave válida da Groq na barra lateral ou nos Secrets!")
            else:
                with st.spinner("IA analisando a documentação e identificando os parâmetros técnicos..."):
                    prompt_analise = f"""
                    Você é um engenheiro eletricista especialista em painéis elétricos.
                    Analise o texto fornecido do edital/especificação técnica e extraia as informações pedidas.
                    
                    Você deve mapear cada campo exatamente para uma das opções válidas listadas abaixo:
                    - icc: ["10 kA", "15 kA", "20 kA", "25 kA", "30 kA", "45 kA", "65 kA", "Não informado"]
                    - dps: ["Classe I", "Classe II", "Classe I + II", "Classe III", "Não terá", "Não informado"]
                    - temp: ["20 °C", "25 °C", "30 °C", "35 °C", "40 °C", "45 °C", "Não informado"]
                    - acessocabos: ["Por Baixo (Inferior)", "Por Cima (Superior)", "Mista (Entrada Cima / Saída Baixo)", "Mista (Entrada Baixo / Saída Cima)", "Não informado"]

                    Retorne EXCLUSIVAMENTE um objeto JSON válido no formato:
                    {{
                        "icc": "valor_escolhido",
                        "dps": "valor_escolhido",
                        "temp": "valor_escolhido",
                        "acessocabos": "valor_escolhido"
                    }}

                    TEXTO DO DOCUMENTO:
                    {texto_arquivo[:6000]}
                    """
                    try:
                        res = requests.post(
                            "https://api.groq.com/openai/v1/chat/completions",
                            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                            json={
                                "model": modelo_selecionado,
                                "messages": [{"role": "user", "content": prompt_analise}],
                                "temperature": 0.0,
                                "response_format": {"type": "json_object"}
                            },
                            timeout=20
                        )
                        if res.status_code == 200:
                            dados = json.loads(res.json()["choices"][0]["message"]["content"])
                            if dados.get("icc") in OPCOES_ICC: st.session_state["icc"] = dados["icc"]
                            if dados.get("dps") in OPCOES_DPS: st.session_state["dps"] = dados["dps"]
                            if dados.get("temp") in OPCOES_TEMP: st.session_state["temp"] = dados["temp"]
                            if dados.get("acessocabos") in OPCOES_ACESSOCABOS: st.session_state["acessocabos"] = dados["acessocabos"]
                            
                            st.success("✨ Campos do formulário atualizados com sucesso com base na documentação!")
                            st.rerun()
                        else:
                            st.error(f"Erro na API Groq ({res.status_code}): {res.text}")
                    except Exception as e:
                        st.error(f"Erro ao conectar com o serviço de IA: {e}")

    except Exception as e:
        st.error(f"Erro ao processar o arquivo anexado: {e}")

st.markdown("<br>", unsafe_allow_html=True)

# Layout Principal
col_form, col_summary = st.columns([1.25, 0.75], gap="large")

with col_form:
    st.markdown('''
    <div class="card-box">
        <div class="card-header">📐 1. Parâmetros Construtivos & Elétricos Gerais</div>
    ''', unsafe_allow_html=True)
    
    opcoes_altura = ["Não informado", "2.000 mm (Padrão)", "1.200 mm a 1.600 mm", "1.600 mm a 2.000 mm", "2.000 mm a 2.300 mm"]
    opcoes_profundidade = ["Não informado", "600 mm (Padrão)", "400 mm a 600 mm", "600 mm a 800 mm", "800 mm a 1.000 mm"]

    c1, c2 = st.columns(2)
    with c1:
        icc = st.selectbox("Corrente Curto (Icc):", OPCOES_ICC, index=OPCOES_ICC.index(st.session_state["icc"]))
        dps_classe = st.selectbox("Classe DPS:", OPCOES_DPS, index=OPCOES_DPS.index(st.session_state["dps"]))
        temp_ambiente = st.selectbox("Temp. Ambiente Máxima:", OPCOES_TEMP, index=OPCOES_TEMP.index(st.session_state["temp"]))
    with c2:
        entrada_saida_cabos = st.selectbox("Acesso Cabos:", OPCOES_ACESSOCABOS, index=OPCOES_ACESSOCABOS.index(st.session_state["acessocabos"]))
        altura_limite = st.selectbox("Limite Altura:", opcoes_altura)
        profundidade_limite = st.selectbox("Limite Profundidade:", opcoes_profundidade)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Coluna Lateral: Resumo das Pendências / RFI
with col_summary:
    st.markdown(f'''
    <div style="position: sticky; top: 20px;">
        <div style="background: #111827; border: 1px solid #1F2937; border-radius: 10px; padding: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                <span style="font-size: 0.9rem; font-weight: 700; color: #F3F4F6;">PAINEL DE CONSOLIDAÇÃO</span>
                <span style="background: #0284C7; color: #FFF; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 600;">{tipo_painel.split(' ')[0]}</span>
            </div>
    ''', unsafe_allow_html=True)

    btn_processar = st.button("RUN AUDIT / GERAR RFI ➔")

    if btn_processar:
        pendencias = []

        if icc == "Não informado": pendencias.append("Qual é a corrente de curto-circuito (Icc em kA) no ponto de instalação?")
        if dps_classe == "Não informado": pendencias.append("Qual é a classe de proteção do DPS exigida?")
        if temp_ambiente == "Não informado": pendencias.append("Qual é a temperatura ambiente máxima no local?")
        if entrada_saida_cabos == "Não informado": pendencias.append("Qual a direção de entrada e saída dos cabos (superior ou inferior)?")

        st.markdown("<br>", unsafe_allow_html=True)
        if pendencias:
            st.markdown(f'''
            <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid #F59E0B; padding: 10px 14px; border-radius: 6px; font-size: 0.8rem; color: #FBBF24; font-family: 'JetBrains Mono', monospace; margin-bottom: 12px;">
                ⚠️ {len(pendencias)} PENDÊNCIA(S) DETECTADA(S)
            </div>
            ''', unsafe_allow_html=True)

            for idx, d in enumerate(pendencias, 1):
                st.markdown(f'<div class="pending-item"><b>{idx}.</b> {d}</div>', unsafe_allow_html=True)
        else:
            st.markdown('''
            <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid #10B981; padding: 12px; border-radius: 6px; font-size: 0.85rem; color: #34D399; text-align: center;">
                ✓ NENHUMA PENDÊNCIA ENCONTRADA! TODOS OS DADOS FORAM PREENCHIDOS.
            </div>
            ''', unsafe_allow_html=True)

    st.markdown('</div></div>', unsafe_allow_html=True)