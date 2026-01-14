import streamlit as st
import random
import requests
import smtplib
import base64
from email.mime.text import MIMEText
from datetime import datetime

# ===============================
# BACKGROUND (FORMA COMPATÍVEL)
# ===============================
def set_background(image_path):
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
        html, body, .stApp {{
            height: 100%;
            margin: 0;
        }}

        .stApp {{
            background-image: url("data:image/jpeg;base64,{encoded}");
            background-size: cover;
            background-position: center center;
            background-repeat: no-repeat;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


set_background("assets/background.jpeg")

# ===============================
# CSS DO CARD (LEGIBILIDADE)
# ===============================
st.markdown("""
<style>

.box {
    background-color: rgba(255,255,255,0.90);
    padding: 32px;
    border-radius: 22px;
    max-width: 520px;
    margin: 100px auto;
    box-shadow: 0 15px 40px rgba(0,0,0,0.25);
}

/* Textos */
.box h1, .box p, .box label {
    color: #111827 !important;
    text-align: center;
}

/* Inputs */
.stTextInput input {
    background-color: #ffffff !important;
    color: #111827 !important;
    border-radius: 12px;
    border: 1px solid #d1d5db;
    padding: 12px;
}

/* Botão */
.stButton > button {
    background-color: #ec4899;
    color: white !important;
    border-radius: 14px;
    padding: 12px;
    width: 100%;
    font-weight: 600;
    border: none;
}

.stButton > button:hover {
    background-color: #db2777;
}

/* Remove fundo padrão */
[data-testid="stAppViewContainer"] {
    background: transparent;
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
# GOOGLE FORMS
# ===============================
ENTRY_NOME = "entry.823027402"
ENTRY_EMAIL = "entry.732833617"
ENTRY_TAMANHO = "entry.1668127447"
ENTRY_DATA = "entry.47767135"

# ===============================
# FRALDAS
# ===============================
FRALDAS = {"P": 21, "M": 45, "G": 21}

# ===============================
# SESSION STATE
# ===============================
if "estoque_fraldas" not in st.session_state:
    st.session_state["estoque_fraldas"] = []
    for t, q in FRALDAS.items():
        st.session_state["estoque_fraldas"].extend([t] * q)

if "emails_usados" not in st.session_state:
    st.session_state["emails_usados"] = set()

# ===============================
# FUNÇÕES
# ===============================
def sortear_tamanho():
    if not st.session_state["estoque_fraldas"]:
        return None
    t = random.choice(st.session_state["estoque_fraldas"])
    st.session_state["estoque_fraldas"].remove(t)
    return t


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
    msg = MIMEText(f"""
Olá, {nome}!

Obrigado por participar do Chá de Fraldas da Maria Teresa 😊

O tamanho de fralda que ficou para você foi:
👉 {tamanho}

Com carinho ❤️
""")
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

nome = st.text_input("Nome completo")
email = st.text_input("E-mail")

if st.button("Confirmar participação"):
    if not nome or not email:
        st.warning("Preencha nome e e-mail.")
        st.stop()

    if email.lower() in st.session_state["emails_usados"]:
        st.error("Este e-mail já participou.")
        st.stop()

    tamanho = sortear_tamanho()
    if not tamanho:
        st.error("Todas as fraldas já foram distribuídas.")
        st.stop()

    data = datetime.now().strftime("%d/%m/%Y")

    if enviar_para_google_forms(nome, email, tamanho, data):
        st.session_state["emails_usados"].add(email.lower())
        enviar_email(email, nome, tamanho)
        st.success(f"Tamanho sorteado: **{tamanho}** 🎉")
    else:
        st.error("Erro ao registrar.")

st.markdown("</div>", unsafe_allow_html=True)
