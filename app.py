from flask import Flask, request, jsonify, render_template
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import threading
import time
import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sections', methods=['GET'])
def get_sections():
    course_code = request.args.get('course_code')
    selected_semester = request.args.get('selectedSemester')
    
    if not course_code or not selected_semester:
        return jsonify({"error": "Course code and semester are required"}), 400
    
    result = fetch_course_sections(course_code, selected_semester)
    
    if isinstance(result, dict) and "error" in result:
        return jsonify(result), 404
    
    return jsonify(result)

@app.route('/notify', methods=['POST'])
def notify():
    data = request.get_json()  # Use get_json() to handle JSON data
    course_code = data.get('courseCode')
    section_code = data.get('sectionCode')
    semester = data.get('semester')
    email = data.get('email')

    availability = check_seat_availability(course_code, section_code, semester)

    if int(availability) > 0:
        print("Seats are available for this section")
        return jsonify({"error": "There are already seats available for this section"}), 400

    # Send confirmation email
    send_confirmation_email(email, course_code, section_code, semester)

    # Start the checking process in a separate thread
    thread = threading.Thread(target=periodically_check, args=(course_code, section_code, semester, email))
    thread.start()

    return jsonify({"message": "Notification setup successful"})

def fetch_course_sections(course_code, selected_semester):
    url = f'https://colleague-ss.uoguelph.ca/Student/Courses/Search?keyword={course_code}'
    
    options = Options()
    options.headless = True
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 20)
        
        button_id = 'collapsible-view-available-sections-for-' + course_code + '-groupHeading'
        button = wait.until(EC.element_to_be_clickable((By.ID, button_id)))
        button.click()
        
        semester_headers = wait.until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[@data-bind='foreach: TermsAndSections']/h4[@data-bind='text: $data.Term.Description()']"))
        )

        sections = []
        for header in semester_headers:
            semester_text = header.text.strip()
            if semester_text == selected_semester + " " + str(datetime.now().year):
                section_list = header.find_element(By.XPATH, "following-sibling::ul[@data-bind='foreach: Sections']")
                
                section_items = section_list.find_elements(By.CLASS_NAME, 'search-nestedaccordionitem')
                
                for item in section_items:
                    section = item.find_element(By.CLASS_NAME, 'search-sectiondetailslink').text.strip()
                    sections.append(section)
        
        return sections
    
    finally:
        driver.quit()

def check_seat_availability(course_code, section_code, semester):
    url = f'https://colleague-ss.uoguelph.ca/Student/Courses/Search?keyword={course_code}'
    
    options = Options()
    options.headless = True
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 20)
        
        button_id = 'collapsible-view-available-sections-for-' + course_code + '-groupHeading'
        button = wait.until(EC.element_to_be_clickable((By.ID, button_id)))
        button.click()
        
        semester_headers = wait.until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[@data-bind='foreach: TermsAndSections']/h4[@data-bind='text: $data.Term.Description()']"))
        )
        
        for header in semester_headers:
            semester_text = header.text.strip()
            if semester_text == semester + " " + str(datetime.now().year):
                section_list = header.find_element(By.XPATH, "following-sibling::ul[@data-bind='foreach: Sections']")
                
                section_items = section_list.find_elements(By.CLASS_NAME, 'search-nestedaccordionitem')
                
                for item in section_items:
                    section = item.find_element(By.CLASS_NAME, 'search-sectiondetailslink').text.strip()
                    if section == section_code:
                        seat_availability = item.find_elements(By.CLASS_NAME, 'search-seatsavailabletext')
                        
                        for availability in seat_availability:
                            if availability.is_displayed():
                                availability_data = availability.text.strip().split(' / ')[0]
                        return availability_data

        return {"error": "Section not found"}
    
    finally:
        driver.quit()  

def periodically_check(course_code, section_code, semester, email):
    while True:
        availability = check_seat_availability(course_code, section_code, semester)
        if int(availability) > 0:
            send_email_notification(email, course_code, section_code, semester, availability)
            print("Spot found")
            break
        time.sleep(15)  # Check every (interval) minutes or whatever


def send_confirmation_email(email, course_code, section_code, semester):
    # Prepare the email message
    msg = MIMEText(f'Thank you for registering for notifications.\n\nWe will notify you when seats become available for course: {course_code}, section: {section_code} in the {semester} semester.')
    msg['Subject'] = 'Course Notification Registration Confirmation'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = email

    try:
        # Connect to the Gmail SMTP server
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # Upgrade the connection to a secure encrypted SSL/TLS connection
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)  
            server.send_message(msg)  # Send the email message
        print("Confirmation email sent successfully")
    except smtplib.SMTPAuthenticationError:
        print("Failed to authenticate. Check your email and password or App Password.")
    except Exception as e:
        print(f"Failed to send confirmation email: {e}")

def send_email_notification(email, course_code, section_code, semester, availability):
    # Prepare the email message
    msg = MIMEText(f'Seats are now available for the coure: {course_code}, section: {section_code} in the {semester} semester.\n\nAvailability: {availability}')
    msg['Subject'] = 'Course Seat Availability Notification'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = email

    try:
        # Connect to the Gmail SMTP server
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # Upgrade the connection to a secure encrypted SSL/TLS connection
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)  
            server.send_message(msg)  
        print("Email sent successfully")
    except smtplib.SMTPAuthenticationError:
        print("Failed to authenticate. Check your email and password or App Password.")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == '__main__':
    app.run(debug=True)
