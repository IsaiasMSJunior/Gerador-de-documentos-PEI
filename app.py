# app.py

import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import json

# === Carrega credenciais do Firebase corrigindo as quebras de linha ===
with open('firebase_key.json', 'r') as f:
    service_account_info = json.load(f)

# se private_key vier com '\\n', converte para '\n'
if 'private_key' in service_account_info:
    service_account_info['private_key'] = service_account_info['private_key'].replace('\\n', '\n')

# === Inicializa o Firebase só na primeira vez ===
try:
    firebase_admin.get_app()
except ValueError:
    cred = credentials.Certificate(service_account_info)
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://SEU_DATABASE.firebaseio.com'  # <-- ajuste para a sua URL
    })

root = db.reference()

# === Estado da sessão ===
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ''

# === Autenticação ===
def login():
    st.subheader("🔑 Login")
    user = st.text_input("Usuário", key="login_user")
    pwd = st.text_input("Senha", type="password", key="login_pass")
    if st.button("Entrar"):
        record = root.child('users').child(user).get()
        if record and record.get('password') == pwd:
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
            ref = root.child('users').child(new_user)
            if ref.get():
                st.error("Usuário já existe.")
            else:
                ref.set({'password': new_pwd})
                st.success("Cadastro realizado!")
                st.rerun()
        else:
            st.warning("Preencha ambos os campos.")

def logout():
    st.session_state.logged_in = False
    st.session_state.username = ''
    st.rerun()

# === CRUD de itens ===
def add_item():
    st.subheader("➕ Adicionar Item")
    nome = st.text_input("Nome do item", key="add_input")
    if st.button("Adicionar"):
        if nome:
            root.child('items').push({'name': nome})
            st.success("Item adicionado.")
            st.rerun()
        else:
            st.warning("Digite um nome válido.")

def view_items():
    st.subheader("📋 Lista de Itens")
    items = root.child('items').get() or {}
    for k, v in items.items():
        st.write(f"- {v.get('name')}  (ID: {k})")

def update_item():
    st.subheader("✏️ Atualizar Item")
    items = root.child('items').get() or {}
    opts = [f"{k}: {v.get('name')}" for k, v in items.items()]
    sel = st.selectbox("Selecione um item", opts, key="upd_sel")
    if sel:
        key = sel.split(":")[0]
        novo = st.text_input("Novo nome", key="upd_input")
        if st.button("Atualizar"):
            if novo:
                root.child('items').child(key).update({'name': novo})
                st.success("Item atualizado.")
                st.rerun()
            else:
                st.warning("Digite um nome válido.")

def delete_item():
    st.subheader("🗑️ Deletar Item")
    items = root.child('items').get() or {}
    opts = [f"{k}: {v.get('name')}" for k, v in items.items()]
    sel = st.selectbox("Selecione um item", opts, key="del_sel")
    if sel and st.button("Deletar"):
        key = sel.split(":")[0]
        root.child('items').child(key).delete()
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
