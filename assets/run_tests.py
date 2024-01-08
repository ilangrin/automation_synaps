from selenium import webdriver
from test_synaps_stg.py import TestLoginSanity, user_list

if __name__ == "__main__":
    for username, password in user_list:
        # Setup Selenium WebDriver
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--auto-open-devtools-for-tabs")
        driver = webdriver.Chrome(options=chrome_options)
        driver.get('https://synaps-stg-aab67ad5805a.herokuapp.com/Signin')
        driver.maximize_window()
        driver.implicitly_wait(2)

        # Create an instance of the test class
        test_instance = TestLoginSanity()

        # Call the test method with setup and user credentials
        test_instance.test_login_sanity_test(driver, username, password)

        # Close the browser after the test is done
        driver.quit()