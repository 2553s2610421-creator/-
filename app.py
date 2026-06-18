import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="학사 일정 플래너",
    page_icon="📅",
    layout="wide"
)

# 2. 미니멀 스타일 CSS 적용
st.markdown("""
    <style>
        html, body, [data-testid="stWidgetLabel"], .stMarkdown, p, span {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
        }
        h1, h2, h3 {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
            font-weight: 600 !important;
            color: #2D3748 !important;
        }
        hr { margin: 1.5rem 0 !important; }
    </style>
""", unsafe_allow_html=True)

# 3. 차분한 뮤트 파스텔 색상 매핑
CATEGORY_INFO = {
    "수행평가": {"color": "#FDE8E8", "text_color": "#E53E3E"},
    "시험": {"color": "#FEF3C7", "text_color": "#D97706"},
    "학교 행사": {"color": "#F3E8FF", "text_color": "#8B5CF6"},
    "동아리": {"color": "#FEFCE8", "text_color": "#CA8A04"},
    "모의고사": {"color": "#DCFCE7", "text_color": "#16A34A"}
}

# 4. 세션 데이터 초기화
if 'events_db' not in st.session_state:
    today = datetime.today().date()
    st.session_state.events_db = [
        {"date": today, "category": "수행평가", "content": "수학 탐구 보고서 제출"},
        {"date": today + timedelta(days=2), "category": "시험", "content": "영어 듣기평가"},
        {"date": today + timedelta(days=4), "category": "학교 행사", "content": "현장체험학습"},
        {"date": today - timedelta(days=1), "category": "동아리", "content": "동아리 정기 활동"},
        {"date": today + timedelta(days=6), "category": "모의고사", "content": "전국연합학력평가"},
    ]

# --- 메인 화면 레이아웃 ---
st.title("📅 학사 일정 플래너")
st.markdown("<p style='color:#718096; font-size:1.05rem;'>월간 학사 일정 및 주요 평가 일정을 한눈에 관리하는 대시보드입니다.</p>", unsafe_allow_html=True)
st.write("---")

# 5. 상단 영역: 오늘 일정 요약
st.subheader("오늘의 일정")
today_date = datetime.today().date()
today_events = [e for e in st.session_state.events_db if e['date'] == today_date]

if today_events:
    cols = st.columns(len(today_events))
    for i, ev in enumerate(today_events):
        info = CATEGORY_INFO[ev['category']]
        with cols[i]:
            st.markdown(
                f"<div style='padding:14px; border-radius:6px; background-color:{info['color']}; "
                f"color:{info['text_color']}; font-weight:500; border-left:4px solid {info['text_color']};'>"
                f"[{ev['category']}] {ev['content']}"
                f"</div>", 
                unsafe_allow_html=True
            )
else:
    st.markdown("<p style='color:#A0AEC0; font-size:0.95rem;'>오늘 예정된 학사 일정이 없습니다.</p>", unsafe_allow_html=True)

st.write("---")

# 6. 본문 영역 분할 (좌: 달력 및 등록 / 우: 주간 요약 및 디데이)
left_col, right_col = st.columns([3, 1])

with left_col:
    now = datetime.today()
    c1, c2 = st.columns(2)
    with c1:
        year = st.selectbox("연도", range(now.year - 1, now.year + 3), index=1)
    with c2:
        month = st.selectbox("월", range(1, 13), index=now.month - 1)
        
    st.subheader(f"{year}년 {month}월")
    
    # 캘린더 요일 헤더
    days_header =
