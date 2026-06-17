import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar

# 1. 페이지 기본 설정 및 스타일 정의
st.set_page_config(
    page_title="우리 반 격자형 학사 일정 캘린더",
    page_icon="📅",
    layout="wide"
)

# 카테고리별 색상 매핑 (요청 사항 완벽 반영)
CATEGORY_INFO = {
    "수행평가": {"emoji": "🔴", "color": "#FFD6D6", "text_color": "#D93838"},    # 연한 빨강 배경 / 진한 빨강 글씨
    "시험": {"emoji": "🟠", "color": "#FFEAD2", "text_color": "#D97706"},        # 연한 주황 / 진한 주황
    "학교 행사": {"emoji": "🟣", "color": "#EFE5FD", "text_color": "#7C3AED"},    # 연한 보라 / 진한 보라
    "동아리": {"emoji": "🟡", "color": "#FEF9C3", "text_color": "#A16207"},      # 연한 노랑 / 진한 노랑
    "모의고사": {"emoji": "🟢", "color": "#DCFCE7", "text_color": "#15803D"}       # 연한 초록 / 진한 초록
}

# 2. 세션 상태를 이용한 데이터 저장소 초기화 (초기 예시 데이터 포함)
if 'events_db' not in st.session_state:
    today = datetime.today().date()
    st.session_state.events_db = [
        {"date": today, "category": "수행평가", "content": "수학 탐구 보고서"},
        {"date": today + timedelta(days=2), "category": "시험", "content": "영어 듣기평가"},
        {"date": today + timedelta(days=4), "category": "학교 행사", "content": "현장체험학습"},
        {"date": today - timedelta(days=2), "category": "동아리", "content": "레고 로봇 조립"},
        {"date": today + timedelta(days=6), "category": "모의고사", "content": "6월 학평"},
    ]

# --- 메인 화면 레이아웃 시작 ---
st.title("📅 우리 반 격자형 학사 일정 캘린더")
st.caption("선생님과 학생이 함께 확인하는 한눈에 보는 달력 대시보드입니다.")
st.write("---")

# 3. 상단: 오늘 일정 표시 영역
st.subheader("📌 오늘 우리의 일정")
today_date = datetime.today().date()
today_events = [e for e in st.session_state.events_db if e['date'] == today_date]

if today_events:
    cols = st.columns(len(today_events))
    for i, ev in enumerate(today_events):
        info = CATEGORY_INFO[ev['category']]
        with cols[i]:
            st.markdown(
                f"<div style='padding:12px; border-radius:8px; background-color:{info['color']}; "
                f"color:{info['text_color']}; font-weight:bold; border-left:5px solid {info['text_color']};'>"
                f"{info['emoji']} [{ev['category']}] {ev['content']}"
                f"</div>", 
                unsafe_allow_html=True
            )
else:
    st.info("🎉 오늘 예정된 공식 일정이 없습니다! 자유 시간을 즐기세요.")

st.write("---")

# 4. 하단 레이아웃 분할 (좌측: 달력 모양 및 입력 / 우측: 이번 주 요약 리스트)
left_col, right_col = st.columns([3, 1])

