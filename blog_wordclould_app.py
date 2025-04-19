from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from textblob import TextBlob
import time
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# 크롬 드라이버 설정
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

# 데이터 수집 함수
def get_blog_data(query, start_date, end_date, max_pages):
    all_text = ""
    headers = {"User-Agent": "Mozilla/5.0"}
    
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
            content = blog_soup.select_one(".se-main-container")
            
            if content:
                all_text += " " + content.get_text()
    
    return all_text

# 감성 분석 함수
def analyze_sentiment(text):
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity
    return "긍정" if sentiment > 0 else "부정" if sentiment < 0 else "중립"

# 워드클라우드 생성 함수
def generate_wordcloud(text):
    wc = WordCloud(width=800, height=400, background_color="white").generate(text)
    plt.figure(figsize=(12, 6))
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.show()

# 예시 실행
query = "프루떼"
start_date = "20230401"
end_date = "20250331"
max_pages = 3

all_text = get_blog_data(query, start_date, end_date, max_pages)

# 감성 분석 결과
sentiment_result = analyze_sentiment(all_text)
print(f"감성 분석 결과: {sentiment_result}")

# 워드클라우드 생성
generate_wordcloud(all_text)

# 셀레니움 드라이버 종료
driver.quit()
