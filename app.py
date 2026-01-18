import streamlit as st
import random
import requests
import smtplib
import base64
import os
from email.mime.text import MIMEText
from datetime import datetime

# ===============================
# CONFIGURAÇÃO DA PÁGINA
# ===============================
st.set_page_config(page_title="Chá de Fraldas", page_icon="🍼")

# ===============================
# FUNÇÃO PARA CARREGAR IMAGEM LOCAL
# ===============================
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def aplicar_estilo_customizado():
    diretorio_atual = os.path.dirname(__file__)
    caminho_imagem = os.path.join(diretorio_atual, 'assets', 'fundo.png')
    
    try:
        bin_str = get_base64_of_bin_file(caminho_imagem)
        fundo_css = f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{bin_str}");
            background-attachment: fixed;
            background-size: cover;
            background-position: center;
        }}
        """
    except Exception:
        fundo_css = "<style>.stApp {{ background-color: #FDFCF0; }}"

    st.markdown(
        fundo_css + 
        """
        <style>
        /* 1. Título Customizado */
        .titulo-custom {
            font-family: 'Times New Roman', Times, serif;
            font-size: 3rem;
            color: #000000 !important;
            text-align: left;
            margin-bottom: 10px;
            font-weight: bold;
            line-height: 1.1;
            -webkit-text-fill-color: #000000 !important;
        }

        /* 2. Legendas (Labels) - SEMPRE PRETO E SEM FUNDO */
        label, .stMarkdown p, [data-testid="stWidgetLabel"] p {
            background-color: transparent !important;
            color: #000000 !important;
            font-weight: 800 !important;
            font-size: 1.1rem !important;
            -webkit-text-fill-color: #000000 !important;
        }

        /* 3. Caixas de Input - SEMPRE ESCURAS */
        div[data-baseweb="input"], [data-testid="stTextInput"] > div {
            background-color: #262730 !important;
            border-radius: 15px !important;
            border: 1px solid rgba(255,255,255,0.2) !important;
        }
        
        /* TEXTO DIGITADO - FORÇAR BRANCO SEMPRE */
        input {
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
        }

        /* Cor do texto de exemplo (placeholder) */
        input::placeholder {
            color: rgba(255,255,255,0.5) !important;
            -webkit-text-fill-color: rgba(255,255,255,0.5) !important;
        }

        /* 4. Estilo do botão ROSA */
        .stButton>button {
            background-color: #f7d1d7 !important;
            color: #000000 !important;
            border-radius: 12px;
            width: 100%;
            height: 3.5em;
            font-weight: bold;
            border: none;
            font-size: 1.1rem;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
        }
        
        .stButton>button:hover {
            background-color: #f2b6c1 !important;
            color: #000000 !important;
            border: none !important;
        }

        /* Limpeza de elementos do Streamlit */
        [data-testid="stHeader"] {background: rgba(0,0,0,0);}
        [data-testid="stToolbar"] {visibility: hidden;}
        </style>
        """,
        unsafe_allow_html=True
    )
aplicar_estilo_customizado()

# ===============================
# SECRETS
# ===============================
try:
    EMAIL = st.secrets["EMAIL"]
    EMAIL_SENHA = st.secrets["EMAIL_SENHA"]
    FORM_URL = st.secrets["FORM_URL"]
except Exception:
    st.error("Erro: Verifique as Secrets no painel do Streamlit.")
    st.stop()

# ===============================
# CONFIGURAÇÕES E LÓGICA
# ===============================
ENTRY_NOME = "entry.823027402"
ENTRY_EMAIL = "entry.732833617"
ENTRY_TAMANHO = "entry.1668127447"
ENTRY_DATA = "entry.47767135"

FRALDAS = {"P": 21, "M": 45, "G": 21}

if "estoque_fraldas" not in st.session_state:
    st.session_state["estoque_fraldas"] = []
    for tamanho, qtd in FRALDAS.items():
        st.session_state["estoque_fraldas"].extend([tamanho] * qtd)

if "emails_usados" not in st.session_state:
    st.session_state["emails_usados"] = set()

def sortear_tamanho():
    if not st.session_state["estoque_fraldas"]: return None
    tamanho = random.choice(st.session_state["estoque_fraldas"])
    st.session_state["estoque_fraldas"].remove(tamanho)
    return tamanho

# ===============================
# LAYOUT
# ===============================
col1, col_central, col3 = st.columns([0.5, 2, 0.5])

with col_central:
    # Título estilizado com HTML para aceitar a fonte serifada
    st.markdown('<h1 class="titulo-custom">🍼 Chá de Bebê da Maria Teresa 🍼<br></h1>', unsafe_allow_html=True)
    
    st.write("Preencha seus dados para receber o tamanho da fralda:")

    nome = st.text_input("Nome completo", placeholder="Seu nome aqui")
    email = st.text_input("E-mail", placeholder="seuemail@exemplo.com")

    if st.button("Confirmar participação"):
        if not nome or not email:
            st.warning("⚠️ Por favor, preencha nome e e-mail.")
            st.stop()

        if email.lower() in st.session_state["emails_usados"]:
            st.error("❌ Este e-mail já participou.")
            st.stop()

        tamanho = sortear_tamanho()
        if tamanho is None:
            st.error("😔 Fraldas esgotadas!")
            st.stop()

        # Lógica de envio (Google Forms e E-mail)
        data_atual = datetime.now().strftime("%d/%m/%Y")
        payload = {ENTRY_NOME: nome, ENTRY_EMAIL: email, ENTRY_TAMANHO: tamanho, ENTRY_DATA: data_atual}
        
        try:
            r = requests.post(FORM_URL, data=payload, timeout=10)
            if r.status_code == 200:
                st.session_state["emails_usados"].add(email.lower())
                st.success(f"Participação confirmada! 🎉\n\nSeu tamanho: **{tamanho}**")
            else:
                st.error("Erro ao registrar dados.")
        except:
            st.error("Erro de conexão.")