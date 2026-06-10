


import streamlit as st
import pandas as pd
from datetime import datetime, date

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="학습 일정 알림이", page_icon="📅", layout="centered")
st.title("📅 수행평가 & 시험 일정 알림이")
st.write("중요한 학교 일정을 등록하고 디데이를 확인하세요!")

# 2. 세션 상태(Session State)를 이용한 임시 데이터 저장소 초기화
if "events" not in st.session_state:
    st.session_state.events = [
        {"구분": "시험", "과목/내용": "1학기 기말고사", "날짜": date(2026, 7, 3), "메모": "수학, 과학 집중 공부"},
        {"구분": "수행", "과목/내용": "영어 에세이 제출", "날짜": date(2026, 6, 15), "메모": "지하철 일지 주제로 작성"},
    ]

# --- 3. 알림(Notification) 영역 ---
st.subheader("🔔 실시간 임박 알림")
today = date.today()
urgent_count = 0

for event in st.session_state.events:
    days_left = (event["날짜"] - today).days
    
    # 마감일이 오늘이거나 3일 이내로 남은 경우 알림 표시
    if 0 <= days_left <= 3:
        st.error(f"⚠️ **[{event['구분']}] {event['과목/내용']}**이(가) **{days_left}일** 남았습니다! 서두르세요!")
        urgent_count += 1
    elif days_left < 0:
        st.info(f"✅ **[{event['구분']}] {event['과목/내용']}** 일정은 종료되었습니다.")

if urgent_count == 0:
    st.success("🎉 3일 이내에 마감되는 급한 일정이 없습니다. 여유롭게 준비하세요!")

st.markdown("---")

# --- 4. 일정 추가 Form ---
st.subheader("➕ 새 일정 등록하기")
with st.form(key="add_event_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    
    with col1:
        event_type = st.selectbox("일정 구분", ["수행", "시험", "기타"])
        title = st.text_input("과목 또는 내용", placeholder="예: 수학 수행평가, 중간고사")
    
    with col2:
        target_date = st.date_input("날짜 지정", min_value=today)
        memo = st.text_input("메모 (선택)", placeholder="준비물이나 범위 기록")
        
    submit_button = st.form_submit_button(label="일정 추가")

    if submit_button:
        if title:
            # 새로운 일정을 세션 상태에 추가
            st.session_state.events.append({
                "구분": event_type,
                "과목/내용": title,
                "날짜": target_date,
                "메모": memo
            })
            st.toast("새 일정이 성공적으로 등록되었습니다! 🎉")
            st.rerun()  # 화면을 새로고침하여 리스트와 알림 갱신
        else:
            st.warning("과목 또는 내용을 입력해주세요!")

# --- 5. 전체 일정 표 및 디데이 표시 ---
st.subheader("📋 나의 전체 일정 목록")

if st.session_state.events:
    # 데이터프레임으로 변환하여 예쁘게 시각화
    df_list = []
    for event in st.session_state.events:
        days_left = (event["날짜"] - today).days
        
        # 디데이 문자열 포맷팅
        if days_left > 0:
            d_day = f"D-{days_left}"
        elif days_left == 0:
            d_day = "D-Day 🔥"
        else:
            d_day = f"종료 (D+{abs(days_left)})"
            
        df_list.append({
            "구분": event["구분"],
            "과목/내용": event["과목/내용"],
            "마감 날짜": event["날짜"].strftime("%Y-%m-%d"),
            "남은 시일": d_day,
            "메모": event["메모"]
        })
        
    df = pd.DataFrame(df_list)
    
    # 테이블 출력
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # 일정 초기화 버튼
    if st.button("🔄 전체 일정 초기화"):
        st.session_state.events = []
        st.rerun()
else:
    st.info("등록된 일정이 없습니다. 새로운 일정을 등록해 보세요!")
