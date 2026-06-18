import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar

# 1. 페이지 기본 설정 (레이아웃을 넓게 쓰고 심플한 아이콘 배치)
st.set_page_config(
    page_title="학사 일정 플래너",
    page_icon="📅",
    layout="wide"
)

# 2. 깔끔하고 모던한 미니멀 스타일 적용 (CSS 코드)
st.markdown("""
    <style>
        /* 기본 고딕 계열의 깔끔한 폰트 및 자극적이지 않은 배경 지향 */
        html, body, [data-testid="stWidgetLabel"], .stMarkdown, p, span {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
        }
        h1, h2, h3 {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
            font-weight: 600 !important;
            color: #2D3748 !important;
        }
        /* 구분선 굵기 조절 */
        hr { margin: 1.5rem 0 !important; }
    </style>
""", unsafe_allow_html=True)

# 3. 차분하고 고급스러운 뮤트 파스텔 색상 매핑 (정돈된 톤)
CATEGORY_INFO = {
    "수행평가": {"emoji": "▫️", "color": "#FDE8E8", "text_color": "#E53E3E"},    # 톤다운된 차분한 레드
    "시험": {"emoji": "▫️", "color": "#FEF3C7", "text_color": "#D97706"},        # 포근한 오렌지 브라운
    "학교 행사": {"emoji": "▫️", "color": "#F3E8FF", "text_color": "#8B5CF6"},    # 은은한 라벤더 퍼플
    "동아리": {"emoji": "▫️", "color": "#FEFCE8", "text_color": "#CA8A04"},      # 채도를 낮춘 차분한 옐로우
    "모의고사": {"emoji": "▫️", "color
