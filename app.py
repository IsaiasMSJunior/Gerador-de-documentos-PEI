# app.py

import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import json

# === Inicialização do Firebase ===
with open('firebase_key.json', 'r') as f:
    service_account_info = json.load(f)

cred = credentials.Certificate(service_account_info)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://gerador-de-documentos-pei-default-rtdb.firebaseio.com/'  # <--- substitua pela URL do seu Realtime Database
})
root = db.reference()

# === Estado da sessão ===
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ''

# === Funções de Autenticação ===
def login():
    st.subheader("🔑 Login")
    username = st.text_input("Usuário", key="login_user")
    password = st.text_input("Senha", type="password", key="login_pass")
    if st.button("Entrar"):
        user_ref = root.child('users').child(username)
        user = user_ref.get()
        if user and user.get('password') == password:
            st.success(f"Bem-vindo(a), {username}!")
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos.")

def signup():
    st.subheader("🆕 Cadastrar Usuário")
    new_user = st.text_input("Escolha um usuário", key="signup_user")
    new_pass = st.text_input("Escolha uma senha", type="password", key="signup_pass")
    if st.button("Cadastrar"):
        if new_user and new_pass:
            user_ref = root.child('users').child(new_user)
            if user_ref.get():
                st.error("Esse usuário já existe.")
            else:
                user_ref.set({'password': new_pass})
                st.success("Usuário cadastrado com sucesso!")
                st.rerun()
        else:
            st.warning("Preencha usuário e senha.")

def logout():
    st.session_state['logged_in'] = False
    st.session_state['username'] = ''
    st.rerun()

# === Funções CRUD ===
def add_item():
    st.subheader("➕ Adicionar Item")
    name = st.text_input("Nome do item", key="add_input")
    if st.button("Adicionar"):
        if name:
            root.child('items').push({'name': name})
            st.success("Item adicionado.")
            st.rerun()
        else:
            st.warning("Digite um nome.")

def view_items():
    st.subheader("📋 Lista de Itens")
    items = root.child('items').get() or {}
    for key, val in items.items():
        st.write(f"- {val.get('name')}  (ID: {key})")

def update_item():
    st.subheader("✏️ Atualizar Item")
    items = root.child('items').get() or {}
    options = [f"{k}: {v.get('name')}" for k, v in items.items()]
    sel = st.selectbox("Selecione", options, key="upd_sel")
    if sel:
        key = sel.split(":")[0]
        novo = st.text_input("Novo nome", key="upd_input")
        if st.button("Atualizar"):
            if novo:
                root.child('items').child(key).update({'name': novo})
                st.success("Item atualizado.")
                st.rerun()
            else:
                st.warning("Digite um novo nome.")

def delete_item():
    st.subheader("🗑️ Deletar Item")
    items = root.child('items').get() or {}
    options = [f"{k}: {v.get('name')}" for k, v in items.items()]
    sel = st.selectbox("Selecione", options, key="del_sel")
    if sel and st.button("Deletar"):
        key = sel.split(":")[0]
        root.child('items').child(key).delete()
        st.success("Item deletado.")
        st.rerun()

def main_app():
    st.title("CRUD App")
    choice = st.sidebar.selectbox("Menu", ["Adicionar", "Visualizar", "Atualizar", "Deletar", "Logout"])
    if choice == "Adicionar":
        add_item()
    elif choice == "Visualizar":
        view_items()
    elif choice == "Atualizar":
        update_item()
    elif choice == "Deletar":
        delete_item()
    elif choice == "Logout":
        logout()

# === Fluxo principal ===
st.title("🔒 App CRUD com Login")
if not st.session_state['logged_in']:
    modo = st.sidebar.selectbox("Escolha", ["Login", "Cadastrar"])
    if modo == "Login":
        login()
    else:
        signup()
else:
    st.sidebar.write(f"👤 {st.session_state['username']}")
    main_app()
