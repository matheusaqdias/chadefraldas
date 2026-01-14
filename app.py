import streamlit as st
import random
import requests
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

# ===============================
# CONFIGURAÇÃO DA PÁGINA E CSS
# ===============================
st.set_page_config(page_title="Chá de Fraldas", page_icon="🍼")

def aplicar_estilo_customizado():
    st.markdown(
        f"""
        <style>
        /* 1. Imagem de fundo em toda a página */
        .stApp {{
            background-image: url("https://github.com/matheusaqdias/chadefraldas/blob/main/assets/fundo.png");
            background-attachment: fixed;
            background-size: cover;
            background-position: center;
        }}

        /* 2. Forçar todos os textos para PRETO */
        h1, h2, h3, p, label, .stMarkdown, .stSuccess, .stError, .stWarning {{
            color: black !important;
            font-weight: 600 !important;
        }}

        /* 3. Estilo das caixas de input (fundo branco semi-transparente) */
        div[data-baseweb="input"] {{
            background-color: rgba(255, 255, 255, 0.8) !important;
            border-radius: 10px !important;
        }}

        /* 4. Estilo do botão */
        .stButton>button {{
            background-color: #333333 !important;
            color: white !important;
            border-radius: 10px;
            width: 100%;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

aplicar_estilo_customizado()

# ===============================
# SECRETS
# ===============================
# Certifique-se de que esses valores estão no seu arquivo .streamlit/secrets.toml
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
# STREAMLIT APP (LAYOUT CENTRALIZADO)
# ===============================

# Criamos 3 colunas para centralizar o formulário no meio da tela
col1, col_central, col3 = st.columns([1, 2, 1])

with col_central:
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