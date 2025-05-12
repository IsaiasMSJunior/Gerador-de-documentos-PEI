# app.py
import os
import json

import streamlit as st
import firebase_admin
from firebase_admin import credentials, db

# Caminho para o JSON de credenciais
KEY_PATH = os.path.join(os.path.dirname(__file__), "firebase_key.json")
if not os.path.exists(KEY_PATH):
    st.error("Arquivo firebase_key.json não encontrado.")
    st.stop()

# Carrega credenciais
cred = credentials.Certificate(KEY_PATH)

# Inicializa o app Firebase apenas se ainda não estiver inicializado
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        # Substitua pela URL do seu Realtime Database (sem barra final)
        "databaseURL": "https://gerador-de-documentos-pei-default-rtdb.firebaseio.com"
    })

st.title("📥 Cadastro de Nome")

# Campo de texto
nome = st.text_input("Nome")

# Botão de inserção
if st.button("Inserir"):
    if not nome.strip():
        st.warning("Por favor, digite um nome antes de inserir.")
    else:
        ref = db.reference("nomes")
        novo = ref.push({"nome": nome})
        st.success(f'✔️ Nome "{nome}" inserido com sucesso! (key: {novo.key})')
        st.rerun()
