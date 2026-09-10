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
# 구역 1: [시간 & 영화별] 개별 영화 일관객 변화 추이
# ==========================================
st.header("📌 구역 1: 개별 영화 일관객 변화 추이")

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
    fig1 = px.line(
        movie_df,
        x='날짜',
        y='일관객',
        title=f"'{selected_movie}' 날짜별 일관객 수 변화",
        labels={'날짜': '날짜', '일관객': '일일 관객 수(명)'},
        markers=True,
        hover_data={'날짜': '|%Y년 %m월 %d일', '일관객': ':,d', '순위': True}
    )

    # 그래프 스타일 조정 (마우스 호버 시 정확한 정보 표기)
    fig1.update_traces(
        hovertemplate="<b>날짜:</b> %{x|%Y-%m-%d}<br><b>일관객:</b> %{y:,}명<br><b>순위:</b> %{customdata[0]}위<extra></extra>"
    )
    fig1.update_layout(
        xaxis_title="날짜",
        yaxis_title="관객 수 (명)",
        hovermode="x unified",
        template="plotly_white"
    )

    # Streamlit에 그래프 출력
    st.plotly_chart(fig1, use_container_width=True)

    # 그래프 아래 설명 문구 추가
    st.info("💡 **이 그래프로 알 수 있는 것:** 주말마다 영화의 관객 수가 늘고 있다는 것을 알 수 있다.")

else:
    st.warning("선택한 영화의 데이터가 존재하지 않습니다.")

st.divider()

# ==========================================
# 구역 2: [시간 & 상위 TOP 5] 관객 합계 상위 5개 영화 비교
# ==========================================
st.header("📌 구역 2: 기간 내 일관객 합계 TOP 5 영화 비교")

# 일관객 합계 상위 5개 영화 추출
top5_movies = df.groupby('영화명')['일관객'].sum().nlargest(5).index.tolist()

# TOP 5 영화 데이터 필터링
top5_df = df[df['영화명'].isin(top5_movies)].sort_values('날짜')

if not top5_df.empty:
    # Plotly 다중 선 그래프 생성 (색상으로 영화 구분)
    fig2 = px.line(
        top5_df,
        x='날짜',
        y='일관객',
        color='영화명',
        title="기간 내 일관객 합계 TOP 5 영화의 날짜별 관객 수 비교",
        labels={'날짜': '날짜', '일관객': '일일 관객 수(명)', '영화명': '영화 제목'},
        markers=True
    )

    # 그래프 스타일 및 호버 템플릿 조정
    fig2.update_traces(
        hovertemplate="<b>영화명:</b> %{fullData.name}<br><b>날짜:</b> %{x|%Y-%m-%d}<br><b>일관객:</b> %{y:,}명<extra></extra>"
    )
    fig2.update_layout(
        xaxis_title="날짜",
        yaxis_title="관객 수 (명)",
        hovermode="x unified",
        template="plotly_white",
        legend_title_text="영화 제목 (클릭 시 켜기/끄기)"
    )

    # Streamlit에 그래프 출력
    st.plotly_chart(fig2, use_container_width=True)

    # 그래프 하단 분석 결과 / 가이드 영역
    st.info("💡 **이 그래프로 알 수 있는 것:** (추후 이 그래프로 알 수 있는 점에 대한 분석 문구가 들어갈 자리입니다.)")

else:
    st.warning("상위 영화 데이터를 불러올 수 없습니다.")

st.divider()

# ==========================================
# 구역 3: [추가 예정 구역] 
# ==========================================
st.header("📌 구역 3: (추후 그래프 추가 구역)")
st.caption("🚀 앞으로 다양한 시간 기준 데이터 분석 시각화 그래프가 이곳에 추가될 예정입니다.")
'''

with open("main.py", "w", encoding="utf-8") as f:
    f.write(main_py_updated)

print("Successfully added graph 2 to main.py.")
