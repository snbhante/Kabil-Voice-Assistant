import os
import gradio as gr
import pandas as pd

import core.state as state
from components.tab2_review import get_sentence_choices

def get_voice_data(lang, search):
    records = state.get_recorded_manifest()
    res = []
    for idx, rec in enumerate(records):
        path, trans, rec_lang, status = rec
        if lang != "All" and rec_lang != lang:
            continue
        if search and search.lower() not in trans.lower():
            continue
        # Show only filename
        res.append([os.path.basename(path), trans, rec_lang, status])
    return res

def play_track(idx):
    records = state.get_recorded_manifest()
    if idx < 0 or idx >= len(records):
        return None, "No track selected.", gr.update(interactive=False), idx
    
    rec = records[idx]
    abs_path = os.path.join(state.PROJECT_ROOT, rec[0])
    trans = rec[1]
    
    if os.path.exists(abs_path):
        return abs_path, f"Playing: {trans}", gr.update(interactive=True), idx
    return None, "Audio file not found.", gr.update(interactive=False), idx

def play_prev(idx):
    if idx > 0:
        return play_track(idx - 1)
    return play_track(idx)

def play_next(idx):
    records = state.get_recorded_manifest()
    if idx != -1 and idx < len(records) - 1:
        return play_track(idx + 1)
    return play_track(idx)

def load_audio_from_table(evt: gr.SelectData, current_data):
    if current_data is None:
        return None, "Error", gr.update(interactive=False), -1
    
    try:
        if hasattr(current_data, "iloc"):
            row = current_data.iloc[evt.index[0]].tolist()
        elif isinstance(current_data, dict) and 'data' in current_data:
            row = current_data['data'][evt.index[0]]
        else:
            row = current_data[evt.index[0]]
    except Exception as e:
        return None, f"Data Error: {str(e)}", gr.update(interactive=False), -1
    
    filename = row[0]
    records = state.get_recorded_manifest()
    
    global_idx = -1
    for i, r in enumerate(records):
        if os.path.basename(r[0]) == filename:
            global_idx = i
            break
            
    return play_track(global_idx)

def go_to_review(global_idx):
    if global_idx == -1:
        return gr.update(), gr.update()
    
    choices = get_sentence_choices()
    if global_idx < len(choices):
        return gr.update(selected="tab-2"), gr.update(value=choices[global_idx], choices=choices)
    return gr.update(), gr.update()

def render(demo, tabs_component, dropdown_component):
    with gr.TabItem("3. Voice data & player", id="tab-3"):
        gr.Markdown("Search and filter through your recorded sentences, and select any track to play back the audio.")
        
        with gr.Row():
            lang_filter = gr.Dropdown(choices=["All", "Chakma", "Pali", "Bengali", "English", "Unknown"], value="All", label="Filter by Language", scale=1)
            search_filter = gr.Textbox(placeholder="Search transcripts...", label="Search", scale=3)
        
        voice_table = gr.Dataframe(
            headers=["File", "Transcript", "Language", "Status"],
            interactive=False,
            label="Voice Tracks (Click a row to play)"
        )
        
        with gr.Row():
            with gr.Column(scale=2, elem_classes="audio-container"):
                selected_audio = gr.Audio(label="Now Playing", interactive=False, type="filepath")
                with gr.Row(elem_classes="overlay-row"):
                    prev_btn = gr.Button("⏮", elem_id="prev_btn", elem_classes=["overlay-icon", "prev-icon"])
                    next_btn = gr.Button("⏭", elem_id="next_btn", elem_classes=["overlay-icon", "next-icon"])
                    edit_voice_btn = gr.Button("Review", elem_id="review_btn", elem_classes=["overlay-icon", "review-icon"])
            with gr.Column(scale=1):
                play_status = gr.Textbox(label="Track Info", interactive=False)
            
        selected_global_idx = gr.State(-1)
            
        lang_filter.change(fn=get_voice_data, inputs=[lang_filter, search_filter], outputs=[voice_table])
        search_filter.change(fn=get_voice_data, inputs=[lang_filter, search_filter], outputs=[voice_table])
        
        voice_table.select(
            fn=load_audio_from_table, 
            inputs=[voice_table], 
            outputs=[selected_audio, play_status, edit_voice_btn, selected_global_idx]
        )
        
        prev_btn.click(
            fn=play_prev,
            inputs=[selected_global_idx],
            outputs=[selected_audio, play_status, edit_voice_btn, selected_global_idx]
        )
        
        next_btn.click(
            fn=play_next,
            inputs=[selected_global_idx],
            outputs=[selected_audio, play_status, edit_voice_btn, selected_global_idx]
        )
        
        edit_voice_btn.click(
            fn=go_to_review,
            inputs=[selected_global_idx],
            outputs=[tabs_component, dropdown_component]
        )
        
        demo.load(fn=lambda: get_voice_data("All", ""), inputs=None, outputs=[voice_table])
        
    return voice_table
