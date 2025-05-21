import streamlit as st
import mysql.connector
import json
import os
import pandas as pd
import calendar
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph
from datetime import datetime
from io import BytesIO
from openpyxl import load_workbook
from openpyxl.styles import PatternFill

# --- Configuração da página ---
st.set_page_config(page_title="Agenda Escolar", layout="wide")

# --- MySQL: lê credenciais do secrets.toml e testa conexão quando solicitado ---
cfg = st.secrets["mysql"]
host     = cfg["host"]
user     = cfg["user"]
password = cfg["password"]
database = cfg["database"]

if st.sidebar.button("Testar Conexão MySQL"):
    conn = None
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        if conn.is_connected():
            st.sidebar.success("Conexão MySQL estabelecida!")
        else:
            st.sidebar.error("Falha ao conectar ao MySQL.")
    except mysql.connector.Error as err:
        st.sidebar.error(f"Erro de conexão: {err}")
    finally:
        if conn is not None and conn.is_connected():
            conn.close()
            st.sidebar.info("Conexão fechada.")

# --- Helpers e Configurações Gerais ---
map_hor = {
    "1ª": "7:00–7:50", "2ª": "7:50–8:40", "3ª": "8:40–9:30",
    "4ª": "9:50–10:40", "5ª": "10:40–11:30", "6ª": "12:20–13:10", "7ª": "13:10–14:00"
}
meses = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho",
         "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]
ano_planej = 2025

