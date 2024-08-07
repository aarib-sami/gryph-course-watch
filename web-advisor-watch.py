from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

courseCode = input("Enter course code (e.g., CIS*1300): ")
sectionToFind = input("Enter the section code to find (e.g., CIS*1300*0101): ")

url = 'https://colleague-ss.uoguelph.ca/Student/Courses/Search?keyword=' + courseCode
driver = webdriver.Chrome()

try:
    driver.get(url)
    
    wait = WebDriverWait(driver, 5)
    button = wait.until(EC.element_to_be_clickable((By.ID, 'collapsible-view-available-sections-for-' + courseCode + '-groupHeading')))
    button.click()

    time.sleep(3)
    
    items = driver.find_elements(By.CLASS_NAME, 'search-nestedaccordionitem')
    
    for item in items:
        sectionLink = item.find_element(By.CLASS_NAME, 'search-sectiondetailslink')
        
        if sectionLink.text.strip() == sectionToFind:
            print(f"Found section {sectionToFind}")
            
            seat_availability = item.find_elements(By.CLASS_NAME, 'search-seatsavailabletext')
            
            for availability in seat_availability:
                if availability.is_displayed():
                    print(availability.text)
            break
    else:
        print(f"Section {sectionToFind} not found.")
    
finally:
    driver.quit()
