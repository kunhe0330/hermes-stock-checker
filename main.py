import requests
import telegram
import os

def send_telegram_message(bot, chat_id, message):
    """텔레그램으로 메시지를 보냅니다."""
    try:
        bot.send_message(chat_id=chat_id, text=message)
        print(f"텔레그램 메시지 발송 성공: {message}")
    except Exception as e:
        print(f"텔레그램 메시지 발송 실패: {e}")

def check_website(url):
    """웹사이트 상태를 확인하고, 정상 페이지이면 True를 반환합니다."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)

        print(f"URL: {url}, Status Code: {response.status_code}")

        if response.status_code == 200 and '인터넷 연결에 문제가 발생했습니다' not in response.text:
            return True
        else:
            return False
    except requests.exceptions.RequestException as e:
        print(f"URL 확인 중 오류 발생 ({url}): {e}")
        return False

def main():
    """메인 실행 함수"""
    print("에르메스 재입고 확인 스크립트 실행")

    try:
        bot_token = os.environ['TELEGRAM_BOT_TOKEN']
        chat_id = os.environ['TELEGRAM_CHAT_ID']
    except KeyError:
        print("오류: TELEGRAM_BOT_TOKEN 또는 TELEGRAM_CHAT_ID 환경 변수가 설정되지 않았습니다.")
        return

    urls_to_check = [
        'https://www.hermes.com/kr/ko/product/picotin-lock-18-%EB%B0%B1-H056289CC89/',
        'https://www.hermes.com/kr/ko/product/picotin-lock-18-%EB%B0%B1-H056289CK89/'
    ]

    bot = telegram.Bot(token=bot_token)

    for url in urls_to_check:
        if check_website(url):
            message = f"🎉 에르메스 재입고 알림! 🎉\n\n상품 페이지가 활성화되었습니다.\n아래 링크를 지금 확인해보세요!\n\n{url}"
            send_telegram_message(bot, chat_id, message)

    print("확인 완료.")

if __name__ == '__main__':
    main()
