import streamlit as st
import requests
from bs4 import BeautifulSoup
import datetime
import time
import urllib.parse
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# 감성 단어 사전
positive_words = [
    "좋다", "재밌다", "감동", "최고", "추천", "맛있다", "유익하다", "흥미롭다", "괜찮다",
    "즐겁다", "행복하다", "친절하다", "아름답다", "멋지다", "감사하다", "감격", "대박",
    "환상적이다", "완벽하다", "기쁘다", "기분 좋다", "만족스럽다", "기대 이상", "인상 깊다"
]

negative_words = [
    "별로", "나쁘다", "지루하다", "최악", "불편", "실망", "아쉽다", "짜증", "비추",
    "불만", "형편없다", "실수", "불쾌하다", "후회", "속상하다", "짜증나다", "지저분하다",
    "불친절", "어이없다", "의외로 별로", "실패", "다신 안 간다", "실망스럽다", "별로였다"
]

def analyze_sentiment(text):
    pos = sum(text.count(w) for w in positive_words)
    neg = sum(text.count(w) for w in negative_words)
    if pos > neg:
        return "긍정"
    elif neg > pos:
        return "부정"
    else:
        return "중립"

# Streamlit UI
st.title("🔍 네이버 블로그/카페 감성 분석 + 워드클라우드")
query = st.text_input("검색어를 입력하세요", "여주 농촌체험")

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("시작 날짜", datetime.date(2025, 3, 1))
with col2:
    end_date = st.date_input("종료 날짜", datetime.date(2025, 4, 20))

max_pages = st.slider("검색할 페이지 수", 1, 10, 3)

if st.button("분석 시작"):
    with st.spinner("네이버 데이터 수집 중..."):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        sentiment_results = {"긍정": 0, "부정": 0, "중립": 0}
        detailed_results = []
        all_text = ""

        for page in range(1, max_pages + 1):
            start = (page - 1) * 10 + 1
            encoded_query = urllib.parse.quote(query)
            url = (
                f"https://search.naver.com/search.naver"
                f"?where=view&query={encoded_query}"
                f"&nso=so%3Add%2Cp%3Afrom{start_date.strftime('%Y%m%d')}to{end_date.strftime('%Y%m%d')}"
                f"&start={start}"
            )

            st.info(f"[{page}페이지 요청 중] URL: {url}")

            try:
                res = requests.get(url, headers=headers, timeout=5)
                soup = BeautifulSoup(res.text, "html.parser")
                total_items = soup.select(".total_wrap.api_ani_send")  # 핵심 셀렉터

                if not total_items:
                    st.warning(f"{page}페이지에 결과가 없습니다.")
                    continue

                for item in total_items:
                    title_tag = item.select_one(".api_txt_lines.total_tit")
                    desc_tag = item.select_one(".total_dsc")

                    title = title_tag.get_text(strip=True) if title_tag else ""
                    description = desc_tag.get_text(strip=True) if desc_tag else ""
                    text = f"{title} {description}"
                    all_text += " " + text

                    sentiment = analyze_sentiment(text)
                    sentiment_results[sentiment] += 1
                    detailed_results.append((title, sentiment))

                time.sleep(1)

            except Exception as e:
                st.error(f"❌ {page}페이지 오류: {e}")
                break

        if not all_text.strip():
            st.error("❌ 분석할 텍스트가 없습니다. 검색어 또는 기간을 확인해주세요.")
        else:
            st.subheader("📊 감성 분석 결과")
            st.success(f"👍 긍정: {sentiment_results['긍정']}개")
            st.warning(f"😐 중립: {sentiment_results['중립']}개")
            st.error(f"👎 부정: {sentiment_results['부정']}개")

            with st.expander("게시글별 감성 분석 결과"):
                for i, (title, sentiment) in enumerate(detailed_results, 1):
                    st.write(f"{i}. [{sentiment}] {title}")

            st.subheader("☁️ 워드클라우드")
            wc = WordCloud(font_path="NanumGothic.ttf", width=800, height=400, background_color="white").generate(all_text)
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.imshow(wc, interpolation='bilinear')
            ax.axis("off")
            st.pyplot(fig)
