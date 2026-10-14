import os
import sys
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import gradio as gr

# Setup core paths
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from components import tab1_record, tab2_review, tab3_player
from components.tab1_record import get_current_sentence_display, resolve_category, get_tts_language_for_category
from components.tab2_review import get_sentence_choices

def load_from_url(tab1_category, request: gr.Request):
    tab_sel = "tab-1"
    choice_sel = None
    choices = get_sentence_choices()

    if request and hasattr(request, 'query_params'):
        # Route specific tabs
        target_tab = request.query_params.get("tab")
        if target_tab == "review":
            tab_sel = "tab-2"
        
        # Deep link specific audio
        item_id = request.query_params.get("id")
        if item_id is not None:
            try:
                idx = int(item_id)
                if idx < len(choices):
                    tab_sel = "tab-2"
                    choice_sel = choices[idx]
            except ValueError:
                pass
                
    resolved_cat = resolve_category(tab1_category)
    sentence_html = get_current_sentence_display(resolved_cat)
    tts_lang = get_tts_language_for_category(resolved_cat)
    return gr.update(selected=tab_sel), gr.update(value=choice_sel, choices=choices), gr.update(value=resolved_cat), sentence_html, gr.update(value=tts_lang)


css = """
.audio-container { position: relative !important; }

/* We keep native backward/forward visible now so the full cluster matches the image */

.overlay-row {
    position: absolute !important;
    bottom: 35px !important;
    left: 0 !important;
    width: 100% !important;
    display: flex !important;
    justify-content: center !important;
    gap: 15px !important;
    pointer-events: none !important; /* allow clicks to pass through empty space */
}

.overlay-icon { 
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: var(--body-text-color) !important;
    font-size: 22px !important;
    min-width: unset !important;
    padding: 0 !important;
    width: 34px !important;
    height: 34px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    pointer-events: auto !important; /* re-enable clicks on the buttons */
}
.overlay-icon:hover {
    color: var(--color-accent) !important;
}

/* Positioning them perfectly around the native Play/Backward/Forward cluster */
.prev-icon { 
    position: absolute !important;
    left: calc(50% - 75px) !important; 
    margin-left: 0 !important;
    font-size: 20px !important;
}
.next-icon { 
    position: absolute !important;
    left: calc(50% + 41px) !important; 
    margin-left: 0 !important;
    font-size: 20px !important;
}
.review-icon { 
    position: absolute !important;
    left: auto !important; 
    right: 25px !important; 
    bottom: 4px !important;
    margin-left: 0 !important; 
    border: 1px solid var(--border-color-primary) !important;
    border-radius: 6px !important;
    width: auto !important;
    height: 26px !important;
    padding: 0 12px !important;
    font-size: 13px !important;
}

/* TTS Voice Action Buttons - render as normal buttons without radio circles */
.tts-action-buttons input[type="radio"] {
    display: none !important;
}

.tts-action-buttons label {
    cursor: pointer !important;
    justify-content: center !important;
    text-align: center !important;
    transition: all 0.15s ease-in-out !important;
    user-select: none !important;
}

.tts-action-buttons label span {
    margin-left: 0 !important;
    margin-right: 0 !important;
    text-align: center !important;
}

.tts-action-buttons label:hover {
    background-color: var(--button-secondary-background-fill-hover, rgba(255, 255, 255, 0.08)) !important;
    border-color: var(--button-secondary-border-color-hover, var(--border-color-accent)) !important;
}

.tts-action-buttons label:active {
    transform: translateY(1px) !important;
    background-color: var(--button-secondary-background-fill, rgba(255, 255, 255, 0.12)) !important;
}

/* Remove persistent selected highlight so it behaves like a normal button click */
.tts-action-buttons label.selected,
.tts-action-buttons label:has(input:checked) {
    background-color: transparent !important;
    border-color: var(--border-color-primary) !important;
}

.tts-action-buttons label.selected:hover,
.tts-action-buttons label:has(input:checked):hover {
    background-color: var(--button-secondary-background-fill-hover, rgba(255, 255, 255, 0.08)) !important;
}

.tts-action-buttons label:focus,
.tts-action-buttons label:focus-within {
    outline: none !important;
    box-shadow: none !important;
}

/* Italicize 'Select Category / Language' options & text in Tab 1 */
.category-dropdown,
.category-dropdown input,
.category-dropdown .wrap,
.category-dropdown span,
.category-dropdown [role="option"],
.category-dropdown li,
.category-dropdown .single-select {
    font-style: italic !important;
}

/* Main sentence row & Prev / Next navigation buttons */
.main-sentence-row {
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
    margin: 8px 0 !important;
}

.main-sentence-row .sentence-box {
    flex: 8 1 0% !important;
    order: 2 !important;
}

.main-sentence-row .prev-sent-btn {
    flex: 1 1 auto !important;
    order: 1 !important;
    min-width: 75px !important;
}

.main-sentence-row .next-sent-btn {
    flex: 1 1 auto !important;
    order: 3 !important;
    min-width: 75px !important;
}

.sentence-box {
    background: var(--input-background-fill) !important;
    border: var(--input-border-width) solid var(--input-border-color) !important;
    border-radius: var(--input-radius) !important;
    padding: 12px 18px !important;
    min-height: 84px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    text-align: center !important;
}

.sentence-box *,
.sentence-box .prose,
.sentence-box .prose * {
    text-align: center !important;
    justify-content: center !important;
    align-items: center !important;
}

.sentence-box .prose {
    width: 100% !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
}

.sent-nav-btn {
    height: 44px !important;
    min-height: 44px !important;
    align-self: center !important;
    font-weight: 600 !important;
    border: 1px solid var(--border-color-primary) !important;
    background: var(--button-secondary-background-fill) !important;
    border-radius: var(--radius-sm, 6px) !important;
}

.sent-nav-btn:hover {
    background: var(--button-secondary-background-fill-hover) !important;
    color: var(--color-accent) !important;
}

/* Small screen responsiveness for Tab 1 sentence and navigation */
@media (max-width: 640px) {
    .main-sentence-row {
        flex-wrap: wrap !important;
        gap: 10px 8px !important;
    }
    
    .main-sentence-row .sentence-box {
        order: 1 !important;
        flex: 1 1 100% !important;
        width: 100% !important;
        min-width: 100% !important;
    }
    
    .main-sentence-row .prev-sent-btn {
        order: 2 !important;
        flex: 1 1 calc(50% - 4px) !important;
        width: calc(50% - 4px) !important;
        height: 38px !important;
        min-height: 38px !important;
    }
    
    .main-sentence-row .next-sent-btn {
        order: 3 !important;
        flex: 1 1 calc(50% - 4px) !important;
        width: calc(50% - 4px) !important;
        height: 38px !important;
        min-height: 38px !important;
    }
}

/* Filter & Search Box container */
.filter-search-box {
    margin-bottom: 6px !important;
    gap: 4px !important;
}

.filter-search-box > .row:first-child {
    margin-bottom: 2px !important;
}

/* Pagination controls row */
.pagination-controls-row,
.pagination-top-row {
    display: flex !important;
    flex-direction: row !important;
    justify-content: flex-end !important;
    align-items: center !important;
    gap: 4px !important;
    height: 22px !important;
    min-height: 22px !important;
    margin: 4px 0 2px 0 !important;
    padding: 0 !important;
    width: 100% !important;
    box-sizing: border-box !important;
}

/* Centered pagination status row below pagination */
.pagination-status-row {
    display: flex !important;
    flex-direction: row !important;
    justify-content: center !important;
    align-items: center !important;
    text-align: center !important;
    margin: 2px 0 4px 0 !important;
    padding: 0 !important;
    width: 100% !important;
    box-sizing: border-box !important;
}

.pagination-status,
.pagination-status * {
    font-size: 11px !important;
    color: var(--body-text-color-subdued, #a1a1aa) !important;
    white-space: nowrap !important;
    line-height: 18px !important;
    text-align: center !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    margin: 0 !important;
    padding: 0 !important;
}

.pagination-btn {
    height: 20px !important;
    min-height: 20px !important;
    max-height: 20px !important;
    line-height: 18px !important;
    padding: 0 8px !important;
    font-size: 11px !important;
    font-weight: 500 !important;
    border: 1px solid var(--border-color-primary, #3f3f46) !important;
    border-radius: 4px !important;
    background: var(--button-secondary-background-fill, #27272a) !important;
    color: var(--body-text-color, #e4e4e7) !important;
    white-space: nowrap !important;
    flex-shrink: 0 !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    cursor: pointer !important;
    box-shadow: none !important;
    margin: 0 !important;
    transition: all 0.15s ease !important;
}

.pagination-btn:hover {
    background: var(--button-secondary-background-fill-hover, #3f3f46) !important;
    color: var(--color-accent, #ea580c) !important;
    border-color: var(--border-color-accent, #71717a) !important;
}

/* Jump input styling */
.jump-input,
.jump-input > div,
.jump-input .block,
.jump-input .wrap,
.jump-input .form {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    margin: 0 !important;
    width: 32px !important;
    min-width: 32px !important;
    max-width: 32px !important;
    height: 20px !important;
    min-height: 20px !important;
    max-height: 20px !important;
    display: inline-flex !important;
    align-items: center !important;
}

.jump-input input[type="number"],
.jump-input input {
    width: 32px !important;
    min-width: 32px !important;
    max-width: 32px !important;
    height: 20px !important;
    min-height: 20px !important;
    max-height: 20px !important;
    line-height: 18px !important;
    font-size: 11px !important;
    text-align: center !important;
    padding: 0 !important;
    margin: 0 !important;
    background: var(--input-background-fill, #18181b) !important;
    border: 1px solid var(--border-color-primary, #3f3f46) !important;
    border-radius: 4px !important;
    color: var(--body-text-color, #e4e4e7) !important;
    box-shadow: none !important;
    -moz-appearance: textfield !important;
}

.jump-input input::-webkit-outer-spin-button,
.jump-input input::-webkit-inner-spin-button {
    -webkit-appearance: none !important;
    margin: 0 !important;
}

/* Default table toolbar & action buttons in default positions */
.voice-tracks-table .toolbar {
    display: flex !important;
    align-items: center !important;
    justify-content: flex-end !important;
    gap: 4px !important;
}

.voice-tracks-table .toolbar-buttons {
    display: inline-flex !important;
    align-items: center !important;
    gap: 4px !important;
}

.voice-tracks-table .toolbar-buttons button {
    height: 20px !important;
    min-height: 20px !important;
    max-height: 20px !important;
    width: 22px !important;
    min-width: 22px !important;
    max-width: 22px !important;
    padding: 0 !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
}

/* Responsive adjustment for small screens */
@media (max-width: 640px) {
    .pagination-top-row {
        justify-content: space-between !important;
        gap: 3px !important;
    }
}

/* Scrollbar styling: Totally hide/remove all scrollbars across all elements & pages; only keep in fullscreen table */
html, body, * {
    scrollbar-width: none !important;
    -ms-overflow-style: none !important;
}

::-webkit-scrollbar,
*::-webkit-scrollbar {
    display: none !important;
    width: 0 !important;
    height: 0 !important;
    background: transparent !important;
}

/* Only display scroll indicator thumb when table is in fullscreen mode */
.voice-tracks-table.fullscreen,
.voice-tracks-table.fullscreen *,
.table-container.fullscreen,
.table-container.fullscreen *,
.voice-tracks-table:has(.fullscreen),
.voice-tracks-table:has(.fullscreen) *,
:fullscreen .voice-tracks-table,
:fullscreen .voice-tracks-table * {
    scrollbar-width: thin !important;
    scrollbar-color: var(--border-color-primary, rgba(255, 255, 255, 0.25)) transparent !important;
}

.voice-tracks-table.fullscreen ::-webkit-scrollbar,
.table-container.fullscreen ::-webkit-scrollbar,
.voice-tracks-table:has(.fullscreen) ::-webkit-scrollbar,
:fullscreen .voice-tracks-table ::-webkit-scrollbar {
    display: block !important;
    width: 6px !important;
    height: 6px !important;
    background: transparent !important;
}

.voice-tracks-table.fullscreen ::-webkit-scrollbar-track,
.table-container.fullscreen ::-webkit-scrollbar-track,
.voice-tracks-table:has(.fullscreen) ::-webkit-scrollbar-track,
:fullscreen .voice-tracks-table ::-webkit-scrollbar-track {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

.voice-tracks-table.fullscreen ::-webkit-scrollbar-button,
.table-container.fullscreen ::-webkit-scrollbar-button,
.voice-tracks-table:has(.fullscreen) ::-webkit-scrollbar-button,
:fullscreen .voice-tracks-table ::-webkit-scrollbar-button {
    display: none !important;
    width: 0 !important;
    height: 0 !important;
}

.voice-tracks-table.fullscreen ::-webkit-scrollbar-corner,
.table-container.fullscreen ::-webkit-scrollbar-corner,
.voice-tracks-table:has(.fullscreen) ::-webkit-scrollbar-corner,
:fullscreen .voice-tracks-table ::-webkit-scrollbar-corner {
    background: transparent !important;
}

.voice-tracks-table.fullscreen ::-webkit-scrollbar-thumb,
.table-container.fullscreen ::-webkit-scrollbar-thumb,
.voice-tracks-table:has(.fullscreen) ::-webkit-scrollbar-thumb,
:fullscreen .voice-tracks-table ::-webkit-scrollbar-thumb {
    display: block !important;
    background: var(--border-color-primary, rgba(255, 255, 255, 0.25)) !important;
    border-radius: 9999px !important;
    border: none !important;
}

.voice-tracks-table.fullscreen ::-webkit-scrollbar-thumb:hover,
.table-container.fullscreen ::-webkit-scrollbar-thumb:hover,
.voice-tracks-table:has(.fullscreen) ::-webkit-scrollbar-thumb:hover,
:fullscreen .voice-tracks-table ::-webkit-scrollbar-thumb:hover {
    background: var(--color-accent, #bd6516) !important;
}

/* Table view options row: cleanly aligned immediately below table */
#fs_sync_row,
.fs-sync-row {
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
    margin-top: 6px !important;
    margin-bottom: 10px !important;
}

.fs-sync-row > * {
    margin: 0 !important;
}

.fs-sync-row .gradio-checkbox label {
    font-size: 13px !important;
    font-weight: 500 !important;
    cursor: pointer !important;
}

.fs-sync-row button {
    height: 38px !important;
    min-height: 38px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
}

/* Pop-up Modal Dialog Styling */
.modal-overlay:not(.hide-container):not(.hidden):not([style*="display: none"]) {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    width: 100vw !important;
    height: 100vh !important;
    background: rgba(0, 0, 0, 0.72) !important;
    backdrop-filter: blur(5px) !important;
    -webkit-backdrop-filter: blur(5px) !important;
    z-index: 99999 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    padding: 20px !important;
    box-sizing: border-box !important;
}

.modal-overlay.hide-container,
.modal-overlay.hidden,
.modal-overlay[style*="display: none"] {
    display: none !important;
}

.modal-card {
    background: var(--background-fill-primary, #18181b) !important;
    border: 1px solid var(--border-color-primary, #3f3f46) !important;
    border-radius: 12px !important;
    padding: 24px !important;
    width: 100% !important;
    max-width: 650px !important;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7) !important;
    margin: auto !important;
}

.modal-header {
    display: flex !important;
    align-items: center !important;
    margin-bottom: 4px !important;
}

.modal-header h3 {
    margin: 0 !important;
}

/* Remove outer borders around text input fields in modal */
.modal-card .gradio-textbox,
.modal-card .block,
.modal-card .wrap,
.modal-card [data-testid="textbox"] {
    border: none !important;
    box-shadow: none !important;
    background: transparent !important;
}

.modal-card .gradio-textbox textarea,
.modal-card .gradio-textbox input {
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    background: var(--background-fill-secondary, #27272a) !important;
    border-radius: 8px !important;
    padding: 10px 14px !important;
}

.modal-card .gradio-textbox textarea:focus,
.modal-card .gradio-textbox input:focus {
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
}

/* Tab 2: Remove divider line between Transcript and Context */
#edit_voice_details_group #tab2_trans_ctx_box,
#edit_voice_details_group .trans-ctx-box {
    gap: 0 !important;
    padding: 0 !important;
    border: none !important;
    background: transparent !important;
}

#edit_voice_details_group #tab2_trans_ctx_box > *,
#edit_voice_details_group #tab2_trans_ctx_box .form,
#edit_voice_details_group #tab2_trans_ctx_box .form > * {
    gap: 0 !important;
    border-top: none !important;
    border-bottom: none !important;
    box-shadow: none !important;
}

#edit_voice_details_group #tab2_transcript_input {
    border-bottom: none !important;
    border-bottom-width: 0 !important;
    border-bottom-left-radius: 0 !important;
    border-bottom-right-radius: 0 !important;
    margin-bottom: 0 !important;
}

#edit_voice_details_group #tab2_context_input {
    border-top: none !important;
    border-top-width: 0 !important;
    border-top-left-radius: 0 !important;
    border-top-right-radius: 0 !important;
    margin-top: 0 !important;
}

#edit_voice_details_group #tab2_context_input label {
    margin-top: 4px !important;
}
"""

