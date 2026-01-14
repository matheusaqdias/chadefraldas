import streamlit as st
import random
import requests
from datetime import datetime
import smtplib
from email.message import EmailMessage

st.title("👶 Chá de Fraldas da Maria Teresa")

FRALDAS = {"P": 21, "M": 45, "G": 21}

if "fraldas" not in st.session_state:
    st.session_state.fraldas = FRALDAS.copy()

# CONFIG
FORM_ID = st.secrets["FORM_ID"]
EMAIL = st.secrets["EMAIL"]
EMAIL_SENHA = st.secrets["EMAIL_SENHA"]

# IDs dos campos do Form
ENTRY_NOME = "entry.823027402"
ENTRY_EMAIL = "entry.732833617"
ENTRY_TAMANHO = "entry.1668127447"
ENTRY_DATA = "entry.47767135"

1YfvHozok8Wc1fUXG7eUuW-rZ6dbwkLW0NQudg5M0D2k


def enviar_para_form(nome, email, tamanho):
    url = f"https://docs.google.com/forms/d/e/{FORM_ID}/formResponse"
    data = {
        ENTRY_NOME: nome,
        ENTRY_EMAIL: email,
        ENTRY_TAMANHO: tamanho,
        ENTRY_DATA: datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    }
    requests.post(url, data=data)

def enviar_email(dest, nome, tamanho):
    msg = EmailMessage()
    msg["Subject"] = "Confirmação Chá de Fraldas"
    msg["From"] = EMAIL
    msg["To"] = dest
    msg.set_content(
        f"Olá {nome},\n\n"
        f"O tamanho da fralda ficou: {tamanho}\n\n"
        "Obrigado por participar!"
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(EMAIL, EMAIL_SENHA)
        s.send_message(msg)

nome = st.text_input("Nome")
email = st.text_input("E-mail")

if st.button("Confirmar"):
    disponiveis = [k for k, v in st.session_state.fraldas.items() if v > 0]
    if not disponiveis:
        st.error("Fraldas esgotadas.")
    else:
        tamanho = random.choice(disponiveis)
        st.session_state.fraldas[tamanho] -= 1

        enviar_para_form(nome, email, tamanho)
        enviar_email(email, nome, tamanho)

        st.success(f"{nome}, sua fralda é tamanho {tamanho}")
