import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

@pytest.fixture()
def setup():
    chrome_options = Options()
    driver = webdriver.Chrome(options=chrome_options)
    driver.get('https://synaps-stg-aab67ad5805a.herokuapp.com/Signin')
    driver.maximize_window()
    driver.implicitly_wait(10)
    yield driver
    driver.quit()

class TestLoginSanity:
    counter = 0

    def find_and_interact(self, driver, wait, xpath):
        try:
            element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            element.click()
        except TimeoutException:
            print(f"Element with xpath {xpath} not found.")
            self.print_page_source(driver)
            raise

    def print_page_source(self, driver):
        print(driver.page_source)

    @pytest.mark.parametrize("username,password", [("test01@synaps.co", "123456")])
    def test_login_sanity_test(self, setup, username, password):
        TestLoginSanity.counter += 1
        driver = setup
        actions = ActionChains(driver)
        wait = WebDriverWait(driver, 10)
        wait3 = WebDriverWait(driver, 3)

        self.find_and_interact(driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[2]/div[1]/div/button')
        driver.find_element(By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[4]/div/input').send_keys(username)
        driver.find_element(By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[5]/div/input').send_keys(password)
        self.find_and_interact(driver, wait, '//*[@id="default-checkbox"]')

        # תחילת תהליך בדיקה

        # כפתור לוג אין
        self.find_and_interact(driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[7]/button')

        # תנאי שימוש
        self.find_and_interact(driver, wait, '/html/body/div[3]/div/div/div[1]/button')
        # בחירת אתגר
        self.find_and_interact(driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[3]/div[1]/div[2]/div/button')
        element_challenge_info = driver.find_element(By.ID, "challenge_info")
        driver.execute_script("arguments[0].click();", element_challenge_info)
        time.sleep(4)
        self.find_and_interact(driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[7]/div/div/button')

        # שלב 1
        element_brainwrite = driver.find_element(By.ID, "brain_write")
        driver.execute_script("arguments[0].click();", element_brainwrite)
        self.find_and_interact(driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[4]/div/div/button')

        for _ in range(5):
            next_text = self.get_next_name()
            try:
                text_area = driver.find_element(By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[4]/div[3]/textarea')
                text_area.send_keys(next_text)
                driver.find_element(By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[4]/div/div/button').click()
                time.sleep(1)
            except NoSuchElementException:
                print('Text area not found, continuing with the script.')
                self.print_page_source(driver)
                continue

        # בחירת רעיון טוב
        try:
            driver.find_element(By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[2]/div[3]').click()
            source_element = driver.find_element(By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/p[2]')
            copied_text = source_element.text
            target_text_area = driver.find_element(By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[1]/div[2]/div/textarea')
            target_text_area.clear()
            target_text_area.send_keys(f"{copied_text}_{TestLoginSanity.counter}")
            time.sleep(1)
        except NoSuchElementException:
            print('Final text area not found, terminating the script.')
            self.print_page_source(driver)
            return

        # אישור
        self.find_and_interact(driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[2]/div/div[2]/button')
        self.find_and_interact(driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[3]/div[2]')

        # פופאפ
        modal = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.CLASS_NAME, "ReactModal__Overlay")))
        button_inside_modal = modal.find_element(By.XPATH, '/html/body/div[3]/div/div/div[2]/div/button')
        button_inside_modal.click()

        # שלב 2
        element_bad_idea = driver.find_element(By.ID, "bad_idea")
        driver.execute_script("arguments[0].click();", element_bad_idea)
        self.find_and_interact(driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[4]/div/div/button')

        for _ in range(5):
            next_text = self.get_next_name()
            try:
                text_area = driver.find_element(By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[4]/textarea')
                text_area.send_keys(next_text)
            except NoSuchElementException:
                print('Text area not found, terminating the script.')
                self.print_page_source(driver)
                return

    def get_next_name(self):
        # פונקציה לדוגמה להחזרת שם הבא
        return "Example Text"
