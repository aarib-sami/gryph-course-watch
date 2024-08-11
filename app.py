from flask import Flask, request, jsonify, render_template
from datetime import datetime
import threading
import time
import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
import re
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


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

def escape_css_selector(value):
    """Escape special characters for use in a CSS selector."""
    return re.sub(r'([ #!$%&\'()*+,.\/:;<=>?@[\]^`{|}~])', r'\\\1', value)

def fetch_course_sections(course_code, selected_semester):
    url = f'https://colleague-ss.uoguelph.ca/Student/Courses/Search?keyword={course_code}'
    sectionsList = []

    # Escape the special characters in the course code for the CSS selector
    escaped_course_code = escape_css_selector(course_code)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        
        # Wait for the button to be clickable and click it
        button_selector = f'#collapsible-view-available-sections-for-{escaped_course_code}-groupHeading'
        
        try:
            # Attempt to find and click the button
            page.wait_for_selector(button_selector, state='visible', timeout=5000)
            page.click(button_selector)
        except PlaywrightTimeoutError:
            browser.close()
            return sectionsList
        
        # Wait for the section items to be loaded
        try:
            # Attempt to find sections
            page.wait_for_selector('ul[data-bind="foreach: Sections"]', timeout=5000)
        except PlaywrightTimeoutError:
            browser.close()
            return sectionsList


        # Find the semester text
        sectionSemester = page.query_selector_all('h4[data-bind="text: $data.Term.Description()"]')

        # Go through each semester text, compare with desired semester
        for semester in sectionSemester:
            if semester.text_content().strip() == selected_semester + " " + str(datetime.now().year):
                # Locate the course sections within the desired semester
                semesterSection = semester.query_selector('xpath=following-sibling::ul[@data-bind="foreach: Sections"]')
                # Have variable for each course
                sections = semesterSection.query_selector_all('.search-nestedaccordionitem')
                for section in sections:
                    courseCode = section.query_selector('.search-sectiondetailslink')
                    sectionsList.append(courseCode.text_content().strip())
        
        return sectionsList
        browser.close()

def check_seat_availability(course_code, section_code, selectedSemester):
    url = f'https://colleague-ss.uoguelph.ca/Student/Courses/Search?keyword={course_code}'

    # Escape the special characters in the course code for the CSS selector
    escaped_course_code = escape_css_selector(course_code)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        
        # Wait for the button to be clickable and click it
        button_selector = f'#collapsible-view-available-sections-for-{escaped_course_code}-groupHeading'
        page.wait_for_selector(button_selector, state='visible', timeout=5000)
        page.click(button_selector)

        # Wait for the section items to be loaded
        page.wait_for_selector('ul[data-bind="foreach: Sections"]', timeout=10000)
        
        # Find the semester text
        sectionSemester = page.query_selector_all('h4[data-bind="text: $data.Term.Description()"]')

        # Go through each semester text, compare with desired semester
        for semester in sectionSemester:
            if semester.text_content().strip() == selectedSemester + " " + str(datetime.now().year):
                # Locate the course sections within the desired semester
                semesterSection = semester.query_selector('xpath=following-sibling::ul[@data-bind="foreach: Sections"]')
                # Have variable for each course
                sections = semesterSection.query_selector_all('.search-nestedaccordionitem')
                for section in sections:
                    courseCode = section.query_selector('.search-sectiondetailslink')
                    if courseCode.text_content().strip() == section_code:
                        availabilityText = section.query_selector('.search-seatsavailabletext')
                        availability = availabilityText.text_content().strip().split(' / ')[0]
                        print(availability)
                        return availability
                        
        browser.close()

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
