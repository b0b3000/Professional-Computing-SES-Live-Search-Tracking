from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException
import unittest
import time
import random


class FlaskAppTest(unittest.TestCase):

    def setUp(self):
        # Set up the Selenium web driver (using Chrome here)
        self.driver = webdriver.Chrome()
        self.driver.get("http://127.0.0.1:5000")

    def handle_alert(self):
        """Utility function to handle alerts if present."""
        try:
            alert = WebDriverWait(self.driver, 5).until(EC.alert_is_present())
            alert_text = alert.text
            print(f"Alert detected: {alert_text}")
            alert.accept()
            return alert_text
        except TimeoutException:
            # No alert found
            return None

    def test_homepage_loads(self):
        self.assertIn("GPS Data Visualization v1.0", self.driver.title)

        # iframe for the map is visible
        map_element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "map-iframe"))
        )
        self.assertTrue(map_element.is_displayed())

    def test_start_search(self):
        main_page = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Start Search')]")
        main_page.click()
        start_search_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "start-search"))
        )
        start_search_button.click()
        alert_txt = self.handle_alert()
        self.assertEqual(alert_txt, "Search started!")  
        session_id_element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "search-panel"))  # assuming this element updates with session data
        )
        self.assertTrue(session_id_element.is_displayed())

    def test_end_search_without_active_session(self):
        main_page = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Start Search')]")
        main_page.click()
        end_search_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "end-search"))
        )
        end_search_button.click()
        alert_txt = self.handle_alert()
        self.assertEqual(alert_txt, "Search is not currently running.")  

    def select_random_base_station(self):
        """Selects a random base station from the available checkboxes."""
        base_station_checkboxes = self.driver.find_elements(By.CLASS_NAME, "container-checkbox")
        if len(base_station_checkboxes) == 0:
            self.fail("No base stations available to select")
        random_base_checkbox = random.choice(base_station_checkboxes)
        random_base_checkbox.click()
        print(f"Selected base station: {random_base_checkbox.get_attribute('value')}")

    def test_update_map(self):
        main_page = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Start Search')]")
        main_page.click()
        self.select_random_base_station()

        # Click the "Fetch Latest GPS Data" button
        latest_data = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "fetch-data-button"))
        )
        latest_data.click()

        # Handle alert
        alert_txt = self.handle_alert()
        self.assertIsNone(alert_txt)  # alert shouldnt appear if base station(s) was selected
        updated_map = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "map-iframe"))
        )
        self.assertTrue(updated_map.is_displayed())

    def test_filter_search(self):
        historical_data_page = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Historical Data')]")
        historical_data_page.click()
        start_date_input = self.driver.find_element(By.ID, "start-date")
        end_date_input = self.driver.find_element(By.ID, "end-date")
        base_station_select = self.driver.find_element(By.ID, "base-station")
        start_date_input.send_keys("2024-01-01")
        end_date_input.send_keys("2024-12-31")
        base_station_select.send_keys(Keys.CONTROL, "A")
        filter_button = self.driver.find_element(By.XPATH, "//input[@class='filter-submit']")
        filter_button.click()
        filtered_results = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "scrollable-table"))
        )
        self.assertTrue(filtered_results.is_displayed())

    def test_download_gpx_file(self):
        pass

    def tearDown(self):
        # Close the browser window
        self.driver.quit()


if __name__ == "__main__":
    unittest.main()