with left_col:
    # 연도 및 월 선택 컨트롤
    now = datetime.today()
    c1, c2 = st.columns(2)
    with c1:
        year = st.selectbox("연도 선택", range(now.year - 1, now.year + 3), index=1)
    with c2:
        month = st.selectbox("월 선택", range(1, 13), index=now.month - 1)
        
    st.subheader(f"🗓️ {year}년 {month}월 달력")
    
    # --- HTML 격자형 캘린더 생성 ---
    # 요일 헤더
    days_header = ["일", "월", "화", "수", "목", "금", "토"]
    header_html = "".join([f"<div style='text-align:center; font-weight:bold; background-color:#f3f4f6; padding:8px; border:1px solid #e5e7eb;'>{d}</div>" for d in days_header])
    
    # 해당 월의 달력 날짜 계산
    cal = calendar.Calendar(firstweekday=6) # 일요일부터 시작
    month_days = cal.monthdatescalendar(year, month)
    
    cells_html = ""
    for week in month_days:
        for day in week:
            # 선택한 달이 아닌 날짜는 흐리게 처리
            if day.month != month:
                cells_html += "<div style='min-height:100px; background-color:#f9fafb; color:#d1d5db; border:1px solid #e5e7eb; padding:4px;'></div>"
                continue
            
            # 오늘 날짜 강조 스타일 테두리
            is_today = "border:2px solid #3b82f6; background-color:#eff6ff;" if day == today_date else "border:1px solid #e5e7eb;"
            
            # 해당 날짜의 일정이 있는지 확인 후 배지 생성
            day_events = [e for e in st.session_state.events_db if e['date'] == day]
            events_html = ""
            for ev in day_events:
                info = CATEGORY_INFO[ev['category']]
                events_html += (
                    f"<div style='font-size:11px; padding:2px 4px; margin-top:3px; border-radius:4px; "
                    f"background-color:{info['color']}; color:{info['text_color']}; font-weight:bold; "
                    f"white-space:nowrap; overflow:hidden; text-overflow:ellipsis;' title='{ev['content']}'>"
                    f"{info['emoji']} {ev['content']}"
                    f"</div>"
                )
                
            cells_html += (
                f"<div style='min-height:105px; {is_today} padding:6px; display:flex; flex-direction:column; justify-content:flex-start;'>"
                f"<span style='font-weight:bold; font-size:14px;'>{day.day}</span>"
                f"{events_html}"
                f"</div>"
            )
            
    # 전체 캘린더 그리드 조립 및 출력
    calendar_main_html = f"""
    <div style="display: grid; grid-template-columns: repeat(7, 1fr); gap: 2px; width: 100%;">
        {header_html}
        {cells_html}
    </div>
    """
    st.markdown(calendar_main_html, unsafe_allow_html=True)
    st.write("")
    
    # --- 일정 등록 Form ---
    with st.expander("➕ 새로운 일정 등록하기", expanded=False):
        with st.form("add_event_form", clear_on_submit=True):
            in_date = st.date_input("날짜", datetime.today())
            in_cate = st.selectbox("종류", list(CATEGORY_INFO.keys()))
            in_cont = st.text_input("내용", placeholder="예: 국어 1단원 수행평가 제출")
            submit = st.form_submit_button("캘린더에 추가")
            
            if submit:
                if not in_cont.strip():
                    st.error("내용을 입력하셔야 등록됩니다!")
                else:
                    st.session_state.events_db.append({"date": in_date, "category": in_cate, "content": in_cont})
                    st.success("일정이 추가되었습니다!")
                    st.rerun()

with right_col:
    st.subheader("📊 이번 주 요약 목록")
    
    # 오늘부터 일주일 뒤까지 범위 지정
    end_of_week = today_date + timedelta(days=7)
    week_events = [e for e in st.session_state.events_db if today_date <= e['date'] <= end_of_week]
    # 날짜 순 정렬
    week_events.sort(key=lambda x: x['date'])
    
    if week_events:
        st.caption(f"{today_date} ~ {end_of_week} (7일간)")
        for ev in week_events:
            info = CATEGORY_INFO[ev['category']]
            # 요일 구하기
            ko_days = ["월", "화", "수", "목", "금", "토", "일"]
            weekday_str = ko_days[ev['date'].weekday()]
            
            st.markdown(
                f"<div style='padding:10px; margin-bottom:8px; border-radius:6px; background-color:{info['color']}; color:{info['text_color']};'>"
                f"<b>📅 {ev['date'].strftime('%m/%d')}({weekday_str})</b><br>"
                f"{info['emoji']} {ev['content']}"
                f"</div>",
                unsafe_allow_html=True
            )
    else:
        st.write("이번 주말까지 예정된 일정이 없습니다. 🙌")

    # 관리자 기능 (데이터 전체 삭제)
    st.write("---")
    with st.expander("⚙️ 캘린더 데이터 관리"):
        if st.button("모든 일정 초기화"):
            st.session_state.events_db = []
            st.success("모든 일정이 초기화되었습니다.")
            st.rerun()
