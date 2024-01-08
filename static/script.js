const BASE_URL = 'http://127.0.0.1:8000';

document.getElementById('generateButton').addEventListener('click', function () {
    const inputText = document.getElementById('inputText').value;
    const outputText = document.getElementById('outputText');
    
    outputText.value = '';

    const encodedInputText = encodeURIComponent(inputText);
    const url = `${BASE_URL}/joke?input=${encodedInputText}`;

    const eventSource = new EventSource(url);

    eventSource.onmessage = function (event) {
        const chunk = event.data
                        .replaceAll("<new-line>", "\n")
                        .replaceAll("<tab>", "\t")
                        .replaceAll("<space>", " ");
        outputText.value += chunk;
    };

    eventSource.onerror = function (error) {
        console.error('EventSource failed:', error);
        eventSource.close();
    };
});