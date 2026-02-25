from flask import Flask, request, redirect, session, render_template_string, url_for
import sqlite3, uuid, time, hashlib
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "insano_single"

ADMIN_USER = "admin"
ADMIN_PASS_HASH = hashlib.sha256("1234".encode()).hexdigest()

# ================= DATABASE =================
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS produtos (
        nome TEXT PRIMARY KEY,
        valor REAL,
        estoque INTEGER,
        ativo INTEGER
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS pedidos (
        id TEXT PRIMARY KEY,
        produto TEXT,
        valor REAL,
        status TEXT,
        data REAL
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS cupons (
        codigo TEXT PRIMARY KEY,
        desconto INTEGER
    )""")

    base = [
        ("100 Coins", 5, 999, 1),
        ("1.000 Coins", 25, 999, 1),
        ("10.000 Coins", 120, 999, 1),
        ("100.000 Coins", 500, 999, 1),
        ("700.000 Coins", 2500, 999, 1),
    ]

    for p in base:
        try: c.execute("INSERT INTO produtos VALUES (?,?,?,?)", p)
        except: pass

    conn.commit()
    conn.close()

init_db()

# ================= HELPERS =================
def luhn_check(card_number):
    digits = [int(d) for d in card_number if d.isdigit()]
    checksum = 0
    parity = len(digits) % 2
    for i, digit in enumerate(digits):
        if i % 2 == parity:
            digit *= 2
            if digit > 9: digit -= 9
        checksum += digit
    return checksum % 10 == 0

def sha256(txt):
    return hashlib.sha256(txt.encode()).hexdigest()

# ================= ESTILO GLOBAL =================
STYLE = """
<style>
body{
background:#0f0f0f;
color:white;
font-family:Arial;
text-align:center;
}
.card{
width:400px;
margin:40px auto;
padding:20px;
background:#1a1a1a;
border-radius:15px;
box-shadow:0 0 30px #a020f0;
}
button{
background:#a020f0;
border:none;
padding:10px;
border-radius:10px;
color:white;
cursor:pointer;
box-shadow:0 0 15px #a020f0;
}
input{
width:90%;
padding:8px;
margin:5px;
border-radius:8px;
border:none;
}
a{color:#a020f0;text-decoration:none;}
</style>
"""

# ================= LOJA =================
@app.route("/")
def loja():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM produtos WHERE ativo=1")
    produtos = c.fetchall()
    conn.close()

    html = STYLE + "<div class='card'><h1>🛍 Cyber Store</h1>"
    for p in produtos:
        html += f"""
        <p>{p[0]} - R$ {p[1]} (Estoque: {p[2]})
        <a href='/checkout/{p[0]}'><button>Comprar</button></a></p>
        """
    html += "<br><a href='/admin'>Admin</a></div>"
    return html

# ================= CHECKOUT =================
@app.route("/checkout/<produto>", methods=["GET","POST"])
def checkout(produto):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM produtos WHERE nome=?", (produto,))
    item = c.fetchone()

    if not item:
        return "Produto inválido"

    valor = item[1]

    if request.method == "POST":
        numero = request.form["numero"]

        if not luhn_check(numero):
            return "Cartão inválido"

        pedido_id = str(uuid.uuid4())[:8]

        c.execute("INSERT INTO pedidos VALUES (?,?,?,?,?)",
                  (pedido_id, produto, valor, "Pago", time.time()))
        conn.commit()
        conn.close()

        return redirect(f"/sucesso/{pedido_id}")

    conn.close()

    return STYLE + f"""
    <div class='card'>
    <h2>{produto} - R$ {valor}</h2>
    <form method='post'>
    <input name='numero' placeholder='Número do Cartão' required>
    <input placeholder='Nome no Cartão' required>
    <input placeholder='Validade' required>
    <input placeholder='CVV' required>
    <br><br>
    <button>Pagar</button>
    </form>
    </div>
    """

# ================= SUCESSO =================
@app.route("/sucesso/<pedido_id>")
def sucesso(pedido_id):
    return STYLE + f"""
    <div class='card'>
    <h1>✅ Pagamento Aprovado</h1>
    <p>ID: {pedido_id}</p>
    <a href='/'>Voltar</a>
    </div>
    """

# ================= ADMIN =================
@app.route("/admin", methods=["GET","POST"])
def admin():
    if request.method == "POST":
        if request.form.get("user") == ADMIN_USER and \
           sha256(request.form.get("senha")) == ADMIN_PASS_HASH:
            session["admin"] = True

    if not session.get("admin"):
        return STYLE + """
        <div class='card'>
        <h2>🔐 Login Admin</h2>
        <form method='post'>
        <input name='user' placeholder='Usuário'>
        <input type='password' name='senha' placeholder='Senha'>
        <button>Entrar</button>
        </form>
        </div>
        """

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM pedidos")
    pedidos = c.fetchall()
    conn.close()

    html = STYLE + "<div class='card'><h2>📊 Painel Admin</h2>"
    for p in pedidos:
        html += f"<p>{p[0]} | {p[1]} | R$ {p[2]}</p>"
    html += "<br><a href='/'>Voltar</a></div>"
    return html

if __name__ == "__main__":
    app.run()
