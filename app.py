import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar

# 1. 페이지 설정
st.set_page_config(page_title="학사 일정 플래너", page_icon="📅", layout="wide")

# 2. 색상 상수 정의
CATEGORY_INFO = {
    "수행평가": {"color": "#FDE8E8", "text": "#E53E3E"},
    "시험": {"color": "#FEF3C7", "text": "#D97706"},
    "학교 행사": {"color": "#F3E8FF", "text": "#8B5CF6"},
    "동아리": {"color": "#FEFCE8", "text": "#CA8A04"},
    "모의고사": {"color": "#DCFCE7", "text": "#16A34A"}
}

# 3. 데이터 초기화
if 'events_db' not in st.session_state:
    t = datetime.today().date()
    st.session_state.events_db = [
        {"date": t, "category": "수행평가", "content": "수학 탐구 보고서 제출"},
        {"date": t + timedelta(days=2), "category": "시험", "content": "영어 듣기평가"},
        {"date": t + timedelta(days=4), "category": "학교 행사", "content": "현장체험학습"},
        {"date": t - timedelta(days=1), "category": "동아리", "content": "동아리 정기 활동"},
        {"date": t + timedelta(days=6), "category": "모의고사", "content": "전국연합학력평가"},
    ]

# 4. 메인 타이틀
st.title("📅 학사 일정 플래너")
st.write("---")

# 5. 오늘 일정
st.subheader("오늘의 일정")
today_date = datetime.today().date()
today_evs = [e for e in st.session_state.events_db if e['date'] == today_date]

if today_evs:
    cols = st.columns(len(today_evs))
    for i, ev in enumerate(today_evs):
        info = CATEGORY_INFO[ev['category']]
        with cols[i]:
            st.markdown(f"<div style='padding:12px; border-radius:6px; background:{info['color']}; color:{info['text']}; font-weight:bold;'>[{ev['category']}] {ev['content']}</div>", unsafe_allow_html=True)
else:
    st.write("오늘 예정된 학사 일정이 없습니다.")

st.write("---")

# 6. 메인 화면 레이아웃
left_col, right_col = st.columns([3, 1])

with left_col:
    now = datetime.today()
    c1, c2 = st.columns(2)
    year = c1.selectbox("연도", range(now.year - 1, now.year + 3), index=1)
    month = c2.selectbox("월", range(1, 13), index=now.month - 1)
    
    st.subheader(f"{year}년 {month}월")
    
    # 캘린더 그리기 (한 줄 코딩으로 잘림 문제 원천 차단)
    hd = "<div style='display:grid; grid-template-columns:repeat(7,1fr); gap:2px; text-align:center; font-weight:bold;'>"
    hd += "<div style='color:#E53E3E;'>일</div><div>월</div><div>화</div><div>수</div><div>목</div><div>금</div><div style='color:#3182CE;'>토</div></div>"
    st.markdown(hd, unsafe_allow_html=True)
    
    cal = calendar.Calendar(firstweekday=6)
    weeks = cal.monthdatescalendar(year, month)
    
    cells = "<div style='display:grid; grid-template-columns:repeat(7,1fr); gap:2px;'>"
    for wk in weeks:
        for day in wk:
            if day.month != month:
                cells += "<div style='min-height:90px; background:#F7FAFC; border:1px solid #EDF2F7;'></div>"
                continue
                
            bg = "#F7FAFC" if day == today_date else "#FFFFFF"
            border = "2px solid #3182CE" if day == today_date else "1px solid #EDF2F7"
            
            day_idx = day.weekday()
            tc = "#E53E3E" if day_idx == 6 else ("#3182CE" if day_idx == 5 else "#4A5568")
            
            ev_html = ""
            for ev in [e for e in st.session_state.events_db if e['date'] == day]:
                info = CATEGORY_INFO[ev['category']]
                ev_html += f"<div style='font-size:11px; padding:2px; margin-top:2px; border-radius:3px; background:{info['color']}; color:{info['text']}; font-weight:500; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;'>{ev['content']}</div>"
            
            cells += f"<div style='min-height:90px; background:{bg}; border:{border}; padding:4px;'><b style='color:{tc};'>{day.day}</b>{ev_html}</div>"
            
    cells += "</div>"
    st.markdown(cells, unsafe_allow_html=True)
    st.write("")
    
    # 일정 등록
    with st.expander("➕ 신규 일정 등록", expanded=False):
        with st.form("add_form", clear_on_submit=True):
            in_date = st.date_input("날짜", datetime.today())
            in_cate = st.selectbox("분류", list(CATEGORY_INFO.keys()))
            in_cont = st.text_input("내용")
            if st.form_submit_button("등록"):
                if in_cont.strip():
                    st.session_state.events_db.append({"date": in_date, "category": in_cate, "content": in_cont})
                    st.success("등록되었습니다.")
                    st.rerun()
                else:
                    st.error("내용을 입력해주세요.")

with right_col:
    st.subheader("주간 요약 및 디데이")
    up_evs = [e for e in st.session_state.events_db if e['date'] >= today_date]
    up_evs.sort(key=lambda x: x['date'])
    
    if up_evs:
        for ev in up_evs[:4]:
            info = CATEGORY_INFO[ev['category']]
            d = (ev['date'] - today_date).days
            d_str = "D-Day" if d == 0 else f"D-{d}"
            w_list = ["월", "화", "수", "목", "금", "토", "일"]
            w_str = w_list[ev['date'].weekday()]
            
            st.markdown(f"<div style='padding:10px; margin-bottom:8px; border-radius:6px; background:{info['color']}; color:{info['text']}; border-left:4px solid {info['text']};'><span style='float:right; background:#FFF; padding:1px 4px; border-radius:4px; font-size:0.8rem; border:1px solid {info['text']};'>{d_str}</span><b>{ev['date'].strftime('%m/%d')}({w_str})</b><br><span style='font-size:0.9rem;'>{ev['content']}</span></div>", unsafe_allow_html=True)
    else:
        st.write("예정된 일정이 없습니다.")

    st.write("---")
    with st.expander("시스템 관리"):
        if st.button("전체 데이터 초기화"):
            st.session_state.events_db = []
            st.success("초기화 완료")
            st.rerun()
