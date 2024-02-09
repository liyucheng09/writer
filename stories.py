from selenium.webdriver.common.keys import Keys
import traceback
from selenium.webdriver.common.by import By
from selenium import webdriver
from tqdm import tqdm
import pandas as pd

class ChromeCrawler:

    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        self.driver = webdriver.Chrome(options = options)
        # self.driver = webdriver.Chrome()
    
    def get_articles(self, news_urls):
        all_articles = {}
        single_url = isinstance(news_urls, str)
        if single_url:
            news_urls = [news_urls]
        for url in tqdm(news_urls):
            if url in all_articles:
                continue
            if url == '-':
                all_articles[url] = '-'
                continue
            try:
                self.driver.get(url)
            except:
                traceback.print_exc()
                all_articles[url] = '-'
                continue
            try:
                main_element = self.driver.find_element(By.TAG_NAME, 'main')
                paras = main_element.find_elements(By.TAG_NAME, 'p')
                assert paras[0] != '', 'Empty p'
                all_articles[url] = '\n'.join([para.text for para in paras])
            except:
                try:
                    self.driver.execute_script("arguments[0].click();", self.driver.find_element(By.TAG_NAME,'main'))
                    paras = main_element.find_elements(By.TAG_NAME, 'p')
                    assert paras[0] != '', 'Empty <p>'
                    all_articles[url] = '\n'.join([para.text for para in paras])
                except:
                    traceback.print_exc()
                    all_articles[url] = '-'
                    continue
        if single_url:
            return all_articles[url]
        return all_articles