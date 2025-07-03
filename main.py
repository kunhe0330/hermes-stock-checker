import requests
import telegram
import os
import asyncio
from bs4 import BeautifulSoup
from flask import Flask

# Flask 앱 초기화 (이 부분이 반드시 최상단에 있어야 합니다)
app = Flask(__name__)

async def send_telegram_message(bot, chat_id, message):
    """텔레그램으로 메시지를 비동기 방식으로 보냅니다."""
    try:
        await bot.send_message(chat_id=chat_id, text=message)
        print(f"텔레그램 메시지 발송 성공: {message}")
    except Exception as e:
        print(f"텔레그램 메시지 발송 실패: {e}")

def check_stock_status(url):
    """웹사이트 상태를 확인하여 3가지 상태 중 하나를 반환합니다: CART_ACTIVE, PAGE_ACTIVE, NO_PAGE"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200 or '인터넷 연결에 문제가 발생했습니다' in response.text:
            print(f"URL: {url}, 상태: NO_PAGE (페이지 없음)")
            return "NO_PAGE"

        soup = BeautifulSoup(response.text, 'lxml')
        form = soup.find('form', id='add-to-cart-form')
        
        if form:
            add_to_cart_button = form.find('button')
            if add_to_cart_button and not add_to_cart_button.has_attr('disabled'):
                print(f"URL: {url}, 상태: CART_ACTIVE (장바구니 활성화)")
                return "CART_ACTIVE"
        
        print(f"URL: {url}, 상태: PAGE_ACTIVE (상세페이지만 활성화)")
        return "PAGE_ACTIVE"

    except Exception as e:
        print(f"URL 확인 중 오류 발생 ({url}): {e}")
        return "NO_PAGE"

async def run_check():
    """실제 확인 로직을 실행하는 비동기 함수"""
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        print("오류: 텔레그램 환경 변수가 설정되지 않았습니다.")
        return

    urls_to_check = [
        'https://www.hermes.com/kr/ko/product/picotin-lock-18-%EB%B0%B1-H056289CC89/',
        'https://www.hermes.com/kr/ko/product/picotin-lock-18-%EB%B0%B1-H056289CK89/'
    ]
    
    bot = telegram.Bot(token=bot_token)
    
    for url in urls_to_check:
        status = check_stock_status(url)
        
        if status == "CART_ACTIVE":
            message = f"🛒 **장바구니 활성화!** 🛒\n\n'장바구니 담기' 버튼이 활성화되었습니다! 지금 바로 확인하세요!\n\n{url}"
            await send_telegram_message(bot, chat_id, message)
        
        elif status == "PAGE_ACTIVE":
            message = f"📄 **상세 페이지 활성화!** 📄\n\n품절이었던 상품 페이지가 열렸습니다. 곧 장바구니가 활성화될 수 있습니다.\n\n{url}"
            await send_telegram_message(bot, chat_id, message)

    print("확인 완료.")

# Cron-job.org에서 접속할 주소 ('/')
@app.route("/")
def trigger_check():
    """HTTP 요청을 받으면 비동기 체크 함수를 실행합니다."""
    asyncio.run(run_check())
    return "Check complete.", 200

# Cloud Run 환경에서 서버를 실행하기 위한 부분
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
