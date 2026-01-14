import streamlit as st
import random
import requests
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

# ===============================
# CONFIGURAÇÕES (SECRETS)
# ===============================
EMAIL = st.secrets["EMAIL"]
EMAIL_SENHA = st.secrets["EMAIL_SENHA"]

FORM_URL = st.secrets["FORM_URL"]

# IDs reais do seu Google Form
ENTRY_NOME = "entry.823027402"
ENTRY_EMAIL = "entry.732833617"
ENTRY_TAMANHO = "entry.1668127447"
ENTRY_DATA = "entry.47767135"

# ===============================
# FUNÇÕES
# ===============================

def sortear_tamanho():
    tamanhos = ["RN", "P", "M", "G", "XG"]
    pesos = [1, 2, 3, 3, 2]
    return random.choices(tamanhos, weights=pesos, k=1)[0]


def enviar_para_google_forms(nome, email, tamanho, data):
    payload = {
        ENTRY_NOME: nome,
        ENTRY_EMAIL: email,
        ENTRY_TAMANHO: tamanho,
        ENTRY_DATA: data
    }

    response = requests.post(
        FORM_URL,
        data=payload,
        timeout=10
    )

    return response.status_code


def enviar_email(destinatario, nome, tamanho):
    msg = MIMEText(
        f"""
Olá, {nome}!

Obrigado por participar do Chá de Fraldas 😊

O tamanho de fralda que ficou para você foi:
👉 {tamanho}

Aguardamos você no chá!

Com carinho ❤️
"""
    )

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

st.title("🍼 Chá de Fraldas – Confirmação")

st.write("Preencha os dados abaixo para receber o tamanho da fralda:")

nome = st.text_input("Nome completo")
email = st.text_input("E-mail")

if st.button("Confirmar participação"):
    if not nome or not email:
        st.warning("Preencha nome e e-mail.")
    else:
        tamanho = sortear_tamanho()
        data = datetime.now().strftime("%d/%m/%Y")

        status = enviar_para_google_forms(nome, email, tamanho, data)

        if status == 200:
            enviar_email(email, nome, tamanho)
            st.success(f"Participação confirmada! 🎉\n\nTamanho sorteado: **{tamanho}**")
        else:
            st.error("Erro ao registrar no formulário. Tente novamente.")
