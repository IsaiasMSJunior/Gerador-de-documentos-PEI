# app.py

import os
import streamlit as st
import firebase_admin
from firebase_admin import credentials, db

# === Credenciais embutidas ===
service_account_info = {
    "type": "service_account",
    "project_id": "gerador-de-documentos-pei",
    "private_key_id": "828aa53f8815622c59582b3b9da01986e28f5764",
    "private_key": """-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC1g+dtQAi6qvKi
u0vs13qecK68Bl1rs/puRL8OSNXqDtgG9Cd8YINWbuU44XDGSxK+SwnoKL71oV2G
tZ8sULsUZ7K4GD1u8wQoJ2JXWaho+BU6Iu2bywl+Qi4LsbIyZA3fbyFLSo1diZMy
jEXD69pgYQdCRqCtrR/p2Lppbqi/XfrhyHFbmuVu2Hk0r0CGrG+y5DDYuHsLW6ec
5txqFakb+wd0gb5YF3GEq45Z662rG6x0pgMKhr3O9GMngPuxIqwLgZt4bnA5bBJy
pOmztpLV6Io8KuJqfDmvLhpUDq/wWMSZLlUek4rxQnMpc5ypoTyvmLXUqz/yko+S
nJaKG2IXAgMBAAECggEAUsc6QeT7diGisJro57RnC52I2l+uuADmmuYIGVwXDfxC
AX3UChE7pC3DpHqPQycWf6jZ9kGqwHscG2R1mDCi+I3H/9OyJIh4I1W+r+ZH+sL0
b0RhhvSDukw1EokxonBlsTlNfjgcGwW0Fs/Iuy4ys1RcipmKClpTHQKFFLLuCwLr
kjkpUAn7aS1nkCUmDgkGzgK70eeMITNYRQkhigHs5ng3EK6g++S7rHrHXSEiDwJb
pUT1ZanT1I6Wy354OIeG3No6t0v6jGBkmWRKDKWOstahTtM4/QO6k5hk4d2BQjBt
ff5FIXQJLUudODde62H6y0kBucVGwDA0Xsbb+X48nQKBgQDxqHi4Orl9MNB3SSRE
xwZVCfH6/zjyJ1s52DDSsvDX4MItdbcHKYT+I+3bN7Gs6GODyHMQjp9skD4OhrD+
cleJvdKXPzuaKkga8/DZ77WfXkL0adwtrBALTgplkiVRXzF2/2HztfV6HLdvrs3t
dy2Sdpsw7omigwP+NxnsIVI0dQKBgQDASa2R+4uiF46NNPA/K4aX3GGgfzPKRdy5
VF8phaPcZJ0Xvpit1SE2/nCjP/YpuCrduU2iv0TaJ/ruvLMF+B4o7PLsPoU1CdWu
2mkM1SAJUZikPwHPrzeQFBofHMvbJ3Z58d7SJBaOC7gcTrkIVejM3zRjq9JsQwVu
G0NlEI462wKBgQDLu9Eq4LeJCCJ4rr1ZDsIT57KOfaWw4eVTOyTOPfY2ylJqqReJ
fkOVTw01CBtPPwzHCbOYfeWCTYlEDeIiYpvSkKp+wNyq+IKZ1pdz5Vgl5/5iuOzb
xHgyT7UMNM4pcCvvuxcFtJ4kORmdmq4aSaOuGzhzZGe9Dt/K7wF3xg/cEQKBgAin
yF5X2lMziEEm7uGJDgfr7aER2Lz0JBlbiOUPlO6owMF+3NSGUXZuQZe3m1cJaTSN
0MbQoULIpez1JYHRR1pEQDMOJWTbyniScEQZm9WPjLVn+KbmljOwE/TukOaOgjC/
CG6hHTrLoD/18zJC27XNHkiWRWSGJ8prA7+a3SwdAoGBAMycUb7G7b77OVklxiDD
iuSIncgHCA/s6njsFYi8FHYVV9No0nkYaBEcKucY4/DG2C8DYSJhAOEc/pqHeXBj
C/NXeMogjLINqYEkb6EZb5XiBshvUkCRt5F7tPtCB3vbPg4XMte02Q4+TzK71b0Y
JhFF38L3IKfrSd8BHuTIx0hG
-----END PRIVATE KEY-----\n""",
    "client_email": "firebase-adminsdk-fbsvc@gerador-de-documentos-pei.iam.gserviceaccount.com",
    "client_id": "108880766335552663495",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40gerador-de-documentos-pei.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

# === Inicialização única do Firebase ===
try:
    firebase_admin.get_app()
except ValueError:
    cred = credentials.Certificate(service_account_info)
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://gerador-de-documentos-pei.firebaseio.com"
    })

