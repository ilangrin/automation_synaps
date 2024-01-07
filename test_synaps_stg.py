import time

import pytest
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
counter1, counter2, name_index = 1, 1, 0
class TestLoginSanity:
    def find_and_interact(self, driver: object, wait: object, button_xpath: object, textarea_xpath: object = None,
                          next_text: object = None) -> object:
        """
        Helper method to find and click a button, and optionally interact with a textarea.
        :type wait: object
        :rtype:
        """
        button = wait.until( EC.element_to_be_clickable( (By.XPATH, button_xpath) ) )
        button.click()

        if textarea_xpath and next_text is not None:
            try:
                textarea = wait.until( EC.element_to_be_clickable((By.XPATH, textarea_xpath) ) )
                textarea.clear()
                textarea.send_keys( next_text )

            except StaleElementReferenceException:
                textarea = driver.find_element( By.XPATH, textarea_xpath )
                textarea.clear()
                textarea.send_keys( next_text )

    def get_next_name(self):
        global counter1, counter2, name_index
        name_list = ["brain_write", "bad_idea", "melioration", "perspective", "hobbies", "biomimicry", "sit_minus",
                     "trends"]

        # Create the next name
        name = f"test_{name_list[name_index]}_{counter1}_{counter2}"

        # Update counters
        counter2 += 1
        if counter2 > 5:
            counter2 = 1
            name_index += 1
            if name_index >= len( name_list ):
                name_index = 0
                counter1 += 1

        return name

    @pytest.fixture()
    def setup(self):
        chrome_options = Options()
        chrome_options.add_argument( "--auto-open-devtools-for-tabs" )
        driver = webdriver.Chrome( options=chrome_options )
        driver.get( 'https://synaps-stg-aab67ad5805a.herokuapp.com/Signin' )
        driver.maximize_window()
        driver.implicitly_wait( 10 )
        yield driver

        driver.close()

    def test_login_sanity_test(self, setup):
        driver = setup

        actions = ActionChains( driver )
        wait = WebDriverWait( driver, 10 )
        wait3 = WebDriverWait( driver, 3 )
        self.find_and_interact( driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[2]/div[1]/div/button' )
        driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[4]/div/input' ).send_keys("test11@synaps.co")
        driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[5]/div/input' ).send_keys( "123456" )
        self.find_and_interact( driver, wait, '//*[@id="default-checkbox"]' )

        # תחילת תהליך בדיקה

        # כפתור לוג אין
        self.find_and_interact( driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[7]/button' )
        #   בחירת אווטר
        try:

            selection_page_element = wait.until(
                EC.visibility_of_element_located( (By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[2]/img[8]') ) )
            selection_page_element.click()
        except TimeoutException:

            print( "avatar page not found, continuing with the script." )

        # תנאי שימוש
        self.find_and_interact( driver, wait, '/html/body/div[3]/div/div/div[1]/button' )
        # בחירת אתגר
        self.find_and_interact( driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[3]/div[1]/div[2]/div/button' )

        element_challenge_info = driver.find_element( By.ID, "challenge_info" )
        driver.execute_script( "arguments[0].click();", element_challenge_info )
        time.sleep( 4 )
        self.find_and_interact( driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[7]/div/div/button' )
        element_brainwrite = driver.find_element( By.ID, "brain_write" )
        driver.execute_script( "arguments[0].click();", element_brainwrite )
        self.find_and_interact( driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[4]/div/div/button' )


        for _ in range( 5 ):
            next_text = self.get_next_name()
            driver.find_element(By.XPATH,'//*[@id="mobile-modal"]/div/div[2]/div[4]/textarea').send_keys(next_text)
            driver.find_element(By.XPATH,'//*[@id="mobile-modal"]/div/div[2]/div[4]/div/div/button').click()
            time.sleep( 2 )
            #self.find_and_interact( driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[2]/div/div[2]/button')



        # בחירת רעיון טוב
        driver.find_element(By.XPATH,'//*[@id="mobile-modal"]/div/div[2]/div[2]/div[2]').click()
        source_element = driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/p[2]' )
        copied_text = source_element.text
        target_text_area = driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[1]/div[2]/textarea' )
        target_text_area.clear()
        target_text_area.send_keys( copied_text )
        self.find_and_interact( driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[2]/div/div[2]/button' )
        self.find_and_interact( driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[3]/div[2]' )
        time.sleep( 5 )

        driver.quit()
