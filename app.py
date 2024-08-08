from flask import Flask, request, jsonify, render_template
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

app = Flask(__name__)

def fetch_course_sections(course_code, selected_semester):
    url = f'https://colleague-ss.uoguelph.ca/Student/Courses/Search?keyword={course_code}'
    
    options = Options()
    options.headless = True
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 20)  # Increased wait time
        
        # Wait and click the button
        button_id = 'collapsible-view-available-sections-for-' + course_code + '-groupHeading'
        print(f"Button ID: {button_id}")
        button = wait.until(EC.element_to_be_clickable((By.ID, button_id)))
        button.click()
        
        # Wait for the semester headers to be present
        print("Waiting for semester headers...")
        semester_headers = wait.until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[@data-bind='foreach: TermsAndSections']/h4[@data-bind='text: $data.Term.Description()']"))
        )
        print("Semester headers found.")

        sections = []
        for header in semester_headers:
            semester_text = header.text.strip()
            print(f"Found semester header: {semester_text}")
            if semester_text == selected_semester + " " + str(datetime.now().year):
                # Find the <ul> element directly following the <h4> element
                section_list = header.find_element(By.XPATH, "following-sibling::ul[@data-bind='foreach: Sections']")
                
                section_items = section_list.find_elements(By.CLASS_NAME, 'search-nestedaccordionitem')
                
                for item in section_items:
                    section = item.find_element(By.CLASS_NAME, 'search-sectiondetailslink').text.strip()
                    sections.append(section)

        if not sections:
            return {"error": "No sections found"}
        
        return sections
    
    finally:
        driver.quit()



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

if __name__ == '__main__':
    app.run(debug=True)
