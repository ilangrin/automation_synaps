import time
import pytest
import threading
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from utils import modal_check_thread


DEFAULT_PASSWORD = "123456"

counter1, counter2, name_index = 1, 1, 0  # משתנים גלובליים


class TestLoginSanity:
    counter = 0
    user_list = [(f"test0{i}@synaps.co", DEFAULT_PASSWORD) for i in range( 1, 2 )]

    # הגדרת המשתנה name_index ברמת המחלקה
    name_index = 0

    def find_and_interact(self, driver: object, wait: object, button_xpath: object, textarea_xpath: object = None,
                          next_text: object = None) -> object:
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
        # שימוש במשתנים גלובליים
        global counter1, counter2, name_index
        name_list = ["brain_write", "bad_idea", "melioration", "perspective", "hobbies", "biomimicry", "sit_minus",
                     "trends"]

        # יצירת שם חדש
        name = f"test_{name_list[name_index]}_{counter1}_{counter2}"

        # עדכון המונים
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
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.get('https://synaps-stg-aab67ad5805a.herokuapp.com/Signin')
        self.driver.maximize_window()
        self.driver.implicitly_wait(10)

        # Starting the modal checking thread
        self.modal_thread = threading.Thread(target=modal_check_thread, args=(self.driver,))
        self.modal_thread.daemon = True
        self.modal_thread.start()

        yield self.driver

        # Make sure to close the driver after the test finishes
        self.driver.quit()

    def teardown_method(self, method):
        # Stopping the modal thread safely
        if self.modal_thread.is_alive():
            self.modal_thread.join()

    @pytest.mark.parametrize("username,password", user_list)
    def test_login_sanity_test(self, setup, username, password):
        TestLoginSanity.counter += 1
        driver = setup
        wait = WebDriverWait(driver, 5)

        # Find and interact with elements
        self.find_and_interact(driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[2]/div[1]/div/button')
        driver.find_element(By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[4]/div/input').send_keys(username)
        driver.find_element(By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[5]/div/input').send_keys(password)
        self.find_and_interact(driver, wait, '//*[@id="default-checkbox"]')

        # Login process
        driver.find_element(By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[7]/button').click()

        # Selecting avatar
        try:
            avatar = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[2]/img[8]')))
            avatar.click()
        except TimeoutException:
            print("Avatar page not found, continuing with the script.")

        # Rest of the test...
        modal = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "ReactModal__Overlay")))
        modal_button = modal.find_element(By.XPATH, '//*[@id="cookiesAccept"]')
        modal_button.click()
        # בחירת אתגר
        self.find_and_interact( driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[3]/div[1]/div[2]/div/button' )
        element_challenge_info = driver.find_element( By.ID, "challenge_info" )
        driver.execute_script( "arguments[0].click();", element_challenge_info )
        time.sleep( 4 )
        self.find_and_interact( driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[7]/div/div/button' )

        # שלב 1
        element_brainwrite = driver.find_element( By.ID, "brain_write" )
        driver.execute_script( "arguments[0].click();", element_brainwrite )
        self.find_and_interact( driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[4]/div/div/button' )

        for _ in range( 5 ):
            next_text = self.get_next_name()

            # Try to enter the text and click the button
            try:
                textarea = driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[4]/div[3]/textarea' )
                submit_button = driver.find_element( By.XPATH,
                                                     '//*[@id="mobile-modal"]/div/div[2]/div[4]/div[4]/div/button' )

                textarea.clear()  # Clear the textarea before sending keys
                textarea.send_keys( next_text )
                submit_button.click()
                time.sleep( 1 )

            except NoSuchElementException:
                # If the textarea is not found, skip to the next iteration
                print( "Textarea not found. Skipping to the next iteration." )
                continue

            except WebDriverException as e:
                print( f"First attempt failed. Retrying... Error: {e}" )
                # Retry once more
                try:
                    textarea.clear()
                    textarea.send_keys( next_text )
                    submit_button.click()
                    time.sleep( 1 )

                except WebDriverException as e:
                    print( f"Second attempt also failed. Proceeding to next iteration. Error: {e}" )
                    # Optionally, you can raise an exception here to fail the test or just continue

            # בחירת רעיון טוב
        driver.find_element( By.XPATH,'//*[@id="mobile-modal"]/div/div[2]/div[2]/div[3]/div/p[2]').click()
        source_element = driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/p[2]')
        copied_text = source_element.text
        target_text_area = driver.find_element( By.XPATH,'//*[@id="mobile-modal"]/div/div[2]/div[1]/div[2]/div/textarea')
        target_text_area.clear()
        target_text_area.send_keys( f"{copied_text}_{TestLoginSanity.counter}" )
        time.sleep( 1 )
            # אישור
        self.find_and_interact(driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[2]/div/div[2]/button')
        self.find_and_interact( driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[3]/div[2]')
            #פופאפ


        modal = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "ReactModal__Overlay")))
        button_inside_modal = modal.find_element( By.XPATH, '//*[@id="greatWorkClosing"]' )
        button_inside_modal.click()

        # שלב 2
        element_bad_idea = driver.find_element( By.ID, "bad_idea" )
        driver.execute_script( "arguments[0].click();", element_bad_idea )
        self.find_and_interact( driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[4]/div/div/button' )

        for _ in range( 5 ):
            next_text = self.get_next_name()

            # Try to enter the text and click the button
            try:
                textarea = driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[4]/textarea' )
                submit_button = driver.find_element( By.XPATH,
                                                     '//*[@id="mobile-modal"]/div/div[2]/div[4]/div/div/button' )

                textarea.clear()  # Clear the textarea before sending keys
                textarea.send_keys( next_text )
                submit_button.click()
                time.sleep( 1 )

            except NoSuchElementException:
                # If the textarea is not found, skip to the next iteration
                print( "Textarea not found. Skipping to the next iteration." )
                continue

            except WebDriverException as e:
                print( f"First attempt failed. Retrying... Error: {e}" )
                # Retry once more
                try:
                    textarea.clear()
                    textarea.send_keys( next_text )
                    submit_button.click()
                    time.sleep( 1 )

                except WebDriverException as e:
                    print( f"Second attempt also failed. Proceeding to next iteration. Error: {e}" )
                    # Optionally, you can raise an exception here to fail the test or just continue

            #  בחירת רעיון טוב
        driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[2]/div[3]' ).click()
        source_element = driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/p[2]' )
        copied_text = source_element.text
        target_text_area = driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[1]/div[2]/textarea' )
        target_text_area.clear()
        target_text_area.send_keys( f"{copied_text}_{TestLoginSanity.counter}" )
        time.sleep( 1 )
        # אישור
        self.find_and_interact( driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[2]/div/div[2]/button' )
        self.find_and_interact( driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[3]/div[2]' )
        # פופאפ

        modal = WebDriverWait( driver, 5 ).until(
            EC.visibility_of_element_located( (By.CLASS_NAME, "ReactModal__Overlay") ) )
        button_inside_modal = modal.find_element( By.XPATH, '/html/body/div[3]/div/div/div[2]/div/button' )
        button_inside_modal.click()


        #שלב 3

        element_melioration = driver.find_element( By.ID, "melioration" )
        driver.execute_script( "arguments[0].click();", element_melioration )
        self.find_and_interact( driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[4]/div/div/button' )

        for _ in range( 5 ):
            next_text = self.get_next_name()

            # Try to enter the text and click the button
            try:
                textarea = driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[4]/textarea' )
                submit_button = driver.find_element( By.XPATH,
                                                     '//*[@id="mobile-modal"]/div/div[2]/div[4]/div/div/button' )

                textarea.clear()  # Clear the textarea before sending keys
                textarea.send_keys( next_text )
                submit_button.click()
                time.sleep( 1 )

            except NoSuchElementException:
                # If the textarea is not found, skip to the next iteration
                print( "Textarea not found. Skipping to the next iteration." )
                continue

            except WebDriverException as e:
                print( f"First attempt failed. Retrying... Error: {e}" )
                # Retry once more
                try:
                    textarea.clear()
                    textarea.send_keys( next_text )
                    submit_button.click()
                    time.sleep( 1 )

                except WebDriverException as e:
                    print( f"Second attempt also failed. Proceeding to next iteration. Error: {e}" )
                    # Optionally, you can raise an exception here to fail the test or just continue

            #  בחירת רעיון טוב
        driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[2]/div[3]' ).click()
        source_element = driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/p[2]' )
        copied_text = source_element.text
        target_text_area = driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[1]/div[2]/textarea' )
        target_text_area.clear()
        target_text_area.send_keys( f"{copied_text}_{TestLoginSanity.counter}" )
        time.sleep( 1 )
        # אישור
        self.find_and_interact( driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[2]/div/div[2]/button' )
        self.find_and_interact( driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[3]/div[2]' )
        # פופאפ

        modal = WebDriverWait( driver, 5 ).until(
            EC.visibility_of_element_located( (By.CLASS_NAME, "ReactModal__Overlay") ) )
        button_inside_modal = modal.find_element( By.XPATH, '/html/body/div[3]/div/div/div[2]/div/button' )
        button_inside_modal.click()


        #שלב 4

        element_perspective = driver.find_element( By.ID, "perspective" )
        driver.execute_script( "arguments[0].click();", element_perspective)
        self.find_and_interact( driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[4]/div/div/button' )

        for _ in range( 5 ):
            next_text = self.get_next_name()

            # Try to enter the text and click the button
            try:
                textarea = driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[4]/textarea' )
                submit_button = driver.find_element( By.XPATH,
                                                     '//*[@id="mobile-modal"]/div/div[2]/div[4]/div/div/button' )

                textarea.clear()  # Clear the textarea before sending keys
                textarea.send_keys( next_text )
                submit_button.click()
                time.sleep( 1 )

            except NoSuchElementException:
                # If the textarea is not found, skip to the next iteration
                print( "Textarea not found. Skipping to the next iteration." )
                continue

            except WebDriverException as e:
                print( f"First attempt failed. Retrying... Error: {e}" )
                # Retry once more
                try:
                    textarea.clear()
                    textarea.send_keys( next_text )
                    submit_button.click()
                    time.sleep( 1 )

                except WebDriverException as e:
                    print( f"Second attempt also failed. Proceeding to next iteration. Error: {e}" )
                    # Optionally, you can raise an exception here to fail the test or just continue

            #  בחירת רעיון טוב
        driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[2]/div[3]' ).click()
        source_element = driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/p[2]' )
        copied_text = source_element.text
        target_text_area = driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[1]/div[2]/textarea' )
        target_text_area.clear()
        target_text_area.send_keys( f"{copied_text}_{TestLoginSanity.counter}" )
        time.sleep( 1 )
        # אישור
        self.find_and_interact( driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[2]/div/div[2]/button' )
        self.find_and_interact( driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[3]/div[2]' )
        # פופאפ

        modal = WebDriverWait( driver, 5 ).until(
            EC.visibility_of_element_located( (By.CLASS_NAME, "ReactModal__Overlay") ) )
        button_inside_modal = modal.find_element( By.XPATH, '/html/body/div[3]/div/div/div[2]/div/button' )
        button_inside_modal.click()

        #שלב 5

        element_hobbies = driver.find_element( By.ID, "hobbies" )
        driver.execute_script( "arguments[0].click();", element_hobbies)
        self.find_and_interact( driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[4]/div/div/button' )

        for _ in range( 5 ):
            next_text = self.get_next_name()

            # Try to enter the text and click the button
            try:
                textarea = driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[4]/textarea' )
                submit_button = driver.find_element( By.XPATH,
                                                     '//*[@id="mobile-modal"]/div/div[2]/div[4]/div/div/button' )

                textarea.clear()  # Clear the textarea before sending keys
                textarea.send_keys( next_text )
                submit_button.click()
                time.sleep( 1 )

            except NoSuchElementException:
                # If the textarea is not found, skip to the next iteration
                print( "Textarea not found. Skipping to the next iteration." )
                continue

            except WebDriverException as e:
                print( f"First attempt failed. Retrying... Error: {e}" )
                # Retry once more
                try:
                    textarea.clear()
                    textarea.send_keys( next_text )
                    submit_button.click()
                    time.sleep( 1 )

                except WebDriverException as e:
                    print( f"Second attempt also failed. Proceeding to next iteration. Error: {e}" )
                    # Optionally, you can raise an exception here to fail the test or just continue

            #  בחירת רעיון טוב
        driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[2]/div[3]' ).click()
        source_element = driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/p[2]' )
        copied_text = source_element.text
        target_text_area = driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[1]/div[2]/textarea' )
        target_text_area.clear()
        target_text_area.send_keys( f"{copied_text}_{TestLoginSanity.counter}" )
        time.sleep( 1 )
        # אישור
        self.find_and_interact( driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[2]/div/div[2]/button' )
        self.find_and_interact( driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[3]/div[2]' )
        # פופאפ

        modal = WebDriverWait( driver, 5 ).until(
            EC.visibility_of_element_located( (By.CLASS_NAME, "ReactModal__Overlay") ) )
        button_inside_modal = modal.find_element( By.XPATH, '/html/body/div[3]/div/div/div[2]/div/button' )
        button_inside_modal.click()

        #שלב 6

        element_biomimicry = driver.find_element( By.ID, "biomimicry" )
        driver.execute_script( "arguments[0].click();", element_biomimicry)
        self.find_and_interact( driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[4]/div/div/button' )

        for _ in range( 5 ):
            next_text = self.get_next_name()

            # Try to enter the text and click the button
            try:
                textarea = driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[4]/textarea' )
                submit_button = driver.find_element( By.XPATH,
                                                     '//*[@id="mobile-modal"]/div/div[2]/div[4]/div/div/button' )

                textarea.clear()  # Clear the textarea before sending keys
                textarea.send_keys( next_text )
                submit_button.click()
                time.sleep( 1 )

            except NoSuchElementException:
                # If the textarea is not found, skip to the next iteration
                print( "Textarea not found. Skipping to the next iteration." )
                continue

            except WebDriverException as e:
                print( f"First attempt failed. Retrying... Error: {e}" )
                # Retry once more
                try:
                    textarea.clear()
                    textarea.send_keys( next_text )
                    submit_button.click()
                    time.sleep( 1 )

                except WebDriverException as e:
                    print( f"Second attempt also failed. Proceeding to next iteration. Error: {e}" )
                    # Optionally, you can raise an exception here to fail the test or just continue
            #  בחירת רעיון טוב
        driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[2]/div[3]' ).click()
        source_element = driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/p[2]' )
        copied_text = source_element.text
        target_text_area = driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[1]/div[2]/textarea' )
        target_text_area.clear()
        target_text_area.send_keys( f"{copied_text}_{TestLoginSanity.counter}" )
        time.sleep( 1 )
        # אישור
        self.find_and_interact( driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[2]/div/div[2]/button' )
        self.find_and_interact( driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[3]/div[2]' )
        # פופאפ

        modal = WebDriverWait( driver, 5 ).until(
            EC.visibility_of_element_located( (By.CLASS_NAME, "ReactModal__Overlay") ) )
        button_inside_modal = modal.find_element( By.XPATH, '/html/body/div[3]/div/div/div[2]/div/button' )
        button_inside_modal.click()

        #שלב 7

        element_sit_minus = driver.find_element( By.ID, "sit_minus" )
        driver.execute_script( "arguments[0].click();", element_sit_minus)
        self.find_and_interact( driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[4]/div/div/button' )

        for _ in range( 5 ):
            next_text = self.get_next_name()

            # Try to enter the text and click the button
            try:
                textarea = driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[4]/textarea' )
                submit_button = driver.find_element( By.XPATH,
                                                     '//*[@id="mobile-modal"]/div/div[2]/div[4]/div/div/button' )

                textarea.clear()  # Clear the textarea before sending keys
                textarea.send_keys( next_text )
                submit_button.click()
                time.sleep( 1 )

            except NoSuchElementException:
                # If the textarea is not found, skip to the next iteration
                print( "Textarea not found. Skipping to the next iteration." )
                continue

            except WebDriverException as e:
                print( f"First attempt failed. Retrying... Error: {e}" )
                # Retry once more
                try:
                    textarea.clear()
                    textarea.send_keys( next_text )
                    submit_button.click()
                    time.sleep( 1 )

                except WebDriverException as e:
                    print( f"Second attempt also failed. Proceeding to next iteration. Error: {e}" )
                    # Optionally, you can raise an exception here to fail the test or just continue
            #  בחירת רעיון טוב
        driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[2]/div[3]' ).click()
        source_element = driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/p[2]' )
        copied_text = source_element.text
        target_text_area = driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[1]/div[2]/textarea' )
        target_text_area.clear()
        target_text_area.send_keys( f"{copied_text}_{TestLoginSanity.counter}" )
        time.sleep( 1 )
        # אישור
        self.find_and_interact( driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[2]/div/div[2]/button' )
        self.find_and_interact( driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[3]/div[2]' )
        # פופאפ

        modal = WebDriverWait( driver, 5 ).until(
            EC.visibility_of_element_located( (By.CLASS_NAME, "ReactModal__Overlay") ) )
        button_inside_modal = modal.find_element( By.XPATH, '/html/body/div[3]/div/div/div[2]/div/button' )
        button_inside_modal.click()

        # שלב 8

        element_trends = driver.find_element( By.ID, "trends" )
        driver.execute_script( "arguments[0].click();", element_trends)
        self.find_and_interact( driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[4]/div/div/button' )

        for _ in range( 5 ):
            next_text = self.get_next_name()

            # Try to enter the text and click the button
            try:
                textarea = driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[4]/textarea' )
                submit_button = driver.find_element( By.XPATH,
                                                     '//*[@id="mobile-modal"]/div/div[2]/div[4]/div/div/button' )

                textarea.clear()  # Clear the textarea before sending keys
                textarea.send_keys( next_text )
                submit_button.click()
                time.sleep( 1 )

            except NoSuchElementException:
                # If the textarea is not found, skip to the next iteration
                print( "Textarea not found. Skipping to the next iteration." )
                continue

            except WebDriverException as e:
                print( f"First attempt failed. Retrying... Error: {e}" )
                # Retry once more
                try:
                    textarea.clear()
                    textarea.send_keys( next_text )
                    submit_button.click()
                    time.sleep( 1 )

                except WebDriverException as e:
                    print( f"Second attempt also failed. Proceeding to next iteration. Error: {e}" )
                    # Optionally, you can raise an exception here to fail the test or just continue
            #  בחירת רעיון טוב
        driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[2]/div[3]' ).click()
        source_element = driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/p[2]' )
        copied_text = source_element.text
        target_text_area = driver.find_element( By.XPATH, '//*[@id="mobile-modal"]/div/div[2]/div[1]/div[2]/textarea' )
        target_text_area.clear()
        target_text_area.send_keys( f"{copied_text}_{TestLoginSanity.counter}" )
        time.sleep( 1 )
        # אישור
        self.find_and_interact( driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[2]/div/div[2]/button' )
        self.find_and_interact( driver, wait, '//*[@id="mobile-modal"]/div/div[2]/div[3]/div[2]' )
        # פופאפ

        modal = WebDriverWait( driver, 5 ).until(
            EC.visibility_of_element_located( (By.CLASS_NAME, "ReactModal__Overlay") ) )
        button_inside_modal = modal.find_element( By.XPATH, '/html/body/div[3]/div/div/div[2]/div/button' )
        button_inside_modal.click()




        driver.quit()
