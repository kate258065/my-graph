# Update main.py to remove the explanation text area ("이 그래프로 알 수 있는 것")
main_py_updated = '''import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 페이지 설정
st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    page_icon="🎬",
    layout="wide"
)

# 2. 데이터 로드 및 전처리 (캐싱 활용)
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"
    # CSV 읽기 (날짜 열을 문자열로 다루기 위해 dtype 지정)
    df = pd.read_csv(url, dtype={'날짜': str})
    
    # '날짜' 열을 진짜 datetime 객체로 변환 (YYYYMMDD 형식)
    df['날짜'] = pd.to_datetime(df['날짜'], format='%Y%m%d')
    
    # 일관객, 누적관객 등 수치형 데이터 타입 정제
    numeric_cols = ['순위', '일관객', '누적관객', '스크린수', '상영횟수']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
            
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()

# 3. 메인 타이틀 및 소개
st.title("🎬 영화 데이터 그래프 도감 1 - 시간")
st.markdown("""
이 앱은 1년치(365일) 일별 박스오피스 10위권 기록 데이터를 기반으로 **시간의 흐름에 따른 영화 관객 수 및 트렌드**를 시각화합니다.
""")

st.divider()

# ==========================================
# 구역 1: [시간 & 영화별] 일관객 변화 추이
# ==========================================
st.header("📌 구역 1: 영화별 일관객 변화 추이")

# 영화 목록 추출 (영화명 기준 정렬)
movie_list = sorted(df['영화명'].unique())

# 영화 선택 드롭다운
selected_movie = st.selectbox(
    "📊 추이를 확인할 영화를 선택하세요:",
    options=movie_list,
    index=0
)

# 선택된 영화 데이터 필터링 (날짜순 정렬)
movie_df = df[df['영화명'] == selected_movie].sort_values('날짜')

if not movie_df.empty:
    # Plotly 선 그래프 생성
    fig = px.line(
        movie_df,
        x='날짜',
        y='일관객',
        title=f"'{selected_movie}' 날짜별 일관객 수 변화",
        labels={'날짜': '날짜', '일관객': '일일 관객 수(명)'},
        markers=True,
        hover_data={'날짜': '|%Y년 %m월 %d일', '일관객': ':,d', '순위': True}
    )

    # 그래프 스타일 조정 (마우스 호버 시 정확한 정보 표기)
    fig.update_traces(
        hovertemplate="<b>날짜:</b> %{x|%Y-%m-%d}<br><b>일관객:</b> %{y:,}명<br><b>순위:</b> %{customdata[0]}위<extra></extra>"
    )
    fig.update_layout(
        xaxis_title="날짜",
        yaxis_title="관객 수 (명)",
        hovermode="x unified",
        template="plotly_white"
    )

    # Streamlit에 그래프 출력
    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("선택한 영화의 데이터가 존재하지 않습니다.")

st.divider()

# ==========================================
# 구역 2: [추가 예정 구역] 
# ==========================================
st.header("📌 구역 2: (추후 그래프 추가 구역)")
st.caption("🚀 앞으로 다양한 시간 기준 데이터 분석 시각화 그래프가 이곳에 추가될 예정입니다.")
'''

with open("main.py", "w", encoding="utf-8") as f:
    f.write(main_py_updated)

print("Updated main.py without '이 그래프로 알 수 있는 것' section.")
