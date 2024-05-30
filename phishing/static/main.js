// Ensure the JavaScript code runs after the entire HTML has been fully loaded
document.addEventListener("DOMContentLoaded", function() {
    const storeUrl = document.querySelector('body').dataset.storeUrl;
    // Add an event listener to the 'Check URL' button
    document.querySelector("button").addEventListener("click", function() {
        // Clear all rectangles from the screenz
        const rectangleContainer = document.getElementById("rectangle-container");
        rectangleContainer.innerHTML = '';
        // Get the URL string
        const url = document.getElementById("url").value;
        // Get the English box value
        const isEnglishChecked = document.getElementById("englishCheckbox").checked;
        const analysingMessage = document.getElementById("analysing-message");
        const waitingMessage = document.getElementById("waiting-message");
        // Retrieve the CSRF token from the HTML document
        const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;
        // If the URL is not valid, return the error message
        if (!isValidUrl(url)) {
            displayErrorMessage('Invalid URL');
            return;
        }
        // Display the analysis and waiting messages
        analysingMessage.style.display = "block";
        waitingMessage.style.display = "block";
        // Send the URL, the state of the checkbox and the CSRF token using a POST request
        fetchWithTimeout(storeUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken
            },
            body: `url=${encodeURIComponent(url)}&isEnglish=${isEnglishChecked}`
        // 4 minutes timeout
        }, 240000)
        // Receive response and convert it to JSON format
        .then(response => response.json())
        .then(data => {
            // Fade-out the analysing and waiting messages
            fadeOutElement(analysingMessage);
            fadeOutElement(waitingMessage, () => {
                if (data.status !== 'success') {
                    // If unsuccessful, display the error message
                    displayErrorMessage('Invalid URL');
                } else {
                    // If successful, display the 'Done' message
                    displayDoneMessage();
                    // Display the rectangles after a delay of 2.5 seconds
                    setTimeout(() => {
                        displayRectangles(data.detailed_results);
                    }, 2500);
                }
            });
        })
        // In case some error occurs, display the same error message
        .catch(error => {
            // Fade-out the analysing and waiting messages
            fadeOutElement(analysingMessage);
            fadeOutElement(waitingMessage, () => {
                displayErrorMessage('Invalid URL');
            });
        });
    });
    
    // Perform the network request with a timeout feature
    function fetchWithTimeout(url, options, timeout) {
        // One of the two objects is expected in the future (in a race)
        return Promise.race([
            // First promise: network request
            fetch(url, options),
            // Second promise: timeout
            new Promise((_, reject) =>
                // Reject the fetch if it hasn't completed and displays the same error
                setTimeout(() => reject(new Error('Invalid URL')), timeout))
        ]);
    }
    
    // Validate a string to see if it is a properly formatted URL
    function isValidUrl(string) {
        try {
            new URL(string);
            return true;
        } catch (_) {
            return false;  
        }
    }
    
    // Create and display the error message
    function displayErrorMessage(message) {
        // Select the element with the ID 'error-message'
        const errorMessage = document.getElementById("error-message");
        errorMessage.textContent = message;
        // Opacity is set to 1, making it visible
        errorMessage.style.opacity = 1;
        fadeOutMessage(errorMessage);
    }
    
    // Create and display the done message
    function displayDoneMessage() {
        const doneMessage = document.createElement('div');
        doneMessage.id = 'done-message';
        // Fade-in using the CSS animation
        doneMessage.className = 'message fade-in';
        doneMessage.textContent = 'Done';
        // Append the element to the messages div
        document.querySelector('.message-container').appendChild(doneMessage);
        // Remove the message after 2.5 seconds
        setTimeout(() => {
            doneMessage.remove();
        }, 2500);
    }
    
    // Gradually fade-out the error message
    function fadeOutMessage(element) {
        setTimeout(() => {
            // setInterval executes its callback function every 100 milliseconds
            let fadeEffect = setInterval(() => {
                // If the function is called for the first time, opacity is set to 1
                if (!element.style.opacity) {
                    element.style.opacity = 1;
                }
                // If the opacity is greater than 0, gradually decrease it
                if (element.style.opacity > 0) {
                    element.style.opacity -= 0.1;
                } else {
                    // If the opacity is 0, setInterval is stopped
                    clearInterval(fadeEffect);
                    // The text is cleared
                    element.textContent = '';
                }
            }, 100);
        // Keep the error message on the screen for 5 seconds
        }, 5000);
    }
    
    // Fade-out the analysing and waiting messages
    function fadeOutElement(element, callback) {
        // Use the CSS animation
        element.classList.add('fade-out');
        setTimeout(() => {
            // Hide the element
            element.style.display = 'none';
            element.classList.remove('fade-out');
            // callback function is called if it is provided
            if (callback) callback();
        // The fade-out transition should take 500 milliseconds
        }, 500);
    }

    // Display the results as rectangles
    function displayRectangles(detailedResults) {
        // Select the element with the following ID
        const rectangleContainer = document.getElementById("rectangle-container");
        // Clears its HTML to reset any existing content 
        rectangleContainer.innerHTML = '';
        // Track the type of the last result processed
        let previousResultType = null;
        // Iterate over the array results
        detailedResults.forEach((result, index) => {
            setTimeout(() => {
                // For each result create a div
                const rect = document.createElement('div');
                rect.className = 'rectangle';
                // If the index is even, swipe-in from the left, else from the right
                rect.classList.add(index % 2 === 0 ? 'rectangle-swipe-left' : 'rectangle-swipe-right');
                // 2 child div's are created
                const rectLeft = document.createElement('div');
                // The left div contains the result character 
                rectLeft.className = 'rectangle-left letter-' + result[1];
                rectLeft.textContent = result[1];
                // The right div contains the informative message
                const rectRight = document.createElement('div');
                rectRight.className = 'rectangle-right';
                rectRight.innerHTML = getMessage(result);
                // Check if this is the second rectangle
                if (result[0] === 'cues and spelling' || (result[0] === 'blacklists' && previousResultType === 'random forest')) {
                    // If it is, append them reversed
                    rect.appendChild(rectRight);
                    rect.appendChild(rectLeft);
                } else {
                    rect.appendChild(rectLeft);
                    rect.appendChild(rectRight);
                }
                // Append the rectangle to the container to make it visible
                rectangleContainer.appendChild(rect);
                // Update it for the reversed appending step
                previousResultType = result[0];
            // The delay increases by 500 milliseconds for each result, creating a staggered effect
            }, 500 * index);
        });
        // Its display style is set to block, making it visible with all the rectangles
        rectangleContainer.style.display = "block";
    }

    // Generate a message based on the content of the result
    function getMessage(result) {
        let message = "";
        switch (result[0]) {
            // If the test is random forest
            case 'random forest':
                // Display a suggestive message
                message = "Our random forest algorithm has predicted the website is " +
                          (result[1] === 'L' ? "legitimate." : "phishing.");
                break;
            case 'cues and spelling':
                message = result[1] === 'L' 
                          ? "No urgency or trust cues and no spelling errors were found."
                          : "Our algorithm has found urgency or trust cues, or spelling errors.";
                break;
            case 'blacklists':
                message = result[1] === 'L' 
                          ? "The website was not found in any of our blacklists."
                          : "The website was found in one of our blacklists.";
                break;
            case 'malicious files':
                message = "The URL provided is downloading a file, and the file is " +
                          (result[1] === 'L' ? "safe." : "malicious.");
                break;
        }
        return message;
    }
});