def carregar_json(nome):
    if os.path.exists(nome):
        with open(nome, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def salvar_json(nome, conteudo):
    with open(nome, 'w', encoding='utf-8') as f:
        json.dump(conteudo, f, ensure_ascii=False, indent=2)

def extrai_serie(turma: str) -> str:
    return turma[:-1]

def set_border(par: Paragraph):
    p = par._p
    pPr = p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bd = OxmlElement('w:bottom')
    bd.set(qn('w:val'),'single'); bd.set(qn('w:sz'),'4')
    bd.set(qn('w:space'),'1'); bd.set(qn('w:color'),'auto')
    pBdr.append(bd); pPr.append(pBdr)

def insert_after(par: Paragraph, text='') -> Paragraph:
    new_p = OxmlElement('w:p'); par._p.addnext(new_p)
    para = Paragraph(new_p, par._parent)
    if text: para.add_run(text)
    return para

# --- Funções de geração de documentos ---

def gerar_agenda_template(entries, df_bank, professor, semana, bimestre, cores_turmas):
    wb = load_workbook("agenda_modelo.xlsx")
    ws = wb.active
    ws["B1"] = professor
    ws["E1"] = semana
    row_map = {"1ª":4, "2ª":6, "3ª":8, "4ª":12, "5ª":14, "6ª":18, "7ª":20}
    col_map = {"Segunda":"C", "Terça":"D", "Quarta":"E", "Quinta":"F", "Sexta":"G"}
    for e in entries:
        col, row = col_map[e["dia"]], row_map[e["aula"]]
        ws[f"{col}{row}"] = f"{e['turma']} – {e['disciplina']}"
        color = cores_turmas.get(e["turma"], "#FFFFFF").lstrip("#")
        fill = PatternFill(start_color=color, end_color=color, fill_type="solid")
        ws[f"{col}{row}"].fill = fill
        ws[f"{col}{row+1}"] = (
            f"Aula {e['num']} – " +
            df_bank.loc[
                (df_bank["DISCIPLINA"]==e["disciplina"]) &
                (df_bank["ANO/SÉRIE"]==extrai_serie(e["turma"])) &
                (df_bank["BIMESTRE"]==bimestre) &
                (df_bank["Nº da aula"]==e["num"])
            ]["TÍTULO DA AULA"].iloc[0]
            if not df_bank.empty else ""
        )
        ws[f"{col}{row+1}"].fill = fill
    out = BytesIO(); wb.save(out); out.seek(0)
    return out

# (mantenha aqui as demais funções gerar_plano_template, gerar_guia_template, gerar_planejamento_template)

# --- Inicialização de estados ---
if "extras" not in st.session_state:
    extras = carregar_json("extras.json") or {}
    extras.setdefault("metodologia",[])
    extras.setdefault("recursos",[])
    extras.setdefault("criterios",[])
    st.session_state.extras = extras

if "pagina" not in st.session_state:
    st.session_state.pagina = "Cadastro de Professor"
if "professores" not in st.session_state:
    st.session_state.professores = carregar_json("professores.json") or []
if "turmas" not in st.session_state:
    st.session_state.turmas = carregar_json("turmas.json") or {}
if "horarios" not in st.session_state:
    st.session_state.horarios = carregar_json("horarios.json") or []

# --- Sidebar de navegação ---
pages = [
    "Cadastro de Professor","Cadastro de Turmas","Cadastro de Horário",
    "Gerar Agenda e Plano","Cadastro Extras","Gerar Guia",
    "Gerar Planejamento Bimestral"
]
for p in pages:
    if st.sidebar.button(p, use_container_width=True):
        st.session_state.pagina = p
    st.sidebar.markdown("\n")

# --- Páginas do app ---
# 1. Cadastro de Professor
if st.session_state.pagina == "Cadastro de Professor":
    st.header("Cadastro de Professor")
    nome = st.text_input("Nome")
    disciplinas = st.multiselect(
        "Disciplina(s)",
        ["Arte","Ciências","Ed. Física","Ed. Financeira","Geografia","História",
         "Português","Inglês","Matemática","PV","Redação","Tecnologia","OE Port","OE Mat"]
    )
    if st.button("Salvar Professor"):
        st.session_state.professores.append({"nome":nome,"disciplinas":disciplinas})
        salvar_json("professores.json", st.session_state.professores)
        st.success("Professor salvo!")
    for p in st.session_state.professores:
        st.write(f"{p['nome']} — {', '.join(p['disciplinas'])}")

# 2. Cadastro de Turmas
elif st.session_state.pagina == "Cadastro de Turmas":
    st.header("Cadastro de Turmas")
    saved = st.session_state.turmas
    default_s = sorted({t[:-1] for t in saved.keys()})
    default_seg = []
    if any(s in ["6º","7º","8º","9º"] for s in default_s): default_seg.append("Ensino Fundamental")
    if any(s in ["1º","2º","3º"] for s in default_s): default_seg.append("Ensino Médio")
    segmento = st.multiselect("Segmento(s)", ["Ensino Fundamental","Ensino Médio"], default=default_seg)
    anos = []
    if "Ensino Fundamental" in segmento: anos+=["6º","7º","8º","9º"]
    if "Ensino Médio" in segmento: anos+=["1º","2º","3º"]
    series = st.multiselect("Ano/Série", anos, default=default_s)
    turma_map = {
        "6º":["6ºA","6ºB","6ºC","6ºD"],"7º":["7ºA","7ºB","7ºC"],
        "8º":["8ºA","8ºB","8ºC","8ºD"],"9º":["9ºA","9ºB","9ºC","9ºD"],
        "1º":["1ºA","1ºB","1ºC","1ºD","1ºE"],
        "2º":["2ºA ADM","2ºB ADM","2ºC"],"3º":["3ºA","3ºA ADM","3ºB ADM","3ºB LOG"]
    }
    op = sum((turma_map.get(s,[]) for s in series), [])
    sel = st.multiselect("Turma(s)", op, default=list(saved.keys()), key="sel_turmas")
    cores = {
        t: st.color_picker(f"Cor {t}", value=saved.get(t,"#FFFFFF"), key=f"cor_{t}")
        for t in sel
    }
    if st.button("Salvar Turmas"):
        st.session_state.turmas = cores
        salvar_json("turmas.json", st.session_state.turmas)
        st.success("Turmas salvas!")

# 3. Cadastro de Horário
elif st.session_state.pagina == "Cadastro de Horário":
    st.header("Cadastro de Horário")
    if st.button("Adicionar Linha"):
        st.session_state.horarios.append({'turma':None,'disciplina':None,'dia':None,'aula':None})
    for i, itm in enumerate(st.session_state.horarios):
        cols = st.columns(6)
        turmas = list(st.session_state.turmas.keys())
        discs  = sorted({d for p in st.session_state.professores for d in p["disciplinas"]})
        dias   = ["Segunda","Terça","Quarta","Quinta","Sexta"]
        aulas  = list(map_hor.keys())
        itm['turma']      = cols[0].selectbox("Turma", turmas,
                                index=turmas.index(itm.get('turma')) if itm.get('turma') in turmas else 0,
                                key=f"turma_{i}")
        itm['disciplina'] = cols[1].selectbox("Disciplina", discs,
                                index=discs.index(itm.get('disciplina')) if itm.get('disciplina') in discs else 0,
                                key=f"disc_{i}")
        itm['dia']        = cols[2].selectbox("Dia", dias,
                                index=dias.index(itm.get('dia')) if itm.get('dia') in dias else 0,
                                key=f"dia_{i}")
        itm['aula']       = cols[3].selectbox("Aula", aulas,
                                index=aulas.index(itm.get('aula')) if itm.get('aula') in aulas else 0,
                                key=f"aula_{i}")
        cols[4].text_input("Horário", map_hor.get(itm['aula'],""), disabled=True, key=f"hor_{i}")
        if cols[5].button("X", key=f"rm_{i}"):
            st.session_state.horarios.pop(i)
            break
    if st.button("Salvar Horários"):
        salvar_json("horarios.json", st.session_state.horarios)
        st.success("Horários salvos!")
    if st.session_state.horarios:
        st.dataframe(pd.DataFrame(st.session_state.horarios).sort_values("dia
