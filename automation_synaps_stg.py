from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoAlertPresentException
import time
import pytest

class TestLoginSanity:
    texts = {
        "brainwrite": ["Test 1", "Test 2", "Test 3", "Test 4", "Test 5"],
        "brainwrite_test": ["brainwrite_test 1", "brainwrite_test 2", "brainwrite_test 3", "brainwrite_test 4", "brainwrite_test 5"]
    }
    current_index = 0

    @pytest.fixture()
    def setup(self):
        driver = webdriver.Chrome()
        driver.get('https://synaps-stg-aab67ad5805a.herokuapp.com/Signin')
        driver.maximize_window()
        driver.implicitly_wait(10)
        yield driver
        driver.close()

    def get_next_text(self, test_type="brainwrite"):
        text = self.texts[test_type][self.current_index]
        self.current_index = (self.current_index + 1) % len(self.texts[test_type])
        return text

    def test_login_sanity_test(self, setup):
        driver = setup
        wait = WebDriverWait(driver, 10)

        self.login(driver, wait)
        self.brainwrite_process(driver, wait)
        self.test_area_interaction(driver, wait)

        driver.quit()

    def login(self, driver, wait):
        driver.find_element(By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[2]/div[1]/div/button').click()
        time.sleep(2)
        driver.find_element(By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[4]/div/input').send_keys("ilangrin@gmail.com")
        driver.find_element(By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[5]/div/input').send_keys("123456")
        checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="default-checkbox"]')))
        checkbox.click()
        login_submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[7]/button')))
        login_submit_button.click()
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "ReactModal__Overlay")))
        button = driver.find_element(By.XPATH, '/html/body/div[3]/div/div/div[1]/button')
        button.click()

    def brainwrite_process(self, driver, wait):
        next_element_xpath = '//*[@id="mobile-modal"]/div/div[2]/div[3]/div[2]/div[2]/p[1]'
        wait.until(EC.visibility_of_element_located((By.XPATH, next_element_xpath)))
        element = driver.find_element(By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[3]/div[2]/div[2]/p[1]')
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        driver.find_element(By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[3]/div[2]/div[2]/div/button').click()
        element_challenge_info = driver.find_element(By.ID, "challenge_info")
        driver.execute_script("arguments[0].click();", element_challenge_info)
        time.sleep(4)
        driver.find_element(By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[7]/div/div/button').click()
        element_brainwrite = driver.find_element(By.ID, "brain_write")
        driver.execute_script("arguments[0].click();", element_brainwrite)
        time.sleep(4)

        for _ in range(5):
            driver.find_element(By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[4]/div/div/button').click()
            textarea = driver.find_element(By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[4]/div[3]/textarea')
            next_text = self.get_next_text()
            textarea.clear()
            textarea.send_keys(next_text)
            link = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id="mobile-modal"]/div/div[2]/div[4]/div[4]/div/button")))
            link.click()

    #def test_area_interaction(self, driver, wait):
        driver.find_element(By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[2]/div[2]').click()
        textarea_test = driver.find_element(By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[1]/div[2')
