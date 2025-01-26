import time
import pytest
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from state_manager import get_next_name

counter1, counter2, name_index = 1, 1, 0

# Define user_list outside the class
user_list = [
    ("test01@synaps.co", "123456"), ("test02@synaps.co", "123456"), ("test03@synaps.co", "123456"),
    ("test04@synaps.co", "123456"), ("test05@synaps.co", "123456"), ("test06@synaps.co", "123456"),
    ("test07@synaps.co", "123456"), ("test08@synaps.co", "123456"), ("test09@synaps.co", "123456"),
    ("test10@synaps.co", "123456")
]

class TestLoginSanity:
    counter = 0

    def find_and_interact(self, driver: object, wait: object, button_xpath: object, textarea_xpath: object = None,
                          next_text: object = None) -> object:
        button = wait.until(EC.element_to_be_clickable((By.XPATH, button_xpath)))
        button.click()

        if textarea_xpath and next_text is not None:
            try:
                textarea = wait.until(EC.element_to_be_clickable((By.XPATH, textarea_xpath)))
                textarea.clear()
                textarea.send_keys(next_text)
            except StaleElementReferenceException:
                textarea = driver.find_element(By.XPATH, textarea_xpath)
                textarea.clear()
                textarea.send_keys(next_text)

    def get_next_name(self):
        global counter1, counter2, name_index
        name_list = ["brain_write", "bad_idea", "Combine", "perspective", "hobbies", "Bio Mimic", "Less is More",
                     "trends"]

        name = f"test_{name_list[name_index]}_{counter1}_{counter2}"

        counter2 += 1
        if counter2 > 5:
            counter2 = 1
            name_index += 1
            if name_index >= len(name_list):
                name_index = 0
                counter1 += 1

        return name

    @pytest.fixture()
    def setup(self):
        chrome_options = Options()
        chrome_options.add_argument("--new-window")
        driver = webdriver.Chrome(options=chrome_options)
        driver.get('https://synaps-stg-aab67ad5805a.herokuapp.com/Signin')
        driver.maximize_window()
        driver.implicitly_wait(12)
        yield driver

    @pytest.mark.parametrize("username, password", user_list)
    def test_login_sanity_test(self, setup, username, password, element_melioration=None):
        driver = setup

        driver.maximize_window()

        actions = ActionChains(driver)
        wait = WebDriverWait(driver, 10)
        self.find_and_interact( driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[2]/div[1]/div/button')
        driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[4]/div/input').send_keys(username)
        driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[5]/div/input').send_keys(password)

        # תחילת תהליך בדיקה

            # כפתור לוג אין
        self.find_and_interact( driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[6]/button')

        # תנאי שימוש
        self.find_and_interact( driver, wait, '/html/body/div[3]/div/div/div[1]/button' )
        # בחירת אתגר
        self.find_and_interact( driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[3]/div[1]/div[2]/div/button' )
        element_challenge_info = driver.find_element( By.ID, "challenge_info" )
        driver.execute_script( "arguments[0].click();", element_challenge_info )
        time.sleep(3)
        self.find_and_interact( driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[7]/div/div/button' )

        # שלב 1
        time.sleep(1)
        element_brainwrite = driver.find_element( By.ID, "brain_write" )
        driver.execute_script( "arguments[0].click();", element_brainwrite )
        self.find_and_interact( driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[4]/div/div/button' )


        for _ in range( 3):
            next_text = get_next_name()
            time.sleep(2)
            driver.find_element(By.XPATH,"//*[@id=\"mobile-modal\"]/div/div[2]/div[4]/div[3]/textarea").send_keys(next_text)
            driver.find_element(By.XPATH,'//*[@id="mobile-modal"]/div/div[2]/div[4]/div/div/button').click()
            time.sleep(2)


            # בחירת רעיון טוב
        driver.find_element(By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[2]/div[1]').click()
        source_element = driver.find_element(By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/p[2]')
        copied_text = source_element.text
        target_text_area = driver.find_element(By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[1]/div[2]/div/textarea')
        target_text_area.clear()
        target_text_area.send_keys(f"{copied_text}_{TestLoginSanity.counter}")
        time.sleep(2)
            # אישור
        self.find_and_interact(driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[2]/div/div[2]/button')
        self.find_and_interact(driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[3]/div[2]')

            #פופאפ
        try:
            modal = WebDriverWait( driver, 5 ).until(
                EC.visibility_of_element_located( (By.CLASS_NAME, "ReactModal__Overlay") ) )
            button_inside_modal = modal.find_element( By.XPATH, '/html/body/div[3]/div/div/div[2]/div/button' )
            button_inside_modal.click()
        except TimeoutException:
            print( "Modal popup did not appear." )



        # שלב 2
        time.sleep(2)
        element_bad_idea = driver.find_element( By.ID, "bad_idea")
        driver.execute_script( "arguments[0].click();", element_bad_idea)
        self.find_and_interact( driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[4]/div/div/button')

        for _ in range(3):
            next_text = get_next_name()
            driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[4]/div[3]/textarea').send_keys(next_text)
            driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[4]/div[4]/div/button' ).click()
            time.sleep(2)

            #  בחירת רעיון טוב
        driver.find_element(By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[2]/div[2]').click()
        source_element = driver.find_element(By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/p[2]')
        copied_text = source_element.text
        target_text_area = driver.find_element(By.XPATH,'//*[@id="mobile-modal"]/div/div[2]/div[1]/div[2]/div/textarea')
        target_text_area.clear()
        target_text_area.send_keys( f"{copied_text}_{TestLoginSanity.counter}" )
        time.sleep(2)
        # אישור
        self.find_and_interact(driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[2]/div/div[2]/button')
        self.find_and_interact(driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[3]/div[2]/div/p[2]')
        # פופאפ

        try:
            modal = WebDriverWait( driver, 5 ).until(
                EC.visibility_of_element_located( (By.CLASS_NAME, "ReactModal__Overlay") ) )
            button_inside_modal = modal.find_element( By.XPATH, '/html/body/div[3]/div/div/div[2]/div/button' )
            button_inside_modal.click()
        except TimeoutException:
            print( "Modal popup did not appear." )


        #שלב 3
        time.sleep(2)
        element_melioration = driver.find_element( By.ID, "melioration")
        driver.execute_script( "arguments[0].click();", element_melioration)
        self.find_and_interact( driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[4]/div/div/button')

        for _ in range(3):
            next_text = get_next_name()
            driver.find_element(By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[4]/div[3]/textarea').send_keys(next_text)
            driver.find_element(By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[4]/div[4]/div/button').click()
            time.sleep(2)

            # בחירת רעיון טוב
        driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[2]/div[2]').click()
        source_element = driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/p[2]')
        copied_text = source_element.text
        target_text_area = driver.find_element( By.XPATH,'//*[@id="mobile-modal"]/div/div[2]/div[1]/div[2]/div/textarea')
        target_text_area.clear()
        target_text_area.send_keys( f"{copied_text}_{TestLoginSanity.counter}" )
        time.sleep(2)
        # אישור
        self.find_and_interact( driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[2]/div/div[2]/button')
        self.find_and_interact( driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[3]/div[1]/div/p[2]')
        # פופאפ

        try:
            modal = WebDriverWait( driver, 5 ).until(
                EC.visibility_of_element_located( (By.CLASS_NAME, "ReactModal__Overlay") ) )
            button_inside_modal = modal.find_element( By.XPATH, '/html/body/div[3]/div/div/div[2]/div/button' )
            button_inside_modal.click()
        except TimeoutException:
            print( "Modal popup did not appear." )

        #שלב 4
        time.sleep(2)
        element_perspective = driver.find_element( By.ID, "perspective" )
        driver.execute_script("arguments[0].click();", element_perspective)
        self.find_and_interact(driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[4]/div/div/button')

        for _ in range(3):
            next_text = get_next_name()
            driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[4]/div[3]/textarea').send_keys(next_text)
            driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[4]/div[4]/div/button').click()
            time.sleep(2)

            #  בחירת רעיון טוב
        driver.find_element(By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[2]/div[3]').click()
        source_element = driver.find_element(By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/p[2]')
        copied_text = source_element.text
        target_text_area = driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[1]/div[2]/div/textarea')
        target_text_area.clear()
        target_text_area.send_keys( f"{copied_text}_{TestLoginSanity.counter}" )
        time.sleep(2)
        # אישור
        self.find_and_interact(driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[2]/div/div[2]/button')
        self.find_and_interact(driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[3]/div[1]')
        # פופאפ

        modal = WebDriverWait( driver, 5 ).until(EC.visibility_of_element_located( (By.CLASS_NAME, "ReactModal__Overlay") ) )
        button_inside_modal = modal.find_element( By.XPATH, '//*[@id="greatWorkClosing"]')
        button_inside_modal.click()

        #שלב 5
        time.sleep(2)
        element_hobbies = driver.find_element( By.ID, "hobbies" )
        driver.execute_script("arguments[0].click();", element_hobbies)
        self.find_and_interact(driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[4]/div/div/button')

        for _ in range(3):
            next_text = get_next_name()
            driver.find_element(By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[4]/div[3]/textarea').send_keys( next_text )
            driver.find_element(By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[4]/div[4]/div/button').click()
            time.sleep(2)

            #  בחירת רעיון טוב
        driver.find_element(By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[2]/div[1]').click()
        source_element = driver.find_element(By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/p[2]')
        copied_text = source_element.text
        target_text_area = driver.find_element(By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[1]/div[2]/div/textarea')
        target_text_area.clear()
        target_text_area.send_keys( f"{copied_text}_{TestLoginSanity.counter}" )
        time.sleep(2)
        # אישור
        self.find_and_interact(driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[2]/div/div[2]/button')
        self.find_and_interact(driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[3]/div[1]')
        # פופאפ

        modal = WebDriverWait( driver, 5 ).until(EC.visibility_of_element_located( (By.CLASS_NAME, "ReactModal__Overlay") ) )
        button_inside_modal = modal.find_element( By.XPATH, '//*[@id="greatWorkClosing"]')
        button_inside_modal.click()

        #שלב 6
        element_biomimicry = driver.find_element( By.ID, "biomimicry")
        driver.execute_script("arguments[0].click();", element_biomimicry)
        time.sleep(2)
        self.find_and_interact(driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[4]/div/div/button')

        for _ in range(3):
            next_text = get_next_name()
            driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[4]/div[3]/textarea').send_keys( next_text )
            driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[4]/div/div/button').click()
            time.sleep(2)

            #  בחירת רעיון טוב
        driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[2]/div[3]' ).click()
        source_element = driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/p[2]' )
        copied_text = source_element.text
        target_text_area = driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[1]/div[2]/div/textarea')
        target_text_area.clear()
        target_text_area.send_keys( f"{copied_text}_{TestLoginSanity.counter}" )
        time.sleep(2)
        # אישור
        self.find_and_interact( driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[2]/div/div[2]/button' )
        self.find_and_interact( driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[3]/div[2]' )
        # פופאפ

        modal = WebDriverWait( driver, 5 ).until(
            EC.visibility_of_element_located( (By.CLASS_NAME, "ReactModal__Overlay") ) )
        button_inside_modal = modal.find_element( By.XPATH, '/html/body/div[3]/div/div/div[2]/div/button' )
        button_inside_modal.click()

        #שלב 7
        time.sleep(2)
        element_sit_minus = driver.find_element( By.ID, "sit_minus" )
        driver.execute_script( "arguments[0].click();", element_sit_minus)
        self.find_and_interact(driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[4]/div/div/button')

        retries = 3
        for attempt in range( retries ):
            try:
                modal = WebDriverWait( driver, 5 ).until(
                    EC.visibility_of_element_located( (By.CLASS_NAME, "ReactModal__Overlay") )
                )
                close_button = modal.find_element( By.XPATH, '//button[@class="close-button"]' )
                close_button.click()
                break
            except StaleElementReferenceException:
                print( f"ניסיון {attempt + 1} לאתר את המודאל נכשל." )
            except TimeoutException:
                print( "המודאל לא הופיע בזמן." )

            time.sleep(1)

            #  בחירת רעיון טוב
        driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[2]/div[1]').click()
        source_element = driver.find_element(By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/p[2]')
        copied_text = source_element.text
        target_text_area = driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[1]/div[2]/div/textarea')
        target_text_area.clear()
        target_text_area.send_keys( f"{copied_text}_{TestLoginSanity.counter}")

        # אישור
        self.find_and_interact(driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[2]/div/div[2]/button')
        self.find_and_interact(driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[3]/div[2]')
        # פופאפ

        modal = WebDriverWait( driver, 5 ).until(EC.visibility_of_element_located( (By.CLASS_NAME, "ReactModal__Overlay") ) )
        button_inside_modal = modal.find_element( By.XPATH, '/html/body/div[3]/div/div/div[2]/div/button')
        button_inside_modal.click()

        # שלב 8
        time.sleep( 3 )
        element_trends = driver.find_element( By.ID, "trends" )
        driver.execute_script( "arguments[0].click();", element_trends)
        self.find_and_interact( driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[4]/div/div/button')

        for _ in range(5):
            next_text = get_next_name()
            driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[4]/div[3]/textarea').send_keys( next_text )
            driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[4]/div/div/button').click()
            time.sleep(1)

            #  בחירת רעיון טוב
        driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[2]/div[3]' ).click()
        source_element = driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/p[2]')
        copied_text = source_element.text
        target_text_area = driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[1]/div[2]/div/textarea')
        target_text_area.clear()
        target_text_area.send_keys( f"{copied_text}_{TestLoginSanity.counter}" )
        time.sleep(2)
        # אישור
        self.find_and_interact( driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[2]/div/div[2]/button' )
        self.find_and_interact( driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[3]/div[2]' )
        # פופאפ

        modal = WebDriverWait( driver, 5).until(EC.visibility_of_element_located( (By.CLASS_NAME, "ReactModal__Overlay") ) )
        button_inside_modal = modal.find_element( By.XPATH, '/html/body/div[3]/div/div/div[2]/div/button' )
        button_inside_modal.click()