# Update main.py to include Graph 5 (Heatmap for Monthly x Weekday Total Audience)
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
# 구역 3: [시간 & 총 관객수] 날짜별 10위권 일관객 총합 영역 그래프
# ==========================================
st.header("📌 구역 3: 날짜별 10위권 일관객 총합 추이")

# 날짜별 10위권 일관객 합계 계산
daily_sum_df = df.groupby('날짜')['일관객'].sum().reset_index().sort_values('날짜')

if not daily_sum_df.empty:
    # Plotly 영역 그래프 (Area Chart) 생성
    fig3 = px.area(
        daily_sum_df,
        x='날짜',
        y='일관객',
        title="날짜별 박스오피스 10위권 일관객 총합 추이",
        labels={'날짜': '날짜', '일관객': '10위권 관객 총합(명)'}
    )

    # 합계가 가장 컸던 날 상위 3일 추출
    top3_days = daily_sum_df.nlargest(3, '일관객')

    # 그래프 상에 TOP 3 peak 지점 어노테이션(표시) 추가
    for idx, row in top3_days.iterrows():
        date_str = row['날짜'].strftime('%Y-%m-%d')
        audience_cnt = row['일관객']
        
        fig3.add_annotation(
            x=row['날짜'],
            y=audience_cnt,
            text=f"🏆 TOP {top3_days.index.get_loc(idx)+1}<br>{date_str}<br>({audience_cnt:,}명)",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor="#E74C3C",
            ax=0,
            ay=-45,
            bgcolor="rgba(255, 255, 255, 0.9)",
            bordercolor="#E74C3C",
            borderwidth=1.5,
            borderpad=4
        )

    # 호버 포맷 및 레이아웃 설정
    fig3.update_traces(
        hovertemplate="<b>날짜:</b> %{x|%Y-%m-%d}<br><b>10위권 관객 총합:</b> %{y:,}명<extra></extra>"
    )
    fig3.update_layout(
        xaxis_title="날짜",
        yaxis_title="관객 총합 (명)",
        hovermode="x unified",
        template="plotly_white"
    )

    # Streamlit에 그래프 출력
    st.plotly_chart(fig3, use_container_width=True)

    # 그래프 하단 분석 결과 / 가이드 영역
    st.info("💡 **이 그래프로 알 수 있는 것:** (추후 이 그래프로 알 수 있는 점에 대한 분석 문구가 들어갈 자리입니다.)")

else:
    st.warning("일관객 총합 데이터를 불러올 수 없습니다.")

st.divider()

# ==========================================
# 구역 4: [총 관객수 & 10위권 진입 일수] TOP 10 영화 가로 막대그래프
# ==========================================
st.header("📌 구역 4: 기간 내 일관객 총합 TOP 10 영화 순위")

# 영화별 일관객 합계 및 10위권 진입 일수(데이터 등장 횟수) 집계
top10_summary = df.groupby('영화명').agg(
    일관객_합계=('일관객', 'sum'),
    진입일수=('날짜', 'nunique')
).reset_index()

# 일관객 합계 기준 상위 10개 영화 추출 및 관객 수 적은 순 정렬 (Plotly 가로 막대 그래프는 아래에서 위로 그려지므로 관객 수가 많은 영화가 상단에 배치되도록 함)
top10_movies_df = top10_summary.nlargest(10, '일관객_합계').sort_values('일관객_합계', ascending=True)

if not top10_movies_df.empty:
    # Plotly 가로 막대 그래프 생성
    fig4 = px.bar(
        top10_movies_df,
        x='일관객_합계',
        y='영화명',
        orientation='h',
        title="기간 내 일관객 총합 TOP 10 영화",
        labels={'일관객_합계': '일관객 총합(명)', '영화명': '영화 제목', '진입일수': '10위권 진입 일수'},
        text='일관객_합계',
        color='일관객_합계',
        color_continuous_scale='Blues'
    )

    # 막대에 텍스트 포맷팅 및 호버 정보 추가
    fig4.update_traces(
        texttemplate='%{x:,}명',
        textposition='outside',
        customdata=top10_movies_df[['진입일수']],
        hovertemplate="<b>영화명:</b> %{y}<br><b>일관객 총합:</b> %{x:,}명<br><b>10위권 진입 일수:</b> %{customdata[0]}일<extra></extra>"
    )

    fig4.update_layout(
        xaxis_title="일관객 총합 (명)",
        yaxis_title="영화 제목",
        template="plotly_white",
        coloraxis_showscale=False,
        height=500
    )

    # Streamlit에 그래프 출력
    st.plotly_chart(fig4, use_container_width=True)

    # 그래프 하단 분석 결과 / 가이드 영역
    st.info("💡 **이 그래프로 알 수 있는 것:** (추후 이 그래프로 알 수 있는 점에 대한 분석 문구가 들어갈 자리입니다.)")

