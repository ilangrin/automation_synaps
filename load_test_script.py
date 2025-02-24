import time
import threading
import random  # For random user selection
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

# Updated user list with emails from locust_user_0@synaps.co to locust_user_500@synaps.co
user_list = [(f"locust_user_{i}@synaps.co", "123456") for i in range( 500 )]


class TestLoginSanity:
    successful_tests = 0  # Counter for successful tests
    failed_tests = 0  # Counter for failed tests
    lock = threading.Lock()  # To prevent race conditions

    def find_and_interact(self, driver, wait, button_xpath, textarea_xpath=None, next_text=None):
        try:
            button = wait.until( EC.element_to_be_clickable( (By.XPATH, button_xpath) ) )
            button.click()
            if textarea_xpath and next_text is not None:
                textarea = wait.until( EC.element_to_be_clickable( (By.XPATH, textarea_xpath) ) )
                textarea.clear()
                textarea.send_keys( next_text )
        except (StaleElementReferenceException, NoSuchElementException, TimeoutException) as e:
            print( f"Element interaction failed at {button_xpath or textarea_xpath}: {e}" )

    def login_user(self, username, password):
        chrome_options = Options()
        chrome_options.add_argument( "--new-window" )  # Each user starts in a new window
        driver = webdriver.Chrome( options=chrome_options )

        try:
            driver.get( 'https://synapsc.herokuapp.com' )
            driver.maximize_window()
            wait = WebDriverWait( driver, 15 )  # Increased wait time to allow for page loading

            # Login steps
            self.find_and_interact( driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[2]/div[1]/div/button' )
            driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[4]/div/input' ).send_keys( username )
            driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[5]/div/input' ).send_keys( password )
            self.find_and_interact( driver, wait, '//*[@id="default-checkbox"]' )
            self.find_and_interact( driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[7]/button' )  # Login button
            self.find_and_interact( driver, wait, '/html/body/div[3]/div/div/div[1]/button' )
            self.find_and_interact( driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[2]/img[10]' )

            time.sleep( 5 )

            # Attempt to interact with "challenge_info" after login
            try:
                element_challenge_info = wait.until( EC.visibility_of_element_located( (By.ID, "challenge_info") ) )
                driver.execute_script( "arguments[0].click();", element_challenge_info )

                # Increment successful tests
                with self.lock:
                    TestLoginSanity.successful_tests += 1

            except TimeoutException as e:
                print( f"Failed to find 'challenge_info' for {username}: {e}" )
                # Increment failed tests
                with self.lock:
                    TestLoginSanity.failed_tests += 1

        except Exception as e:
            print( f"Error during login for {username}: {e}" )
            # Increment failed tests
            with self.lock:
                TestLoginSanity.failed_tests += 1

        finally:
            # Ensure driver quits, closing the browser instance
            driver.quit()


def run_user_test(delay):
    """Run the test for a random user after a specified delay."""
    time.sleep( delay )
    test = TestLoginSanity()
    random_user = random.choice( user_list )  # Select a random user
    test.login_user( *random_user )


# Launch each user test in a new thread with a 2-second delay
threads = []
num_threads = 500  # Number of concurrent threads
for index in range( num_threads ):
    delay = index * 2  # Each thread starts with a 2-second delay from the previous one
    thread = threading.Thread( target=run_user_test, args=(delay,) )
    threads.append( thread )
    thread.start()

# Wait for all threads to complete
for thread in threads:
    thread.join()

# Print the final report
print( "\nTest Execution Summary:" )
print( f"Total Tests Run: {num_threads}" )
print( f"Successful Tests: {TestLoginSanity.successful_tests}" )
print( f"Failed Tests: {TestLoginSanity.failed_tests}" )