init_pagination_js = """
() => {
    let wasFullscreen = false;
    
    function isTableFullscreen() {
        const table = document.querySelector('.voice-tracks-table');
        return !!(
            (table && (table.querySelector('.fullscreen') || table.classList.contains('fullscreen'))) ||
            document.querySelector('.table-container.fullscreen') ||
            document.querySelector('.voice-tracks-table.fullscreen') ||
            document.querySelector('.fullscreen') ||
            document.fullscreenElement
        );
    }

    function checkFullscreenSync() {
        const isNowFullscreen = isTableFullscreen();
        if (isNowFullscreen !== wasFullscreen) {
            wasFullscreen = isNowFullscreen;
            const btn = document.querySelector('#fs_sync_btn button') || document.getElementById('fs_sync_btn');
            if (btn) {
                btn.click();
            }
        }
    }

    if (!window._tableFsSyncWatcherInitialized) {
        window._tableFsSyncWatcherInitialized = true;
        
        setInterval(checkFullscreenSync, 120);
        
        document.addEventListener('click', (e) => {
            const fsBtn = e.target.closest('.voice-tracks-table .toolbar-buttons button, .toolbar-buttons button, button[title*="fullscreen" i], button[aria-label*="fullscreen" i]');
            if (fsBtn) {
                setTimeout(checkFullscreenSync, 50);
                setTimeout(checkFullscreenSync, 120);
                setTimeout(checkFullscreenSync, 300);
            }
        });
        
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                setTimeout(checkFullscreenSync, 50);
                setTimeout(checkFullscreenSync, 120);
                setTimeout(checkFullscreenSync, 300);
            }
        });
        
        // Auto-play audio when loaded in audio container
        document.addEventListener('canplay', (e) => {
            if (e.target && (e.target.tagName === 'AUDIO' || (e.target.closest && e.target.closest('.audio-container')))) {
                e.target.play().catch(() => {});
            }
        }, true);
        
        // Auto-play helper when table row is clicked
        document.addEventListener('click', (e) => {
            const tableRow = e.target.closest('.voice-tracks-table tr, .voice-tracks-table tbody tr, .voice-tracks-table td');
            if (tableRow) {
                let attempts = 0;
                const tryPlay = () => {
                    const audio = document.querySelector('.audio-container audio');
                    if (audio && audio.src) {
                        audio.play().catch(() => {});
                    } else if (attempts < 12) {
                        attempts++;
                        setTimeout(tryPlay, 100);
                    }
                };
                setTimeout(tryPlay, 100);
            }
        });
    }
}
"""

