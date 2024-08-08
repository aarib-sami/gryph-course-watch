from flask import Flask, request, jsonify, render_template
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = Flask(__name__)

def fetch_course_sections(course_code):
    url = f'https://colleague-ss.uoguelph.ca/Student/Courses/Search?keyword={course_code}'
    
    options = Options()
    options.headless = True
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 5)  # Reduced wait time for faster execution
        
        button = wait.until(EC.element_to_be_clickable((By.ID, 'collapsible-view-available-sections-for-' + course_code + '-groupHeading')))
        button.click()
        
        wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'search-nestedaccordionitem')))
        items = driver.find_elements(By.CLASS_NAME, 'search-nestedaccordionitem')
        
        sections = []
        for item in items:
            section = item.find_element(By.CLASS_NAME, 'search-sectiondetailslink').text.strip()
            sections.append(section)
        
        return sections
    
    finally:
        driver.quit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sections', methods=['GET'])
def get_sections():
    course_code = request.args.get('course_code')
    if not course_code:
        return jsonify({"error": "Course code is required"}), 400
    
    sections = fetch_course_sections(course_code)
    return jsonify(sections)

if __name__ == '__main__':
    app.run(debug=True)
