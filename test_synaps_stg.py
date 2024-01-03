from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options

import time
import pytest


class TestLoginSanity:
    def find_and_interact(self, driver, wait, button_xpath, textarea_xpath=None, next_text=None):
        """
        Helper method to find and click a button, and optionally interact with a textarea.
        """
        button = wait.until( EC.element_to_be_clickable( (By.XPATH, button_xpath) ) )
        button.click()

        if textarea_xpath and next_text is not None:
            try:
                textarea = wait.until( EC.element_to_be_clickable( (By.XPATH, textarea_xpath) ) )
                textarea.clear()
                textarea.send_keys( next_text )
            except StaleElementReferenceException:
                textarea = driver.find_element( By.XPATH, textarea_xpath )
                textarea.clear()
                textarea.send_keys( next_text )

    def get_next_name(self):
        global counter1, counter2, name_index
        counter1, counter2, name_index = 1, 1, 0
        name_list = ["brain_write", "bad_idea", "melioration", "perspective", "hobbies", "biomimicry", "sit_minus",
                     "trends"]
        # יצירת השם הבא
        name = f"test_{name_list[name_index]}_{counter1}_{counter2}"

        # עדכון המונים
        counter2 += 1
        if counter2 > 5:
            counter2 = 1
            counter1 += 1
            if counter1 > 5:
                counter1 = 1
                name_index += 1
                if name_index >= len( name_list ):
                    name_index = 0

        return name

    @pytest.fixture()
    def setup(self):
        chrome_options = Options()
        chrome_options.add_argument("--auto-open-devtools-for-tabs")  # This argument opens DevTools.
        driver = webdriver.Chrome(options=chrome_options)
        driver.get('https://synaps-stg-aab67ad5805a.herokuapp.com/Signin')
        driver.maximize_window()
        driver.implicitly_wait(10)
        yield driver
      #driver.close()

    def test_login_sanity_test(self, setup):
        driver = setup

        actions = ActionChains( driver )
        wait = WebDriverWait( driver, 5 )
        wait3 = WebDriverWait( driver, 3 )
        self.find_and_interact( driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[2]/div[1]/div/button' )
        driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[4]/div/input' ).send_keys(
            "test08@synaps.co" )
        driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[5]/div/input' ).send_keys( "123456" )
        self.find_and_interact( driver, wait, '//*[@id="default-checkbox"]' )

        # תחילת תהליך בדיקה

        # Click the login button
        self.find_and_interact( driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[7]/button' )

        self.find_and_interact( driver, wait, '/html/body/div[3]/div/div/div[1]/button')

        self.find_and_interact( driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[3]/div[2]/div[2]/div/button' )
        self.find_and_interact( driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[3]/div[2]/div[2]/p[1]' )
        element = driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[3]/div[2]/div[2]/p[1]' )
        driver.execute_script( "arguments[0].scrollIntoView(true);", element )

        # בחירת אתגר

        self.find_and_interact( driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[3]/div[2]/div[2]/div/button' )
        element_challenge_info = driver.find_element( By.ID, "challenge_info" )
        driver.execute_script( "arguments[0].click();", element_challenge_info )
        time.sleep( 4 )
        self.find_and_interact( driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[7]/div/div/button' )
        element_brainwrite = driver.find_element( By.ID, "brain_write" )
        driver.execute_script( "arguments[0].click();", element_brainwrite )
        time.sleep( 4 )

        for _ in range( 5 ):
            next_text = self.get_next_name()
            self.find_and_interact(
                driver, wait,
                '//*[@id="mobile-modal"]/div/div[2]/div[4]/div/div/button',
                '//*[@id="mobile-modal"]/div/div[2]/div[4]/textarea',
                next_text )

            self.find_and_interact( driver, wait, "//*[contains(text(), 'הוסף רעיון')]" )


        # בחירת רעיון טוב
        good_next_text = self.get_next_name + "good"()
        self.find_and_interact( driver, wait, '' )
        self.find_and_interact(
            driver, wait,
            '//*[@id="mobile-modal"]/div/div[2]/div[2]/div[2]',
            '//*[@id="mobile-modal"]/div/div[2]/div[1]/div[2]/textarea', good_next_text )



        time.sleep( 10 )

        #driver.quit()
