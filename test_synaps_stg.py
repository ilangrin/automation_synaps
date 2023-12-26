from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import TimeoutException
import time
import pytest


class TestLoginSanity:



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
        driver = webdriver.Chrome()
        driver.get( 'https://synaps-stg-aab67ad5805a.herokuapp.com/Signin')
        driver.maximize_window()
        driver.implicitly_wait( 10 )
        yield driver
        driver.close()



    def test_login_sanity_test(self, setup):
        driver = setup


        actions = ActionChains( driver )
        wait = WebDriverWait( driver, 5 )
        wait3 = WebDriverWait( driver, 3 )
        driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[2]/div[1]/div/button' ).click()
        time.sleep( 2 )
        driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[4]/div/input' ).send_keys("test08@synaps.co" )
        driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[5]/div/input' ).send_keys( "123456" )
        checkbox = wait.until( EC.element_to_be_clickable( (By.XPATH, '//*[@id="default-checkbox"]') ) )
        checkbox.click()
#תחילת תהליך בדיקה


        # Click the login button
        login_submit_button = wait.until(EC.element_to_be_clickable( (By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[7]/button') ) )
        login_submit_button.click()

        try:

            selection_page_element = wait.until(EC.visibility_of_element_located( (By.XPATH, '/html/body/div[3]/div/div/div[1]/button') ) )
            selection_page_element.click()
        except TimeoutException:

            print( "avatar page not found, continuing with the script." )

        try:
            WebDriverWait( driver, 5 ).until(EC.visibility_of_element_located( (By.CLASS_NAME, "ReactModal__Overlay") ) )

        except TimeoutException:
            print( "The ReactModal__Overlay element did not appear within 5 seconds." )

        button = driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[3]/div[2]/div[2]/div/button' )
        button.click()
        next_element_xpath = '//*[@id="mobile-modal"]/div/div[2]/div[3]/div[2]/div[2]/p[1]'
        wait.until( EC.visibility_of_element_located( (By.XPATH, next_element_xpath) ) )
        element = driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[3]/div[2]/div[2]/p[1]' )
        driver.execute_script( "arguments[0].scrollIntoView(true);", element )
        #בחירת אתגר
        driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[3]/div[2]/div[2]/div/button' ).click()
        element_challenge_info = driver.find_element( By.ID, "challenge_info" )
        driver.execute_script( "arguments[0].click();", element_challenge_info )
        time.sleep( 4 )
        driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[7]/div/div/button' ).click()
        element_brainwrite = driver.find_element( By.ID, "brain_write" )
        driver.execute_script( "arguments[0].click();", element_brainwrite )
        time.sleep( 4 )

        for _ in range( 5 ):  # Replace with the number of times you want to repeat
            # Click the button
            button = wait.until( EC.element_to_be_clickable( (By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[4]/div/div/button') ) )
            button.click()
            # Interact with the textarea
            try:
                textarea = wait.until(
                    EC.element_to_be_clickable( (By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[4]/textarea') ) )
                next_text = self.get_next_name()
                textarea.clear()
                textarea.send_keys( next_text )
            except StaleElementReferenceException:
                # Re-find the textarea element
                textarea = driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[4]/textarea' )
                textarea.clear()
                textarea.send_keys( next_text )


            link = wait.until( EC.element_to_be_clickable( (By.XPATH, "//*[contains(text(), 'הוסף רעיון')]") ) )
            link.click()
#בחירת רעיון טוב
        bestIdea = driver.find_element(By.XPATH,'//*[@id="mobile-modal"]/div/div[2]/div[2]/div[2]')
        bestIdea.click()
        Justify = driver.find_element(By.XPATH,'//*[@id="mobile-modal"]/div/div[2]/div[1]/div[2]/textarea')
        Justify.send_keys("test")

        time.sleep(10)






        driver.quit()
