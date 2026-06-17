import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 1. 페이지 기본 설정 및 테마
st.set_page_config(
    page_title="우리 반 일정 & 수행평가 캘린더",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. 세션 상태(Session State)를 이용한 데이터 초기화 (DB 대용)
if 'events' not in st.session_state:
    # 기본 예시 데이터 제공
    today = datetime.today().date()
    st.session_state.events = pd.DataFrame([
        {"날짜": today, "종류": "수행평가 🔴", "내용": "수학 탐구 보고서 제출"},
        {"날짜": today + timedelta(days=2), "종류": "시험 🟠", "내용": "영어 듣기 평가"},
        {"날짜": today + timedelta(days=4), "종류": "학교 행사 🟣", "내용": "현장체험학습"},
    ])

# 카테고리별 색상 매핑 (안내용)
CATEGORY_COLORS = {
    "수행평가 🔴": "🔴 빨간색",
    "시험 🟠": "🟠 주황색",
    "학교 행사 🟣": "🟣 보라색",
    "기타 일정 🔵": "🔵 파란색"
}

# --- 메인 화면 레이아웃 분할 ---
st.title("📅 우리 반 일정 & 수행평가 캘린더")
st.markdown("선생님과 학생이 함께 공유하는 학사 일정 관리 공간입니다.")
st.write("---")

# 상단: 오늘 일정 간단 표시 칸
st.subheader("📌 오늘 우리의 일정")
today_date = datetime.today().date()
today_events = st.session_state.events[st.session_state.events["날짜"] == today_date]

if not today_events.empty:
    cols = st.columns(len(today_events))
    for i, (_, row) in enumerate(today_events.iterrows()):
        with cols[i % len(cols)]:
            st.info(f"**[{row['종류']}]**\n\n{row['내용']}")
else:
    st.success("🎉 오늘 예정된 공식 일정이 없습니다! 힘내세요!")

st.write("---")

# --- 하단 레이아웃 (좌측: 메인 기능 / 우측: 이번 주 요약 사이드바 역할) ---
left_col, right_col = st.columns([3, 1])

with left_col:
    st.subheader("🗓️ 전체 일정 보기")
    
    # 예외 처리: 데이터가 비어있을 때
    if st.session_state.events.empty:
        st.info("등록된 일정이 없습니다. 아래에서 첫 일정을 등록해보세요!")
    else:
        # 날짜 정렬 후 보기 좋게 출력
        display_df = st.session_state.events.sort_values(by="날짜").copy()
        display_df["날짜"] = display_df["날짜"].astype(str) # 출력용 변환
        
        # 데이터프레임 스타일 적용 (가독성 확보)
        st.dataframe(
            display_df, 
            use_container_width=True, 
            column_config={
                "날짜": st.column_config.TextColumn("📅 날짜"),
                "종류": st.column_config.TextColumn("🏷️ 분류"),
                "내용": st.column_config.TextColumn("📝 상세 내용")
            },
            hide_index=True
        )
    
    st.write("---")
    
    # 일정 등록 Form
    st.subheader("➕ 새 일정 등록하기")
    with st.form("event_form", clear_on_submit=True):
        input_date = st.date_input("날짜 선택", datetime.today())
        input_category = st.selectbox("일정 종류", list(CATEGORY_COLORS.keys()))
        input_content = st.text_input("일정 내용 (예: 국어 1단원 수행평가)", placeholder="내용을 입력하세요")
        
        submit_button = st.form_submit_button("일정 추가하기")
        
        if submit_button:
            if not input_content.strip():
                st.error("⚠️ 일정 내용을 입력해주세요!")
            else:
                # 새 데이터를 데이터프레임에 추가
                new_data = pd.DataFrame([{"날짜": input_date, "종류": input_category, "내용": input_content}])
                st.session_state.events = pd.concat([st.session_state.events, new_data], ignore_index=True)
                st.success("✅ 일정이 성공적으로 등록되었습니다!")
                st.rerun() # 화면 즉시 새로고침

with right_col:
    st.subheader("📊 이번 주 일정 요약")
    
    # 이번 주 범위 계산 (오늘부터 7일간)
    end_of_week = today_date + timedelta(days=7)
    
    # 필터링
    week_events = st.session_state.events[
        (st.session_state.events["날짜"] >= today_date) & 
        (st.session_state.events["날짜"] <= end_of_week)
    ].sort_values(by="날짜")
    
    if not week_events.empty:
        st.caption(f"{today_date} ~ {end_of_week} (7일간)")
        for _, row in week_events.iterrows():
            # 날짜 요일 구하기
            days = ["월", "화", "수", "목", "금", "토", "일"]
            weekday = days[row['날짜'].weekday()]
            
            st.markdown(f"**📅 {row['날짜'].strftime('%m/%d')}({weekday})**")
            st.markdown(f"{row['종류']} - {row['내용']}")
            st.markdown("---")
    else:
        st.write("이번 주말까지 예정된 일정이 없습니다. 🙌")

    # [차별화 기능] 일정 초기화/관리 기능 추가
    st.write("")
    st.write("")
    with st.expander("⚙️ 일정 관리방 (초기화)"):
        st.warning("주의: 초기화 시 현재 세션에 입력된 모든 데이터가 삭제됩니다.")
        if st.button("모든 일정 삭제"):
            st.session_state.events = pd.DataFrame(columns=["날짜", "종류", "내용"])
            st.success("초기화 완료!")
            st.rerun()
