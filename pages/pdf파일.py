import json
import os
from datetime import datetime, timedelta
import streamlit as st
from google import genai
from google.genai import types

# 1. 페이지 설정
st.set_page_config(
    page_title="시험 & 수행평가 링크 아카이브", page_icon="🔗", layout="centered"
)

# 🔐 선생님 전용 등록 비밀번호 (원하는 대로 바꾸셔도 됩니다)
UPLOAD_PASSWORD = "qwerty123"

# 고정된 7개 과목 리스트
SUBJECTS = ["국어", "수학", "영어", "역사", "과학", "사회", "가정·정보"]

DATA_FILE = "links.json"


# 2. 데이터 저장/로드 함수
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {sub: [] for sub in SUBJECTS}
    return {sub: [] for sub in SUBJECTS}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# 데이터 초기화
if "db" not in st.session_state:
    st.session_state.db = load_data()


# ⏱️ 3개월 지난 링크 자동 삭제 함수
def clean_old_links(data):
    three_months_ago = datetime.now() - timedelta(
        days=90
    )  # 3개월(90일) 전 날짜 계산
    updated = False

    for sub in SUBJECTS:
        current_links = data.get(sub, [])
        valid_links = []

        for link in current_links:
            # 등록일이 없는 옛날 데이터 방어 코드
            if "date" not in link:
                valid_links.append(link)
                continue

            # 문자열로 저장된 날짜를 데이터 형식으로 변환하여 비교
            link_date = datetime.strptime(link["date"], "%Y-%m-%d")
            if link_date >= three_months_ago:
                valid_links.append(link)
            else:
                updated = True  # 삭제된 게 있다면 저장하기 위해 체크

        data[sub] = valid_links

    if updated:
        save_data(data)
    return data


# 앱 시작 시 오래된 링크 자동 청소
st.session_state.db = clean_old_links(st.session_state.db)


# 3. AI 자동 과목 분류 함수 (Gemini API 활용)
def classify_with_ai(title_text):
    api_key = st.secrets.get("GEMINI_API_KEY")

    if not api_key:
        for sub in SUBJECTS:
            if sub in title_text:
                return sub
        return "미분류"

    try:
        client = genai.Client(api_key=api_key)
        prompt = f"""
        입력된 텍스트를 보고 다음 7개 과목 중 가장 연관 깊은 과목 하나만 정확히 골라줘.
        과목 리스트: {', '.join(SUBJECTS)}
        
        텍스트: "{title_text}"
        
        주의: 오직 과목 이름만 딱 한 단어로 답변해줘. 매칭되는 게 없으면 '미분류'라고 해줘.
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        result = response.text.strip()
        return result if result in SUBJECTS else "미분류"
    except Exception as e:
        return "미분류"


# --- UI 시작 ---
st.title("🔗 시험 & 수행평가 자료 링크 보관소")
st.write(
    "선생님들이 공유해주신 각종 PDF 링크나 드라이브 주소를 모아두는 곳입니다."
)
st.caption("⚠️ 등록된 링크는 3개월(90일)이 지나면 자동으로 삭제됩니다.")
st.write("---")

# 4. 링크 등록 섹션 (선생님용)
st.header("➕ 새 자료 링크 등록하기")
with st.form("link_form", clear_on_submit=True):
    title = st.text_input(
        "📝 자료 설명 (예: 1학기 국어 수행평가 안내 파일)",
        placeholder="텍스트를 분석하여 과목이 자동으로 분류됩니다.",
    )
    url = st.text_input(
        "🔗 링크 주소 (URL)",
        placeholder="https://drive.google.com/... 혹은 파일 링크",
    )

    # 🔐 비밀번호 입력칸 추가 (검은 점으로 가려지게 type="password" 설정)
    password_input = st.text_input(
        "🔒 등록 비밀번호 입력",
        type="password",
        placeholder="선생님 인증 비밀번호를 입력하세요",
    )

    submit_btn = st.form_submit_button(label="🚀 등록하기")

    if submit_btn:
        if not title or not url:
            st.error("설명과 링크 주소를 모두 입력해주세요!")
        elif password_input != UPLOAD_PASSWORD:
            st.error("❌ 비밀번호가 틀렸습니다! 아무나 등록할 수 없습니다.")
        else:
            with st.spinner("AI가 과목을 자동으로 분류하는 중..."):
                assigned_subject = classify_with_ai(title)

            if assigned_subject == "미분류":
                assigned_subject = "국어"

            # 데이터 저장 (오늘 날짜 포함해서 저장)
            today_str = datetime.now().strftime("%Y-%m-%d")
            new_item = {"title": title, "url": url, "date": today_str}

            st.session_state.db[assigned_subject].append(new_item)
            save_data(st.session_state.db)

            st.success(
                f"🎉 '{title}' 자료가 **[{assigned_subject}]** 과목으로 자동 분류되어 등록되었습니다!"
            )

st.write("---")

# 5. 과목별 조회 섹션 (학생/교사 공용)
st.header("📖 과목별 자료 보기")

tabs = st.tabs([f"📚 {sub}" for sub in SUBJECTS])

for idx, sub in enumerate(SUBJECTS):
    with tabs[idx]:
        st.subheader(f"{sub} 자료실")
        links = st.session_state.db.get(sub, [])

        if not links:
            st.info(f"현재 {sub} 과목에 등록된 링크 자료가 없습니다.")
        else:
            for l_idx, link_item in enumerate(links):
                with st.container():
                    col1, col2 = st.columns([5, 1])
                    with col1:
                        # 등록일자도 함께 표시해 줌 (보기 좋게)
                        date_display = link_item.get("date", "날짜 불명")
                        st.markdown(
                            f"🔗 **{link_item['title']}** <span style='color:gray; font-size:12px;'>({date_display} 등록)</span>",
                            unsafe_allow_html=True,
                        )
                    with col2:
                        st.link_button("바로가기", link_item["url"])
                st.write("")