# Build Gradio App
with gr.Blocks(title="Kabil Data Collector", css=css, theme=gr.themes.Default(primary_hue="orange").set(button_primary_background_fill="#bd6516", button_primary_background_fill_hover="#a35410")) as demo:
    with gr.Row():
        gr.Markdown("# 🎙️ Kabil Audio Data Collection")
    
    with gr.Tabs() as tabs:
        tab1_cat, tab1_display, tab1_tts_voice = tab1_record.render()
        sentence_dropdown = tab2_review.render()
        voice_table = tab3_player.render(demo, tabs, sentence_dropdown)
            
    demo.load(
        fn=load_from_url, 
        inputs=[tab1_cat], 
        outputs=[tabs, sentence_dropdown, tab1_cat, tab1_display, tab1_tts_voice], 
        js=init_pagination_js
    )


# Build FastAPI App
app = FastAPI(title="Kabil Voice Assistant")

# Mount the data directory so audio files can be fetched by the frontend if needed
app.mount("/data", StaticFiles(directory=os.path.join(PROJECT_ROOT, "data")), name="data")

# Mount the Gradio app at /
app = gr.mount_gradio_app(app, demo, path="/")

if __name__ == "__main__":
    print("Starting Kabil Voice Assistant App...")
    print("Access the unified app at: http://127.0.0.1:8000/")
    print("-" * 50)
    uvicorn.run(app, host="127.0.0.1", port=8000)

