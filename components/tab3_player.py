import os
import gradio as gr
import pandas as pd

import core.state as state
from components.tab2_review import get_sentence_choices

PAGE_SIZE = 10

def get_filtered_records(lang, search):
    records = state.get_recorded_manifest()
    res = []
    for idx, rec in enumerate(records):
        path, trans, rec_lang, status = rec
        clean_lang = state.get_clean_language_name(rec_lang)
        if lang != "All" and clean_lang != lang:
            continue
        if search and search.lower() not in trans.lower():
            continue
        # Show transcript, clean language name, status, filename
        res.append([trans, clean_lang, status, os.path.basename(path)])
    return res

def get_paginated_data(lang, search, page, is_fullscreen=False):
    filtered = get_filtered_records(lang, search)
    total_items = len(filtered)
    
    if is_fullscreen:
        status_text = f"Showing all {total_items} tracks (Fullscreen)"
        jump_update = gr.update(value=1, minimum=1, maximum=1)
        return filtered, status_text, 1, jump_update

    total_pages = max(1, (total_items + PAGE_SIZE - 1) // PAGE_SIZE)
    try:
        page = int(page)
    except (ValueError, TypeError):
        page = 1
    page = max(1, min(page, total_pages))
    
    start_idx = (page - 1) * PAGE_SIZE
    end_idx = min(start_idx + PAGE_SIZE, total_items)
    page_data = filtered[start_idx:end_idx]
    
    status_text = f"Page {page} of {total_pages} ({total_items} tracks)"
    jump_update = gr.update(value=page, minimum=1, maximum=total_pages)
    return page_data, status_text, page, jump_update

def on_filter_change(lang, search, is_fs):
    return get_paginated_data(lang, search, 1, bool(is_fs))

def on_prev_page(lang, search, current_page, is_fs):
    return get_paginated_data(lang, search, current_page - 1, bool(is_fs))

def on_next_page(lang, search, current_page, is_fs):
    return get_paginated_data(lang, search, current_page + 1, bool(is_fs))

def on_jump_page(lang, search, jump_page, is_fs):
    return get_paginated_data(lang, search, jump_page, bool(is_fs))

def on_fullscreen_sync(lang, search, is_fs):
    is_fs_bool = bool(is_fs)
    page_data, status_text, page, jump_update = get_paginated_data(lang, search, 1, is_fullscreen=is_fs_bool)
    return page_data, status_text, page, jump_update, is_fs_bool



def play_track(idx):
    records = state.get_recorded_manifest()
    if idx < 0 or idx >= len(records):
        return None, "", "", gr.update(interactive=False), idx
    
    rec = records[idx]
    abs_path = os.path.join(state.PROJECT_ROOT, rec[0])
    trans = rec[1]
    lang = rec[2] if len(rec) > 2 else "Unknown"
    clean_lang = state.get_clean_language_name(lang)
    context = state.get_context_for_transcript(trans, clean_lang)
    
    if os.path.exists(abs_path):
        return abs_path, trans, context, gr.update(interactive=True), idx
    gr.Warning(f"Audio file not found: {os.path.basename(abs_path)}")
    return None, trans, context, gr.update(interactive=False), idx

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
        return None, "", "", gr.update(interactive=False), -1
    
    try:
        if hasattr(current_data, "iloc"):
            row = current_data.iloc[evt.index[0]].tolist()
        elif isinstance(current_data, dict) and 'data' in current_data:
            row = current_data['data'][evt.index[0]]
        else:
            row = current_data[evt.index[0]]
    except Exception as e:
        return None, "", "", gr.update(interactive=False), -1
    
    filename = row[3]
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
        
        current_page_state = gr.State(1)
        
        with gr.Column(elem_classes=["filter-search-box"]):
            with gr.Row():
                lang_filter = gr.Dropdown(choices=["All", "Chakma", "Pali", "Bengali", "English", "Unknown"], value="All", label="Filter by Language", scale=1)
                search_filter = gr.Textbox(placeholder="Search transcripts...", label="Search", scale=3)
            
            with gr.Row(elem_classes=["pagination-controls-row"]):
                prev_page_btn = gr.Button("◀ Previous Page", elem_classes=["pagination-btn", "prev-page-btn"])
                jump_input = gr.Number(value=1, precision=0, minimum=1, maximum=1, show_label=False, container=False, elem_classes=["jump-input"])
                next_page_btn = gr.Button("Next Page ▶", elem_classes=["pagination-btn", "next-page-btn"])
            
            with gr.Row(elem_classes=["pagination-status-row"]):
                page_status = gr.Markdown("Page 1 of 1 (0 tracks)", elem_classes=["pagination-status"])
        
        voice_table = gr.Dataframe(
            headers=["Transcript", "Language", "Status", "File"],
            interactive=False,
            label="Voice Tracks (Click a row to play)",
            elem_classes=["voice-tracks-table"]
        )
        
        with gr.Row(elem_id="fs_sync_row", elem_classes=["fs-sync-row"]):
            fs_state_box = gr.Checkbox(value=False, label="Show all recorded sentences", elem_id="fs_state_box", scale=1)
            fs_sync_btn = gr.Button("🔄 Sync Fullscreen View", elem_id="fs_sync_btn", scale=1)
        
        with gr.Row():
            with gr.Column(scale=2, elem_classes="audio-container"):
                selected_audio = gr.Audio(label="Now Playing", interactive=False, type="filepath", autoplay=True)
                with gr.Row(elem_classes="overlay-row"):
                    prev_btn = gr.Button("⏮", elem_id="prev_btn", elem_classes=["overlay-icon", "prev-icon"])
                    next_btn = gr.Button("⏭", elem_id="next_btn", elem_classes=["overlay-icon", "next-icon"])
                    edit_voice_btn = gr.Button("Review", elem_id="review_btn", elem_classes=["overlay-icon", "review-icon"])
            with gr.Column(scale=1):
                play_transcript = gr.Textbox(label="Transcript", interactive=False, lines=1, max_lines=2)
                play_context = gr.Textbox(label="Context", interactive=False, lines=2, max_lines=5)
            
        selected_global_idx = gr.State(-1)
            
        lang_filter.change(
            fn=on_filter_change, 
            inputs=[lang_filter, search_filter, fs_state_box], 
            outputs=[voice_table, page_status, current_page_state, jump_input]
        )
        
        search_filter.change(
            fn=on_filter_change, 
            inputs=[lang_filter, search_filter, fs_state_box], 
            outputs=[voice_table, page_status, current_page_state, jump_input]
        )
        
        prev_page_btn.click(
            fn=on_prev_page,
            inputs=[lang_filter, search_filter, current_page_state, fs_state_box],
            outputs=[voice_table, page_status, current_page_state, jump_input]
        )
        
        next_page_btn.click(
            fn=on_next_page,
            inputs=[lang_filter, search_filter, current_page_state, fs_state_box],
            outputs=[voice_table, page_status, current_page_state, jump_input]
        )
        
        jump_input.submit(
            fn=on_jump_page,
            inputs=[lang_filter, search_filter, jump_input, fs_state_box],
            outputs=[voice_table, page_status, current_page_state, jump_input]
        )
        
        fs_state_box.change(
            fn=on_filter_change,
            inputs=[lang_filter, search_filter, fs_state_box],
            outputs=[voice_table, page_status, current_page_state, jump_input]
        )
        
        fs_sync_btn.click(
            fn=on_fullscreen_sync,
            inputs=[lang_filter, search_filter, fs_state_box],
            outputs=[voice_table, page_status, current_page_state, jump_input, fs_state_box],
            js="""(lang, search, fsBox) => {
                const table = document.querySelector('.voice-tracks-table');
                const isFs = !!(
                    (table && (table.querySelector('.fullscreen') || table.classList.contains('fullscreen'))) ||
                    document.querySelector('.table-container.fullscreen') ||
                    document.querySelector('.voice-tracks-table.fullscreen') ||
                    document.querySelector('.fullscreen') ||
                    document.fullscreenElement
                );
                return [lang, search, isFs];
            }"""
        )
        
        voice_table.select(
            fn=load_audio_from_table, 
            inputs=[voice_table], 
            outputs=[selected_audio, play_transcript, play_context, edit_voice_btn, selected_global_idx]
        )
        
        prev_btn.click(
            fn=play_prev,
            inputs=[selected_global_idx],
            outputs=[selected_audio, play_transcript, play_context, edit_voice_btn, selected_global_idx]
        )
        
        next_btn.click(
            fn=play_next,
            inputs=[selected_global_idx],
            outputs=[selected_audio, play_transcript, play_context, edit_voice_btn, selected_global_idx]
        )
        
        edit_voice_btn.click(
            fn=go_to_review,
            inputs=[selected_global_idx],
            outputs=[tabs_component, dropdown_component]
        )
        
        demo.load(
            fn=lambda: on_filter_change("All", "", False), 
            inputs=None, 
            outputs=[voice_table, page_status, current_page_state, jump_input]
        )
        
    return voice_table
