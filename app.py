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

try:
    if "GROQ_API_KEY" in st.secrets:
        api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    pass

if not api_key:
    api_key = os.environ.get("GROQ_API_KEY", "")

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
        "meta-llama/llama-3.1-8b-instant",
        "meta-llama/llama-3.3-70b-versatile"
    ]
)

# ------------------------------------------------------------------------------
# OPÇÕES TÉCNICAS COMPLETAS PARA O FORMULÁRIO
# ------------------------------------------------------------------------------
OPCOES_TENSAO = ["Não informado", "220V", "380V", "440V", "480V"]
OPCOES_ICC = ["Não informado", "10 kA", "15 kA", "20 kA", "25 kA", "30 kA", "45 kA", "65 kA", "85 kA"]
OPCOES_IP = ["Não informado", "IP31", "IP40", "IP42", "IP54", "IP55", "IP65"]
OPCOES_FORMA = ["Não informado", "Forma 1", "Forma 2a", "Forma 2b", "Forma 3a", "Forma 3b", "Forma 4a", "Forma 4b"]
OPCOES_DPS = ["Não informado", "Classe I", "Classe II", "Classe I + II", "Classe III", "Não terá"]
OPCOES_CORRENTE_BUS = ["Não informado", "400 A", "630 A", "800 A", "1000 A", "1250 A", "1600 A", "2000 A", "2500 A", "3150 A", "4000 A"]
OPCOES_MATERIAL_BUS = ["Não informado", "Cobre Eletrolítico", "Alumínio"]
OPCOES_TEMP = ["Não informado", "20 °C", "25 °C", "30 °C", "35 °C", "40 °C", "45 °C"]
OPCOES_ACESSOCABOS = ["Não informado", "Por Baixo (Inferior)", "Por Cima (Superior)", "Mista (Entrada Cima / Saída Baixo)", "Mista (Entrada Baixo / Saída Cima)"]
OPCOES_COR = ["Não informado", "RAL 7032", "RAL 7035", "Munsell N6.5"]

CAMPOS_CHAVE = [
    "tensao", "icc", "ip", "forma", "dps", 
    "corrente_bus", "material_bus", "temp", "acessocabos", "cor"
]

