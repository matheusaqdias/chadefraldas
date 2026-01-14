import streamlit as st
import random
import requests
import smtplib
import base64
from email.mime.text import MIMEText
from datetime import datetime

# ===============================
# BACKGROUND (IMAGEM SEM CORTE)
# ===============================
def set_background(image_path):
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpeg;base64,{encoded}");
        background-size: contain;
        background-position: center top;
        background-repeat: no-repeat;
        background-color: #fdecef;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


set_background("assets/background.jpeg")

# ===============================
# CSS GLOBAL
# ===============================
st.markdown("""
<style>

/* ---------- CARD ---------- */
.box {
    background-color: rgba(255,255,255,0.96);
    padding: 28px;
    border-radius: 18px;
    max-width: 520px;
    margin: 80px auto;
    box-shadow: 0 10px 30px rgba(0,0,0,0.15);
}

/* ---------- TEXTOS ---------- */
.box h1, 
.box h2, 
.box h3, 
.box p, 
.box label, 
.box span {
    color: #1f2937 !important;
    text-align: center;
}

/* ---------- INPUTS ---------- */
.stTextInput > div > div > input {
    background-color: #ffffff !important;
    color: #111827 !important;
    border-radius: 10px;
    border: 1px solid #d1d5db;
    padding: 10px;
}

/* Placeholder */
.stTextInput input::placeholder {
    color: #9ca3af;
}

/* ---------- BOTÃO ---------- */
.stButton > button {
    background-color: #ec4899;
    color: white !important;
    border-radius: 14px;
    padding: 12px;
    font-weight: 600;
    width: 100%;
    border: none;
}

.stButton > button:hover {
    background-color: #db2777;
}

/* ---------- MENSAGENS ---------- */
.stSuccess, .stError, .stWarning {
    border-radius: 12px;
}

/* ---------- REMOVE FUNDO ESCURO ---------- */
[data-testid="stAppViewContainer"] {
    background-color: transparent;
}

</style>
""", unsafe_allow_html=True)

# ===============================
# SECRETS
# ===============================
EMAIL = st.secrets["EMAIL"]
EMAIL_SENHA = st.secrets["EMAIL_SENHA"]
FORM_URL = st.secrets["FORM_URL"]

# ===============================
# GOOGLE FORMS (IDs)
# ===============================
ENTRY_NOME = "entry.823027402"
ENTRY_EMAIL = "entry.732833617"
ENTRY_TAMANHO = "entry.1668127447"
ENTRY_DATA = "entry.47767135"

# ===============================
# CONFIGURAÇÃO DAS FRALDAS
# ===============================
FRALDAS = {
    "P": 21,
    "M": 45,
    "G": 21
}

# ===============================
# SESSION STATE
# ===============================
if "estoque_fraldas" not in st.session_state:
    st.session_state["estoque_fraldas"] = []
    for tamanho, qtd in FRALDAS.items():
        st.session_state["estoque_fraldas"].extend([tamanho] * qtd)

if "emails_usados" not in st.session_state:
    st.session_state["emails_usados"] = set()

# ===============================
# FUNÇÕES
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

    r = requests.post(FORM_URL, data=payload, timeout=10)
    return r.status_code == 200


def enviar_email(destinatario, nome, tamanho):
    corpo = f"""
Olá, {nome}!

Obrigado por participar do nosso Chá de Fraldas da Maria Teresa 😊

O tamanho de fralda que ficou para você foi:
👉 {tamanho}

Aguardamos você no chá!

Com carinho ❤️
"""

    msg = MIMEText(corpo)
    msg["Subject"] = "Confirmação – Chá de Fraldas"
    msg["From"] = EMAIL
    msg["To"] = destinatario

    with smtplib.SMTP("smtp.gmail.com", 587) as s:
        s.starttls()
        s.login(EMAIL, EMAIL_SENHA)
        s.send_message(msg)

# ===============================
# APP
# ===============================
st.markdown('<div class="box">', unsafe_allow_html=True)

st.title("🍼 Chá de Fraldas")
st.write("Preencha seus dados para receber o tamanho da fralda:")

nome = st.text_input("Nome completo", placeholder="Digite seu nome")
email = st.text_input("E-mail", placeholder="Digite seu e-mail")

if st.button("Confirmar participação"):
    if not nome or not email:
        st.warning("Preencha nome e e-mail.")
        st.stop()

    if email.lower() in st.session_state["emails_usados"]:
        st.error("Este e-mail já participou do sorteio.")
        st.stop()

    tamanho = sortear_tamanho()

    if tamanho is None:
        st.error("Todas as fraldas já foram distribuídas. Obrigado!")
        st.stop()

    data = datetime.now().strftime("%d/%m/%Y")

    sucesso = enviar_para_google_forms(nome, email, tamanho, data)

    if sucesso:
        st.session_state["emails_usados"].add(email.lower())
        enviar_email(email, nome, tamanho)
        st.success(f"Participação confirmada! 🎉\n\nTamanho sorteado: **{tamanho}**")
    else:
        st.error("Erro ao registrar no formulário. Tente novamente.")

st.markdown('</div>', unsafe_allow_html=True)
