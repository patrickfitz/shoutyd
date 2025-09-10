/* shoutyd javascript functions */
/* set and store color mode */
const html = document.documentElement;
let currentIndex = 0;

// about dialog
const aboutDialog = document.getElementById('aboutDialog');
document.getElementById('about_data').addEventListener('click', () => aboutDialog.showModal());
document.getElementById('closeDialog').addEventListener('click', () => aboutDialog.close());

// about dialog
const settingsDialog = document.getElementById('settingsDialog');
document.getElementById('settings_data').addEventListener('click', () => settingsDialog.showModal());
document.getElementById('closeDialog').addEventListener('click', () => settingsDialog.close());


// loading dialog
function pleaseWait() {
    document.getElementById("loader").classList.toggle("hidden");
}

// Handle form submission

document.getElementById('userForm').addEventListener('submit', function (event) {
    event.preventDefault(); // Prevent default form submission
    const jsonData = getFormDataAsJSON(this);
    console.log(jsonData);
    // Call the Python function via WebUI
    webui.call('process_form', jsonData);
});



/* light / dark /default modes */
const toggleBtn = document.getElementById('theme-toggle');
const modes = ['auto', 'light', 'dark'];
//const data-theme = ['auto', 'light', 'dark'];
function applyMode(mode) {
    const htmlElement = document.querySelector("html");
    if (mode === 'dark') {
        //html.style.setProperty('color-scheme', 'dark');
        htmlElement.setAttribute('data-theme', 'dark');
        toggleBtn.innerHTML = '<span class="material-icons md-24">dark_mode</span>';
    } else if (mode === 'light') {
        //html.style.setProperty('color-scheme', 'light');
        htmlElement.setAttribute('data-theme', 'dark');
        toggleBtn.innerHTML = '<span class="material-icons md-24">light_mode</span>';
    } else {
        //html.style.setProperty('color-scheme', 'light dark');
        htmlElement.setAttribute('data-theme', 'light dark');
        toggleBtn.innerHTML = '<span class="material-icons md-24">computer</span>';
    }
    localStorage.setItem('theme-mode', mode);
    localStorage.setItem('data-mode', mode);
}

toggleBtn.addEventListener('click', () => {
    currentIndex = (currentIndex + 1) % modes.length;
    applyMode(modes[currentIndex]);
});

// Load saved theme on start
const savedMode = localStorage.getItem('theme-mode') || 'auto';
currentIndex = modes.indexOf(savedMode);
console.log(savedMode);
applyMode(savedMode);

//convert form to json data
function getFormDataAsJSON(formElement) {
    const formData = new FormData(formElement);
    const jsonData = {};
    for (const [name, value] of formData.entries()) {
        if (jsonData[name]) {
            if (!Array.isArray(jsonData[name])) {
                jsonData[name] = [jsonData[name]];
            }
            jsonData[name].push(value);
        } else {
            jsonData[name] = value;
        }
    }
    return JSON.stringify(jsonData);
}


<!-- material dialog -->
function showDialog(title, message) {
    document.getElementById('material-dialog').style.display = 'flex';
    document.querySelector('.dialog-title').innerHTML = title;
    document.querySelector('.dialog-message').innerHTML = message;
}

function showDialog2(message) {
    document.getElementById('material-dialog').style.display = 'flex';
    document.getElementById('loader').style.display = 'flex';
}

function fillDialog(title, message) {
    document.getElementById('loader').style.display = 'none';
    document.querySelector('.dialog-title').innerHTML = title;
    document.querySelector('.dialog-message').innerHTML = message;
    document.getElementById('material-dialog').style.display = 'flex';
}


function hideDialog() {
    const dialog = document.getElementById('material-dialog');
    const container = dialog.querySelector('.dialog-container');

    // Start fade-out animation
    container.style.animation = 'fadeOut 0.2s ease-out';

    // Wait for animation to finish before hiding the dialog
    setTimeout(() => {
        dialog.style.display = 'none';
        container.style.animation = 'fadeIn 0.2s ease-out'; // Reset for next time
    }, 200);
}

document.getElementById('material-dialog').addEventListener('click', hideDialog);

function submitDialog() {
    const msg = "User clicked OK!";
    hideDialog();
    webui.call("on_dialog_submit", msg);
}

// Close dialog when clicking the background

