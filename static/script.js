// Base URL for the API
const BASE_URL = 'http://127.0.0.1:8000';

// Add click event listener to the generate joke button
document.getElementById('generateButton').addEventListener('click', function () {
    // Retrieve input text value and get references to the loader and output text elements
    const inputText = document.getElementById('inputText').value;
    const loader = document.getElementById('loader');
    const outputText = document.getElementById('outputText');
    
    // Display the loader and clear the output text
    loader.style.display = 'block';
    outputText.value = '';

    // Encode the input text for URL and construct the request URL
    const encodedInputText = encodeURIComponent(inputText);
    const url = `${BASE_URL}/joke?input=${encodedInputText}`;

    // Create a new EventSource for server-sent events
    const eventSource = new EventSource(url);

    // Handle incoming messages (joke chunks)
    eventSource.onmessage = function (event) {
        // Replace placeholder text with actual characters
        const chunk = event.data
                        .replaceAll("<new-line>", "\n")
                        .replaceAll("<tab>", "\t")
                        .replaceAll("<space>", " ");
        outputText.value += chunk;
    };

    // Handle errors during the EventSource connection
    eventSource.onerror = function (error) {
        console.error('EventSource failed:', error);
        eventSource.close();
        loader.style.display = 'none';
    };
});
