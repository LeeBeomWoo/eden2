import os
import re
import sys
from flask import Flask, request, abort

from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError

from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    StickerMessage
)


from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)

# Vercel이 최상위에서 명확히 인식할 수 있도록 Flask 인스턴스 선언
app = Flask(__name__)

# -----------------------------------------------------------------
# 1. 멤버 닉네임 - LINE User ID 매핑 사전
# -----------------------------------------------------------------
USER_ID_MAP = {
    # 🏆 트로피 그룹
    "86 르페": "Ue2693f02f77ac9e3cb2cf03c5a6ab789",
    "86 반하": "Ua14c6391cd86b3a55366031a1453c685",
    "86 철이": "U0819698e89263d8f93e8a58057cc9d84",
    
    # 📌 핀 그룹
    "⛑️93 주휴📌": "U0998f4ee7c132766c81230fd6877985f",
    "04 망두📌": "U69838e4f843f28938af0fed3f442eceb",
    "⛑️91 율희📌": "Ua89c6031259ef0eb95730982bf401129",
    
    # 📚 책 그룹
    "⛑️91 미트📚": "U_MEAT_USER_ID_HERE"
}

# -----------------------------------------------------------------
# 2. 아이콘 분류별 멤버 리스트
# -----------------------------------------------------------------
TROPHY_MEMBERS = ["86 르페", "86 반하", "86 철이"]
PIN_MEMBERS = ["⛑️93 주휴📌", "04 망두📌", "⛑️91 율희📌"]
BOOK_MEMBERS = ["⛑️91 미트📚"]

def build_group_mention(member_list):

    mention_text = ""

    for nickname in member_list:
        if USER_ID_MAP.get(nickname):
            mention_text += f"@{nickname} "

    return mention_text.strip()

