import streamlit as st
import requests
from bs4 import BeautifulSoup
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import datetime
import time

# Streamlit UI
st.title("🔍 네이버 블로그 키워드 워드클라우드 분석기")
st.markdown("네이버 블로그의 게시물 제목과 본문을 분석하여 워드클라우드를 생성합니다.")

query = st.text_input("검색어를 입력하세요 (예: 여주 농촌체험)", value="여주 농촌체험")
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("시작 날짜", datetime.date(2025, 3, 1))
with col2:
    end_date = st.date_input("종료 날짜", datetime.date(2025, 6, 30))

max_pages = st.slider("검색할 페이지 수 (1페이지당 약 10개 게시글)", min_value=1, max_value=10, value=3)

if st.button("분석 시작"):
    with st.spinner("네이버 블로그 데이터를 수집 중입니다..."):
        all_text = ""
        headers = {"User-Agent": "Mozilla/5.0"}
        for page in range(1, max_pages + 1):
            url = f"https://search.naver.com/search.naver?where=view&sm=tab_jum&query={query}&nso=so%3Add%2Cp%3Afrom{start_date.strftime('%Y%m%d')}to{end_date.strftime('%Y%m%d')}&start={(page - 1) * 10 + 1}"
            res = requests.get(url, headers=headers)
            soup = BeautifulSoup(res.text, "html.parser")
            items = soup.select(".api_txt_lines.total_tit")
            for item in items:
                title = item.text.strip()
                all_text += " " + title
                
                # 본문 내용 수집
                blog_url = item['href']
                blog_res = requests.get(blog_url, headers=headers)
                blog_soup = BeautifulSoup(blog_res.text, "html.parser")
                content = blog_soup.select_one(".se-main-container")
                
                if content:
                    # 본문 텍스트를 추출해서 합침
                    all_text += " " + content.get_text()

            time.sleep(1)

        if all_text.strip() == "":
            st.warning("데이터를 수집하지 못했습니다. 키워드나 기간을 변경해 보세요.")
        else:
            # 워드클라우드 생성
            st.subheader("📊 워드클라우드 결과")
            wc = WordCloud(font_path="NanumGothic.ttf", width=800, height=400, background_color="white").generate(all_text)
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.imshow(wc, interpolation='bilinear')
            ax.axis("off")
            st.pyplot(fig)
