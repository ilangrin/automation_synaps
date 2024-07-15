import time
import pytest
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

class TestLoginSanity:
    counter = 0
    user_list = [
        ("test01@synaps.co", "123456"), ("test02@synaps.co", "123456"),
        ("test03@synaps.co", "123456"), ("test04@synaps.co", "123456"),
        ("test05@synaps.co", "123456"), ("test06@synaps.co", "123456"),
        ("test07@synaps.co", "123456"), ("test08@synaps.co", "123456"),
        ("test09@synaps.co", "123456"), ("test10@synaps.co", "123456")
    ]

    def find_and_interact(self, driver, wait, element_locator, action="click", text=None, timeout=10):
        try:
            element = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(element_locator))
            if action == "click":
                element.click()
            elif action == "send_keys" and text is not None:
                element.clear()
                element.send_keys(text)
        except (StaleElementReferenceException, TimeoutException, NoSuchElementException) as e:
            print(f"Element with locator {element_locator} not found: {e}")
            self.print_page_source(driver)
            raise

    def print_page_source(self, driver):
        with open("page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("Page source saved to page_source.html")

    def get_next_name(self):
        name_list = ["brain_write", "bad_idea", "melioration", "perspective", "hobbies", "biomimicry", "sit_minus", "trends"]
        index = (TestLoginSanity.counter // 5) % len(name_list)
        counter1 = TestLoginSanity.counter // (5 * len(name_list)) + 1
        counter2 = TestLoginSanity.counter % 5 + 1
        return f"test_{name_list[index]}_{counter1}_{counter2}"

    @pytest.fixture()
    def setup(self):
        chrome_options = Options()
        driver = webdriver.Chrome(options=chrome_options)
        driver.get('https://synaps-stg-aab67ad5805a.herokuapp.com/Signin')
        driver.maximize_window()
        driver.implicitly_wait(10)
        yield driver
        driver.quit()

    @pytest.mark.parametrize("username,password", user_list)
    def test_login_sanity_test(self, setup, username, password):
        TestLoginSanity.counter += 1
        driver = setup
        wait = WebDriverWait(driver, 10)

        self.find_and_interact(driver, wait, (By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[2]/div[1]/div/button'))
        self.find_and_interact(driver, wait, (By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[4]/div/input'), action="send_keys", text=username)
        self.find_and_interact(driver, wait, (By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[5]/div/input'), action="send_keys", text=password)
        self.find_and_interact(driver, wait, (By.XPATH, '//*[@id="default-checkbox"]'))

        self.find_and_interact(driver, wait, (By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[7]/button'))
        self.find_and_interact(driver, wait, (By.XPATH, '/html/body/div[3]/div/div/div[1]/button'))
        self.find_and_interact(driver, wait, (By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[3]/div[1]/div[2]/div/button'))

        element_challenge_info = driver.find_element(By.ID, "challenge_info")
        driver.execute_script("arguments[0].click();", element_challenge_info)
        time.sleep(4)

        self.find_and_interact(driver, wait, (By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[7]/div/div/button'))

        for stage_id in ["brain_write", "bad_idea", "melioration", "perspective", "hobbies", "biomimicry", "sit_minus", "trends"]:
            element = driver.find_element(By.ID, stage_id)
            driver.execute_script("arguments[0].click();", element)
            self.perform_stage_actions(driver, wait)

    def perform_stage_actions(self, driver, wait):
        for _ in range(5):
            next_text = self.get_next_name()
            self.find_and_interact(driver, wait, (By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[4]/div[3]/textarea'), action="send_keys", text=next_text, timeout=20)
            self.find_and_interact(driver, wait, (By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[4]/div/div/button'))
            time.sleep(2)

        self.select_best_idea(driver, wait)

    def select_best_idea(self, driver, wait):
        self.find_and_interact(driver, wait, (By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[2]/div[3]'))
        source_element = driver.find_element(By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/p[2]')
        copied_text = source_element.text
        self.find_and_interact(driver, wait, (By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[1]/div[2]/div/textarea'), action="send_keys", text=f"{copied_text}_{TestLoginSanity.counter}")
        time.sleep(2)
        self.find_and_interact(driver, wait, (By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[2]/div/div[2]/button'))
        self.find_and_interact(driver, wait, (By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[3]/div[2]'))

        modal = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.CLASS_NAME, "ReactModal__Overlay")))
        button_inside_modal = modal.find_element(By.XPATH, '/html/body/div[3]/div/div/div[2]/div/button')
        button_inside_modal.click()
