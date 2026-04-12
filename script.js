// ═══ Ad2Page — Frontend Logic ═══
// Key philosophy: We ENHANCE the existing page, not replace it.
// The backend should return modifications/injections, not a new page.

document.addEventListener('DOMContentLoaded', () => {

    // ── State ──────────────────────────────────────────────────────────
    let activeTab = 'image';
    let activeDevice = 'desktop';
    let activeView = 'preview';
    let showingEnhanced = true;
    let variations = [];
    let currentVarIndex = 0;
    let originalHtml = '';

    // ── Element refs ───────────────────────────────────────────────────
    const form = document.getElementById('main-form');
    const generateBtn = document.getElementById('generate-btn');
    const btnText = document.getElementById('btn-text');
    const btnIcon = document.getElementById('btn-icon');
    const btnLoader = document.getElementById('btn-loader');
    const statusBar = document.getElementById('status-bar');
    const emptyState = document.getElementById('empty-state');
    const frameWrap = document.getElementById('frame-wrap');
    const iframe = document.getElementById('preview-frame');
    const codeView = document.getElementById('code-view');
    const diffView = document.getElementById('diff-view');
    const codeOutput = document.getElementById('code-output');
    const copyBtn = document.getElementById('copy-btn');
    const urlDisplay = document.getElementById('url-display');
    const resultsMeta = document.getElementById('results-meta');
    const varPills = document.getElementById('var-pills');
    const mismatchText = document.getElementById('mismatch-text');
    const changesList = document.getElementById('changes-list');
    const baAfter = document.getElementById('ba-after');
    const baBefore = document.getElementById('ba-before');
    const diffOriginal = document.getElementById('diff-original');
    const diffEnhanced = document.getElementById('diff-enhanced');
    const iframeShell = document.getElementById('iframe-shell');
    const fileInput = document.getElementById('ad_image');
    const uploadInner = document.getElementById('upload-inner');

    // ── Tab switching ──────────────────────────────────────────────────
    document.querySelectorAll('.itab').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.itab').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
            btn.classList.add('active');
            activeTab = btn.dataset.tab;
            document.getElementById(`tab-${activeTab}`).classList.add('active');
        });
    });

    // ── Tone cards ─────────────────────────────────────────────────────
    document.querySelectorAll('.tone-card').forEach(card => {
        card.addEventListener('click', () => {
            document.querySelectorAll('.tone-card').forEach(c => c.classList.remove('active'));
            card.classList.add('active');
        });
    });

    // ── File upload preview ────────────────────────────────────────────
    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            const file = fileInput.files[0];
            const reader = new FileReader();
            reader.onload = e => {
                uploadInner.innerHTML = `
                    <img src="${e.target.result}" class="upload-preview-img" alt="Ad preview">
                    <p class="upload-sub" style="margin-top:6px; color: var(--accent);">✓ ${file.name}</p>
                `;
            };
            reader.readAsDataURL(file);
        }
    });

    // ── Device toggles ─────────────────────────────────────────────────
    document.querySelectorAll('.dsw').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.dsw').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            activeDevice = btn.dataset.device;
            if (activeDevice === 'mobile') {
                iframeShell.classList.add('mobile');
            } else {
                iframeShell.classList.remove('mobile');
            }
        });
    });

    // ── View toggles ───────────────────────────────────────────────────
    document.querySelectorAll('.vsw').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.vsw').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            activeView = btn.dataset.view;
            updateViewDisplay();
        });
    });

    function updateViewDisplay() {
        frameWrap.classList.toggle('hidden', activeView !== 'preview');
        codeView.classList.toggle('hidden', activeView !== 'code');
        diffView.classList.toggle('hidden', activeView !== 'diff');
    }

    // ── Before/After ───────────────────────────────────────────────────
    baAfter.addEventListener('click', () => {
        showingEnhanced = true;
        baAfter.classList.add('active');
        baBefore.classList.remove('active');
        renderCurrentVariation();
    });

    baBefore.addEventListener('click', () => {
        showingEnhanced = false;
        baBefore.classList.add('active');
        baAfter.classList.remove('active');
        renderOriginal();
    });

    // ── Analysis card toggles ─────────────────────────────────────────
    document.getElementById('ac-toggle').addEventListener('click', () => {
        document.getElementById('ac-body').classList.toggle('hidden');
    });
    document.getElementById('cc-toggle').addEventListener('click', () => {
        document.getElementById('cc-body').classList.toggle('hidden');
    });

    // ── Status step progression ────────────────────────────────────────
    let statusInterval = null;

    function startStatusAnimation() {
        const steps = ['ss1', 'ss2', 'ss3', 'ss4'];
        let currentStep = 0;
        document.querySelectorAll('.sstep').forEach(s => {
            s.classList.remove('active', 'done');
        });
        document.getElementById(steps[0]).classList.add('active');

        statusInterval = setInterval(() => {
            if (currentStep < steps.length - 1) {
                document.getElementById(steps[currentStep]).classList.remove('active');
                document.getElementById(steps[currentStep]).classList.add('done');
                currentStep++;
                document.getElementById(steps[currentStep]).classList.add('active');
            }
        }, 2200);
    }

    function stopStatusAnimation() {
        clearInterval(statusInterval);
        document.querySelectorAll('.sstep').forEach(s => {
            s.classList.remove('active');
            s.classList.add('done');
        });
    }

    // ── Form submit ────────────────────────────────────────────────────
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const landingUrl = document.getElementById('landing_url').value.trim();
        const tone = document.querySelector('input[name="tone"]:checked')?.value || 'professional';

        if (!landingUrl) {
            flashError(document.getElementById('landing_url'), 'Please enter a landing page URL');
            return;
        }

        // Validate active input tab
        if (activeTab === 'image' && fileInput.files.length === 0) {
            flashError(document.getElementById('upload-zone'), 'Please upload an ad image');
            return;
        }
        if (activeTab === 'text' && !document.getElementById('ad_text').value.trim()) {
            flashError(document.getElementById('ad_text'), 'Please enter your ad copy');
            return;
        }
        if (activeTab === 'video' && !document.getElementById('ad_video').value.trim()) {
            flashError(document.getElementById('ad_video'), 'Please enter a video URL');
            return;
        }

        // Build form data
        const formData = new FormData();
        formData.append('landing_url', landingUrl);
        formData.append('tone', tone);

        if (activeTab === 'image') formData.append('file', fileInput.files[0]);
        else if (activeTab === 'text') formData.append('ad_text', document.getElementById('ad_text').value.trim());
        else if (activeTab === 'video') formData.append('ad_video', document.getElementById('ad_video').value.trim());

        // Show loading state
        setLoading(true);
        urlDisplay.textContent = landingUrl;
        startStatusAnimation();
        emptyState.classList.add('hidden');
        frameWrap.classList.add('hidden');
        codeView.classList.add('hidden');
        diffView.classList.add('hidden');
        resultsMeta.classList.add('hidden');

        try {
            const response = await fetch('https://ad2landing-2.onrender.com/api/generate', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                let msg = `Server error (${response.status})`;
                try {
                    const err = await response.json();
                    msg = err.detail || msg;
                } catch { }
                throw new Error(msg);
            }

            const data = await response.json();
            stopStatusAnimation();
            processResponse(data, landingUrl);

        } catch (err) {
            stopStatusAnimation();
            console.error('Generation error:', err);
            showToast(`❌ ${err.message}`, 'error');
            emptyState.classList.remove('hidden');
        } finally {
            setLoading(false);
        }
    });

    // ── Process API response ───────────────────────────────────────────
    function processResponse(data, landingUrl) {
        variations = data.variations || [];

        // Capture original page HTML if provided
        originalHtml = data.original_html || '';

        if (!variations.length) {
            showToast('No variations returned. Check your inputs.', 'error');
            emptyState.classList.remove('hidden');
            return;
        }

        // Show results meta
        resultsMeta.classList.remove('hidden');

        // Mismatch analysis
        const firstVar = variations[0];
        if (firstVar.mismatch_analysis) {
            mismatchText.textContent = firstVar.mismatch_analysis;
        } else if (data.ad_analysis?.key_messages) {
            mismatchText.textContent = `Ad promotes: "${data.ad_analysis.key_messages}". Enhancements align the page messaging and CTAs to match this offer precisely.`;
        }

        // Build variation pills
        varPills.innerHTML = '';
        variations.forEach((v, i) => {
            const pill = document.createElement('button');
            pill.className = `var-pill${i === 0 ? ' active' : ''}`;
            pill.textContent = `Var ${v.variation_number || i + 1}`;
            pill.addEventListener('click', () => {
                document.querySelectorAll('.var-pill').forEach(p => p.classList.remove('active'));
                pill.classList.add('active');
                currentVarIndex = i;
                if (showingEnhanced) renderCurrentVariation();
                else renderOriginal();
            });
            varPills.appendChild(pill);
        });

        currentVarIndex = 0;
        showingEnhanced = true;
        baAfter.classList.add('active');
        baBefore.classList.remove('active');

        renderCurrentVariation();
        buildDiffView();

        // Show frame
        emptyState.classList.add('hidden');
        frameWrap.classList.remove('hidden');
        copyBtn.classList.remove('hidden');

        // Switch to preview
        activeView = 'preview';
        document.querySelectorAll('.vsw').forEach(b => b.classList.remove('active'));
        document.querySelector('.vsw[data-view="preview"]').classList.add('active');
        updateViewDisplay();

        showToast('✓ Personalized page ready!', 'success');
    }

    function renderCurrentVariation() {
        const v = variations[currentVarIndex];
        const html = v.html || '';
        iframe.srcdoc = html;
        codeOutput.textContent = html;

        // Changes list
        changesList.innerHTML = '';
        if (v.change_log?.length) {
            v.change_log.forEach(item => {
                const li = document.createElement('li');
                li.textContent = item.change + (item.reason ? ` — ${item.reason}` : '');
                changesList.appendChild(li);
            });
        } else if (v.changes_summary) {
            // Fallback: split by newline or sentences
            v.changes_summary.split('\n').filter(Boolean).forEach(line => {
                const li = document.createElement('li');
                li.textContent = line.replace(/^[-•*]\s*/, '');
                changesList.appendChild(li);
            });
        } else {
            changesList.innerHTML = '<li style="color:var(--text3)">Enhancements applied to copy, CTAs, and messaging alignment.</li>';
        }
    }

    function renderOriginal() {
        if (originalHtml) {
            iframe.srcdoc = originalHtml;
        } else {
            // Fallback: show original URL in iframe
            const landingUrl = document.getElementById('landing_url').value.trim();
            if (landingUrl) {
                iframe.src = landingUrl;
            }
        }
    }

    function buildDiffView() {
        const v = variations[currentVarIndex];
        const enhanced = v.html || '';

        // Show simplified key changes in diff view (not full HTML diff — too noisy)
        if (v.change_log?.length) {
            diffOriginal.innerHTML = '';
            diffEnhanced.innerHTML = '';

            v.change_log.forEach(item => {
                const origEl = document.createElement('div');
                origEl.style.marginBottom = '12px';
                origEl.innerHTML = `<span class="diff-removed">[BEFORE] ${escHtml(item.original || item.element || item.change || '')}</span>`;
                diffOriginal.appendChild(origEl);

                const enhEl = document.createElement('div');
                enhEl.style.marginBottom = '12px';
                enhEl.innerHTML = `<span class="diff-added">[AFTER] ${escHtml(item.enhanced || item.new_value || item.change || '')}</span>`;
                diffEnhanced.appendChild(enhEl);
            });
        } else {
            diffOriginal.innerHTML = '<span style="color:var(--text3); font-size:12px;">Original content from scraped page.</span>';
            diffEnhanced.innerHTML = '<span style="color:var(--text3); font-size:12px;">Enhanced with ad-matched copy & CRO improvements.</span>';
        }
    }

    // ── Copy HTML ──────────────────────────────────────────────────────
    copyBtn.addEventListener('click', () => {
        const v = variations[currentVarIndex];
        if (!v) return;
        navigator.clipboard.writeText(v.html || '').then(() => {
            copyBtn.classList.add('copied');
            copyBtn.innerHTML = '<i class="fa-solid fa-check"></i> Copied!';
            setTimeout(() => {
                copyBtn.classList.remove('copied');
                copyBtn.innerHTML = '<i class="fa-regular fa-copy"></i> Copy HTML';
            }, 2000);
        });
    });

    document.getElementById('copy-code-btn').addEventListener('click', () => {
        const v = variations[currentVarIndex];
        if (!v) return;
        navigator.clipboard.writeText(v.html || '').then(() => {
            showToast('Code copied to clipboard!', 'success');
        });
    });

    // ── Helpers ────────────────────────────────────────────────────────
    function setLoading(state) {
        generateBtn.disabled = state;
        btnLoader.classList.toggle('hidden', !state);
        btnIcon.classList.toggle('hidden', state);
        btnText.textContent = state ? 'Personalizing...' : 'Personalize Page';
        statusBar.classList.toggle('hidden', !state);
    }

    function flashError(el, msg) {
        el.style.borderColor = 'var(--red)';
        showToast(msg, 'error');
        setTimeout(() => { el.style.borderColor = ''; }, 2500);
    }

    function escHtml(str) {
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    // ── Toast notifications ────────────────────────────────────────────
    function showToast(msg, type = 'success') {
        const existing = document.querySelector('.toast');
        if (existing) existing.remove();

        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.style.cssText = `
            position: fixed;
            bottom: 24px;
            right: 24px;
            background: ${type === 'success' ? 'var(--green)' : 'var(--red)'};
            color: #fff;
            padding: 10px 18px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 500;
            font-family: var(--font-body);
            z-index: 9999;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            animation: slideInToast 0.3s ease;
        `;
        toast.textContent = msg;

        const style = document.createElement('style');
        style.textContent = `@keyframes slideInToast { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }`;
        document.head.appendChild(style);

        document.body.appendChild(toast);
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transition = 'opacity 0.3s';
            setTimeout(() => toast.remove(), 300);
        }, 3500);
    }
});