import os
import pandas as pd
import asyncio
import aiofiles
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import logging
import re

logging.basicConfig(filename='scraping.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def initialize_webdriver():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    webdriver_path = os.path.join(script_dir, 'chromedriver.exe')
    chrome_browser_path = r"chrome.exe"
    options = Options()
    options.binary_location = chrome_browser_path
    service = Service(webdriver_path)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(15)  
    return driver

def clean_html(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text).strip()

async def get_movie_data(driver, url, sr):
    data = {
        'sr': sr,
        'Title': None,
        'Year': None,
        'Genres': [],
        'Director': [],
        'Writer': [],
        'Cast': [],
        'Metascore': None,
        'Synopsis': None,
        'Runtime': None,
        'IMDb_Score': None,
        'User_Reviews_Count': "0",
        'Critic_Reviews_Count': "0",
        'User_Review_1': None,
        'User_Review_2': None,
        'User_Review_3': None,
        'Critic_Review_1': None,
        'Critic_Review_2': None,
        'Box_Office_Budget': None,
        'Box_Office_USA_Weekend': None,
        'Box_Office_Worldwide': None,
        'Keywords': [],
        'Production_Companies': []
    }

    try:
        driver.get(url)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1')))
        title_element = driver.find_element(By.CSS_SELECTOR, 'span.hero__primary-text')
        data['Title'] = clean_html(title_element.get_attribute('innerHTML')) if title_element else "N/A"
        data['Production_Companies'] = [a.text for a in driver.find_elements(By.XPATH, '//li[@data-testid="title-details-companies"]//div[@class="ipc-metadata-list-item__content-container"]//ul/li/a')]
        
        try:
            year_element = driver.find_element(By.XPATH, '(//a[@class="ipc-link ipc-link--baseAlt ipc-link--inherit-color"])[6]')
            data['Year'] = clean_html(year_element.get_attribute('innerHTML')) if year_element else "N/A"
        except Exception as e:
            logging.error(f"Year not found for {url}: {e}")
            data['Year'] = "N/A"

        genre_elements = driver.find_elements(By.CSS_SELECTOR, 'div.ipc-chip-list__scroller span.ipc-chip__text')
        data['Genres'] = [clean_html(genre.get_attribute('innerHTML')) for genre in genre_elements] if genre_elements else []
        
        try:
            director_element = driver.find_element(By.XPATH, '//li[@data-testid="title-pc-principal-credit"][1]//a')
            data['Director'] = [clean_html(director_element.get_attribute('innerHTML'))] if director_element else []
        except Exception as e:
            logging.error(f"Director not found for {url}: {e}")
            data['Director'] = []

        try:
            writer_elements = driver.find_elements(By.XPATH, '//li[@data-testid="title-pc-principal-credit"][2]//a')
            data['Writer'] = [clean_html(writer.get_attribute('innerHTML')) for writer in writer_elements] if writer_elements else []
        except Exception as e:
            logging.error(f"Writers not found for {url}: {e}")
            data['Writer'] = []

        try:
            cast_elements = driver.find_elements(By.XPATH, '//li[@data-testid="title-pc-principal-credit"][3]//a')
            cast_set = set()
            for cast in cast_elements:
                name = clean_html(cast.get_attribute('innerHTML'))
                if name != "Stars":
                    cast_set.add(name)
            data['Cast'] = list(cast_set)
        except Exception as e:
            logging.error(f"Cast not found for {url}: {e}")
            data['Cast'] = []

        try:
            metascore_element = driver.find_element(By.CSS_SELECTOR, 'span.sc-b0901df4-0')
            data['Metascore'] = clean_html(metascore_element.get_attribute('innerHTML')) if metascore_element else "N/A"
        except Exception as e:
            logging.error(f"Metascore not found for {url}: {e}")
            data['Metascore'] = "N/A"

        synopsis_element = driver.find_element(By.CSS_SELECTOR, 'span[data-testid="plot-xl"]')
        data['Synopsis'] = clean_html(synopsis_element.get_attribute('innerHTML')) if synopsis_element else "N/A"
        
        try:
            runtime_element = driver.find_element(By.CSS_SELECTOR, 'li[data-testid="title-techspec_runtime"] .ipc-metadata-list-item__content-container')
            data['Runtime'] = clean_html(runtime_element.get_attribute('innerHTML')) if runtime_element else "N/A"
        except Exception as e:
            logging.error(f"Runtime not found for {url}: {e}")
            data['Runtime'] = "N/A"

        try:
            imdb_score_element = driver.find_element(By.CSS_SELECTOR, 'div[data-testid="hero-rating-bar__aggregate-rating__score"] span.sc-d541859f-1')
            data['IMDb_Score'] = clean_html(imdb_score_element.get_attribute('innerHTML')) if imdb_score_element else "N/A"
        except Exception as e:
            logging.error(f"IMDb Score not found for {url}: {e}")
            data['IMDb_Score'] = "N/A"
        
        try:
            user_reviews_count_element = driver.find_element(By.CSS_SELECTOR, 'a.ipc-link--baseAlt[href*="/reviews/"] span.score')
            data['User_Reviews_Count'] = clean_html(user_reviews_count_element.get_attribute('innerHTML')) if user_reviews_count_element else "0"
        except Exception as e:
            logging.error(f"User reviews count not found for {url}: {e}")
            data['User_Reviews_Count'] = "0"

        try:
            critic_reviews_count_element = driver.find_element(By.CSS_SELECTOR, 'a.ipc-link--baseAlt[href*="/externalreviews/"] span.score')
            data['Critic_Reviews_Count'] = clean_html(critic_reviews_count_element.get_attribute('innerHTML')) if critic_reviews_count_element else "0"
        except Exception as e:
            logging.error(f"Critic reviews count not found for {url}: {e}")
            data['Critic_Reviews_Count'] = "0"
        
        try:
            box_office_data = {}
            box_office_section = driver.find_element(By.CSS_SELECTOR, 'section[data-testid="BoxOffice"]')
            box_office_items = box_office_section.find_elements(By.CSS_SELECTOR, 'li[data-testid^="title-boxoffice-"]')

            for item in box_office_items:
                label = clean_html(item.find_element(By.CSS_SELECTOR, 'span.ipc-metadata-list-item__label').get_attribute('innerHTML'))
                value = clean_html(item.find_element(By.CSS_SELECTOR, 'span.ipc-metadata-list-item__list-content-item').get_attribute('innerHTML'))
                box_office_data[label] = value

            data['Box_Office_Budget'] = box_office_data.get('Budget', 'N/A')
            data['Box_Office_USA_Weekend'] = box_office_data.get('Opening weekend US & Canada', 'N/A')
            data['Box_Office_Worldwide'] = box_office_data.get('Gross worldwide', 'N/A')
        except Exception as e:
            logging.error(f"Failed to fetch box office data for {url}: {e}")
            data['Box_Office_Budget'] = "N/A"
            data['Box_Office_USA_Weekend'] = "N/A"
            data['Box_Office_Worldwide'] = "N/A"
        
        try:
            user_reviews_link_element = driver.find_element(By.CSS_SELECTOR, 'a.isReview[href*="/reviews/"]')
            user_reviews_url = user_reviews_link_element.get_attribute('href')
        except Exception as e:
            logging.error(f"Failed to fetch user reviews link for {url}: {e}")
            user_reviews_url = None

        try:
            critic_reviews_link_element = driver.find_element(By.CSS_SELECTOR, 'a.isReview[href*="/criticreviews/"]')
            critic_reviews_url = critic_reviews_link_element.get_attribute('href')
        except Exception as e:
            logging.error(f"Failed to fetch critic reviews link for {url}: {e}")
            critic_reviews_url = None
        
        if user_reviews_url:
            try:
                driver.get(user_reviews_url)
                WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[data-testid="review-card-parent"]')))
                user_review_elements = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="review-card-parent"]')
                filtered_reviews = []
                for review in user_review_elements:
                    spoiler_button = review.find_elements(By.XPATH, './/button[contains(@aria-label, "Expand Spoiler")]')
                    if not spoiler_button:
                        filtered_reviews.append(review)

                review_count = min(len(filtered_reviews), 3)
                for i in range(review_count):
                    review_text = clean_html(filtered_reviews[i].find_element(By.CSS_SELECTOR, 'h3.ipc-title__text').get_attribute('innerHTML'))
                    data[f'User_Review_{i+1}'] = review_text
                
                for i in range(review_count, 3):
                    data[f'User_Review_{i+1}'] = "N/A"
            except Exception as e:
                logging.error(f"Failed to fetch user reviews for {user_reviews_url}: {e}")
                for i in range(1, 4):
                    data[f'User_Review_{i}'] = "N/A"
        
        if critic_reviews_url:
            try:
                driver.get(critic_reviews_url)
                WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'li[data-testid="list-item"]')))
                critic_review_elements = driver.find_elements(By.CSS_SELECTOR, 'li[data-testid="list-item"]')
                review_count = min(len(critic_review_elements), 2)
                for i in range(review_count):
                    score = clean_html(critic_review_elements[i].find_element(By.CSS_SELECTOR, 'div.sc-d8486f96-2').get_attribute('innerHTML'))
                    critic_name = clean_html(critic_review_elements[i].find_element(By.CSS_SELECTOR, 'span.sc-d8486f96-5').get_attribute('innerHTML'))
                    review_text = clean_html(critic_review_elements[i].find_element(By.CSS_SELECTOR, 'div.sc-d8486f96-3.blaUqS + div').get_attribute('innerHTML'))

                    data[f'Critic_Review_{i+1}'] = f"Score: {score}\nCritic: {critic_name}\nReview: {review_text}"
                
                for i in range(review_count, 2):
                    data[f'Critic_Review_{i+1}'] = "N/A"
            except Exception as e:
                logging.error(f"Failed to fetch critic reviews for {critic_reviews_url}: {e}")
                for i in range(1, 3):
                    data[f'Critic_Review_{i}'] = "N/A"
            
        keyword_elements = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="storyline-plot-keywords"] a.ipc-chip__text')
        data['Keywords'] = [clean_html(keyword.get_attribute('innerHTML')) for keyword in keyword_elements] if keyword_elements else []

    except Exception as e:
        logging.error(f"An error occurred while scraping data from {url}: {e}")
    
    return data

