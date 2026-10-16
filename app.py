
from flask import (
    Flask, request, redirect, url_for, render_template_string,
    flash, Response
)
import sqlite3
import csv
import io
import os
from datetime import date

app = Flask(__name__)
app.secret_key = "clinica-vida-plus-chave-local"

PASTA = os.path.dirname(os.path.abspath(__file__))
BANCO = os.path.join(PASTA, "clinica_vida.db")

STATUS = [
    "Agendada", "Confirmada", "Aguardando",
    "Em atendimento", "Concluída", "Cancelada", "Faltou"
]


# =========================================================
# BANCO DE DADOS
# =========================================================

def conectar():
    con = sqlite3.connect(BANCO)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


def inicializar():
    with conectar() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS pacientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cpf TEXT NOT NULL UNIQUE,
            nascimento TEXT,
            telefone TEXT,
            email TEXT
        );

        CREATE TABLE IF NOT EXISTS medicos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            especialidade TEXT NOT NULL,
            telefone TEXT,
            ativo INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS consultas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_id INTEGER NOT NULL,
            medico_id INTEGER NOT NULL,
            data TEXT NOT NULL,
            horario TEXT NOT NULL,
            motivo TEXT,
            status TEXT NOT NULL DEFAULT 'Agendada',
            observacoes TEXT,
            FOREIGN KEY (paciente_id) REFERENCES pacientes(id),
            FOREIGN KEY (medico_id) REFERENCES medicos(id),
            UNIQUE (medico_id, data, horario)
        );
        """)

        # Médicos fictícios para demonstração
        if con.execute("SELECT COUNT(*) FROM medicos").fetchone()[0] == 0:
            con.executemany("""
                INSERT INTO medicos (nome, especialidade, telefone)
                VALUES (?, ?, ?)
            """, [
                ("Dra. Marina Costa", "Clínica geral", ""),
                ("Dr. Rafael Mendes", "Pediatria", ""),
                ("Dra. Beatriz Lima", "Cardiologia", "")
            ])


# =========================================================
# INTERFACE
# =========================================================

HTML = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ titulo }} | Clínica Vida+</title>
<style>
:root {
    --azul:#183b65;
    --azul2:#2868d7;
    --fundo:#f2f5fa;
    --texto:#253247;
    --borda:#dfe6ef;
    --verde:#087c67;
}
* { box-sizing:border-box }
body {
    margin:0; background:var(--fundo); color:var(--texto);
    font-family:Arial,Helvetica,sans-serif;
}
.layout { display:grid; grid-template-columns:235px 1fr; min-height:100vh }
aside { background:var(--azul); color:white; padding:22px 14px }
.logo { font-size:25px; font-weight:bold; padding:8px 10px 22px }
.logo span { color:#69e0c9 }
aside a {
    display:block; padding:12px 10px; margin:4px 0;
    border-radius:8px; color:#e8eff9; text-decoration:none;
}
aside a:hover { background:#31547c }
main { min-width:0 }
.topo {
    background:white; border-bottom:1px solid var(--borda);
    padding:17px 25px; display:flex; justify-content:space-between;
    align-items:center; gap:12px;
}
.conteudo { padding:25px; max-width:1400px; margin:auto }
h1 { color:var(--azul); margin:0 0 8px }
h2 { color:var(--azul); font-size:19px }
p { line-height:1.5 }
.sub { color:#66758b; margin-top:0 }
.cartoes { display:grid; grid-template-columns:repeat(4,1fr); gap:13px; margin:20px 0 }
.cartao,.painel {
    background:white; border:1px solid var(--borda);
    border-radius:13px; padding:18px; margin-bottom:16px;
}
.cartao small { color:#68778b }
.numero { font-size:32px; font-weight:bold; color:var(--azul); margin-top:8px }
button,.botao {
    display:inline-block; padding:10px 14px; border:0;
    border-radius:8px; background:var(--azul2); color:white;
    font-weight:bold; cursor:pointer; text-decoration:none; font-size:14px;
}
.secundario { background:#e9f0fc; color:#234e91 }
.verde { background:var(--verde) }
input,select,textarea {
    display:block; width:100%; padding:10px;
    margin:6px 0 14px; border:1px solid #cbd5e1;
    border-radius:8px; background:white; font:inherit;
}
label { font-weight:bold; font-size:14px }
.grade { display:grid; grid-template-columns:1fr 1fr; gap:14px }
table { width:100%; border-collapse:collapse; background:white }
th,td { text-align:left; padding:11px; border-bottom:1px solid var(--borda) }
th { background:#f6f8fc; color:#53647a; font-size:12px }
.tabela { overflow-x:auto }
.pill {
    display:inline-block; padding:5px 9px; border-radius:20px;
    background:#e9f0fc; color:#234e91; font-size:12px; font-weight:bold;
}
.flash { padding:12px; background:#dff7eb; border-radius:8px; margin-bottom:15px }
.erro { background:#ffe8e8 }
.acoes { display:flex; gap:8px; flex-wrap:wrap; margin-bottom:15px }
.vazio { padding:22px; text-align:center; color:#66758b }
@media(max-width:850px) {
    .layout { grid-template-columns:1fr }
    aside { padding:12px }
    .logo { padding:6px 8px 12px }
    .menu { display:flex; overflow-x:auto; gap:3px }
    aside a { white-space:nowrap; padding:9px }
    .conteudo { padding:15px }
    .cartoes { grid-template-columns:repeat(2,1fr) }
    .grade { grid-template-columns:1fr }
}
@media print {
    aside,.topo .acoes,.nao-imprimir,button { display:none!important }
    .layout { display:block }
    .conteudo { padding:0 }
    body { background:white }
}
</style>
</head>
<body>
<div class="layout">
<aside>
    <div class="logo">Clínica <span>Vida+</span></div>
    <nav class="menu">
        <a href="/">▦ Painel inicial</a>
        <a href="/pacientes">♙ Pacientes</a>
        <a href="/medicos">⚕ Médicos</a>
        <a href="/consultas">▣ Agenda de consultas</a>
        <a href="/fila">☷ Fila de atendimento</a>
        <a href="/relatorios">▤ Relatórios</a>
        <a href="/documentacao">▧ Documentação acadêmica</a>
    </nav>
</aside>
<main>
    <div class="topo">
        <strong>{{ titulo }}</strong>
        <div class="acoes">
            <button class="secundario" onclick="window.print()">Imprimir</button>
        </div>
    </div>
    <div class="conteudo">
        {% for categoria,mensagem in get_flashed_messages(with_categories=true) %}
        <div class="flash {{ 'erro' if categoria == 'erro' else '' }}">
            {{ mensagem }}
        </div>
        {% endfor %}
        {{ conteudo|safe }}
    </div>
</main>
</div>
</body>
</html>
"""


