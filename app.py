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
from components.tab2_review import get_sentence_choices

def load_from_url(request: gr.Request):
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
                
    return gr.update(selected=tab_sel), gr.update(value=choice_sel, choices=choices)

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

/* Custom TTS Action Box styling to match gr.Dropdown / gr.Radio */
.tts-action-box {
    background: var(--input-background-fill) !important;
    border: var(--input-border-width) solid var(--input-border-color) !important;
    border-radius: var(--input-radius) !important;
    overflow: hidden !important;
    display: flex !important;
    flex-direction: column !important;
    padding: 0 !important;
    gap: 0 !important;
    height: 100% !important;
}
.tts-action-label {
    font-size: var(--input-text-size) !important;
    color: var(--body-text-color-subdued) !important;
    padding: 8px 12px 4px 12px !important;
    margin: 0 !important;
    line-height: 1 !important;
}
.tts-btn {
    border: none !important;
    border-radius: 0 !important;
    box-shadow: none !important;
    flex-grow: 1 !important;
    margin: 0 !important;
    min-height: 32px !important;
}
.tts-btn:hover {
    filter: brightness(0.95);
}
"""

# Build Gradio App
with gr.Blocks(title="Kabil Data Collector", css=css, theme=gr.themes.Default(primary_hue="orange").set(button_primary_background_fill="#bd6516", button_primary_background_fill_hover="#a35410")) as demo:
    with gr.Row():
        gr.Markdown("# 🎙️ Kabil Audio Data Collection")
    
    with gr.Tabs() as tabs:
        tab1_record.render()
        sentence_dropdown = tab2_review.render()
        voice_table = tab3_player.render(demo, tabs, sentence_dropdown)
            
    demo.load(fn=load_from_url, inputs=None, outputs=[tabs, sentence_dropdown])


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

