from flask import Flask, request, render_template_string, redirect
import sqlite3, uuid, base64
import qrcode
from io import BytesIO

app = Flask(__name__)
app.secret_key = "epic_og_secret"

# ================= DATABASE =================
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS produtos (
        nome TEXT PRIMARY KEY,
        valor REAL
    )""")

    base = [
        ("100 Robux", 5),
        ("1.000 Robux", 25),
        ("10.000 Robux", 120),
        ("100.000 Robux", 500),
        ("700.000 Robux", 2500),
    ]

    for p in base:
        try:
            c.execute("INSERT INTO produtos VALUES (?,?)", p)
        except:
            pass

    conn.commit()
    conn.close()

init_db()

# ================= LOJA =================
@app.route("/")
def loja():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM produtos")
    produtos = c.fetchall()
    conn.close()

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<title>Epic OG Store</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
:root{
--bg:#0f0f12;
--card:#1a1a1f;
--neon:#9d00ff;
--text:#ffffff;
}
body{
margin:0;
background:var(--bg);
font-family:Arial;
color:var(--text);
}
header{
display:flex;
justify-content:space-between;
padding:20px 40px;
background:#111;
}
.logo{
font-size:24px;
color:var(--neon);
font-weight:bold;
}
.grid{
display:grid;
grid-template-columns:repeat(auto-fit,minmax(250px,1fr));
gap:25px;
padding:40px;
}
.card{
background:var(--card);
padding:25px;
border-radius:20px;
box-shadow:0 0 30px rgba(157,0,255,0.2);
text-align:center;
transition:0.3s;
}
.card:hover{
transform:translateY(-5px);
box-shadow:0 0 40px rgba(157,0,255,0.6);
}
.price{
color:var(--neon);
font-size:20px;
margin:10px 0;
}
.btn{
padding:10px 20px;
border:none;
border-radius:12px;
cursor:pointer;
margin:5px;
}
.card-btn{
background:var(--neon);
color:white;
}
.pix-btn{
background:#00c853;
color:white;
}
</style>
</head>
<body>

<header>
<div class="logo">⚡ Epic OG Store</div>
</header>

<div class="grid">
{% for p in produtos %}
<div class="card">
<h2>{{p[0]}}</h2>
<div class="price">R$ {{p[1]}}</div>
<a href="/cartao/{{p[0]}}">
<button class="btn card-btn">💳 Cartão</button>
</a>
<a href="/pix/{{p[0]}}">
<button class="btn pix-btn">💜 Pix</button>
</a>
</div>
{% endfor %}
</div>

</body>
</html>
""", produtos=produtos)

# ================= CARTAO DEMO =================
@app.route("/cartao/<produto>", methods=["GET","POST"])
def cartao(produto):
    if request.method == "POST":
        pedido_id = str(uuid.uuid4())[:8]
        return redirect(f"/sucesso/{pedido_id}")

    return f"""
    <body style="background:#0f0f12;color:white;font-family:Arial;text-align:center;padding:50px">
    <h2>💳 Cartão - Pagamento Simulado</h2>
    <h3>{produto}</h3>
    <form method="post">
    <input placeholder="Número do Cartão" required style="padding:10px;margin:5px;border-radius:8px"><br>
    <input placeholder="Nome no Cartão" required style="padding:10px;margin:5px;border-radius:8px"><br>
    <input placeholder="Validade" required style="padding:10px;margin:5px;border-radius:8px"><br>
    <input placeholder="CVV" required style="padding:10px;margin:5px;border-radius:8px"><br><br>
    <button style="padding:10px 20px;background:#9d00ff;border:none;border-radius:10px;color:white;cursor:pointer">
    Pagar
    </button>
    </form>
    <p style="color:red;margin-top:20px;">
    ⚠️ Sistema DEMO - Nenhum pagamento real é processado.
    </p>
    </body>
    """

# ================= PIX DEMO =================
@app.route("/pix/<produto>")
def pix(produto):
    pedido_id = str(uuid.uuid4())[:8]
    codigo_pix = f"PIX-DEMO-{pedido_id}"

    qr = qrcode.make(codigo_pix)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()

    return f"""
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
    body {{
        background:#0f0f12;
        color:white;
        font-family:Arial;
        text-align:center;
        padding:30px;
    }}
    .box {{
        background:#1a1a1f;
        padding:30px;
        border-radius:20px;
        box-shadow:0 0 40px rgba(157,0,255,0.4);
    }}
    img {{
        width:250px;
    }}
    .code {{
        background:#111;
        padding:10px;
        border-radius:10px;
        margin:15px 0;
        color:#9d00ff;
    }}
    </style>
    </head>
    <body>
    <div class="box">
    <h2>💜 PIX - Pagamento Simulado</h2>
    <p><b>Produto:</b> {produto}</p>

    <img src="data:image/png;base64,{img_str}">
    <div class="code">{codigo_pix}</div>

    <p>⏳ Aguardando pagamento...</p>
    <p id="timer">10</p>

    <script>
    let timeLeft = 10;
    let timer = document.getElementById("timer");
    let interval = setInterval(() => {{
        timeLeft--;
        timer.innerText = timeLeft;
        if(timeLeft <= 0){{
            clearInterval(interval);
            window.location.href="/sucesso/{pedido_id}";
        }}
    }}, 1000);
    </script>

    <p style="color:red;margin-top:20px;">
    ⚠️ Sistema DEMO - Nenhum pagamento real é processado.
    </p>

    </div>
    </body>
    </html>
    """

# ================= SUCESSO =================
@app.route("/sucesso/<pedido_id>")
def sucesso(pedido_id):
    return f"""
    <body style="background:#0f0f12;color:white;font-family:Arial;text-align:center;margin-top:150px">
    <h1>✅ Pagamento Aprovado</h1>
    <h3>ID do Pedido: {pedido_id}</h3>
    <a href="/" style="color:#9d00ff;">Voltar para loja</a>
    </body>
    """

if __name__ == "__main__":
    app.run()# ================= ESTILO GLOBAL =================
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
