from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

courseCode = input("Enter course code (e.g., CIS*1300): ")
sectionToFind = input("Enter the section code to find (e.g., CIS*1300*0101): ")

url = 'https://colleague-ss.uoguelph.ca/Student/Courses/Search?keyword=' + courseCode

options = Options()
options.headless = True
options.add_argument('--disable-gpu')
driver = webdriver.Chrome(options=options)

try:
    driver.get(url)
    wait = WebDriverWait(driver, 5)

    button = wait.until(EC.element_to_be_clickable((By.ID, 'collapsible-view-available-sections-for-' + courseCode + '-groupHeading')))
    button.click()

    wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'search-nestedaccordionitem')))
    items = driver.find_elements(By.CLASS_NAME, 'search-nestedaccordionitem')

    for item in items:
        section = item.find_element(By.CLASS_NAME, 'search-sectiondetailslink')
        if section.text.strip() == sectionToFind:
            print(f"Found section {sectionToFind}")

            seatAvailability = item.find_elements(By.CLASS_NAME, 'search-seatsavailabletext')
            for availability in seatAvailability:
                if availability.is_displayed():
                    print("Seat availability information:", availability.text)
            break
    else:
        print(f"Section {sectionToFind} not found.")

finally:
    driver.quit()