def pagina(titulo, conteudo, **dados):
    corpo = render_template_string(conteudo, **dados)
    return render_template_string(
        HTML, titulo=titulo, conteudo=corpo
    )


def consultar(sql, parametros=()):
    with conectar() as con:
        return con.execute(sql, parametros).fetchall()


# =========================================================
# PAINEL INICIAL
# =========================================================

@app.route("/")
def inicio():
    hoje = date.today().isoformat()

    pacientes = consultar(
        "SELECT COUNT(*) total FROM pacientes"
    )[0]["total"]

    medicos = consultar(
        "SELECT COUNT(*) total FROM medicos WHERE ativo=1"
    )[0]["total"]

    consultas = consultar(
        """SELECT COUNT(*) total FROM consultas
           WHERE data=? AND status!='Cancelada'""",
        (hoje,)
    )[0]["total"]

    fila = consultar(
        """SELECT COUNT(*) total FROM consultas
           WHERE data=? AND status IN ('Aguardando','Confirmada')""",
        (hoje,)
    )[0]["total"]

    agenda = consultar("""
        SELECT c.*, p.nome paciente, m.nome medico,
               m.especialidade
        FROM consultas c
        JOIN pacientes p ON p.id=c.paciente_id
        JOIN medicos m ON m.id=c.medico_id
        WHERE c.data=?
        ORDER BY c.horario
    """, (hoje,))

    corpo = """
    <h1>Bem-vindo à Clínica Vida+</h1>
    <p class="sub">Central de recepção, agendamento e controle de consultas.</p>

    <div class="acoes">
        <a class="botao" href="/pacientes/novo">+ Cadastrar paciente</a>
        <a class="botao" href="/consultas/nova">+ Agendar consulta</a>
    </div>

    <div class="cartoes">
        <div class="cartao"><small>Pacientes cadastrados</small>
        <div class="numero">{{ pacientes }}</div></div>
        <div class="cartao"><small>Médicos ativos</small>
        <div class="numero">{{ medicos }}</div></div>
        <div class="cartao"><small>Consultas hoje</small>
        <div class="numero">{{ consultas }}</div></div>
        <div class="cartao"><small>Na fila / confirmadas</small>
        <div class="numero">{{ fila }}</div></div>
    </div>

    <section class="painel">
        <h2>Agenda de hoje</h2>
        <div class="tabela"><table>
        <tr><th>Horário</th><th>Paciente</th><th>Médico</th><th>Status</th></tr>
        {% for c in agenda %}
        <tr>
            <td>{{ c.horario }}</td>
            <td>{{ c.paciente }}</td>
            <td>{{ c.medico }}<br>{{ c.especialidade }}</td>
            <td><span class="pill">{{ c.status }}</span></td>
        </tr>
        {% else %}
        <tr><td colspan="4" class="vazio">Nenhuma consulta para hoje.</td></tr>
        {% endfor %}
        </table></div>
    </section>

    <section class="painel">
        <h2>Rotina da recepção</h2>
        1. Localize ou cadastre o paciente.<br>
        2. Escolha o médico e o horário disponível.<br>
        3. Confirme a presença do paciente.<br>
        4. Atualize a fila conforme o atendimento avança.<br>
        5. Consulte os relatórios quando necessário.
    </section>
    """
    return pagina(
        "Painel inicial", corpo, pacientes=pacientes,
        medicos=medicos, consultas=consultas, fila=fila,
        agenda=agenda
    )


