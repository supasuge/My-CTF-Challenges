// Command definitions
const commands = {
    'dir': ' Directory of C:\\WINDOWS\\SYSTEM32\n\n flag.txt\n README.md\n',
    'type': 'Outputs the content of a file.',
    'help': 'Available commands: dir, type flag.txt, help, whoami, clear',
    'whoami': 'C:\\Users\\XP_User',
    'clear': '', // We'll handle 'clear' separately
};

let inputLine = [];
let cursorPosition = 0;

let terminal = document.getElementById('terminal');
let inputLineDiv = document.getElementById('input-line');
let inputBeforeCursor = inputLineDiv.querySelector('.input-before-cursor');
let inputAfterCursor = inputLineDiv.querySelector('.input-after-cursor');
let cursorSpan = inputLineDiv.querySelector('.cursor');

function updateInputLine() {
    inputBeforeCursor.textContent = inputLine.slice(0, cursorPosition).join('');
    inputAfterCursor.textContent = inputLine.slice(cursorPosition).join('');
}

function processCommand() {
    const input = inputLine.join('').trim();
    const output = document.getElementById('terminal');

    output.removeChild(inputLineDiv);

    const commandLine = document.createElement('div');
    commandLine.textContent = 'C:\\WINDOWS\\SYSTEM32>' + input;
    output.appendChild(commandLine);

    if (input.toLowerCase() === 'clear') {
        terminal.innerHTML = '<div>Microsoft® Windows DOS</div><div>© Microsoft Corp 1990-2001.</div><br>';
    } else {
        const commandOutput = document.createElement('div');
        if (commands[input.toLowerCase()]) {
            commandOutput.innerHTML = commands[input.toLowerCase()].replace(/\n/g, '<br>');
        } else {
            commandOutput.textContent = `'${input}' is not recognized as an internal or external command.`;
        }
        output.appendChild(commandOutput);
    }
    inputLineDiv = document.createElement('div');
    inputLineDiv.id = 'input-line';
    inputLineDiv.innerHTML = 'C:\\WINDOWS\\SYSTEM32>&nbsp;<span class="input-before-cursor"></span><span class="cursor">█</span><span class="input-after-cursor"></span>';
    output.appendChild(inputLineDiv);
    inputLine = [];
    cursorPosition = 0;
    inputBeforeCursor = inputLineDiv.querySelector('.input-before-cursor');
    inputAfterCursor = inputLineDiv.querySelector('.input-after-cursor');
    cursorSpan = inputLineDiv.querySelector('.cursor');

    updateInputLine();
    output.scrollTop = output.scrollHeight;
}

document.addEventListener('keydown', function(e) {
    if (e.key.length === 1 && !e.ctrlKey && !e.altKey) {
        inputLine.splice(cursorPosition, 0, e.key);
        cursorPosition++;
    } else if (e.key === 'Backspace') {
        if (cursorPosition > 0) {
            inputLine.splice(cursorPosition - 1, 1);
            cursorPosition--;
        }
        e.preventDefault(); // Prevent default backspace action
    } else if (e.key === 'Delete') {
        if (cursorPosition < inputLine.length) {
            inputLine.splice(cursorPosition, 1);
        }
    } else if (e.key === 'ArrowLeft') {
        if (cursorPosition > 0) {
            cursorPosition--;
        }
    } else if (e.key === 'ArrowRight') {
        if (cursorPosition < inputLine.length) {
            cursorPosition++;
        }
    } else if (e.key === 'Enter') {
        processCommand();
    } else {
        // Ignore other keys
    }
    updateInputLine();
});
