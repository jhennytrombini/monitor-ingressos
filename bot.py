import cloudscraper
from bs4 import BeautifulSoup
import os
from datetime import datetime, timedelta

# ===== CONFIGURAÇÕES =====
EVENTOS = {
    "BTS 28/10": "https://www.ticketmaster.com.br/event/venda-geral-bts-world-tour-arirang-28-10",
    "BTS 30/10": "https://www.ticketmaster.com.br/event/venda-geral-bts-world-tour-arirang-30-10",
    "BTS 31/10": "https://www.ticketmaster.com.br/event/venda-geral-bts-world-tour-arirang-31-10"
}

def enviar_telegram(mensagem):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={mensagem}"
        try:
            import requests
            requests.get(url, timeout=10)
        except:
            pass

def verificar():
    # Cria o scraper que tenta burlar o bloqueio 403
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )
    
    resultados_html = ""
    agora_brasil = datetime.now() - timedelta(hours=3)
    hora_formatada = agora_brasil.strftime('%d/%m/%Y %H:%M:%S')

    for nome, url in EVENTOS.items():
        try:
            # Tenta acessar o site com o scraper
            response = scraper.get(url, timeout=20)
            
            if response.status_code != 200:
                esta_disponivel = False
                status_texto = f"STATUS {response.status_code} (Bloqueio)"
                cor = "orange"
            else:
                soup = BeautifulSoup(response.text, "html.parser")
                texto = soup.text.lower()
                
                termos_esgotado = ["esgotado", "indisponível", "sold out", "não há ingressos", "vendas encerradas"]
                
                # Critério: Se o site carregou algo real e não tem termos de esgotado
                esta_disponivel = len(texto) > 1000 and not any(p in texto for p in termos_esgotado)
                
                status_texto = "DISPONÍVEL" if esta_disponivel else "ESGOTADO"
                cor = "green" if esta_disponivel else "red"

            resultados_html += f"<li><b style='color:{cor}'>{nome}: {status_texto}</b> - <a href='{url}'>Link</a></li>"

            if esta_disponivel:
                enviar_telegram(f"🚨 INGRESSO DISPONÍVEL: {nome}\n{url}")

        except Exception as e:
            resultados_html += f"<li>{nome}: Erro de conexão</li>"

    html_content = f"""
    <html>
    <head><meta charset='UTF-8'><meta http-equiv='refresh' content='60'></head>
    <body style='font-family: sans-serif; text-align: center; padding-top: 50px;'>
        <h1>Monitor de Ingressos BTS 💜</h1>
        <p>Última atualização (Maringá): {hora_formatada}</p>
        <ul style='list-style: none; padding: 0;'>{resultados_html}</ul>
        <p style='font-size: 12px; color: gray;'>Bot operando via CloudScraper no GitHub Actions</p>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    verificar()