# =========================================================
# PACIENTES
# =========================================================

FORM_PACIENTE = """
<h1>{{ titulo_form }}</h1>
<p class="sub">Preencha os dados administrativos do cadastro.</p>
<section class="painel">
<form method="post">
    <label>Nome completo *</label>
    <input name="nome" maxlength="120" required value="{{ p.nome if p else '' }}">

    <label>CPF ou identificador fictício *</label>
    <input name="cpf" maxlength="30" required value="{{ p.cpf if p else '' }}">

    <label>Data de nascimento</label>
    <input type="date" name="nascimento" value="{{ p.nascimento or '' if p else '' }}">

    <label>Telefone</label>
    <input name="telefone" maxlength="40" value="{{ p.telefone or '' if p else '' }}">

    <label>E-mail</label>
    <input type="email" name="email" maxlength="120" value="{{ p.email or '' if p else '' }}">

    <button>Salvar paciente</button>
    <a class="botao secundario" href="/pacientes">Cancelar</a>
</form>
</section>
"""


@app.route("/pacientes")
def pacientes():
    busca = request.args.get("busca", "").strip()

    registros = consultar("""
        SELECT * FROM pacientes
        WHERE nome LIKE ? OR cpf LIKE ? OR telefone LIKE ?
        ORDER BY nome
    """, (f"%{busca}%", f"%{busca}%", f"%{busca}%"))

    corpo = """
    <h1>Pacientes</h1>
    <p class="sub">Cadastre e localize pacientes da clínica.</p>
    <div class="acoes">
        <a class="botao" href="/pacientes/novo">+ Novo paciente</a>
    </div>
    <section class="painel">
    <form method="get" class="nao-imprimir">
        <label>Buscar por nome, CPF ou telefone</label>
        <input name="busca" value="{{ busca }}">
        <button>Pesquisar</button>
    </form>
    <div class="tabela"><table>
    <tr><th>Nome</th><th>Identificador</th><th>Telefone</th><th>Ação</th></tr>
    {% for p in registros %}
    <tr>
        <td>{{ p.nome }}</td><td>{{ p.cpf }}</td>
        <td>{{ p.telefone or '—' }}</td>
        <td><a href="/pacientes/{{ p.id }}/editar">Editar</a></td>
    </tr>
    {% else %}
    <tr><td colspan="4" class="vazio">Nenhum paciente encontrado.</td></tr>
    {% endfor %}
    </table></div>
    </section>
    """
    return pagina("Pacientes", corpo, registros=registros, busca=busca)


