// tts.js - Core TTS and Highlighting Engine

document.addEventListener('DOMContentLoaded', () => {
    // Check if pages data exists
    if (typeof bookPagesData === 'undefined' || bookPagesData.length === 0) {
        document.getElementById('page-display').innerHTML = "<p>No content available.</p>";
        return;
    }

    const pageDisplay = document.getElementById('page-display');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const pageNumSpan = document.getElementById('current-page-num');
    const progressBar = document.getElementById('progress-bar');
    
    // TTS Controls
    const playBtn = document.getElementById('tts-play');
    const pauseBtn = document.getElementById('tts-pause');
    const stopBtn = document.getElementById('tts-stop');
    const voiceSelect = document.getElementById('tts-voice');
    const rateSelect = document.getElementById('tts-rate');

    let currentPageIndex = 0;
    const totalPages = bookPagesData.length;
    let sentences = [];
    
    // Speech Synthesis setup
    const synth = window.speechSynthesis;
    let utterance = null;
    let isPlaying = false;
    let isPaused = false;
    let currentSentenceIndex = 0;
    
    // Progress Tracking
    let timeSpentSeconds = 0;
    let timeTrackingInterval = setInterval(() => {
        timeSpentSeconds++;
    }, 1000);

    function saveProgress(pageIndex) {
        if (typeof bookId === 'undefined') return;
        
        fetch('/api/update_progress', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                book_id: bookId,
                last_page_read: pageIndex + 1,
                time_spent: timeSpentSeconds
            })
        }).then(res => {
            if (res.ok) timeSpentSeconds = 0; // Reset after successful save
        }).catch(err => console.error('Failed to save progress', err));
    }

    // Save progress periodically and when leaving
    setInterval(() => saveProgress(currentPageIndex), 30000); // Save every 30s
    window.addEventListener('beforeunload', () => saveProgress(currentPageIndex));

    // --- Pagination & Content Rendering ---
    
    function renderPage(index, direction = 'none') {
        if (index < 0 || index >= totalPages) return;
        
        // Stop any ongoing speech when turning page
        stopTTS();
        
        // Animation Logic
        if (direction !== 'none') {
            const outClass = direction === 'next' ? 'fade-out-left' : 'fade-out-right';
            pageDisplay.classList.add(outClass);
            
            setTimeout(() => {
                updateContentAndRender(index);
                pageDisplay.classList.remove(outClass);
                // Trigger reflow
                void pageDisplay.offsetWidth;
            }, 300);
        } else {
            updateContentAndRender(index);
        }
    }
    
    function updateContentAndRender(index) {
        currentPageIndex = index;
        pageNumSpan.textContent = index + 1;
        progressBar.style.setProperty('--progress', `${((index + 1) / totalPages) * 100}%`);
        
        // Save progress when turning pages
        saveProgress(index);
        
        let rawText = bookPagesData[index];
        
        // Regex to split by sentences (handles period, question mark, exclamation point, Devanagari danda, or newlines)
        let sentenceMatches = rawText.match(/[^.!?।॥\n]+[.!?।॥\n]+(?:\s|$)|[^.!?।॥\n]+$/g);
        
        if (!sentenceMatches || sentenceMatches.length === 0) {
            sentenceMatches = [rawText];
        }

        sentences = sentenceMatches.map(s => s.trim()).filter(s => s.length > 0);
        
        let htmlContent = '';
        sentences.forEach((sentence, i) => {
            htmlContent += `<span id="sentence-${i}" class="tts-sentence">${sentence} </span>`;
        });
        
        pageDisplay.innerHTML = htmlContent;
        
        // Update nav buttons
        prevBtn.style.opacity = index === 0 ? '0.3' : '1';
        prevBtn.style.pointerEvents = index === 0 ? 'none' : 'auto';
        
        nextBtn.style.opacity = index === totalPages - 1 ? '0.3' : '1';
        nextBtn.style.pointerEvents = index === totalPages - 1 ? 'none' : 'auto';
    }

    prevBtn.addEventListener('click', () => {
        if (currentPageIndex > 0) renderPage(currentPageIndex - 1, 'prev');
    });

    nextBtn.addEventListener('click', () => {
        if (currentPageIndex < totalPages - 1) renderPage(currentPageIndex + 1, 'next');
    });

    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowLeft') {
            if (currentPageIndex > 0) renderPage(currentPageIndex - 1, 'prev');
        } else if (e.key === 'ArrowRight') {
            if (currentPageIndex < totalPages - 1) renderPage(currentPageIndex + 1, 'next');
        }
    });

    // --- TTS Logic ---

    function populateVoiceList() {
        let voices = synth.getVoices();
        voiceSelect.innerHTML = '';
        
        // Detect language of the book to auto-select the best voice
        let hasDevanagari = false;
        if (bookPagesData.length > 0 && /[\u0900-\u097F]/.test(bookPagesData[0])) {
            hasDevanagari = true;
        }

        let bestVoiceIndex = 0;
        let foundMatch = false;

        voices.forEach((voice, index) => {
            const option = document.createElement('option');
            option.textContent = `${voice.name} (${voice.lang})`;
            option.setAttribute('data-lang', voice.lang);
            option.setAttribute('data-name', voice.name);
            voiceSelect.appendChild(option);
            
            // Auto-select logic
            if (!foundMatch) {
                if (hasDevanagari && (voice.lang.includes('mr') || voice.lang.includes('hi') || voice.lang.includes('in'))) {
                    bestVoiceIndex = index;
                    foundMatch = true;
                } else if (!hasDevanagari && (voice.lang.includes('en') || voice.lang.includes('us') || voice.lang.includes('gb'))) {
                    if (voice.default || voice.name.includes('Google')) {
                        bestVoiceIndex = index;
                        foundMatch = true;
                    } else if (bestVoiceIndex === 0) {
                        bestVoiceIndex = index; // Fallback to first English
                    }
                }
            }
        });
        
        if (voices.length > 0) {
            voiceSelect.selectedIndex = bestVoiceIndex;
        }
    }

    populateVoiceList();
    if (speechSynthesis.onvoiceschanged !== undefined) {
        speechSynthesis.onvoiceschanged = populateVoiceList;
    }

    function removeHighlights() {
        document.querySelectorAll('.tts-sentence.highlight').forEach(el => {
            el.classList.remove('highlight');
        });
    }

    function highlightSentence(index) {
        removeHighlights();
        const el = document.getElementById(`sentence-${index}`);
        if (el) {
            el.classList.add('highlight');
            // Auto scroll to element smoothly
            el.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }

    function playTTS() {
        if (synth.speaking && isPaused) {
            synth.resume();
            isPaused = false;
            isPlaying = true;
            updateButtons();
            return;
        }

        if (synth.speaking) {
            console.error('speechSynthesis.speaking');
            return;
        }

        if (sentences.length === 0) return;

        // Create utterance containing all sentences joined, or read them sequentially
        // To get accurate word boundaries, we speak sentence by sentence using recursion
        
        currentSentenceIndex = 0;
        speakNextSentence();
    }
    
    function speakNextSentence() {
        if (currentSentenceIndex >= sentences.length) {
            stopTTS();
            // Automatically turn page when done if not last page
            if (currentPageIndex < totalPages - 1) {
                renderPage(currentPageIndex + 1, 'next');
                setTimeout(playTTS, 1500); // Wait for animation then continue reading
            }
            return;
        }

        const textToSpeak = sentences[currentSentenceIndex];
        utterance = new SpeechSynthesisUtterance(textToSpeak);
        
        // Apply voice and rate based on dropdown selection
        const selectedOption = voiceSelect.selectedOptions[0];
        if (selectedOption) {
            const selectedName = selectedOption.getAttribute('data-name');
            const voices = synth.getVoices();
            for (let i = 0; i < voices.length; i++) {
                if (voices[i].name === selectedName) {
                    utterance.voice = voices[i];
                    break;
                }
            }
        }
        
        utterance.rate = parseFloat(rateSelect.value);

        utterance.onstart = () => {
            isPlaying = true;
            isPaused = false;
            updateButtons();
            highlightSentence(currentSentenceIndex);
        };

        utterance.onend = () => {
            if (isPlaying && !isPaused) {
                currentSentenceIndex++;
                speakNextSentence();
            }
        };

        utterance.onerror = (e) => {
            console.error('SpeechSynthesisUtterance.onerror', e);
            // Sometimes it throws error on manual stop, ignore if so
        };

        synth.speak(utterance);
    }

    function pauseTTS() {
        if (synth.speaking && !synth.paused) {
            synth.pause();
            isPaused = true;
            isPlaying = false;
            updateButtons();
        }
    }

    function stopTTS() {
        synth.cancel();
        isPlaying = false;
        isPaused = false;
        currentSentenceIndex = 0;
        removeHighlights();
        updateButtons();
    }

    function updateButtons() {
        if (isPlaying && !isPaused) {
            playBtn.disabled = true;
            playBtn.classList.add('playing-pulse');
            pauseBtn.disabled = false;
            stopBtn.disabled = false;
        } else if (isPaused) {
            playBtn.disabled = false;
            playBtn.classList.remove('playing-pulse');
            pauseBtn.disabled = true;
            stopBtn.disabled = false;
        } else {
            playBtn.disabled = false;
            playBtn.classList.remove('playing-pulse');
            pauseBtn.disabled = true;
            stopBtn.disabled = true;
        }
    }

    playBtn.addEventListener('click', playTTS);
    pauseBtn.addEventListener('click', pauseTTS);
    stopBtn.addEventListener('click', stopTTS);
    
    // Stop TTS if user changes voice or rate while playing
    voiceSelect.addEventListener('change', () => {
        if (isPlaying) {
            stopTTS();
            playTTS();
        }
    });
    
    rateSelect.addEventListener('change', () => {
        if (isPlaying) {
            stopTTS();
            playTTS();
        }
    });

    // Initial render using saved progress if available
    let initialPage = 0;
    if (typeof lastPageRead !== 'undefined' && lastPageRead > 0 && lastPageRead <= totalPages) {
        initialPage = lastPageRead - 1;
    }
    renderPage(initialPage, 'none');
});