else:
    st.warning("TOP 10 영화 데이터를 불러올 수 없습니다.")

st.divider()

# ==========================================
# 구역 5: [월 x 요일] 월x요일별 일관객 합계 히트맵
# ==========================================
st.header("📌 구역 5: 월×요일별 일관객 합계 히트맵")

# 데이터 카피 후 월 및 요일 파생 변수 생성
heatmap_df = df.copy()
heatmap_df['월'] = heatmap_df['날짜'].dt.month.astype(str) + "월"
heatmap_df['요일_num'] = heatmap_df['날짜'].dt.dayofweek  # 0:월, 1:화 ... 6:일

# 요일 정렬 기준 및 이름 매핑
weekday_names = {0: '월요일', 1: '화요일', 2: '수요일', 3: '목요일', 4: '금요일', 5: '토요일', 6: '일요일'}
heatmap_df['요일'] = heatmap_df['요일_num'].map(weekday_names)

# 월 및 요일 순서 보장을 위한 정렬
month_order = [f"{i}월" for i in range(1, 13)]
weekday_order = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']

# 월 x 요일 그룹화 및 관객 합계 계산
pivot_df = heatmap_df.groupby(['월', '요일', '요일_num'])['일관객'].sum().reset_index()

# 피벗 테이블 생성 (Y축: 월, X축: 요일)
pivot_table = pivot_df.pivot(index='월', columns='요일', values='일관객')

# 존재하지 않는 월/요일이 있을 경우 대비 및 순서 적용
existing_months = [m for m in month_order if m in pivot_table.index]
existing_weekdays = [w for w in weekday_order if w in pivot_table.columns]
pivot_table = pivot_table.reindex(index=existing_months, columns=existing_weekdays).fillna(0)

if not pivot_table.empty:
    # Plotly 히트맵 생성 (색이 진할수록 관객이 많음)
    fig5 = px.imshow(
        pivot_table,
        labels=dict(x="요일", y="월", color="일관객 합계(명)"),
        x=existing_weekdays,
        y=existing_months,
        color_continuous_scale="Viridis",
        title="월×요일별 관객 합계 히트맵 (색상이 진할수록 관객 수 증가)",
        aspect="auto"
    )

    # 셀 수치 포맷팅 및 호버 표기 설정
    fig5.update_traces(
        hovertemplate="<b>%{y} %{x}</b><br>일관객 합계: %{z:,}명<extra></extra>"
    )

    fig5.update_layout(
        xaxis_title="요일",
        yaxis_title="월",
        template="plotly_white",
        height=550
    )

    # Streamlit에 그래프 출력
    st.plotly_chart(fig5, use_container_width=True)

    # 그래프 하단 분석 결과 / 가이드 영역
    st.info("💡 **이 그래프로 알 수 있는 것:** (추후 이 그래프로 알 수 있는 점에 대한 분석 문구가 들어갈 자리입니다.)")

else:
    st.warning("월×요일별 데이터를 불러올 수 없습니다.")

st.divider()

# ==========================================
# 구역 6: [추가 예정 구역] 
# ==========================================
st.header("📌 구역 6: (추후 그래프 추가 구역)")
st.caption("🚀 앞으로 다양한 시간 기준 데이터 분석 시각화 그래프가 이곳에 추가될 예정입니다.")
'''

with open("main.py", "w", encoding="utf-8") as f:
    f.write(main_py_updated)

print("Successfully added graph 5 to main.py.")
