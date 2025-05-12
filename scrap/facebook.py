import time
from selenium import webdriver
from settings import Settings
from scrap.scraping_functions import ScrapingFunctions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from database.agent import Agent, EnumDatabaseNames, EnumCollectionNames
import random
from datetime import datetime
from enum import Enum

class EnumStatus(Enum):
    INITIAL_SCRAP = "INITIAL_SCRAP"
    COMPLEMENT_INFORMATION = "COMPLEMENT_INFORMATION"
    AGENT_ACTION = "AGENT_ACTION"
    CLEAN_DATA = "CLEAN_DATA"

class FacebookScraper:
    @staticmethod
    def login(driver: webdriver) -> webdriver:
        driver.get("https://www.facebook.com")

        time.sleep(10)

        # Find email field
        email_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "email"))
        )
        email = Settings.FACEBOOK_EMAIL
        for c in email:
            email_input.send_keys(c)
            time.sleep(random.uniform(0.5, 0.8))

        # Find password field
        password_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "pass"))
        )
        password = Settings.FACEBOOK_PASSWORD
        for c in password:
            password_input.send_keys(c)
            time.sleep(random.uniform(0.5, 2))

        # Click login
        login_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, "login"))
        )
        login_btn.click()
        time.sleep(5)

        return driver

    @staticmethod
    def search_in_marketplace(driver: webdriver,) -> webdriver:
        search_url = 'https://www.facebook.com/marketplace/107754842580338/search/?query=iphone'
        driver.get(search_url)
        time.sleep(10)

    @staticmethod
    def find_all_available_products(driver: webdriver) -> list[dict]:
        ScrapingFunctions.skip_lazy_loading(driver)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        all_items_information = []

        all_available_products = soup.find_all('div', attrs={'class': 'x9f619 x78zum5 x1r8uery xdt5ytf x1iyjqo2 xs83m0k x1e558r4 x150jy0e x1iorvi4 xjkvuk6 xnpuxes x291uyu x1uepa24'})
        print(f'Found {len(all_available_products)} products')
        for product in all_available_products:
            product_link = product.find('a', {'class': 'x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1heor9g xkrqix3 x1sur9pj x1s688f x1lku1pv'})
            info = product.find_all('div', {'class': 'x1gslohp xkh6y0r'})
            if len(info) > 2:
                item_price = info[0]
                item_description = info[1]
                item_location = info[2]

                item_dict = {
                    'link': 'https://www.facebook.com'+product_link['href'] if product_link else None,
                    'price': item_price.text.strip() if item_price else None,
                    'description': item_description.text.strip() if item_description else None,
                    'location': item_location.text.strip() if item_location else None,
                    'collection_date': datetime.now(),
                    'status': EnumStatus.INITIAL_SCRAP.value
                }
                all_items_information.append(item_dict)

                print(item_dict)
        return all_items_information

    @staticmethod
    def find_all_new_products(available_products: list[dict]) -> list[dict]:
        #1. Find all already registered items
        agent = Agent(EnumDatabaseNames.DIGITAL_MARKETPLACE.value)
        db = agent.database
        all_registered_links = db[EnumCollectionNames.FACEBOOK_MARKET_PLACE.value].distinct('link')

        new_registered_products = []

        #2. Check if it's already in the database.
        #   If not. Register it.
        for product in available_products:
            if product['link'] not in all_registered_links:
                new_registered_products.append(product)
            else:
                db[EnumCollectionNames.FACEBOOK_MARKET_PLACE.value].update_one({'link': product['link']}, {'$set': {'last_seem_at':datetime.now()}})

        db[EnumCollectionNames.FACEBOOK_MARKET_PLACE.value].insert_many(new_registered_products)
        return new_registered_products

    @staticmethod
    def complement_available_product_info(driver: webdriver) -> None:
        # 1. Find all already registered items
        agent = Agent(EnumDatabaseNames.DIGITAL_MARKETPLACE.value)
        db = agent.database

        all_scraped_items_cursor = db[EnumCollectionNames.FACEBOOK_MARKET_PLACE.value].find({
            'status': EnumStatus.INITIAL_SCRAP.value,
        })

        all_scraped_items = list(all_scraped_items_cursor)

        def close_register_modal():
            # Wait for the close button with aria-label="Fechar" to be clickable
            close_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Fechar' and @role='button']"))
            )

            # Scroll to it (optional) and click
            driver.execute_script("arguments[0].scrollIntoView(true);", close_button)
            close_button.click()

        def click_show_more_if_available():
            xpath = "//span[contains(@class, 'x193iq5w') and text()='Ver mais']"

            ver_mais = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )

            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", ver_mais)
            ver_mais.click()

        for item in all_scraped_items:
            driver.get(item['link'])
            time.sleep(5)
            try:
                close_register_modal()
                time.sleep(2)
                click_show_more_if_available()
                time.sleep(2)
            except Exception:
                pass


            soup = BeautifulSoup(driver.page_source, 'html.parser')
            seller_description = soup.find('div', {
                'class': 'xz9dl7a x4uap5 xsag5q8 xkhd6sd x126k92a'})
            condition = soup.find('span', {
                'class': 'x1e558r4 xp4054r x3hqpx7'})

            if seller_description:
                db[EnumCollectionNames.FACEBOOK_MARKET_PLACE.value].update_one(
                    {"_id": item["_id"]},
                    {"$set": {
                        'seller_description': seller_description.text.strip(),
                        'status': EnumStatus.COMPLEMENT_INFORMATION.value
                    }}
                )
            if condition:
                db[EnumCollectionNames.FACEBOOK_MARKET_PLACE.value].update_one(
                    {"_id": item["_id"]},
                    {"$set": {
                        'condition': condition.text.strip(),
                        'status': EnumStatus.COMPLEMENT_INFORMATION.value
                    }}
                )

if __name__ == '__main__':
    driver = ScrapingFunctions.create_driver()
    try:
        FacebookScraper.login(driver)
        time.sleep(10)
        FacebookScraper.search_in_marketplace(driver)
        time.sleep(10)
        available_products = FacebookScraper.find_all_available_products(driver)
        FacebookScraper.find_all_new_products(available_products)


        #Starts a new driver with no login information in it.
        driver.quit()
        driver = ScrapingFunctions.create_driver()
        FacebookScraper.complement_available_product_info(driver)
    except Exception as e:
        print(f'Exception occurred: {e}')
    finally:
        driver.quit()