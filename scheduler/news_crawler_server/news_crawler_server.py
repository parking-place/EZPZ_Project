import sys
sys.path.append('/app/EZPZ_Project/modules/crawlers/news')
#from daum_news_crawler import get_news
import daum_news_crawler
import naver_news_crawler
import news_crawlers

comp2= naver_news_crawler.get_news('삼성전자')
#print("comp2")