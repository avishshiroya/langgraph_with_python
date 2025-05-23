$(document).ready(function () {
    // Sidebar Toggle
    $('#menu-toggle').on('click', function () {
        $('.sidebar').toggleClass('collapsed');
        $('.main-content .input-area').css('left', $('.sidebar').width() + 'px');
    });

    // Adjust input area position on window resize
    $(window).on('resize', function () {
        $('.main-content .input-area').css('left', $('.sidebar').width() + 'px');
    }).trigger('resize'); // Trigger resize on load


    // API Key Placeholder
    const API_KEY = "AIzaSyA7zJ7a2vaa3pc5pAOrdhkmCIaGjm1ZuSo"; // Replace with your actual API Key
    const API_URL = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key=${API_KEY}`;

    // Function to add message to chat box
    function addMessage(sender, text) {
        const chatBox = $('#chat-box');
        const messageDiv = $('<div>').addClass('chat-message');
        if (sender === 'user') {
            messageDiv.addClass('user-message').text(text);
            // Remove greeting and prompts after the first user message
            $('.chat-area').addClass('chat-active');
        } else {
            messageDiv.addClass('bot-message');
            // Simple formatting: Handle basic newlines and potentially code blocks
            const formattedText = text.replace(/\n/g, '<br>');
            // Basic attempt to detect and format code blocks (e.g., ```language\ncode```)
            const codeBlockRegex = /```(\w+)?\n([\s\S]*?)```/g;
            let htmlContent = formattedText.replace(codeBlockRegex, (match, lang, code) => {
                const languageClass = lang ? `language-${lang}` : '';
                return `
        <pre><code class="${languageClass}">${code.trim()}</code></pre>`;
            });
            messageDiv.html(htmlContent); // Use html() to render <br> and
        }
        chatBox.append(messageDiv);
        // Scroll to the bottom
        // chatBox.scrollTop(chatBox[0].scrollHeight);
    }

    // Function to call Gemini API
    async function sendMessageToGemini(text) {
        // Add a placeholder bot message while waiting for response
        const thinkingMessage = addMessage('bot', 'Thinking...');
        const chatBox = $('#chat-box');
        const lastMessage = chatBox.children().last();


        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    contents: [{
                        parts: [{
                            text: text
                        }]
                    }]
                })
            });

            if (!response.ok) {
                const errorBody = await response.json();
                console.error("API error:", response.status, errorBody);
                lastMessage.text(`Error: API returned status ${response.status}`);
                return;
            }

            const data = await response.json();
            console.log("API Response:", data);

            lastMessage.remove(); // Remove the "Thinking..." message

            if (data.candidates && data.candidates[0] && data.candidates[0].content && data.candidates[0].content.parts) {
                const botResponseText = data.candidates[0].content.parts.map(part => part.text).join('');
                addMessage('bot', botResponseText);
            } else {
                addMessage('bot', "Could not get a valid response from the API.");
            }

        } catch (error) {
            console.error("Error calling Gemini API:", error);
            lastMessage.text(`Error: ${error.message}`);
        }
    }

    // Handle user input on Enter key
    $('#user-input').on('keypress', function (e) {
        if (e.which === 13) { // Enter key
            const text = $(this).val().trim();
            if (text) {
                addMessage('user', text);
                $(this).val(''); // Clear input
                sendMessageToGemini(text); // Send to API
            }
        }
    });

    // Handle suggested prompt button click
    $('.prompt-button').on('click', function () {
        const text = $(this).text().trim();
        if (text) {
            addMessage('user', text);
            sendMessageToGemini(text); // Send to API
        }
    });


    // Microphone functionality
    $('#mic-button').on('click', function () {
        // Check for browser support
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            alert("Speech recognition not supported in this browser.");
            return;
        }

        // Request microphone permission
        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(function (stream) {
                // Permission granted, now start recognition
                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                const recognition = new SpeechRecognition();

                recognition.continuous = false; // Stop after one utterance
                recognition.lang = 'en-US'; // Set language
                recognition.interimResults = false; // Only return final results
                recognition.maxAlternatives = 1; // Get the most likely result

                const micIcon = $('#mic-button i');
                micIcon.removeClass('fa-microphone').addClass('fa-spinner fa-spin'); // Show spinner

                recognition.start();

                recognition.onresult = function (event) {
                    const transcript = event.results[0][0].transcript;
                    $('#user-input').val(transcript); // Put transcript in input
                    micIcon.removeClass('fa-spinner fa-spin').addClass('fa-microphone'); // Restore icon
                }

                recognition.onerror = function (event) {
                    console.error('Speech recognition error', event.error);
                    micIcon.removeClass('fa-spinner fa-spin').addClass('fa-microphone'); // Restore icon
                    alert('Speech recognition error: ' + event.error);
                }

                recognition.onend = function () {
                    micIcon.removeClass('fa-spinner fa-spin').addClass('fa-microphone'); // Restore icon if stopped
                }

            })
            .catch(function (err) {
                // Permission denied or other error
                console.error('Microphone access error:', err);
                alert("Microphone access denied or error: " + err.message);
            });
    });

    // Attach file functionality
    $('#attach-file-button').on('click', function () {
        $('#file-input').click(); // Trigger the hidden file input click
    });

    $('#file-input').on('change', function () {
        const files = $(this)[0].files;
        if (files.length > 0) {
            console.log("Selected files:", files);
            // TODO: Implement file upload/processing logic here
            alert(`Selected file: ${files[0].name}. File processing not implemented yet.`);
        }
    });

    // Settings button placeholder (could open a modal)
    $('#settings-button').on('click', function () {
        alert("Settings functionality not implemented yet.");
    });

    // New Chat button placeholder (could clear chat or navigate)
    $('.new-chat-button').on('click', function () {
        if (confirm("Start a new chat?")) {
            $('#chat-box').empty(); // Clear messages
            $('.chat-area').removeClass('chat-active'); // Show greeting again
            $('#user-input').val(''); // Clear input
            // In a real app, you'd likely create a new chat session ID etc.
        }
    });

});