@app.route("/pacientes/novo", methods=["GET", "POST"])
def paciente_novo():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        cpf = request.form.get("cpf", "").strip()

        if not nome or not cpf:
            flash("Nome e identificador são obrigatórios.", "erro")
        else:
            try:
                with conectar() as con:
                    con.execute("""
                        INSERT INTO pacientes
                        (nome, cpf, nascimento, telefone, email)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        nome, cpf,
                        request.form.get("nascimento") or None,
                        request.form.get("telefone", "").strip(),
                        request.form.get("email", "").strip()
                    ))
                flash("Paciente cadastrado com sucesso.")
                return redirect("/pacientes")
            except sqlite3.IntegrityError:
                flash("Esse identificador já está cadastrado.", "erro")

    return pagina(
        "Novo paciente", FORM_PACIENTE,
        titulo_form="Cadastrar paciente", p=None
    )


@app.route("/pacientes/<int:pid>/editar", methods=["GET", "POST"])
def paciente_editar(pid):
    p = consultar(
        "SELECT * FROM pacientes WHERE id=?", (pid,)
    )
    if not p:
        flash("Paciente não encontrado.", "erro")
        return redirect("/pacientes")
    p = p[0]

    if request.method == "POST":
        try:
            with conectar() as con:
                con.execute("""
                    UPDATE pacientes
                    SET nome=?, cpf=?, nascimento=?, telefone=?, email=?
                    WHERE id=?
                """, (
                    request.form.get("nome", "").strip(),
                    request.form.get("cpf", "").strip(),
                    request.form.get("nascimento") or None,
                    request.form.get("telefone", "").strip(),
                    request.form.get("email", "").strip(),
                    pid
                ))
            flash("Cadastro atualizado.")
            return redirect("/pacientes")
        except sqlite3.IntegrityError:
            flash("Identificador já utilizado por outro paciente.", "erro")

    return pagina(
        "Editar paciente", FORM_PACIENTE,
        titulo_form="Editar paciente", p=p
    )


# =========================================================
# MÉDICOS
# =========================================================

FORM_MEDICO = """
<h1>{{ titulo_form }}</h1>
<section class="painel">
<form method="post">
    <label>Nome do médico *</label>
    <input name="nome" required value="{{ m.nome if m else '' }}">

    <label>Especialidade *</label>
    <input name="especialidade" required value="{{ m.especialidade if m else '' }}">

    <label>Telefone</label>
    <input name="telefone" value="{{ m.telefone or '' if m else '' }}">

    {% if m %}
    <label>Situação</label>
    <select name="ativo">
        <option value="1" {{ 'selected' if m.ativo else '' }}>Ativo</option>
        <option value="0" {{ 'selected' if not m.ativo else '' }}>Inativo</option>
    </select>
    {% endif %}

    <button>Salvar médico</button>
    <a class="botao secundario" href="/medicos">Cancelar</a>
</form>
</section>
"""


@app.route("/medicos")
def medicos():
    registros = consultar(
        "SELECT * FROM medicos ORDER BY nome"
    )
    corpo = """
    <h1>Médicos</h1>
    <p class="sub">Gerencie profissionais e especialidades.</p>
    <div class="acoes"><a class="botao" href="/medicos/novo">+ Novo médico</a></div>
    <section class="painel"><div class="tabela"><table>
    <tr><th>Nome</th><th>Especialidade</th><th>Contato</th><th>Situação</th><th>Ação</th></tr>
    {% for m in registros %}
    <tr>
        <td>{{ m.nome }}</td><td>{{ m.especialidade }}</td>
        <td>{{ m.telefone or '—' }}</td>
        <td>{{ 'Ativo' if m.ativo else 'Inativo' }}</td>
        <td><a href="/medicos/{{ m.id }}/editar">Editar</a></td>
    </tr>
    {% endfor %}
    </table></div></section>
    """
    return pagina("Médicos", corpo, registros=registros)


@app.route("/medicos/novo", methods=["GET", "POST"])
def medico_novo():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        esp = request.form.get("especialidade", "").strip()

        if nome and esp:
            with conectar() as con:
                con.execute("""
                    INSERT INTO medicos(nome, especialidade, telefone)
                    VALUES (?, ?, ?)
                """, (
                    nome, esp, request.form.get("telefone", "").strip()
                ))
            flash("Médico cadastrado.")
            return redirect("/medicos")

        flash("Nome e especialidade são obrigatórios.", "erro")

    return pagina(
        "Novo médico", FORM_MEDICO,
        titulo_form="Cadastrar médico", m=None
    )


@app.route("/medicos/<int:mid>/editar", methods=["GET", "POST"])
def medico_editar(mid):
    resultado = consultar(
        "SELECT * FROM medicos WHERE id=?", (mid,)
    )
    if not resultado:
        flash("Médico não encontrado.", "erro")
        return redirect("/medicos")
    m = resultado[0]

    if request.method == "POST":
        with conectar() as con:
            con.execute("""
                UPDATE medicos SET nome=?, especialidade=?,
                telefone=?, ativo=? WHERE id=?
            """, (
                request.form.get("nome", "").strip(),
                request.form.get("especialidade", "").strip(),
                request.form.get("telefone", "").strip(),
                int(request.form.get("ativo", "1")), mid
            ))
        flash("Médico atualizado.")
        return redirect("/medicos")

    return pagina(
        "Editar médico", FORM_MEDICO,
        titulo_form="Editar médico", m=m
    )


# =========================================================
# AGENDAMENTO
# =========================================================

FORM_CONSULTA = """
<h1>Agendar consulta</h1>
<p class="sub">Escolha o paciente, o profissional e o horário.</p>
<section class="painel">
<form method="post">
    <label>Paciente *</label>
    <select name="paciente_id" required>
        <option value="">Selecione</option>
        {% for p in pacientes %}
        <option value="{{ p.id }}">{{ p.nome }} — {{ p.cpf }}</option>
        {% endfor %}
    </select>

    <label>Médico *</label>
    <select name="medico_id" required>
        <option value="">Selecione</option>
        {% for m in medicos %}
        <option value="{{ m.id }}">{{ m.nome }} — {{ m.especialidade }}</option>
        {% endfor %}
    </select>

    <label>Data *</label>
    <input type="date" name="data" min="{{ hoje }}" required>

    <label>Horário *</label>
    <input type="time" name="horario" step="900" required>

    <label>Motivo administrativo</label>
    <input name="motivo" maxlength="160"
           placeholder="Ex.: consulta de rotina">

    <label>Status</label>
    <select name="status">
        {% for s in status %}
        <option>{{ s }}</option>
        {% endfor %}
    </select>

    <label>Observações administrativas</label>
    <textarea name="observacoes" maxlength="500"></textarea>

    <button>Salvar agendamento</button>
    <a class="botao secundario" href="/consultas">Cancelar</a>
</form>
</section>
"""


@app.route("/consultas/nova", methods=["GET", "POST"])
def consulta_nova():
    pacientes_lista = consultar(
        "SELECT * FROM pacientes ORDER BY nome"
    )
    medicos_lista = consultar(
        "SELECT * FROM