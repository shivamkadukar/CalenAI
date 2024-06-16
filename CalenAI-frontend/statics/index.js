function toggleButtonState(isLoading) {
    const submitButton = document.getElementById('submitButton');
    if (isLoading) {
        // Change to loading state
        submitButton.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Generating...`;
        submitButton.disabled = true;
        submitButton.type = 'button'; // Change to regular button to prevent form submission
    } else {
        // Change back to normal state
        submitButton.innerHTML = 'Submit';
        submitButton.disabled = false;
        submitButton.type = 'submit'; // Change back to submit button
    }
}

var downloadButton = document.getElementById('downloadButton');
downloadButton.disabled = true;

document.getElementById('form1').addEventListener('submit', function (e) {
    e.preventDefault();
});

var submitButton = document.getElementById('submitButton');
submitButton.onclick = function () {
    // Show loader
    toggleButtonState(true);

    // Get form data
    var selectedMonth = document.getElementById('monthSelect').value;
    var emailInputs = document.querySelectorAll('[name="email_ids[]"]');
    var emailIds = Array.from(emailInputs).map(input => input.value);

    // AJAX request to Flask backend
    fetch('/api/generate-file', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ month: selectedMonth, emailIds: emailIds }),
    })
        .then(response => response.json())
        .then(data => {
            // Hide loader
            toggleButtonState(false);

            // Show download button with the file link
            downloadButton.disabled = false;
            downloadButton.onclick = function () {
                window.open('/api/download?file=' + data.filePath, '_blank');
            };
        })
        .catch((error) => {
            console.error('Error:', error);
        });
};