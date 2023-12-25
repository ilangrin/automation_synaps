from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoAlertPresentException
import time
import pytest


class TestLoginSanity:

    counter1, counter2, name_index = 1, 1, 0
    name_list = ["brain_write", "bad_idea", "melioration", "perspective", "hobbies", "biomimicry", "sit_minus", "trends"]

    def get_next_name():
        global counter1, counter2, name_index

        # יצירת השם הבא
        name = f"{test}_{name_list[name_index]}_{counter1}_{counter2}"

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
        driver = webdriver.Chrome()
        driver.get( 'https://synaps-dev.herokuapp.com/Signin' )
        driver.maximize_window()
        driver.implicitly_wait( 10 )
        yield driver
        driver.close()

    def get_next_text(self):
        text = self.texts_brainwrite[self.current_index]
        self.current_index = (self.current_index + 1) % len( self.texts_brainwrite )
        return text

    def get_next_text_test(self):
        text = self.texts_brainwrite_test[self.current_index]
        self.current_index = (self.current_index + 1) % len( self.texts_brainwrite_test )
        return text

    def test_login_sanity_test(self, setup):
        driver = setup
        texts_brainwrite = ["Text 1", "Text 2", "Text 3", "Text 4"]

        actions = ActionChains( driver )
        wait = WebDriverWait( driver, 10 )
        wait3 = WebDriverWait( driver, 3 )
        driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[2]/div[1]/div/button' ).click()
        time.sleep( 2 )
        driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[4]/div/input' ).send_keys(
            "ilangrin@gmail.com" )
        driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[5]/div/input' ).send_keys( "123456" )
        checkbox = wait.until( EC.element_to_be_clickable( (By.XPATH, '//*[@id="default-checkbox"]') ) )
        checkbox.click()

        login_submit_button = wait.until(
            EC.element_to_be_clickable( (By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[7]/button') ) )
        login_submit_button.click()
        WebDriverWait( driver, 10 ).until( EC.visibility_of_element_located( (By.CLASS_NAME, "ReactModal__Overlay") ) )
        button = driver.find_element( By.XPATH, '/html/body/div[3]/div/div/div[1]/button' )
        button.click()
        next_element_xpath = '//*[@id="mobile-modal"]/div/div[2]/div[3]/div[2]/div[2]/p[1]'
        wait.until( EC.visibility_of_element_located( (By.XPATH, next_element_xpath) ) )
        element = driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[3]/div[2]/div[2]/p[1]' )
        driver.execute_script( "arguments[0].scrollIntoView(true);", element )
        driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[3]/div[2]/div[2]/div/button' ).click()
        element_challenge_info = driver.find_element( By.ID, "challenge_info" )
        driver.execute_script( "arguments[0].click();", element_challenge_info )
        time.sleep( 4 )
        driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[7]/div/div/button' ).click()
        element_brainwrite = driver.find_element( By.ID, "brain_write" )
        driver.execute_script( "arguments[0].click();", element_brainwrite )
        time.sleep( 4 )

        for _ in range( 5 ):  # Replace number_of_repetitions with the number of times you want to repeat
            # Click the button
            driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[4]/div/div/button' ).click()

            # Interact with the textarea
            textarea = driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[4]/textarea' )
            next_text = self.get_next_text()
            textarea.clear()
            textarea.send_keys( next_text )

            link = wait.until( EC.element_to_be_clickable( (By.XPATH, "//*[contains(text(), 'הוסף רעיון')]") ) )
            link.click()

        driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[2]/div[2]' ).click()
        textarea_test = driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[1]/div[2]/textarea' )
        next_text_test = self.get_next_text_test()
        textarea_test.clear()
        textarea_test.send_keys( next_text_test )

        driver.quit()
