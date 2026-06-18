import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar

# 1. 페이지 설정
st.set_page_config(page_title="학사 일정 플래너", page_icon="📅", layout="wide")

# 2. 차분한 뮤트 파스텔 색상 매핑
CATEGORY_INFO = {
    "수행평가": {"color": "#FDE8E8", "text": "#E53E3E"},
    "시험": {"color": "#FEF3C7", "text": "#D97706"},
    "학교 행사": {"color": "#F3E8FF", "text": "#8B5CF6"},
    "동아리": {"color": "#FEFCE8", "text": "#CA8A04"},
    "모의고사": {"color": "#DCFCE7", "text": "#16A34A"}
}

# 오늘 날짜 기준 설정 (2026년 반영)
today_date = datetime.today().date()

# 3. 세션 데이터 초기화
if 'events_db' not in st.session_state or not st.session_state.events_db:
    st.session_state.events_db = [
        {"date": today_date, "category": "수행평가", "content": "수학 탐구 보고서 제출"},
        {"date": today_date + timedelta(days=2), "category": "시험", "content": "영어 듣기평가"},
        {"date": today_date + timedelta(days=4), "category": "학교 행사", "content": "현장체험학습"},
        {"date": today_date - timedelta(days=1), "category": "동아리", "content": "동아리 정기 활동"},
        {"date": today_date + timedelta(days=6), "category": "모의고사", "content": "전국연합학력평가"},
    ]

# 4. 메인 타이틀
st.title("📅 학사 일정 플래너")
st.divider()

# 5. 상단 영역: 오늘 일정 요약
st.subheader("오늘의 일정")
today_evs = [e for e in st.session_state.events_db if e['date'] == today_date]

if today_evs:
    cols = st.columns(len(today_evs))
    for i, ev in enumerate(today_evs):
        info = CATEGORY_INFO[ev['category']]
        with cols[i]:
            st.info(f"**[{ev['category']}]** {ev['content']}")
else:
    st.write("오늘 예정된 학사 일정이 없습니다.")

st.divider()

# 6. 메인 화면 레이아웃 (좌: 달력 / 우: 주간 요약)
left_col, right_col = st.columns([3, 1])

with left_col:
    now = datetime.today()
    c1, c2 = st.columns(2)
    year = c1.selectbox("연도", range(now.year - 1, now.year + 3), index=1)
    month = c2.selectbox("월", range(1, 13), index=now.month - 1)
    
    st.subheader(f"📅 {year}년 {month}월")
    
    # 캘린더 요일 헤더 (안전한 마크다운 문법으로 교체)
    st.markdown("### `일` | `월` | `화` | `수` | `목` | `금` | `토` ")
    
    cal = calendar.Calendar(firstweekday=6)
    weeks = cal.monthdatescalendar(year, month)
    
    # 달력 날짜 출력
    for wk in weeks:
        cols = st.columns(7)
        for idx, day in enumerate(wk):
            with cols[idx]:
                if day.month != month:
                    st.write("")
                    continue
                
                # 오늘 날짜 강조 표시
                if day == today_date:
                    st.markdown(f"**📍 {day.day}**")
                else:
                    st.write(f"**{day.day}**")
                
                # 해당 날짜의 일정들 노출
                day_evs = [e for e in st.session_state.events_db if e['date'] == day]
                for ev in day_evs:
                    st.caption(f"• {ev['content']}")
                    
    st.divider()
    
    # 상시 노출되는 직관적인 일정 등록 창
    st.subheader("➕ 바로 일정 등록하기")
    with st.form("add_form", clear_on_submit=True):
        f1, f2, f3 = st.columns([1, 1, 2])
        in_date = f1.date_input("날짜 선택", datetime.today())
        in_cate = f2.selectbox("분류 선택", list(CATEGORY_INFO.keys()))
        in_cont = f3.text_input("일정 내용 입력", placeholder="예: 수학 탐구 보고서 제출")
        
        if st.form_submit_button("캘린더에 바로 추가하기"):
            if in_cont.strip():
                st.session_state.events_db.append({"date": in_date, "category": in_cate, "content": in_cont})
                st.success("일정이 정상적으로 추가되었습니다.")
                st.rerun()
            else:
                st.error("내용을 입력하셔야 등록이 완료됩니다.")

with right_col:
    st.subheader("주간 요약 및 디데이")
    
    if st.button("🔄 디데이 안 뜨면 클릭 (동기화)"):
        st.session_state.events_db = []
        st.rerun()
        
    st.write("")

    # 오늘 날짜를 포함하여 다가오는 일정 필터링
    up_evs = [e for e in st.session_state.events_db if e['date'] >= today_date]
    up_evs.sort(key=lambda x: x['date'])
    
    if up_evs:
        for ev in up_evs[:4]:
            d = (ev['date'] - today_date).days
            
            # 다정한 존댓말 코멘트 멘트
            if d == 0:
                d_str = "D-Day"
                comment = "오늘입니다! 파이팅하세요🔥"
            elif d == 1:
                d_str = "D-1"
                comment = "내일이네요! 빠뜨린 게 없는지 확인해 보세요."
            elif d <= 3:
                d_str = f"D-{d}"
                comment = "일정이 코앞으로 다가왔습니다. 조금만 더 힘내세요!"
            elif d <= 7:
                d_str = f"D-{d}"
                comment = "다음 주 일정이네요. 미리 준비해 볼까요?⚙️"
            else:
                d_str = f"D-{d}"
                comment = "아직 여유가 있습니다. 차근차근 준비해 보세요🌱"
                
            w_list = ["월", "화", "수", "목", "금", "토", "일"]
            w_str = w_list[ev['date'].weekday()]
