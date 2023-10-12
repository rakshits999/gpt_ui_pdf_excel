//////////////// speaking javascript///////////////////

runSpeechRecog = () => {
    var questionInput = document.getElementById('question');
    var action = document.getElementById('action');

    questionInput.value = "";

    let recognition = new webkitSpeechRecognition();
    recognition.onstart = () => {
        action.innerHTML = "Listening...";
    }
    recognition.onresult = (e) => {
        var transcript = e.results[0][0].transcript;
        questionInput.value = transcript;
        action.innerHTML = "";
    }
    recognition.start();
}


/////////////// file uploading js//////////////
function uploadFile(input) {
    if (input.files.length > 0) {
        
        document.getElementById("uploadButton").click();
    }
}


// //////////////form action js//////////////

function submitForm() {
    const chatBox = document.getElementById('chat-box');

    var fileTypeSelect = document.getElementById('file_type');
    var form = document.getElementById('question_form');
    const question = document.getElementById('question');
    const userQuestion = document.getElementById('question').value;
    
    chatBox.innerHTML += `<div class="message user user-message"><div class="avatar-holder"><div class="avatar"><svg class="MuiSvgIcon-root MuiSvgIcon-fontSizeMedium css-vubbuv" focusable="false" aria-hidden="true" viewBox="0 0 24 24" data-testid="PersonIcon"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"></path></svg></div></div><div class="message-body"><div class="cell-output">${userQuestion}</div></div></div>`;
    
    
    chatBox.scrollTop = chatBox.scrollHeight;



    if (fileTypeSelect.value === 'pdf') {
        form.action = '/ask_pdf';
    } else if (fileTypeSelect.value === 'csv') {
        form.action = '/ask_csv';
    } else if (fileTypeSelect.value === 'GPT-3.5') {
        form.action = '/gpt_3';
    } else if (fileTypeSelect.value === 'GPT-4') {
        form.action = '/gpt_4';
    }

    const formData = new FormData(form);

    fetch(form.action, {
        method: 'POST',
        body: formData,
    })
        .then(response => response.json())
        .then(data => {
            const botMessage = data.response_text;
            question.value = '';                   
            chatBox.innerHTML += `
            <div class="message generator bot-message"><div class="avatar-holder"><div class="avatar"><svg class="MuiSvgIcon-root MuiSvgIcon-fontSizeMedium css-vubbuv" focusable="false" aria-hidden="true" viewBox="0 0 24 24" data-testid="VoiceChatIcon"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"></path><path d="M11.25 5h1.5v10h-1.5zM8.5 7H10v6H8.5zM6 9h1.5v2H6zm8-2h1.5v6H14zm2.5 2H18v2h-1.5z"></path></svg></div></div><div class="message-body"><div class="cell-output">${botMessage}</div></div></div>`;
            chatBox.scrollTop = chatBox.scrollHeight;

            // Clear the question input
            
        })
        .catch(error => {
            console.error('Error:', error);
        });

    return false;
}

document.getElementById('question_form').onsubmit = function (event) {
    event.preventDefault(); // Prevent the default form submission
    submitForm();
};