// tts.js - Core TTS and Highlighting Engine (Fixed Version)

document.addEventListener('DOMContentLoaded', () => {
    if (typeof bookPagesData === 'undefined' || bookPagesData.length === 0) {
        document.getElementById('page-display').innerHTML = "<p>No content available.</p>";
        return;
    }

    const pageDisplay = document.getElementById('page-display');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const pageNumSpan = document.getElementById('current-page-num');
    const progressBar = document.getElementById('progress-bar');

    const playBtn = document.getElementById('tts-play');
    const pauseBtn = document.getElementById('tts-pause');
    const stopBtn = document.getElementById('tts-stop');
    const voiceSelect = document.getElementById('tts-voice');
    const rateSelect = document.getElementById('tts-rate');

    let currentPageIndex = 0;
    const totalPages = bookPagesData.length;
    let sentences = [];

    const synth = window.speechSynthesis;
    let isPlaying = false;
    let isPaused = false;
    let currentSentenceIndex = 0;
    let isStopped = false;

    let timeSpentSeconds = 0;
    setInterval(() => { timeSpentSeconds++; }, 1000);

    function saveProgress(pageIndex) {
        if (typeof bookId === 'undefined') return;
        fetch('/api/update_progress', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                book_id: bookId,
                last_page_read: pageIndex + 1,
                time_spent: timeSpentSeconds
            })
        }).then(res => { if (res.ok) timeSpentSeconds = 0; })
          .catch(err => console.error('Failed to save progress', err));
    }

    setInterval(() => saveProgress(currentPageIndex), 30000);
    window.addEventListener('beforeunload', () => saveProgress(currentPageIndex));

    function isDevanagariText(text) {
        return /[\u0900-\u097F]/.test(text);
    }

    function splitIntoSentences(text) {
        text = text.replace(/\s+/g, ' ').trim();
        let parts = text.split(/(?<=[।॥.!?])\s+/);
        let result = [];
        let buffer = '';
        for (let part of parts) {
            part = part.trim();
            if (!part) continue;
            buffer += (buffer ? ' ' : '') + part;
            if (buffer.length > 15) {
                result.push(buffer);
                buffer = '';
            }
        }
        if (buffer) result.push(buffer);
        return result.filter(s => s.length > 0);
    }

    function renderPage(index, direction = 'none') {
        if (index < 0 || index >= totalPages) return;
        stopTTS();
        if (direction !== 'none') {
            const outClass = direction === 'next' ? 'fade-out-left' : 'fade-out-right';
            pageDisplay.classList.add(outClass);
            setTimeout(() => {
                updateContentAndRender(index);
                pageDisplay.classList.remove(outClass);
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
        saveProgress(index);
        let rawText = bookPagesData[index];
        sentences = splitIntoSentences(rawText);
        let htmlContent = '';
        sentences.forEach((sentence, i) => {
            htmlContent += `<span id="sentence-${i}" class="tts-sentence">${sentence} </span>`;
        });
        pageDisplay.innerHTML = htmlContent;
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
    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowLeft' && currentPageIndex > 0) renderPage(currentPageIndex - 1, 'prev');
        if (e.key === 'ArrowRight' && currentPageIndex < totalPages - 1) renderPage(currentPageIndex + 1, 'next');
    });

    function populateVoiceList() {
        let voices = synth.getVoices();
        if (voices.length === 0) return;
        voiceSelect.innerHTML = '';
        let hasDevanagari = bookPagesData.length > 0 && isDevanagariText(bookPagesData[0]);
        let bestVoiceIndex = 0;
        let foundBest = false;

        voices.forEach((voice, index) => {
            const option = document.createElement('option');
            option.textContent = `${voice.name} (${voice.lang})`;
            option.setAttribute('data-lang', voice.lang);
            option.setAttribute('data-name', voice.name);
            voiceSelect.appendChild(option);

            if (!foundBest) {
                if (hasDevanagari && voice.lang.startsWith('mr')) {
                    bestVoiceIndex = index; foundBest = true;
                } else if (hasDevanagari && voice.lang.startsWith('hi')) {
                    bestVoiceIndex = index;
                } else if (!hasDevanagari && voice.lang.startsWith('en')) {
                    bestVoiceIndex = index; foundBest = true;
                }
            }
        });
        voiceSelect.selectedIndex = bestVoiceIndex;
    }

    populateVoiceList();
    speechSynthesis.onvoiceschanged = populateVoiceList;
    setTimeout(populateVoiceList, 500);
    setTimeout(populateVoiceList, 1500);

    function removeHighlights() {
        document.querySelectorAll('.tts-sentence.highlight').forEach(el => el.classList.remove('highlight'));
    }

    function highlightSentence(index) {
        removeHighlights();
        const el = document.getElementById(`sentence-${index}`);
        if (el) {
            el.classList.add('highlight');
            el.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }

    function getSelectedVoice() {
        const selectedOption = voiceSelect.selectedOptions[0];
        if (!selectedOption) return null;
        const selectedName = selectedOption.getAttribute('data-name');
        return synth.getVoices().find(v => v.name === selectedName) || null;
    }

    function speakSentence(index) {
        if (isStopped) return;
        if (index >= sentences.length) {
            stopTTS();
            if (currentPageIndex < totalPages - 1) {
                renderPage(currentPageIndex + 1, 'next');
                setTimeout(playTTS, 1500);
            }
            return;
        }

        currentSentenceIndex = index;
        highlightSentence(index);

        const text = sentences[index];
        const utterance = new SpeechSynthesisUtterance(text);
        const voice = getSelectedVoice();
        if (voice) {
            utterance.voice = voice;
            utterance.lang = voice.lang;
        } else {
            utterance.lang = isDevanagariText(text) ? 'hi-IN' : 'en-US';
        }
        utterance.rate = parseFloat(rateSelect.value);

        utterance.onstart = () => {
            isPlaying = true;
            isPaused = false;
            updateButtons();
        };

        utterance.onend = () => {
            if (!isStopped && isPlaying && !isPaused) {
                speakSentence(index + 1);
            }
        };

        utterance.onerror = (e) => {
            if (e.error !== 'interrupted' && !isStopped) {
                speakSentence(index + 1);
            }
        };

        synth.speak(utterance);
    }

    function playTTS() {
        if (isPaused) {
            synth.resume();
            isPaused = false;
            isPlaying = true;
            updateButtons();
            return;
        }
        if (sentences.length === 0) return;
        isStopped = false;
        isPlaying = true;
        synth.cancel();
        setTimeout(() => speakSentence(currentSentenceIndex), 150);
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
        isStopped = true;
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

    voiceSelect.addEventListener('change', () => {
        if (isPlaying || isPaused) {
            let saved = currentSentenceIndex;
            stopTTS();
            currentSentenceIndex = saved;
            setTimeout(playTTS, 200);
        }
    });

    rateSelect.addEventListener('change', () => {
        if (isPlaying || isPaused) {
            let saved = currentSentenceIndex;
            stopTTS();
            currentSentenceIndex = saved;
            setTimeout(playTTS, 200);
        }
    });

    let initialPage = 0;
    if (typeof lastPageRead !== 'undefined' && lastPageRead > 0 && lastPageRead <= totalPages) {
        initialPage = lastPageRead - 1;
    }
    renderPage(initialPage, 'none');
});
