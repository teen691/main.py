import pandas as pd
import plotly.express as px
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    page_icon="🎬",
    layout="wide",
)

# App Title & Description
st.title("🎬 영화 데이터 그래프 도감 1 - 시간")
st.markdown("""
박스오피스 데이터를 바탕으로 **시간의 흐름**에 따른 영화 관객 수 및 시장 변화를 시각화한 도감입니다.
""")


# 데이터 로드 및 전처리 함수 (캐싱 적용)
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"
    df = pd.read_csv(url)

    # Convert '날짜' to datetime format (YYYYMMDD -> datetime)
    df["날짜"] = pd.to_datetime(df["날짜"].astype(str), format="%Y%m%d")

    # Sort by date
    df = df.sort_values("날짜").reset_index(drop=True)
    return df


# Load data with spinner
with st.spinner("데이터를 불러오는 중입니다..."):
    df = load_data()

st.markdown("---")

# ==========================================
# Section 1: 영화별 일관객 변화
# ==========================================
st.header("📌 Section 1. 영화별 일별 관객 수 추이")

# Unique movie titles sorted alphabetically
movie_list = sorted(df["영화명"].dropna().unique())

# Movie selection dropdown
selected_movie = st.selectbox(
    "💡 분석할 영화를 선택하세요:",
    options=movie_list,
    index=0 if len(movie_list) > 0 else None,
)

if selected_movie:
    # Filter dataset for selected movie
    movie_df = df[df["영화명"] == selected_movie].sort_values("날짜")

    # Create Plotly Line Chart
    fig1 = px.line(
        movie_df,
        x="날짜",
        y="일관객",
        title=f"'{selected_movie}' 날짜별 일관객 수 변화",
        labels={"날짜": "날짜", "일관객": "일일 관객 수 (명)"},
        markers=True,
        hover_data={"날짜": "|%Y년 %m월 %d일", "일관객": ":,d"},
    )

    # Customizing chart appearance
    fig1.update_traces(
        line=dict(width=2.5, color="#E50914"),
        marker=dict(size=6),
        hovertemplate="<b>날짜:</b> %{x|%Y-%m-%d}<br><b>일관객:</b> %{y:,}명<extra></extra>",
    )

    fig1.update_layout(
        xaxis_title="날짜",
        yaxis_title="일일 관객 수 (명)",
        hovermode="x unified",
        margin=dict(l=40, r=40, t=60, b=40),
        template="plotly_white",
    )

    # Render chart
    st.plotly_chart(fig1, use_container_width=True)

    # Interpretation placeholder box
    st.info(
        "💡 **이 그래프로 알 수 있는 것:** (여기에 분석 및 인사이트 내용을 작성하세요.)"
    )

st.markdown("---")

# ==========================================
# Section 2: 기간 내 관객수 상위 5개 영화 비교
# ==========================================
st.header("📌 Section 2. 관객수 상위 5개 영화의 일별 관객 수 비교")

# Calculate top 5 movies by total '일관객'
top5_movies = df.groupby("영화명")["일관객"].sum().nlargest(5).index.tolist()

# Filter dataset for top 5 movies
top5_df = df[df["영화명"].isin(top5_movies)].sort_values("날짜")

# Create Plotly Multi-line Chart
fig2 = px.line(
    top5_df,
    x="날짜",
    y="일관객",
    color="영화명",
    title="기간 내 총 관객수 상위 5개 영화의 날짜별 일관객 수 변화",
    labels={
        "날짜": "날짜",
        "일관객": "일일 관객 수 (명)",
        "영화명": "영화 제목",
    },
    markers=True,
)

fig2.update_traces(
    line=dict(width=2),
    marker=dict(size=5),
    hovertemplate="<b>영화:</b> %{fullData.name}<br><b>날짜:</b> %{x|%Y-%m-%d}<br><b>일관객:</b> %{y:,}명<extra></extra>",
)

fig2.update_layout(
    xaxis_title="날짜",
    yaxis_title="일일 관객 수 (명)",
    hovermode="x unified",
    legend=dict(
        title="영화 제목 (클릭하여 켜기/끄기)",
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
    ),
    margin=dict(l=40, r=40, t=60, b=40),
    template="plotly_white",
)

# Render chart
st.plotly_chart(fig2, use_container_width=True)

# Interpretation placeholder box
st.info(
    "💡 **이 그래프로 알 수 있는 것:** (여기에 분석 및 인사이트 내용을 작성하세요.)"
)

st.markdown("---")

# ==========================================
# Section 3: 추가 그래프 영역 (확장용)
# ==========================================
st.header("📌 Section 3. (추가 그래프 영역)")
st.caption(
    "앞으로 추가될 시간 관련 시각화 그래프가 이 구역에 들어갈 예정입니다."
)

with st.container():
    st.write("*(추후 차트 추가 공간)*")
    st.info(
        "💡 **이 그래프로 알 수 있는 것:** (여기에 분석 및 인사이트 내용을 작성하세요.)"
    )
