import streamlit as st
import pandas as pd
from datetime import datetime, date
import os

st.set_page_config(
    page_title="학교 행사·대회 통합 게시판",
    page_icon="🎉",
    layout="wide"
)

DATA_FILE = "events.csv"


# -----------------------
# 데이터 로드
# -----------------------
def load_data():
    try:
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE)

            if not df.empty:
                df["행사일"] = pd.to_datetime(
                    df["행사일"],
                    errors="coerce"
                )

            return df

        return pd.DataFrame(
            columns=[
                "제목",
                "구분",
                "주최",
                "행사일",
                "신청링크",
                "설명"
            ]
        )

    except Exception as e:
        st.error(f"데이터 로드 오류: {e}")
        return pd.DataFrame(
            columns=[
                "제목",
                "구분",
                "주최",
                "행사일",
                "신청링크",
                "설명"
            ]
        )


# -----------------------
# 데이터 저장
# -----------------------
def save_data(df):
    try:
        temp = df.copy()

        if not temp.empty:
            temp["행사일"] = pd.to_datetime(
                temp["행사일"],
                errors="coerce"
            )

        temp.to_csv(DATA_FILE, index=False)

    except Exception as e:
        st.error(f"저장 오류: {e}")


# -----------------------
# 초기 데이터 생성
# -----------------------
if not os.path.exists(DATA_FILE):
    sample = pd.DataFrame([
        {
            "제목": "과학 탐구 대회",
            "구분": "교내 대회",
            "주최": "과학부",
            "행사일": "2026-07-10",
            "신청링크": "",
            "설명": "과학 프로젝트 발표"
        },
        {
            "제목": "청소년 창업 아이디어 공모전",
            "구분": "교외 공모전",
            "주최": "교육청",
            "행사일": "2026-07-20",
            "신청링크": "",
            "설명": "창업 아이디어 제안"
        }
    ])

    sample.to_csv(DATA_FILE, index=False)


df = load_data()

# -----------------------
# 사이드바
# -----------------------
st.sidebar.title("🔎 필터")

types = ["전체"] + sorted(df["구분"].dropna().unique().tolist())

selected_type = st.sidebar.selectbox(
    "구분 선택",
    types
)

keyword = st.sidebar.text_input(
    "검색어"
)

# -----------------------
# 메인
# -----------------------
st.title("🎉 학교 행사·대회 통합 게시판")
st.caption("교내·교외 행사와 대회를 한눈에 확인하세요.")

filtered = df.copy()

if selected_type != "전체":
    filtered = filtered[
        filtered["구분"] == selected_type
    ]

if keyword:
    filtered = filtered[
        filtered.astype(str)
        .apply(
            lambda row:
            row.str.contains(
                keyword,
                case=False,
                na=False
            ).any(),
            axis=1
        )
    ]

# -----------------------
# 통계
# -----------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("전체 행사 수", len(df))

with col2:
    upcoming = 0

    if not df.empty:
        upcoming = (
            pd.to_datetime(df["행사일"])
            >= pd.Timestamp.today()
        ).sum()

    st.metric("예정 행사", upcoming)

with col3:
    urgent = 0

    if not df.empty:
        days = (
            pd.to_datetime(df["행사일"])
            - pd.Timestamp.today()
        ).dt.days

        urgent = ((days >= 0) & (days <= 7)).sum()

    st.metric("7일 이내 행사", urgent)

st.divider()

# -----------------------
# 행사 목록
# -----------------------
st.subheader("📋 행사 목록")

if filtered.empty:
    st.info("등록된 행사가 없습니다.")
else:

    display_df = filtered.copy()

    today = pd.Timestamp.today()

    def mark(date_value):
        try:
            diff = (
                pd.to_datetime(date_value)
                - today
            ).days

            if 0 <= diff <= 7:
                return "🔥 마감 임박"

            return ""

        except:
            return ""

    display_df["상태"] = display_df["행사일"].apply(mark)

    st.dataframe(
        display_df,
        use_container_width=True
    )

# -----------------------
# 일정 보기
# -----------------------
st.divider()
st.subheader("📅 일정 보기")

if not df.empty:

    calendar_df = df.copy()

    calendar_df["행사일"] = pd.to_datetime(
        calendar_df["행사일"],
        errors="coerce"
    )

    calendar_df = calendar_df.sort_values(
        "행사일"
    )

    st.dataframe(
        calendar_df[
            ["행사일", "제목", "구분", "주최"]
        ],
        use_container_width=True
    )

# -----------------------
# 관리자 영역
# -----------------------
st.divider()

with st.expander("✏️ 행사 추가 / 수정 / 삭제"):

    st.subheader("행사 추가")

    with st.form("add_form"):

        title = st.text_input("제목")

        category = st.selectbox(
            "구분",
            [
                "교내 대회",
                "교외 대회",
                "교내 행사",
                "교외 행사",
                "공모전",
                "기타"
            ]
        )

        host = st.text_input("주최")

        event_date = st.date_input(
            "행사일",
            value=date.today()
        )

        link = st.text_input("신청 링크")

        desc = st.text_area("설명")

        submitted = st.form_submit_button(
            "추가"
        )

        if submitted:

            if not title.strip():
                st.warning("제목을 입력하세요.")
            else:
                new_row = pd.DataFrame([{
                    "제목": title,
                    "구분": category,
                    "주최": host,
                    "행사일": event_date,
                    "신청링크": link,
                    "설명": desc
                }])

                df = pd.concat(
                    [df, new_row],
                    ignore_index=True
                )

                save_data(df)

                st.success("행사가 추가되었습니다.")
                st.rerun()

    st.divider()

    st.subheader("행사 삭제")

    if not df.empty:

        delete_idx = st.selectbox(
            "삭제할 행사 선택",
            df.index,
            format_func=lambda x:
            f"{df.loc[x,'제목']} ({df.loc[x,'행사일']})"
        )

        if st.button("삭제"):

            df = df.drop(delete_idx)

            save_data(df)

            st.success("삭제되었습니다.")
            st.rerun()

# -----------------------
# CSV 다운로드
# -----------------------
st.divider()

st.subheader("💾 데이터 백업")

csv = df.to_csv(index=False).encode("utf-8-sig")

st.download_button(
    label="CSV 다운로드",
    data=csv,
    file_name="events_backup.csv",
    mime="text/csv"
)
