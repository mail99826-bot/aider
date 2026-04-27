document.addEventListener('DOMContentLoaded', () => {
    // Import playlist data

    // DOM elements
    const playlistTitle = document.getElementById('playlist-title');
    const lessonSelector = document.getElementById('lesson-selector');
    const lineNumbers = document.getElementById('line-numbers');
    const notesEditor = document.getElementById('notes-editor');
    const themeToggle = document.querySelector('.theme-toggle');
    
    // YouTube player
    let player;

    // Initialize app
    function init() {
        playlistTitle.textContent = playlist.title;
        populateLessonSelector();
        initYouTubePlayer();
        setupNoteEditor();
        setupThemeToggle();
        
        // Load first lesson by default
        if (playlist.lessons.length > 0) {
            lessonSelector.value = 0;
            loadLesson(0);
        }
    }

    // Populate lesson selector dropdown
    function populateLessonSelector() {
        playlist.lessons.forEach((lesson, index) => {
            const option = document.createElement('option');
            option.value = index;
            option.textContent = lesson.name;
            lessonSelector.appendChild(option);
        });
        
        lessonSelector.addEventListener('change', () => {
            loadLesson(lessonSelector.value);
        });
    }

    // Initialize YouTube player
    function initYouTubePlayer() {
        window.onYouTubeIframeAPIReady = function() {
            // This will be overwritten when a lesson is loaded
            player = new YT.Player('player');
        };
    }

    // Load selected lesson
    function loadLesson(index) {
        const lesson = playlist.lessons[index];
        if (!lesson) return;

        if (player.loadVideoById) {
            player.loadVideoById(lesson.videoId);
        } else {
            player = new YT.Player('player', {
                height: '100%',
                width: '100%',
                videoId: lesson.videoId,
                playerVars: {
                    'autoplay': 1,
                    'controls': 1,
                    'rel': 0
                }
            });
        }
    }

    // Setup line-numbered note editor
    function setupNoteEditor() {
        let lines = [''];
        
        // Initial render
        renderEditor();
        
        notesEditor.addEventListener('input', handleEditorInput);
        notesEditor.addEventListener('keydown', handleEditorKeyDown);
        
        function handleEditorInput(e) {
            updateLines();
        }
        
        function handleEditorKeyDown(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                insertNewLine();
                updateLines();
            }
        }

        function updateLines() {
            // Получаем все div элементы внутри редактора (каждая строка - это div)
            const lineNodes = notesEditor.querySelectorAll('div');
            lines = Array.from(lineNodes).map(div => 
                div.textContent === '\n' ? '' : div.textContent
            );
            renderLineNumbers();
        }
        
        function insertNewLine() {
            const selection = window.getSelection();
            const range = selection.getRangeAt(0);
            const currentLineNode = getCurrentLineNode(range.startContainer);
            
            if (!currentLineNode) return;
            
            // Create new line
            const newLine = document.createElement('div');
            newLine.innerHTML = '<br>';
            
            // Insert after current line
            currentLineNode.parentNode.insertBefore(newLine, currentLineNode.nextSibling);
            
            // Move cursor to new line
            range.setStart(newLine, 0);
            range.collapse(true);
            selection.removeAllRanges();
            selection.addRange(range);
            
            // Update lines array
            lines = notesEditor.textContent.replace(/\n$/, '').split('\n');
            renderLineNumbers();
        }
        
        function getCurrentLineNode(node) {
            while (node && node !== notesEditor) {
                if (node.parentNode === notesEditor) {
                    return node;
                }
                node = node.parentNode;
            }
            return null;
        }
        
        function renderEditor() {
            // Создаем начальную пустую строку
            const initialLine = document.createElement('div');
            initialLine.innerHTML = '<br>';
            notesEditor.appendChild(initialLine);
            updateLines();
            notesEditor.focus();
        }
        
        function renderLineNumbers() {
            lineNumbers.innerHTML = lines.map((_, i) => 
                `<div>${i + 1}</div>`
            ).join('');
        }
    }

    // Setup theme toggle
    function setupThemeToggle() {
        const theme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-theme', theme);
        
        if (theme === 'dark') {
            themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
        } else {
            themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
        }
        
        themeToggle.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            
            if (newTheme === 'dark') {
                themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
            } else {
                themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
            }
        });
    }

    init();
});
