import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar

# 1. 페이지 설정
st.set_page_config(page_title="학사 일정 플래너", page_icon="📅", layout="wide")

# 2. 시스템 UI와 충돌 없는 안전한 CSS 스타일 적용 (글자 겹침 현상 해결)
st.markdown("""
    <style>
        /* Streamlit 고유 아이콘이나 버튼 텍스트가 깨지지 않도록 일반 텍스트 및 제목 영역만 타겟팅 */
        h1, h2, h3, .stMarkdown p, .stMarkdown span {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
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

# 4. 세션 데이터 초기화
if 'events_db' not in st.session_state:
    t = datetime.today().date()
    st.session_state.events_db = [
        {"date": t, "category": "수행평가", "content": "수학 탐구 보고서 제출"},
        {"date": t + timedelta(days=2), "category": "시험", "content": "영어 듣기평가"},
        {"date": t + timedelta(days=4), "category": "학교 행사", "content": "현장체험학습"},
        {"date": t - timedelta(days=1), "category": "동아리", "content": "동아리 정기 활동"},
        {"date": t + timedelta(days=6), "category": "모의고사", "content": "전국연합학력평가"},
    ]

# 5. 메인 타이틀
st.title("📅 학사 일정 플래너")
st.write("---")

# 6. 상단 영역: 오늘 일정 요약
st.subheader("오늘의 일정")
today_date = datetime.today().date()
today_evs = [e for e in st.session_state.events_db if e['date'] == today_date]

if today_evs:
    cols = st.columns(len(today_evs))
    for i, ev in enumerate(today_evs):
        info = CATEGORY_INFO[ev['category']]
        with cols[i]:
            st.markdown(f"<div style='padding:12px; border-radius:6px; background:{
