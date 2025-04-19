import streamlit as st
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import datetime
import urllib.parse
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# 감성 단어 사전
positive_words = ["좋다", "최고", "추천", "맛있다", "재밌다", "즐겁다", "감동", "감사", "멋지다"]
negative_words = ["별로", "최악", "실망", "불편", "아쉽다", "짜증", "나쁘다", "후회", "지루하다"]

def analyze_sentiment(text):
    pos = sum([text.count(w) for w in positive_words])
    neg = sum([text.count(w) for w in negative_words])
    if pos > neg:
        return "긍정"
    elif neg > pos:
        return "부정"
    else:
        return "중립"

def get_text_from_url_selenium(driver, url):
    try:
        driver.get("https://www.naver.com")
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        content = soup.select_one(".se-main-container")  # 블로그 글
        if not content:
            content = soup.select_one("#contentArea")  # 카페 글
        return content.get_text(separator=" ") if content else ""
    except Exception as e:
        return ""

# UI
st.title("🧠 본문 기반 감성 분석기 (네이버 블로그/카페)")
query = st.text_input("검색어를 입력하세요", "여주 농촌체험")

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("시작 날짜", datetime.date(2025, 3, 1))
with col2:
    end_date = st.date_input("종료 날짜", datetime.date(2025, 4, 20))

max_pages = st.slider("검색할 페이지 수", 1, 5, 2)

if st.button("분석 시작"):
    with st.spinner("크롬 브라우저를 실행하고 있습니다..."):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(ChromeDriverManager().install())

    sentiment_results = {"긍정": 0, "부정": 0, "중립": 0}
    detailed_results = []
    all_text = ""

    with st.spinner("데이터 수집 중..."):
        headers = {"User-Agent": "Mozilla/5.0"}
        for page in range(1, max_pages + 1):
            start = (page - 1) * 10 + 1
            encoded_query = urllib.parse.quote(query)
            url = (
                f"https://search.naver.com/search.naver"
                f"?where=view&query={encoded_query}"
                f"&nso=so%3Add%2Cp%3Afrom{start_date.strftime('%Y%m%d')}to{end_date.strftime('%Y%m%d')}"
                f"&start={start}"
            )

            res = requests.get(url, headers=headers)
            soup = BeautifulSoup(res.text, "html.parser")
            items = soup.select(".total_wrap.api_ani_send")

            for item in items:
                link_tag = item.select_one(".api_txt_lines.total_tit")
                if not link_tag:
                    continue
                title = link_tag.get_text(strip=True)
                href = link_tag["href"]

                body = get_text_from_url_selenium(driver, href)
                full_text = title + " " + body
                sentiment = analyze_sentiment(full_text)
                sentiment_results[sentiment] += 1
                detailed_results.append((title, sentiment))
                all_text += " " + full_text

            time.sleep(1)

        driver.quit()

    if not all_text.strip():
        st.error("❌ 본문 수집에 실패했습니다. 검색어 또는 기간을 다시 확인해주세요.")
    else:
        st.subheader("📊 감성 분석 결과")
        st.success(f"👍 긍정: {sentiment_results['긍정']}개")
        st.warning(f"😐 중립: {sentiment_results['중립']}개")
        st.error(f"👎 부정: {sentiment_results['부정']}개")

        with st.expander("🔎 게시글별 감성 분석"):
            for i, (title, sentiment) in enumerate(detailed_results, 1):
                st.write(f"{i}. [{sentiment}] {title}")

        st.subheader("☁️ 워드클라우드")
        wc = WordCloud(font_path="NanumGothic.ttf", width=800, height=400, background_color="white").generate(all_text)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.imshow(wc, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig)