def inicializar_campos():
    for key in CAMPOS_CHAVE:
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
            
        st.success(f"✓ Arquivo '{arquivo_anexado.name}' carregado com sucesso!")
        
        # BOTÃO PARA EXTRAÇÃO COMPLETA
        if st.button("🤖 ANALISAR DOCUMENTAÇÃO COMPLETA E AUTO-PREENCHER"):
            if not api_key:
                st.error("Insira uma chave válida da Groq na barra lateral ou nos Secrets!")
            else:
                with st.spinner("IA executando varredura técnica completa no edital..."):
                    prompt_analise = f"""
                    Você é um engenheiro eletricista analista de especificações técnicas para painéis elétricos.
                    Examine o documento fornecido e extraia exatamente as propriedades solicitadas.
                    
                    Você DEVE mapear cada campo exclusivamente para um dos valores válidos abaixo:
                    - tensao: {OPCOES_TENSAO}
                    - icc: {OPCOES_ICC}
                    - ip: {OPCOES_IP}
                    - forma: {OPCOES_FORMA}
                    - dps: {OPCOES_DPS}
                    - corrente_bus: {OPCOES_CORRENTE_BUS}
                    - material_bus: {OPCOES_MATERIAL_BUS}
                    - temp: {OPCOES_TEMP}
                    - acessocabos: {OPCOES_ACESSOCABOS}
                    - cor: {OPCOES_COR}

                    Retorne EXCLUSIVAMENTE um JSON sem formatação adicional:
                    {{
                        "tensao": "valor",
                        "icc": "valor",
                        "ip": "valor",
                        "forma": "valor",
                        "dps": "valor",
                        "corrente_bus": "valor",
                        "material_bus": "valor",
                        "temp": "valor",
                        "acessocabos": "valor",
                        "cor": "valor"
                    }}

                    TEXTO DO DOCUMENTO:
                    {texto_arquivo[:8000]}
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
                            timeout=25
                        )
                        if res.status_code == 200:
                            dados = json.loads(res.json()["choices"][0]["message"]["content"])
                            
                            mapeamento = {
                                "tensao": OPCOES_TENSAO,
                                "icc": OPCOES_ICC,
                                "ip": OPCOES_IP,
                                "forma": OPCOES_FORMA,
                                "dps": OPCOES_DPS,
                                "corrente_bus": OPCOES_CORRENTE_BUS,
                                "material_bus": OPCOES_MATERIAL_BUS,
                                "temp": OPCOES_TEMP,
                                "acessocabos": OPCOES_ACESSOCABOS,
                                "cor": OPCOES_COR
                            }
                            
                            for campo, lista_opcoes in mapeamento.items():
                                if dados.get(campo) in lista_opcoes:
                                    st.session_state[campo] = dados[campo]
                            
                            st.success("✨ Auditoria concluída! Formulário preenchido automaticamente.")
                            st.rerun()
                        else:
                            st.error(f"Erro na API Groq ({res.status_code}): {res.text}")
                    except Exception as e:
                        st.error(f"Erro ao conectar com a IA: {e}")

    except Exception as e:
        st.error(f"Erro ao ler arquivo: {e}")

st.markdown("<br>", unsafe_allow_html=True)

# Layout Principal em Duas Colunas
col_form, col_summary = st.columns([1.3, 0.7], gap="large")

with col_form:
    st.markdown('''
    <div class="card-box">
        <div class="card-header">📐 1. Parâmetros Elétricos & Operacionais</div>
    ''', unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        tensao = st.selectbox("Tensão Nominal:", OPCOES_TENSAO, index=OPCOES_TENSAO.index(st.session_state["tensao"]))
        icc = st.selectbox("Corrente Curto (Icc):", OPCOES_ICC, index=OPCOES_ICC.index(st.session_state["icc"]))
        corrente_bus = st.selectbox("Corrente Barramento:", OPCOES_CORRENTE_BUS, index=OPCOES_CORRENTE_BUS.index(st.session_state["corrente_bus"]))
        material_bus = st.selectbox("Material Barramento:", OPCOES_MATERIAL_BUS, index=OPCOES_MATERIAL_BUS.index(st.session_state["material_bus"]))
        dps_classe = st.selectbox("Classe DPS:", OPCOES_DPS, index=OPCOES_DPS.index(st.session_state["dps"]))

    with c2:
        ip_grau = st.selectbox("Grau de Proteção (IP):", OPCOES_IP, index=OPCOES_IP.index(st.session_state["ip"]))
        forma_seg = st.selectbox("Forma de Segregação:", OPCOES_FORMA, index=OPCOES_FORMA.index(st.session_state["forma"]))
        temp_ambiente = st.selectbox("Temp. Ambiente Máx:", OPCOES_TEMP, index=OPCOES_TEMP.index(st.session_state["temp"]))
        entrada_saida_cabos = st.selectbox("Acesso dos Cabos:", OPCOES_ACESSOCABOS, index=OPCOES_ACESSOCABOS.index(st.session_state["acessocabos"]))
        cor_pintura = st.selectbox("Pintura / Cor:", OPCOES_COR, index=OPCOES_COR.index(st.session_state["cor"]))
        
    st.markdown('</div>', unsafe_allow_html=True)

# Coluna de Consolidação e Geração do RFI
with col_summary:
    st.markdown(f'''
    <div style="position: sticky; top: 20px;">
        <div style="background: #111827; border: 1px solid #1F2937; border-radius: 10px; padding: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                <span style="font-size: 0.9rem; font-weight: 700; color: #F3F4F6;">PAINEL DE AUDITORIA DE RFI</span>
                <span style="background: #0284C7; color: #FFF; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 600;">{tipo_painel.split(' ')[0]}</span>
            </div>
    ''', unsafe_allow_html=True)

    btn_processar = st.button("RUN AUDIT / GERAR RFI ➔")

    if btn_processar:
        pendencias = []

        if tensao == "Não informado": pendencias.append("Qual a tensão de operação nominal do painel (V)?")
        if icc == "Não informado": pendencias.append("Qual a corrente suportável de curto-circuito (Icc em kA)?")
        if corrente_bus == "Não informado": pendencias.append("Qual a corrente nominal do barramento principal (A)?")
        if material_bus == "Não informado": pendencias.append("Qual o material do barramento (Cobre Eletrolítico ou Alumínio)?")
        if ip_grau == "Não informado": pendencias.append("Qual o grau de proteção IP exigido do invólucro?")
        if forma_seg == "Não informado": pendencias.append("Qual a forma construtiva de segregação interna (IEC 61439)?")
        if dps_classe == "Não informado": pendencias.append("Qual a classe dos Supressores de Surto (DPS)?")
        if temp_ambiente == "Não informado": pendencias.append("Qual a temperatura ambiente máxima do ambiente de instalação?")
        if entrada_saida_cabos == "Não informado": pendencias.append("Qual o sentido de entrada e saída dos cabos de força e comando?")
        if cor_pintura == "Não informado": pendencias.append("Qual a especificação da cor do acabamento da pintura?")

        st.markdown("<br>", unsafe_allow_html=True)
        if pendencias:
            st.markdown(f'''
            <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid #F59E0B; padding: 10px 14px; border-radius: 6px; font-size: 0.8rem; color: #FBBF24; font-family: 'JetBrains Mono', monospace; margin-bottom: 12px;">
                ⚠️ {len(pendencias)} DUVIDA(S) TÉCNICA(S) DETECTADA(S)
            </div>
            ''', unsafe_allow_html=True)

            for idx, d in enumerate(pendencias, 1):
                st.markdown(f'<div class="pending-item"><b>{idx}.</b> {d}</div>', unsafe_allow_html=True)
        else:
            st.markdown('''
            <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid #10B981; padding: 12px; border-radius: 6px; font-size: 0.85rem; color: #34D399; text-align: center;">
                ✓ NENHUMA PENDÊNCIA TÉCNICA! O PAINEL ESTÁ TOTALMENTE ESPECIFICADO.
            </div>
            ''', unsafe_allow_html=True)

    st.markdown('</div></div>', unsafe_allow_html=True)
