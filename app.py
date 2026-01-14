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
    # Caminho dinâmico para a imagem na pasta assets
    diretorio_atual = os.path.dirname(__file__)
    caminho_imagem = os.path.join(diretorio_atual, 'assets', 'fundo.png')
    
    try:
        # Tenta converter a imagem para base64
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
    except Exception as e:
        # Se falhar (ex: arquivo não encontrado), usa um fundo de cor sólida
        fundo_css = "<style>.stApp { background-color: #FDFCF0; }"
        st.error(f"Erro ao carregar fundo: {e}")

    # Injeção do CSS completo
    st.markdown(
        fundo_css + 
        """
        /* Estilização de Textos */
        h1, h2, h3, p, label, .stMarkdown, .stSuccess, .stError, .stWarning {
            color: black !important;
            font-weight: 600 !important;
        }

        /* Estilo das caixas de input */
        div[data-baseweb="input"] {
            background-color: rgba(255, 255, 255, 0.8) !important;
            border-radius: 10px !important;
        }

        /* Estilo do botão */
        .stButton>button {
            background-color: #333333 !important;
            color: white !important;
            border-radius: 10px;
            width: 100%;
            height: 3em;
            font-weight: bold;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# Chamar a função de estilo
aplicar_estilo_customizado()

# ===============================
# SECRETS (Devem estar no Streamlit Cloud)
# ===============================
try:
    EMAIL = st.secrets["EMAIL"]
    EMAIL_SENHA = st.secrets["EMAIL_SENHA"]
    FORM_URL = st.secrets["FORM_URL"]
except Exception as e:
    st.error("Erro: Verifique se as Secrets (EMAIL, EMAIL_SENHA, FORM_URL) estão configuradas no Streamlit Cloud.")
    st.stop()

# ===============================
# CONFIGURAÇÕES GOOGLE FORMS E FRALDAS
# ===============================
ENTRY_NOME = "entry.823027402"
ENTRY_EMAIL = "entry.732833617"
ENTRY_TAMANHO = "entry.1668127447"
ENTRY_DATA = "entry.47767135"

FRALDAS = {
    "P": 21,
    "M": 45,
    "G": 21
}

# ===============================
# INICIALIZA SESSION STATE
# ===============================
if "estoque_fraldas" not in st.session_state:
    st.session_state["estoque_fraldas"] = []
    for tamanho, qtd in FRALDAS.items():
        st.session_state["estoque_fraldas"].extend([tamanho] * qtd)

if "emails_usados" not in st.session_state:
    st.session_state["emails_usados"] = set()

# ===============================
# FUNÇÕES DE LÓGICA
# ===============================
def sortear_tamanho():
    if not st.session_state["estoque_fraldas"]:
        return None
    tamanho = random.choice(st.session_state["estoque_fraldas"])
    st.session_state["estoque_fraldas"].remove(tamanho)
    return tamanho

def enviar_para_google_forms(nome, email, tamanho, data):
    payload = {
        ENTRY_NOME: nome,
        ENTRY_EMAIL: email,
        ENTRY_TAMANHO: tamanho,
        ENTRY_DATA: data
    }
    try:
        r = requests.post(FORM_URL, data=payload, timeout=10)
        return r.status_code == 200
    except:
        return False

def enviar_email(destinatario, nome, tamanho):
    corpo = f"""
Olá, {nome}!

Obrigado por participar do nosso Chá de Fraldas 😊

O tamanho de fralda que ficou para você foi:
👉 {tamanho}

Aguardamos você no chá!

Com carinho ❤️
"""
    msg = MIMEText(corpo)
    msg["Subject"] = "Confirmação – Chá de Fraldas"
    msg["From"] = EMAIL
    msg["To"] = destinatario

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as s:
            s.starttls()
            s.login(EMAIL, EMAIL_SENHA)
            s.send_message(msg)
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")

# ===============================
# LAYOUT DO APP
# ===============================
col1, col_central, col3 = st.columns([1, 2, 1])

with col_central:
    st.title("🍼 Chá de Fraldas")
    st.write("Preencha seus dados para receber o tamanho da fralda:")

    nome = st.text_input("Nome completo", placeholder="Seu nome aqui")
    email = st.text_input("E-mail", placeholder="seuemail@exemplo.com")

    if st.button("Confirmar participação"):
        if not nome or not email:
            st.warning("⚠️ Por favor, preencha nome e e-mail.")
            st.stop()

        if email.lower() in st.session_state["emails_usados"]:
            st.error("❌ Este e-mail já participou do sorteio.")
            st.stop()

        tamanho = sortear_tamanho()

        if tamanho is None:
            st.error("😔 Todas as fraldas já foram distribuídas. Obrigado!")
            st.stop()

        data_atual = datetime.now().strftime("%d/%m/%Y")

        sucesso = enviar_para_google_forms(nome, email, tamanho, data_atual)

        if sucesso:
            st.session_state["emails_usados"].add(email.lower())
            enviar_email(email, nome, tamanho)
            st.success(f"Participação confirmada! 🎉\n\nSeu tamanho sorteado foi: **{tamanho}**\nEnviamos uma confirmação para seu e-mail.")
        else:
            st.error("Erro ao registrar no formulário. Verifique sua conexão.")