async def update_csv(df):
    async with aiofiles.open('data/movies_complete_data.csv', mode='w', encoding='utf-8') as f:
        await f.write(df.to_csv(index=False))

async def main():
    search_url = 'https://www.imdb.com/search/title/?title_type=feature&release_date=2024-01-01,2024-01-02&countries=US&languages=en'
    
    all_data = []
    driver = initialize_webdriver()
    
    try:
        logging.info("Navigating to search URL")
        driver.get(search_url)

        while True:
            try:
                see_more_button = driver.find_element(By.XPATH, '//span[contains(@class, "ipc-see-more")]/button[contains(@class, "ipc-see-more__button")]')
                ActionChains(driver).move_to_element(see_more_button).perform()
                WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, '//span[contains(@class, "ipc-see-more")]/button[contains(@class, "ipc-see-more__button")]')))
                see_more_button.click()
                logging.info("Clicked 'See More' button")
                await asyncio.sleep(5)
                WebDriverWait(driver, 20).until(
                    lambda d: len(d.find_elements(By.CSS_SELECTOR, 'a.ipc-title-link-wrapper')) > 0
                )
                logging.info("New movies loaded")

            except Exception as e:
                logging.error(f"Error while trying to click 'See More' button: {e}")
                break

        movie_urls = [element.get_attribute('href') for element in driver.find_elements(By.CSS_SELECTOR, 'a.ipc-title-link-wrapper')]
        logging.info(f"Found {len(movie_urls)} movie URLs on the final page")
        
        for idx, url in enumerate(movie_urls, start=len(all_data) + 1):
            movie_data = await get_movie_data(driver, url, idx)
            movie_data['URL'] = url
            all_data.append(movie_data)
            df = pd.DataFrame(all_data)
            await update_csv(df)
            await asyncio.sleep(2)

    except Exception as e:
        logging.error(f"Failed: {e}")
    finally:
        driver.quit()
    
    df = pd.DataFrame(all_data)
    if not os.path.exists('data'):
        os.makedirs('data')
    df.to_csv('data/movies_complete_data.csv', index=False)
    logging.info("Data scraping complete!")

if __name__ == "__main__":
    asyncio.run(main())