document.getElementById('course-code').disabled = true;
document.getElementById('section-dropdown').disabled = true;
document.getElementById('email').disabled = true;
document.getElementById('submit').disabled = true;

function checkFields() {
    const semester = document.getElementById('semester-dropdown').value;
    const courseCode = document.getElementById('course-code').value;
    const section = document.getElementById('section-dropdown').value;
    const email = document.getElementById('email').value;

    const allFieldsFilled = semester !== 'Select Semester' && courseCode !== '' && section !== 'Select Section' && email !== '';

    document.getElementById('submit').disabled = !allFieldsFilled;
    }

    document.getElementById('semester-dropdown').addEventListener('input', function() {
    const semester = this.value;
    const courseCode = document.getElementById('course-code').value;
    const sectionDropdown = document.getElementById('section-dropdown');
    const loadingSpinner = document.getElementById('loading-spinner');
    const warningMessage = document.getElementById('warning-message');

    if (semester === 'Select Semester') {
        document.getElementById('course-code').value = "";
        document.getElementById('section-dropdown').value = 'Select Section';
        document.getElementById('email').value = "";

        document.getElementById('course-code').disabled = true;
        document.getElementById('section-dropdown').disabled = true;
        document.getElementById('email').disabled = true;
    } else {
        document.getElementById('course-code').disabled = false;
        document.getElementById('section-dropdown').disabled = false;
        document.getElementById('email').disabled = false;
    }
    checkFields();
});

document.getElementById('course-code').addEventListener('input', function() {
    const courseCode = this.value;
    const sectionDropdown = document.getElementById('section-dropdown');
    const semesterDropdown = document.getElementById('semester-dropdown');
    const selectedSemester = semesterDropdown.value;
    const loadingSpinner = document.getElementById('loading-spinner');
    const warningMessage = document.getElementById('warning-message');

    if (/.*\*\d{4}$/.test(courseCode)) {
        loadingSpinner.style.display = 'block';
        sectionDropdown.disabled = true;
        warningMessage.style.display = 'none'; // Hide warning message initially
        document.getElementById('course-code').disabled = true;

        fetch(`/sections?course_code=${courseCode}&selectedSemester=${selectedSemester}`)
            .then(response => response.json())
            .then(sections => {
                if (sections.length === 0) {
                    warningMessage.style.display = 'block'; // Show warning message
                    document.getElementById('course-code').value = "";
                    document.getElementById('course-code').disabled = true 
                    document.getElementById('semester-dropdown').value = 'Select Semester';
                    document.getElementById('email').value = "";
                    document.getElementById('email').disabled = true;
                    setTimeout(() => {
                    warningMessage.style.display = 'none';
                    }, 10000); 
                } else {
                    sections.forEach(section => {
                        const option = document.createElement('option');
                        option.value = section;
                        option.textContent = section;
                        sectionDropdown.appendChild(option);
                    });
                    sectionDropdown.disabled = false;
                }
            })
            .catch(error => {
                console.error('Error fetching sections:', error);
            })
            .finally(() => {
                loadingSpinner.style.display = 'none';
            });
    } 
    checkFields();
});

document.getElementById('section-dropdown').addEventListener('input', checkFields);
document.getElementById('email').addEventListener('input', checkFields);

document.getElementById('course-form').addEventListener('submit', function(event) {
event.preventDefault();

    const courseCode = document.getElementById('course-code').value;
    const sectionCode = document.getElementById('section-dropdown').value;
    const email = document.getElementById('email').value;
    const semester = document.getElementById('semester-dropdown').value;
    const loadingSpinner = document.getElementById('loading-spinner');
    const warningMessage1 = document.getElementById('warning-message1');

    loadingSpinner.style.display = 'block';
    warningMessage1.style.display = 'none'; // Hide warning message initially

    fetch('/notify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ courseCode, sectionCode, email, semester })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            warningMessage1.style.display = 'block';
            document.getElementById('course-code').value = "";
            document.getElementById('section-dropdown').innerHTML = '<option selected>Select Section</option>';
            document.getElementById('email').value = "";

            document.getElementById('course-code').disabled = true;
            document.getElementById('section-dropdown').disabled = true;
            document.getElementById('email').disabled = true;
            
            setTimeout(() => {
            warningMessage1.style.display = 'none';
            }, 10000);
        } else {
            alert(data.message || 'Notification setup successful');
        }
        // Clear all fields
        document.getElementById('course-code').value = '';
        document.getElementById('section-dropdown').innerHTML = '<option selected>Select Section</option>';
        document.getElementById('email').value = '';
        document.getElementById('semester-dropdown').value = 'Select Semester';
        document.getElementById('course-code').disabled = true;
        document.getElementById('section-dropdown').disabled = true;
        document.getElementById('email').disabled = true;
    })
    .catch(error => {
        console.error('Error:', error);
    })
    .finally(() => {
        loadingSpinner.style.display = 'none';
    });
});