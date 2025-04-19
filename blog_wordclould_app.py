from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from textblob import TextBlob
import nltk
import time
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import sys
import os

# nltk 데이터 다운로드 (최초 1회)
nltk.download('punkt')

# 크롬 드라이버 설정
chrome_options = Options()
chrome_options.add_argument("--headless")  # 창 없이 실행
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# 환경에 따라 드라이버 경로 설정
if os.getenv("GITHUB_ACTIONS") == "true":
    driver_path = "/usr/local/bin/chromedriver"  # GitHub Actions용
else:
    from webdriver_manager.chrome import ChromeDriverManager
    driver_path = ChromeDriverManager().install()  # 로컬 자동 설치

driver = webdriver.Chrome(executable_path=driver_path, options=chrome_options)


# 블로그 및 카페 데이터 수집 함수
def get_blog_data(query, start_date, end_date, max_pages):
    all_text = ""
    
    for page in range(1, max_pages + 1):
        url = f"https://search.naver.com/search.naver?where=view&query={query}&nso=so:dd,p:from{start_date}to{end_date}&start={(page - 1) * 10 + 1}"
        
        driver.get(url)
        time.sleep(2)
        
        soup = BeautifulSoup(driver.page_source, "html.parser")
        blog_items = soup.select(".api_txt_lines.total_tit")
        
        for item in blog_items:
            title = item.text.strip()
            all_text += " " + title
            
            blog_url = item['href']
            driver.get(blog_url)
            time.sleep(2)
            
            blog_soup = BeautifulSoup(driver.page_source, "html.parser")
            content = blog_soup.select_one(".se-main-container") or blog_soup.select_one("#contentArea") or blog_soup.select_one("article")

            if content:
                all_text += " " + content.get_text(separator=" ", strip=True)
    
    return all_text


# 감성 분석 함수
def analyze_sentiment(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    return "긍정" if polarity > 0 else "부정" if polarity < 0 else "중립"


# 워드클라우드 생성 함수
def generate_wordcloud(text):
    wc = WordCloud(font_path="NanumGothic.ttf", width=800, height=400, background_color="white").generate(text)
    plt.figure(figsize=(12, 6))
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig("wordcloud.png")  # 저장 (GitHub에서 확인 가능)
    plt.show()


# 실행 예시
if __name__ == "__main__":
    query = "프루떼"
    start_date = "20230401"
    end_date = "20250331"
    max_pages = 3

    print(f"🔍 '{query}'에 대한 게시글을 검색 중...")
    all_text = get_blog_data(query, start_date, end_date, max_pages)

    if all_text.strip() == "":
        print("❗️게시글 데이터를 수집하지 못했습니다.")
        sys.exit(1)

    # 감성 분석 결과
    sentiment_result = analyze_sentiment(all_text)
    print(f"\n💬 감성 분석 결과: {sentiment_result}")

    # 워드클라우드 생성
    print("🌥 워드클라우드 생성 중...")
    generate_wordcloud(all_text)

    driver.quit()
