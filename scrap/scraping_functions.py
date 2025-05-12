from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time


class ScrapingFunctions:
    @staticmethod
    def create_driver(headless: bool= False) -> webdriver.Chrome:
        chrome_options = Options()

        if headless:
            chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36')

        driver = webdriver.Chrome(options=chrome_options)
        return driver

    @staticmethod
    def skip_lazy_loading(driver, top_to_bottom=True, scroll_interval = 1, stop_at = 90, start_at = 1, scroll_unit = 10):
        """
            This method is useful to overcome the lazy loading behavior
            Some sites don't load all page elements at once.
            So we need to scroll it bottom-top to simulate a user interaction, and activate all page-elements.

            Returns:
                this method won't return anything - just simulate user behavior over the page.
        """

        # Function to scroll to a specified percentage of the page
        def scroll_to_percentage(percentage):
            total_height = driver.execute_script("return document.body.scrollHeight")
            position = total_height * (percentage / 100)
            driver.execute_script(f"window.scrollTo(0, {position});")

        def check_if_is_bottom():
            soup = BeautifulSoup(driver.page_source, "html.parser")
            location_limit = soup.find('div', {'class': 'xr1yuqi xkrivgy x4ii5y1 x1gryazu xptc4dh xyamay9 x4uap5 x1l90r2v xkhd6sd'})

            if location_limit:
                return True
            else:
                return None


        if top_to_bottom:
            for percentage in range(start_at, stop_at, scroll_unit):
                scroll_to_percentage(percentage)
                time.sleep(scroll_interval)
                if check_if_is_bottom():
                    break

        else:
            for percentage in range(start_at, stop_at, -scroll_unit):
                scroll_to_percentage(percentage)
                time.sleep(scroll_interval)
                if check_if_is_bottom():
                    break
        time.sleep(3)
        return driver