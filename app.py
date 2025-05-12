# app.py
import os
import json

import streamlit as st
import firebase_admin
from firebase_admin import credentials, db

# Carrega o arquivo de chave de serviço (colocado no mesmo diretório do app)
KEY_PATH = os.path.join(os.path.dirname(__file__), "firebase_key.json")
if not os.path.exists(KEY_PATH):
    st.error("Arquivo firebase_key.json não encontrado.")
    st.stop()

cred = credentials.Certificate(KEY_PATH)
firebase_admin.initialize_app(cred, {
    # Substitua pela URL do seu Realtime Database (sem barra final)
    "databaseURL": "https://SEU_PROJETO.firebaseio.com"
})

st.title("📥 Cadastro de Nome")

# Input de texto
nome = st.text_input("Nome")

# Botão de inserção
if st.button("Inserir"):
    if nome.strip() == "":
        st.warning("Por favor, digite um nome antes de inserir.")
    else:
        ref = db.reference("nomes")  # nó onde serão armazenados os nomes
        novo = ref.push({"nome": nome})
        st.success(f'✔️ Nome "{nome}" inserido com sucesso! (key: {novo.key})')
        # reinicia o app (limpando o input e atualizando o status)
        st.rerun()
