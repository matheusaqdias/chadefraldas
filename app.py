import streamlit as st
import random
import requests
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import base64

# Função para definir imagem de fundo usando base64
def set_bg_image(image_file):
    try:
        with open(image_file, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        st.markdown(
            f"""
            <style>
            body {{
                background-image: url("data:image/png;base64,{encoded}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    except FileNotFoundError:
        st.error(f"Imagem '{image_file}' não encontrada!")

# Use a função
set_bg_image("assets/fundo.png")

# ===============================
# SECRETS
# ===============================
EMAIL = st.secrets["EMAIL"]
EMAIL_SENHA = st.secrets["EMAIL_SENHA"]
FORM_URL = st.secrets["FORM_URL"]

# ===============================
# GOOGLE FORMS (IDs reais)
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
# INICIALIZA SESSION STATE
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

    r = requests.post(
        FORM_URL,
        data=payload,
        timeout=10
    )

    return r.status_code == 200


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

    with smtplib.SMTP("smtp.gmail.com", 587) as s:
        s.starttls()
        s.login(EMAIL, EMAIL_SENHA)
        s.send_message(msg)

# ===============================
# STREAMLIT APP
# ===============================
st.title("🍼 Chá de Fraldas")

st.write("Preencha seus dados para receber o tamanho da fralda:")


nome = st.text_input("Nome completo")
email = st.text_input("E-mail")

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