# 환경변수 설정
configuration = Configuration(access_token=os.environ.get("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.environ.get("LINE_CHANNEL_SECRET"))

@app.route("/")
def home():
    return "Eden LINE Bot (Full Version) is Running!"

@app.route("/api", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'
    

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_message = event.message.text.strip()
    
    # '/'로 시작하지 않으면 반응 안 함
    if not user_message.startswith("/"):
        return
        
    command = user_message[1:].strip()
    reply_text = ""

    # -----------------------------------------------------------------
    # 1. 멘션 및 명령어 분기 (문자열 조합 단계 - API 불필요)
    # -----------------------------------------------------------------
    if command in ["🏆", "방장"]:
        mention_text = build_group_mention(TROPHY_MEMBERS)
        reply_text = mention_text if mention_text else "등록된 방장 멤버 ID가 없습니다."

    elif command in ["벙시작"]:
        mention_text = build_group_mention(TROPHY_MEMBERS)
        reply_text = f"{mention_text} 벙시작!" if mention_text else "등록된 방장 멤버 ID가 없습니다."
        
    elif command in ["벙종"]:
        mention_text = build_group_mention(TROPHY_MEMBERS)
        reply_text = f"{mention_text} 벙종료!" if mention_text else "등록된 방장 멤버 ID가 없습니다."

    elif command in ["📌", "관리자"]:
        mention_text = build_group_mention(PIN_MEMBERS)
        reply_text = mention_text if mention_text else "등록된 관리자 멤버 ID가 없습니다."
        
    elif command in ["관리진"]:
        combined_members = TROPHY_MEMBERS + PIN_MEMBERS
        mention_text = build_group_mention(combined_members)
        reply_text = mention_text if mention_text else "등록된 멤버 ID가 없습니다."

    elif command in ["인증자"]:
        mention_text = build_group_mention(BOOK_MEMBERS)
        reply_text = mention_text if mention_text else "등록된 인증자 멤버 ID가 없습니다."

    elif command in ["인증", "남초", "여초", "동반"]:
        all_members = TROPHY_MEMBERS + PIN_MEMBERS + BOOK_MEMBERS
        mention_text = build_group_mention(all_members)
        reply_text = f"{mention_text} 인증요청!" if mention_text else "등록된 멤버 ID가 없습니다."

    elif command in ["ㅁㄴㅂ", "매너봉"]:
        reply_text = "매너봉 시간입니다! 🤫 쉿!"
        
    elif command in ["벙", "갠벙", "섹벙"]:
        reply_text = (
            "🪷 EDEN 오프라인 벙 기본 준수사항 🪻\n\n"
            "0️⃣ 참여 대상 및 원칙\n"
            "- 에덴의 모든 벙은 반드시 '미클 완료' 후 참여 가능합니다.\n"
            "- 벙은 검사지 유무를 따지지 않습니다.\n"
            "- 바쁨표시(📵), 외출(🏖) 기간 및 미활동 멤버는 벙 참여가 불가하거나 제한될 수 있습니다.\n"
            "- 모든 만남은 개인의 자율적 판단과 책임 하에 이루어지며, 발생한 민형사상 문제에 대해 운영진은 일절 책임지지 않습니다.\n"
            "- 금전 거래, 조건 제시, 강압적 행위, 폭력 및 단체 멤버가 함께하는 성교 행위는 엄격히 금지되며 적발 시 강퇴 처리됩니다.\n\n"
            "💡 상세 벙 규칙은 아래 명령어로 확인하세요.\n"
            "👉 단체벙 안내: /단벙\n"
            "👉 1:1 이성벙 안내: /이성벙\n"
            "👉 동성 간의 벙 안내: /동성벙"
        )
        
    elif command in ["단벙", "단체벙"]:
        reply_text = (
            "👥 EDEN 단체벙(3인 이상) 기준 안내 👥\n\n"
            "1️⃣ 6인 이상 대형 단체벙\n"
            "- 방장 또는 부방장에게 벙 진행의사 통보 후 벙주가 이벤트작성\n"
            "- 특정인원의 참석을 의도적으로 기피하거나 방해하는 행위는 발견즉시 경고처리됨\n"
            "- 벙주는 참여인원수를 정해서 모집해야하며 당일까지 모집 가능합니다.\n"
            "- 마감 안했을시 벙중에라도 참가는 가능합니다.\n"
            "- 벙 24시간 전 운영진 관리 하에 전용 벙방 오픈하며 회비는 철저히 '1/n 원칙'을 준수합니다.\n\n"
            "2️⃣ 3~6인 일반 단체벙\n"
            "- 공지나 게시글 댓글에 '벙지 작성' 후 운영진 멘션 필수. 동성 단체벙은 최대 3인까지 가능.\n"
            "🚨 단체벙 공통 의무사항\n"
            "- 선발대 포함 2인 이상 만난 시점에 공창에 '벙 시작' 보고 및 실황 사진 2매 이상 벙 앨범 업로드.\n"
            "- 벙 종료 시 벙주는 공창에 '벙 종료' 통보 필수."
        )
        
    elif "키워드" in command:
        reply_text = (
            "이성벙, 동성벙, 단벙, 단체벙, 벙, 갠벙, 섹벙, 회칙, 규칙, 입장규칙, 활동규칙, 특별권, 선갠라권, 갠벙권, 경고면제권, 경고삭제권, 통화, 영통, 음통, 다락, 사진, 동영상, 매너봉, 미션, 미클, 공지"
        )
        
    elif "이성벙" in command:
        reply_text = (
            "👩‍❤️‍👨 EDEN 1:1 이성벙 기준 안내 👨‍❤️‍👩\n\n"
            "- 반드시 만남 전 사전에 '벙지 작성' 후 운영진을 멘션해야 합니다.\n"
            "- 만난 시점에 공창에 '벙 시작'을 알리고, 함께 있는 사진을 벙 앨범에 업로드해 주세요.\n"
            "- 상대방이 불편함을 표현할 때 어떠한 억지 강요도 절대 엄금합니다.\n"
            "- 🤐 상호 합의 없이 대화나 사실을 외부에 노출할 경우 즉각 강퇴 처리됩니다."
        )
        
    elif "동성벙" in command:
        reply_text = (
            "👬 EDEN 동성벙 기준 안내 👭\n\n"
            "- 동성 간의 모임도 사전에 '벙지 작성' 후 운영진 멘션이 필수입니다.\n"
            "- 만난 시점에 공창에 '벙 시작' 알림 및 함께 있는 사진을 벙 앨범에 업로드해 주세요.\n"
            "🚨 [의무 이성참여 룰] 동성벙을 연속으로 2회 진행한 이후에는, 반드시 이성이 포함된 벙을 최소 1회 이상 완료해야 합니다."
        )
        
    elif command in ["회칙", "규칙", "공지"]:
        reply_text = (
            "❤️ 고품격 성인 커뮤니티「 𝘌 · 𝘋 · 𝘌 · 𝘕 season 2 」🩷\n"
            "- 불법촬영물, 미성년자 관련 콘텐츠, 강압적 성적 행위, 금전 거래 목적 활동은 엄격히 금지되며 즉각 킥(강퇴) 조치 됩니다."
        )
        
    elif "입장규칙" in command:
        reply_text = (
            "✨️ EDEN 입장 규칙 ✨️\n\n"
            "- 남성: 25~45세(군필) / 여성: 23~45세\n"
            "- 커플, 파트너, 네토 동반 입장 및 원픽 금지.\n"
            "- 신입 초대 시 운영진 전원 멘션 필수."
        )
        
    elif "활동규칙" in command:
        reply_text = (
            "✨️ EDEN 활동 규칙 ✨️\n\n"
            "- 심야(00~07시) 멘션 금지.\n"
            "- 일일 최소 30마디 참여 필수 (눈팅 금지).\n"
            "- 외출 시 방장/부방장에게 사전 공유 후 이모지 적용."
        )
        
    elif "검사지" in command:
        reply_text = (
            "✨️ 검사지에 대한 사항 ✨️\n\n"
            "- STD 12종 검사지(3개월 유효) 자율 운영.\n"
            "- 제출 시 ⛑️ 적용, 만료 시 🪖 적용.\n"
            "- 여성 멤버 제출 시 '노미클갠벙권' 1장 지급."
        )
        
    elif command in ["통화", "영통", "음통", "다락"]:
        reply_text = (
            "✨️ 영통 & 음통 규칙 ✨️\n\n"
            "- 그룹통화 시 반드시 화면 켜두기 필수. 본인 화면 끄고 타인 화면만 보는 행위 금지.\n"
            "- 만취 상태 입장 불가, 타인 불편 시 즉시 종료."
        )
        
    elif command in ["사진", "동영상"]:
        reply_text = (
            "✨️ 사진 및 동영상 규칙 ✨️\n\n"
            "- 과도한 음란성 콘텐츠 금지.\n"
            "- 사진 삭제 시 '보내기 취소' 필수.\n"
            "- 매너봉(오전 8시~오후 10시) 필수."
        )
        
    elif command in ["미션", "미클"]:
        reply_text = (
            "❤️ 미션 클리어(미클) 안내사항 🤍\n\n"
            "- 입장 후 5일 이내 여성 1명 초대 + 3일 정착.\n"
            "- 미클 기간 내 미달성 시 강퇴."
        )
        
    elif command in ["특별권", "선갠라권", "갠벙권","경고면제권","경고삭제권"]:
        reply_text = (
            "📕 특별권 안내 📕\n\n"
            "- 선갠라권, 노미클 갠벙권, 경고면제권, 경고삭제권 등 다양한 혜택이 존재합니다.\n"
            "- 교환 조건 및 기한은 운영진의 안내를 따릅니다."
        )
        
    else:
        # 모든 if/elif 라인과 정확히 일치하게 들여쓰기된 else 문
        reply_text = f"없어요(매우정중히). '{command}'이런 명령어는. 😢"

    
    # -----------------------------------------------------------------
    # 메시지 전송 처리 (오류 유발하는 emojis 제거 완료)
    # -----------------------------------------------------------------
    if reply_text:
        try:
            with ApiClient(configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                
                messages_to_send = []

                if command in ["ㅁㄴㅂ", "매너봉"]:
                    for _ in range(4):
                        messages_to_send.append(
                            StickerMessage(package_id="446", sticker_id="1988")
                        )
                else:
                    # ⭐ emojis 속성을 완전히 없애고 TextMessage만 깔끔하게 보냅니다.
                    # 이렇게 하면 키보드 일반 이모지(🏆, 📌 등)가 깨지지 않고 그대로 잘 갑니다!
                    messages_to_send.append(TextMessage(text=reply_text))

                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=messages_to_send
                    )
                )
        except Exception as e:
            print(f"🚨 전송 단계 예외 발생: {e}", file=sys.stderr)



            
if __name__ == "__main__":
    app.run(port=5000)
