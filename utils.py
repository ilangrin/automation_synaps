import threading
import time
from selenium.common.exceptions import NoSuchElementException

def check_and_close_modal(driver):
    # Implementation
    pass

def modal_check_thread(driver, interval=5):
    while True:
        check_and_close_modal(driver)
        time.sleep(interval)