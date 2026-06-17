import json
import os
import streamlit as st
from google import genai
from google.genai import types

# 1. 페이지 설정
st.set_page_config(
    page_title="시험 & 수행평가 링크 아카이브", page_icon="🔗", layout="centered"
)

# 고정된 7개 과목 리스트
SUBJECTS = [
    "국어",
    "수학",
    "영어",
    "역사",
    "과학",
    "사회",
    "가정·정보",
]  # 가정과 정보를 하나로 묶거나 나눌 수 있습니다.

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


# 3. AI 자동 과목 분류 함수 (Gemini API 활용)
def classify_with_ai(title_text):
    # Streamlit Secrets에서 API 키를 가져옵니다 (배포 시 설정 필요)
    api_key = st.secrets.get("GEMINI_API_KEY")

    if not api_key:
        # API 키가 설정되지 않은 경우, 제목에 과목명이 포함되어 있는지 간단히 체크하는 기본 로직으로 대체
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
st.write("선생님들이 공유해주신 각종 PDF 링크나 드라이브 주소를 모아두는 곳입니다.")
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
    submit_btn = st.form_submit_with_click(label="🚀 등록하기")

    if submit_btn:
        if not title or not url:
            st.error("설명과 링크 주소를 모두 입력해주세요!")
        else:
            with st.spinner("AI가 과목을 자동으로 분류하는 중..."):
                assigned_subject = classify_with_ai(title)

            if assigned_subject == "미분류":
                st.warning(
                    "🤔 AI가 자동으로 과목을 분류하지 못했습니다. 수동 분류 프로세스가 필요할 수 있습니다."
                )
                # 분류 실패 시 기본적으로 첫 번째 과목에 넣거나 수동 선택하게 유도 가능 (여기선 우선 국어로 예시)
                assigned_subject = "국어"

            # 데이터 저장
            new_item = {"title": title, "url": url}
            st.session_state.db[assigned_subject].append(new_item)
            save_data(st.session_state.db)

            st.success(
                f"🎉 '{title}' 자료가 **[{assigned_subject}]** 과목으로 자동 분류되어 등록되었습니다!"
            )

st.write("---")

# 5. 과목별 조회 섹션 (학생/교사 공용)
st.header("📖 과목별 자료 보기")

# 7개 과목을 탭(Tab) 스타일로 보기 좋게 분할
tabs = st.tabs([f"📚 {sub}" for sub in SUBJECTS])

for idx, sub in enumerate(SUBJECTS):
    with tabs[idx]:
        st.subheader(f"{sub} 자료실")
        links = st.session_state.db.get(sub, [])

        if not links:
            st.info(f"현재 {sub} 과목에 등록된 링크 자료가 없습니다.")
        else:
            # 깔끔한 카드 형태로 목록 출력
            for l_idx, link_item in enumerate(links):
                with st.container():
                    col1, col2 = st.columns([5, 1])
                    with col1:
                        st.markdown(f"🔗 **{link_item['title']}**")
                    with col2:
                        st.link_button("바로가기", link_item["url"])
                st.write("")
