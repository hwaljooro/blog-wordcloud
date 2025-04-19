import streamlit as st
import requests
from bs4 import BeautifulSoup
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import datetime
import time

# Streamlit UI
st.title("🔍 네이버 블로그/카페 키워드 워드클라우드")
st.markdown("입력한 키워드에 대해 네이버 블로그/카페 제목을 수집해 워드클라우드를 만듭니다.")

query = st.text_input("검색어를 입력하세요 (예: 여주 농촌체험)", value="여주 농촌체험")

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("시작 날짜", datetime.date(2025, 3, 1))
with col2:
    end_date = st.date_input("종료 날짜", datetime.date(2025, 6, 30))

max_pages = st.slider("검색할 페이지 수", 1, 10, 3)

if st.button("분석 시작"):
    with st.spinner("데이터 수집 중..."):
        collected_text = ""
        headers = {"User-Agent": "Mozilla/5.0"}

        for page in range(1, max_pages + 1):
            start = (page - 1) * 10 + 1
            search_url = (
                f"https://search.naver.com/search.naver"
                f"?where=view&sm=tab_jum&query={query}"
                f"&nso=so:dd,p:from{start_date.strftime('%Y%m%d')}to{end_date.strftime('%Y%m%d')}"
                f"&start={start}"
            )

            try:
                res = requests.get(search_url, headers=headers, timeout=5)
                soup = BeautifulSoup(res.text, "html.parser")

                items = soup.select(".api_txt_lines.total_tit")
                if not items:
                    continue

                for item in items:
                    title = item.get_text(strip=True)
                    collected_text += " " + title

                time.sleep(1)

            except Exception as e:
                st.error(f"페이지 {page}에서 오류 발생: {e}")
                continue

        if not collected_text.strip():
            st.warning("데이터 수집 실패. 다른 키워드나 날짜로 다시 시도해주세요.")
        else:
            st.subheader("📊 워드클라우드 결과")
            wc = WordCloud(
                font_path="NanumGothic.ttf",
                width=800, height=400,
                background_color="white"
            ).generate(collected_text)

            fig, ax = plt.subplots(figsize=(12, 6))
            ax.imshow(wc, interpolation="bilinear")
            ax.axis("off")
            st.pyplot(fig)
