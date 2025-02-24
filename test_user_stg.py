import time
import threading
from selenium import webdriver
from selenium.common.exceptions import (
    StaleElementReferenceException,
    TimeoutException,
    NoSuchElementException
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

user_list = [
    ("test01@synaps.co", "123456"), ("test02@synaps.co", "123456"), ("test03@synaps.co", "123456"),
    ("test04@synaps.co", "123456"), ("test05@synaps.co", "123456"), ("test06@synaps.co", "123456"),
    ("test07@synaps.co", "123456"), ("test08@synaps.co", "123456"), ("test09@synaps.co", "123456"),
    ("test10@synaps.co", "123456")
]

class TestLoginSanity:

    def find_and_interact(self, driver, wait, button_xpath, textarea_xpath=None, next_text=None):
        try:
            button = wait.until(EC.element_to_be_clickable((By.XPATH, button_xpath)))
            button.click()
            if textarea_xpath and next_text is not None:
                textarea = wait.until(EC.element_to_be_clickable((By.XPATH, textarea_xpath)))
                textarea.clear()
                textarea.send_keys(next_text)
        except (StaleElementReferenceException, NoSuchElementException, TimeoutException) as e:
            print(f"Element interaction failed at {button_xpath or textarea_xpath}: {e}")

    def login_user(self, username, password):
        chrome_options = Options()
        chrome_options.add_argument("--new-window")  # Each user starts in a new window
        driver = webdriver.Chrome(options=chrome_options)

        try:
            driver.get('https://synaps-stg-aab67ad5805a.herokuapp.com/Signin')
            driver.maximize_window()
            wait = WebDriverWait(driver, 15)  # Increased wait time to allow for page loading

            # Login steps
            self.find_and_interact(driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[2]/div[1]/div/button')
            driver.find_element(By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[4]/div/input').send_keys(username)
            driver.find_element(By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[5]/div/input').send_keys(password)
            self.find_and_interact(driver, wait, '//*[@id="default-checkbox"]')
            self.find_and_interact(driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[7]/button')  # Login button

            # Pause briefly to let asynchronous elements load
            time.sleep(5)

            # Attempt to interact with "challenge_info" after login
            try:
                element_challenge_info = wait.until(EC.visibility_of_element_located((By.ID, "challenge_info")))
                driver.execute_script("arguments[0].click();", element_challenge_info)
            except TimeoutException as e:
                print(f"Failed to find 'challenge_info' for {username}: {e}")

        except Exception as e:
            print(f"Error during login for {username}: {e}")

        finally:
            # Ensure driver quits, closing the browser instance
            driver.quit()


def run_user_test(user, delay):
    """Run the test for a single user after a specified delay."""
    time.sleep(delay)
    test = TestLoginSanity()
    test.login_user(*user)


# Launch each user test in a new thread with a 2-second delay
threads = []
for index, user in enumerate(user_list):
    delay = index * 2  # Each user starts with a 2-second delay from the previous one
    thread = threading.Thread(target=run_user_test, args=(user, delay))
    threads.append(thread)
    thread.start()

# Wait for all threads to complete
for thread in threads:
    thread.join()
