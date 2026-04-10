import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime

# ===== CONFIGURAÇÕES =====
EVENTOS = {
    "BTS 28/10": "https://www.ticketmaster.com.br/event/venda-geral-bts-world-tour-arirang-28-10",
    "BTS 30/10": "https://www.ticketmaster.com.br/event/venda-geral-bts-world-tour-arirang-30-10",
    "BTS 31/10": "https://www.ticketmaster.com.br/event/venda-geral-bts-world-tour-arirang-31-10"
}

# Funçao para enviar alerta no Telegram
def enviar_telegram(mensagem):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={mensagem}"
        try:
            requests.get(url)
        except Exception as e:
            print(f"Erro ao enviar Telegram: {e}")

# ===== VERIFICAÇÃO =====
def verificar():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    print("\n🔄 Verificando ingressos...\n")
    resultados_html = ""
    tem_ingresso_geral = False

    for nome, url in EVENTOS.items():
        try:
            # Usando uma sessão para ser mais "humano"
            session = requests.Session()
            response = session.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(response.text, "html.parser")
            texto = soup.text.lower()

            indisponivel = ["sold out", "esgotado", "indisponível", "tickets not available"]
            # Verifica se algum termo de 'indisponivel' NÃO está na página
            esta_disponivel = not any(p in texto for p in indisponivel)

            cor = "green" if esta_disponivel else "red"
            status_texto = "DISPONÍVEL" if esta_disponivel else "ESGOTADO"
            
            # Monta a linha do site
            resultados_html += f"<li><b style='color:{cor}'>{nome}: {status_texto}</b> - <a href='{url}'>Link</a></li>"

            if esta_disponivel:
                print(f"🟢 {nome}: DISPONÍVEL!")
                enviar_telegram(f"🚨 INGRESSO DISPONÍVEL: {nome}\nCorra aqui: {url}")
                tem_ingresso_geral = True
            else:
                print(f"🔴 {nome}: ESGOTADO")

        except Exception as e:
            print(f"Erro em {nome}: {e}")
            resultados_html += f"<li>{nome}: Erro na verificação</li>"

    # Criar o arquivo index.html para o GitHub Pages
    agora = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    html_content = f"""
    <html>
    <head><title>Monitor BTS - Arirang</title><meta charset='UTF-8'><meta http-equiv='refresh' content='60'></head>
    <body style='font-family: sans-serif; text-align: center; padding: 50px;'>
        <h1>Monitor de Ingressos BTS 💜</h1>
        <p>Última atualização: {agora}</p>
        <ul style='list-style: none; padding: 0;'>
            {resultados_html}
        </ul>
        <p><i>A página atualiza sozinha a cada minuto.</i></p>
    </body>
    </html>
    """
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

# Executa uma única vez (o GitHub Actions chamará o script de novo depois)
if __name__ == "__main__":
    verificar()
