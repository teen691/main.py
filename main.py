import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="일일 박스오피스 순위",
    page_icon="🎬",
    layout="wide"
)

# 2. 한국 시간(KST) 기준 '어제' 날짜 계산 (YYYYMMDD 형식)
kst = timezone(timedelta(hours=9))
yesterday = datetime.now(kst) - timedelta(days=1)
target_dt = yesterday.strftime("%Y%m%d")
display_date = yesterday.strftime("%Y년 %m월 %d일")

st.title(f"🎬 어제({display_date}) 박스오피스 순위")
st.markdown("영화진흥위원회(KOBIS) 오픈 API를 활용한 실시간 박스오피스 정보입니다.")

# 3. API 호출 함수 (1시간 동안 캐시 유지하여 중복 요청 방지)
@st.cache_data(ttl=3600)
def get_box_office_data(date_str):
    # 비밀 금고(st.secrets)에서 인증키 불러오기
    try:
        api_key = st.secrets["KOBIS_KEY"]
    except Exception:
        return {"error": "secrets.toml 파일에 KOBIS_KEY가 설정되지 않았습니다. Streamlit Cloud 설정을 확인해주세요."}
    
    url = "https://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"
    params = {
        "key": api_key,
        "targetDt": date_str
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        # API 응답 내에 faultInfo(오류 정보)가 포함되어 있는지 확인
        if "faultInfo" in data:
            return {"error": f"KOBIS API 오류 발생: {data['faultInfo']}\n(인증키가 올바른지 확인해주세요.)"}
            
        # 정상적인 데이터 구조인지 확인
        if "boxOfficeResult" not in data or not data["boxOfficeResult"].get("dailyBoxOfficeList"):
            return {"error": "조회된 영화 데이터가 없습니다. 해당 날짜에 집계된 데이터가 없거나 API 점검 중일 수 있습니다."}
            
        return data
        
    except Exception as e:
        return {"error": f"네트워크 요청 중 문제가 발생했습니다: {e}"}

# 데이터 불러오기 실행
result = get_box_office_data(target_dt)

# 4. 오류 발생 시 안내 화면 출력
if "error" in result:
    st.error("⚠️ 데이터를 불러오지 못했습니다.")
    st.info(
        f"**[확인해야 할 사항]**\n\n"
        f"1. **Streamlit Secrets 설정**: `KOBIS_KEY` 값이 올바르게 입력되었는지 확인하세요.\n"
        f"2. **API 인증키 상태**: 영화진흥위원회에서 발급받은 키가 활성화 상태인지 확인하세요.\n"
        f"3. **상세 오류 메시지**: {result['error']}"
    )
else:
    # 5. 데이터 파싱 및 전처리 (문자열 숫자를 숫자로 변환)
    raw_list = result["boxOfficeResult"]["dailyBoxOfficeList"]
    
    df = pd.DataFrame(raw_list)
    
    # 필요한 컬럼만 추출 및 이름 변경
    df_clean = pd.DataFrame({
        "순위": pd.to_numeric(df["rank"]),
        "영화명": df["movieNm"],
        "개봉일": df["openDt"],
        "당일 관객수": pd.to_numeric(df["audiCnt"]),
        "누적 관객수": pd.to_numeric(df["audiAcc"]),
        "스크린수": pd.to_numeric(df["scrnCnt"])
    })
    
    # 순위 기준으로 정렬 보장
    df_clean = df_clean.sort_values("순위").reset_index(drop=True)
    
    # 6. 1위 영화 지표 카드 (3장) 크게 표시
    st.markdown("---")
    st.subheader("🥇 어제의 1위 영화")
    top_movie = df_clean.iloc[0]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="영화명", value=top_movie["영화명"])
    with col2:
        st.metric(label="당일 관객수", value=f"{top_movie['당일 관객수']:,} 명")
    with col3:
        st.metric(label="누적 관객수", value=f"{top_movie['누적 관객수']:,} 명")
        
    st.markdown("---")
    
    # 7. 전체 박스오피스 순위 표 출력
    st.subheader("📊 전체 박스오피스 순위표")
    st.dataframe(
        df_clean,
        use_container_width=True,
        hide_index=True
    )
    
    # 8. 관객수 상위 5편 막대그래프 표시
    st.markdown("---")
    st.subheader("📈 관객수 상위 5편 비교")
    top_5 = df_clean.head(5).set_index("영화명")
    st.bar_chart(top_5["당일 관객수"])
