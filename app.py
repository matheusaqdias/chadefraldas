import streamlit as st
import random
import requests
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from PIL import Image
from io import BytesIO

# ===============================
# FUNÇÃO PARA CARREGAR IMAGEM
# ===============================
def carregar_fundo():
    try:
        # Tenta carregar localmente
        img = Image.open("assets/fundo.png")
    except FileNotFoundError:
        # Se não achar local, pega da URL
        url = "https://github.com/matheusaqdias/chadefraldas/raw/main/assets/fundo.png"
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
    return img

# ===============================
# FUNÇÃO PARA DEFINIR BACKGROUND
# ===============================
def set_background(img):
    # Converte imagem em base64
    import base64
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    # CSS para fundo
    page_bg_img = f"""
    <style>
    body {{
        background-image: url("data:image/png;base64,{img_str}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    .stApp {{
        background-color: rgba(0,0,0,0);
    }}
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)

# ===============================
# CARREGA E DEFINE FUNDO
# ===============================
fundo = carregar_fundo()
set_background(fundo)

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
FRALDAS = {"P": 21, "M": 45, "G": 21}

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

    with smtplib.SMTP("smtp.gmail.com", 587) as s:
        s.starttls()
        s.login(EMAIL, EMAIL_SENHA)
        s.send_message(msg)

# ===============================
# CONTEÚDO CENTRAL EM DIV TRANSPARENTE
# ===============================
st.markdown(
    """
    <div style="background-color: rgba(255,255,255,0.85);
                padding: 30px;
                border-radius: 15px;
                max-width: 600px;
                margin: 50px auto;
                text-align: center;">
    <h1>🍼 Chá de Fraldas</h1>
    <p>Preencha seus dados para receber o tamanho da fralda:</p>
    </div>
    """,
    unsafe_allow_html=True
)

# ===============================
# FORMULÁRIO
# ===============================
with st.form(key="form_participacao"):
    nome = st.text_input("Nome completo")
    email = st.text_input("E-mail")
    submit = st.form_submit_button("Confirmar participação")

if submit:
    if not nome or not email:
        st.warning("Preencha nome e e-mail.")
    elif email.lower() in st.session_state["emails_usados"]:
        st.error("Este e-mail já participou do sorteio.")
    else:
        tamanho = sortear_tamanho()
        if tamanho is None:
            st.error("Todas as fraldas já foram distribuídas. Obrigado!")
        else:
            data = datetime.now().strftime("%d/%m/%Y")
            sucesso = enviar_para_google_forms(nome, email, tamanho, data)
            if sucesso:
                st.session_state["emails_usados"].add(email.lower())
                enviar_email(email, nome, tamanho)
                st.success(f"Participação confirmada! 🎉\n\nTamanho sorteado: **{tamanho}**")
            else:
                st.error("Erro ao registrar no formulário. Tente novamente.")
