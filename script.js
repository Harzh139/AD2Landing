document.addEventListener('DOMContentLoaded', () => {
    // Tab switching logic
    const tabs = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    let activeInputType = 'image';

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            
            tab.classList.add('active');
            const targetId = `tab-${tab.dataset.tab}`;
            document.getElementById(targetId).classList.add('active');
            activeInputType = tab.dataset.tab;
        });
    });

    // File upload logic
    const fileInput = document.getElementById('ad_image');
    const fileNameDisplay = document.getElementById('file-name');
    const fileDropArea = document.getElementById('file-drop-area');

    fileInput.addEventListener('change', (e) => {
        if (fileInput.files.length > 0) {
            fileNameDisplay.textContent = fileInput.files[0].name;
            fileDropArea.style.borderColor = 'var(--primary)';
        }
    });

    // Device toggles
    const deviceBtns = document.querySelectorAll('.toggle-btn');
    const iframeContainer = document.getElementById('iframe-container');

    deviceBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            deviceBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            if (btn.dataset.device === 'mobile') {
                iframeContainer.className = 'iframe-container mobile';
            } else {
                iframeContainer.className = 'iframe-container desktop';
            }
        });
    });

    // Form submission
    const form = document.getElementById('generator-form');
    const generateBtn = document.getElementById('generate-btn');
    const statusMsg = document.getElementById('status-message');
    const statusText = document.getElementById('status-text');
    const iframe = document.getElementById('preview-frame');
    const analysisPanel = document.getElementById('analysis-panel');
    const analysisJson = document.getElementById('analysis-json');
    const minimizePanelBtn = document.getElementById('minimize-panel-btn');
    const copyBtn = document.getElementById('copy-btn');
    const viewBtns = document.querySelectorAll('.view-btn');
    const codeContainer = document.getElementById('code-container');
    const codeOutput = document.getElementById('code-output');
    
    let currentVariations = [];
    let currentHtmlStr = '';

    // Minimize panel logic
    minimizePanelBtn.addEventListener('click', () => {
        analysisPanel.classList.toggle('minimized');
    });

    // View Toggles
    viewBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            viewBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            if (btn.dataset.view === 'preview') {
                iframeContainer.classList.remove('hidden');
                codeContainer.classList.add('hidden');
            } else {
                iframeContainer.classList.add('hidden');
                codeContainer.classList.remove('hidden');
            }
        });
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const landingUrl = document.getElementById('landing_url').value;
        const tone = document.getElementById('tone').value;
        
        if (!landingUrl) {
            alert('Please enter a target landing page URL');
            return;
        }

        const formData = new FormData();
        formData.append('landing_url', landingUrl);
        formData.append('tone', tone);

        if (activeInputType === 'image') {
            if (fileInput.files.length === 0) {
                alert('Please upload an ad image');
                return;
            }
            formData.append('file', fileInput.files[0]);
        } else if (activeInputType === 'text') {
            const text = document.getElementById('ad_text').value;
            if (!text.trim()) {
                alert('Please enter ad text');
                return;
            }
            formData.append('ad_text', text);
        } else if (activeInputType === 'video') {
            const video = document.getElementById('ad_video').value;
            if (!video.trim()) {
                alert('Please enter ad video link');
                return;
            }
            formData.append('ad_video', video);
        }

        generateBtn.disabled = true;
        statusMsg.classList.remove('hidden');
        analysisPanel.classList.add('hidden');
        copyBtn.disabled = true;
        statusText.textContent = 'Analyzing ad and scraping landing page...';

        try {
            const response = await fetch('http://localhost:8000/api/generate', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to generate page');
            }

            const data = await response.json();

            statusText.textContent = 'Generation Complete!';
            setTimeout(() => {
                statusMsg.classList.add('hidden');
            }, 2000);

            currentVariations = data.variations;
            if (currentVariations && currentVariations.length > 0) {
                renderVariationControls();
                setVariation(0);
            }

            if (data.ad_analysis) {
                let analysisText = JSON.stringify(data.ad_analysis, null, 2);
                if (currentVariations.length > 0 && currentVariations[0].mismatch_analysis) {
                    analysisText = `MISMATCH ANALYSIS:\n${currentVariations[0].mismatch_analysis}\n\nAD DATA:\n${analysisText}`;
                }
                analysisJson.textContent = analysisText;
                analysisPanel.classList.remove('hidden');
            }

            copyBtn.disabled = false;

        } catch (error) {
            console.error('Error:', error);
            statusText.textContent = `Error: ${error.message}`;
            statusMsg.querySelector('.spinner').style.display = 'none';
        } finally {
            generateBtn.disabled = false;
        }
    });

    function renderVariationControls() {
        const toggleContainer = document.getElementById('variation-toggles');
        toggleContainer.innerHTML = '';
        currentVariations.forEach((v, index) => {
            const btn = document.createElement('button');
            btn.className = `var-btn ${index === 0 ? 'active' : ''}`;
            btn.textContent = `Var ${v.variation_number}`;
            btn.addEventListener('click', () => {
                document.querySelectorAll('.var-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                setVariation(index);
            });
            toggleContainer.appendChild(btn);
        });
    }

    function setVariation(index) {
        currentHtmlStr = currentVariations[index].html;
        iframe.srcdoc = currentHtmlStr;
        codeOutput.textContent = currentHtmlStr;
    }

    copyBtn.addEventListener('click', () => {
        if (!currentHtmlStr) return;
        navigator.clipboard.writeText(currentHtmlStr).then(() => {
            const originalHtml = copyBtn.innerHTML;
            copyBtn.innerHTML = '<i class="fa-solid fa-check"></i> Copied!';
            setTimeout(() => {
                copyBtn.innerHTML = originalHtml;
            }, 2000);
        });
    });
});
