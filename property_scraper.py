import json
from datetime import datetime, timedelta

from selenium import webdriver
from selenium.common import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

import time


class Bot:
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 30)

    def get_properties(self, num_properties):

        self.driver.get("https://realtylink.org/en/properties~for-rent")
        self.driver.find_element(By.XPATH, "//button[@id='dropdownSort']").click()
        self.driver.find_element(By.XPATH, "//a[contains(text(), 'Less recent publications')]").click()

        all_properties = []
        property_count_old = 0

        date_object = datetime.today()
        formatted_date = date_object.strftime("%Y-%m-%d")

        while True:

            self.driver.find_element(By.XPATH, "//i[@class='fal fa-filter']").click()

            time.sleep(1)
            self.driver.find_element(By.XPATH, "//div[@id='OtherSection-accordion']").click()

            input_area = self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@id='LastModifiedDate-dateFilterPicker']")))
            input_area.clear()
            input_area.send_keys(formatted_date)
            input_area.send_keys(Keys.ENTER)

            time.sleep(1)

            search_button = self.driver.find_element(By.XPATH, "//span[@id='property-count']")
            property_count = int(search_button.text.strip().split()[0])
            search_button.click()

            time.sleep(2)

            self.driver.find_element(By.XPATH, "//a[@id='ButtonViewSummary']").click()

            for _ in range(property_count - property_count_old):

                time.sleep(2)

                link = self.driver.current_url
                print(link)

                title = self.driver.find_element(By.XPATH, "//span[@data-id='PageTitle']").text.strip()
                address = self.driver.find_element(By.XPATH, "//h2[@itemprop='address']").text.strip()
                region = ",".join(address.split(",")[1:])
                price = self.driver.find_elements(By.XPATH, "//span[@class='text-nowrap']")[-1].text.strip().split(" /")[0]
                try:
                    bedrooms = self.driver.find_element(By.XPATH, "//div[@class='col-lg-3 col-sm-6 cac']").text.strip().split()[0]
                except StaleElementReferenceException:
                    bedrooms = None
                except NoSuchElementException:
                    bedrooms = None
                floor_area = self.driver.find_element(By.XPATH, "//div[@class='col-lg-3 col-sm-6 carac-container']//span").text.strip()

                try:
                    description = self.driver.find_element(By.XPATH, "//div[@itemprop='description']").text.strip()
                except NoSuchElementException:
                    description = None

                img_button = self.driver.find_elements(By.XPATH, "//div[@class='photo-buttons legacy-reset ']")
                try:
                    img_button = img_button[-1]
                    count_images = int(img_button.text.strip())
                except ValueError:
                    img_button = img_button[0]
                    count_images = int(img_button.text.strip())
                img_button.click()

                time.sleep(2)
                images = []

                for _ in range(count_images):
                    img_tag = self.driver.find_element(By.XPATH, "//img[@id='fullImg']")
                    images.append(img_tag.get_attribute('src'))
                    img_tag.click()

                all_properties.append(
                    {
                        "link": link,
                        "title": title,
                        "region": region,
                        "address": address,
                        "description": description,
                        "images": images,
                        "publication/update_data": formatted_date,
                        "price": price,
                        "bedrooms": bedrooms,
                        "floor_area": floor_area,
                    }
                )

                if len(all_properties) > num_properties - 1:
                    return self.create_json_file(all_properties)

                self.driver.find_element(By.XPATH, "//div[@class='close icon-close']").click()

                try:
                    self.driver.find_element(By.XPATH, "//li[@class='next']//a").click()
                except:
                    pass

            property_count_old = property_count

            date_object = datetime.strptime(formatted_date, "%Y-%m-%d")
            one_day_ago = date_object - timedelta(days=1)
            formatted_date = one_day_ago.strftime("%Y-%m-%d")

    @staticmethod
    def create_json_file(data_list, filename="properties-new.json"):

        with open(filename, 'w') as json_file:
            json.dump(data_list, json_file, indent=4)


if __name__ == '__main__':

    NUM_PROPERTIES = 60

    b = Bot()
    b.get_properties(NUM_PROPERTIES)
