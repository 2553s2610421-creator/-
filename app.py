import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar

# 1. 페이지 설정
st.set_page_config(page_title="학사 일정 플래너", page_icon="📅", layout="wide")

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
            st.markdown(f"<div style='padding:12px; border-radius:6px; background:{info['color']}; color:{info['text']}; font-weight:bold;'>[{ev['category']}] {ev['content']}</div>", unsafe_allow_html=True)
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
    hd = "<div style='display:grid; grid-template-columns:repeat(7,1fr); gap:2px; text-align:center; font-weight:bold; margin-bottom:5px;'>"
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
    st.write("---")
    
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
    up_evs = [e for e in st.session_state.events_db if e['date'] >= today_date]
    up_evs.sort(key=lambda x: x['date'])
    
    if up_evs:
        for ev in up_evs[:4]:
            info = CATEGORY_INFO[ev['category']]
            d = (ev['date'] - today_date).days
            
            # [피드백 반영] 차분하고 다정한 존댓말 코멘트 멘트
            if d == 0:
                d_str = "D-Day"
                comment = "오늘입니다! 파이팅하세요🔥"
            elif d == 1:
                d_str = "D-1"
                comment = "내일이네요! 누락된 게 없는지 확인해 보세요."
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
            
            st.markdown(
                f"<div style='padding:12px; margin-bottom:10px; border-radius:6px; background:{info['color']}; color:{info['text']}; border-left:4px solid {info['text']};'>"
                f"<span style='float:right; background:#FFF; padding:1px 6px; border-radius:4px; font-size:0.8rem; font-weight:bold; border:1px solid {info['text']};'>{d_str}</span>"
                f"<b>{ev['date'].strftime('%m/%d')}({w_str})</b><br>"
                f"<span style='font-size:0.95rem; font-weight:500; display:block; margin:4px 0;'>{ev['content']}</span>"
                f"<span style='font-size:0.8rem; opacity:0.83; font-style:normal;'>💬 {comment}</span>"
                f"</div>", 
                unsafe_allow_html=True
            )
    else:
        st.write("예정된 일정이 없습니다.")

    st.write("---")
    with st.expander("시스템 관리"):
        if st.button("전체 데이터 초기화"):
            st.session_state.events_db = []
            st.success("초기화 완료")
            st.rerun()