root = db.reference()

# === Estado da sessão ===
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# === Autenticação ===
def login():
    st.subheader("🔑 Login")
    user = st.text_input("Usuário", key="login_user")
    pwd  = st.text_input("Senha", type="password", key="login_pass")
    if st.button("Entrar"):
        record = root.child("users").child(user).get()
        if record and record.get("password") == pwd:
            st.success(f"Bem-vindo(a), {user}!")
            st.session_state.logged_in = True
            st.session_state.username = user
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos.")

def signup():
    st.subheader("🆕 Cadastrar Usuário")
    new_user = st.text_input("Novo usuário", key="signup_user")
    new_pwd  = st.text_input("Nova senha", type="password", key="signup_pass")
    if st.button("Cadastrar"):
        if new_user and new_pwd:
            ref = root.child("users").child(new_user)
            if ref.get():
                st.error("Usuário já existe.")
            else:
                ref.set({"password": new_pwd})
                st.success("Cadastro realizado!")
                st.rerun()
        else:
            st.warning("Preencha ambos os campos.")

def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()

# === CRUD de itens ===
def add_item():
    st.subheader("➕ Adicionar Item")
    nome = st.text_input("Nome do item", key="add_input")
    if st.button("Adicionar"):
        if nome:
            root.child("items").push({"name": nome})
            st.success("Item adicionado.")
            st.rerun()
        else:
            st.warning("Digite um nome válido.")

def view_items():
    st.subheader("📋 Lista de Itens")
    items = root.child("items").get() or {}
    for k, v in items.items():
        st.write(f"- {v.get('name')}  (ID: {k})")

def update_item():
    st.subheader("✏️ Atualizar Item")
    items = root.child("items").get() or {}
    opts = [f"{k}: {v.get('name')}" for k, v in items.items()]
    sel = st.selectbox("Selecione um item", opts, key="upd_sel")
    if sel:
        key = sel.split(":")[0]
        novo = st.text_input("Novo nome", key="upd_input")
        if st.button("Atualizar"):
            if novo:
                root.child("items").child(key).update({"name": novo})
                st.success("Item atualizado.")
                st.rerun()
            else:
                st.warning("Digite um nome válido.")

def delete_item():
    st.subheader("🗑️ Deletar Item")
    items = root.child("items").get() or {}
    opts = [f"{k}: {v.get('name')}" for k, v in items.items()]
    sel = st.selectbox("Selecione um item", opts, key="del_sel")
    if sel and st.button("Deletar"):
        key = sel.split(":")[0]
        root.child("items").child(key).delete()
        st.success("Item deletado.")
        st.rerun()

def main_app():
    st.title("📦 CRUD App")
    escolha = st.sidebar.selectbox("Menu", ["Adicionar", "Visualizar", "Atualizar", "Deletar", "Logout"])
    if escolha == "Adicionar":
        add_item()
    elif escolha == "Visualizar":
        view_items()
    elif escolha == "Atualizar":
        update_item()
    elif escolha == "Deletar":
        delete_item()
    elif escolha == "Logout":
        logout()

# === Fluxo principal ===
st.title("🔒 App CRUD com Login")
if not st.session_state.logged_in:
    modo = st.sidebar.selectbox("Escolha", ["Login", "Cadastrar"])
    if modo == "Login":
        login()
    else:
        signup()
else:
    st.sidebar.write(f"👤 {st.session_state.username}")
    main_app()
