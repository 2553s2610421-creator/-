import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar

# 1. 페이지 설정
st.set_page_config(page_title="학사 일정 플래너", page_icon="📅", layout="wide")

# 2. 스타일 CSS 적용
st.markdown("""
    <style>
        h1, h2, h3, .stMarkdown p, .stMarkdown span {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        }
        h1, h2, h3 {
            font-weight: 600 !important;
            color: #2D3748 !important;
        }
        hr { margin: 1.5rem 0 !important; }
    </style>
""", unsafe_allow_html=True)

# 3. 차분한 뮤트 파스텔 색상 매핑
CATEGORY_INFO = {
    "수행평가": {"color": "#FDE8E8", "text": "#E53E3E"},
    "시험": {"color": "#FEF3C7", "text": "#D97706"},
    "학교 행사": {"color": "#F3E8FF", "text": "#8B5CF6"},
    "동아리": {"color": "#FEFCE8", "text": "#CA8A04"},
    "모의고사": {"color": "#DCFCE7", "text": "#16A34A"}
}

# 오늘 날짜 기준 명확히 설정 (2026년 기준 실시간 반영)
today_date = datetime.today().date()

# 4. 세션 데이터 초기화 (날짜 꼬임 방지를 위해 최신화)
if 'events_db' not in st.session_state or not st.session_state.events_db:
    st.session_state.events_db = [
        {"date": today_date, "category": "수행평가", "content": "수학 탐구 보고서 제출"},
        {"date": today_date + timedelta(days=2), "category": "시험", "content": "영어 듣기평가"},
        {"date": today_date + timedelta(days=4), "category": "학교 행사", "content": "현장체험학습"},
        {"date": today_date - timedelta(days=1), "category": "동아리", "content": "동아리 정기 활동"},
        {"date": today_date + timedelta(days=6), "category": "모의고사", "content": "전국연합학력평가"},
    ]

# 5. 메인 타이틀
st.title("📅 학사 일정 플래너")
st.write("---")

# 6. 상단 영역: 오늘 일정 요약
st.subheader("오늘의 일정")
today_evs = [e for e in st.session_state.events_db if e['date'] == today_date]

if today_evs:
    cols = st.columns(len(today_evs))
    for i, ev in enumerate(today_evs):
        info = CATEGORY_INFO[ev['category']]
        with cols[i]:
            c = info['color']
            t = info['text']
            cat = ev['category']
            cnt = ev['content']
            box_html = f"<div style='padding:12px; border-radius:6px; background:{c}; color:{t}; font-weight:bold;'>[{cat}] {cnt}</div>"
            st.markdown(box_html, unsafe_allow_html=True)
else:
    st.write("오늘 예정된 학사 일정이 없습니다.")

st.write("---")

# 7. 메인 화면 레이아웃
left_col, right_col = st.columns([3, 1])

with left_col:
    now = datetime.today()
    c1, c2 = st.columns(2)
    year = c1.selectbox("연도", range(now.year - 1, now.year + 3), index=1)
    month = c2.selectbox("월", range(1, 13), index=now.month - 1)
    
    st.subheader(f"{year}년 {month}월")
    
    # 캘린더 요일 헤더
    hd = "<div style='display:grid; grid-template-columns:repeat(7,1fr); gap:2px; text-align:center; font-weight:bold; margin-bottom:
