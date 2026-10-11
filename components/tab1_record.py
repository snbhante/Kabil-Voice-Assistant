import os
import csv
import uuid
import traceback
import gradio as gr
import scipy.io.wavfile as wavfile

import core.state as state

# Track current index in unrecorded list per category
unrecorded_indices = {}

def get_unrecorded_sentences(category):
    if not category or category not in state.sentences_by_category:
        return []
    all_sents = state.sentences_by_category[category]
    recorded = state.get_recorded_manifest()
    # Normalize transcripts to avoid spacing mismatch
    recorded_transcripts = {r[1].strip() for r in recorded if len(r) > 1 and r[1]}
    
    unrecorded = [s for s in all_sents if s[0].strip() not in recorded_transcripts]
    return unrecorded

def get_current_sentence_display(category):
    if not category or category not in state.sentences_by_category:
        return "<div style='text-align: center; width: 100%;'>Please select a category.</div>"
    
    unrecorded = get_unrecorded_sentences(category)
    if not unrecorded:
        total = len(state.sentences_by_category.get(category, []))
        return f"<div style='text-align: center; width: 100%;'><h3 style='text-align: center;'>🎉 All sentences recorded!</h3><p style='text-align: center;'>You have completed all <strong>{total}</strong> sentences for this category.</p></div>"
        
    idx = unrecorded_indices.get(category, 0)
    if idx >= len(unrecorded):
        idx = max(0, len(unrecorded) - 1)
        unrecorded_indices[category] = idx
    elif idx < 0:
        idx = 0
        unrecorded_indices[category] = 0
        
    transcript, context = unrecorded[idx]
    progress_info = f"*(Sentence {idx + 1} of {len(unrecorded)} unrecorded)*"
    if context:
        return f"<div style='text-align: center; width: 100%;'><h3 style='text-align: center; margin: 0 0 6px 0; font-size: 1.35rem;'>{transcript}</h3><p style='text-align: center; margin: 4px 0; font-style: italic; color: #d4d4d8;'>(Context: {context})</p><p style='text-align: center; margin: 6px 0 0 0; font-size: 0.9rem; color: #a1a1aa;'>{progress_info}</p></div>"
    return f"<div style='text-align: center; width: 100%;'><h3 style='text-align: center; margin: 0 0 6px 0; font-size: 1.35rem;'>{transcript}</h3><p style='text-align: center; margin: 6px 0 0 0; font-size: 0.9rem; color: #a1a1aa;'>{progress_info}</p></div>"

def prev_sentence(category):
    if category in state.sentences_by_category:
        unrecorded = get_unrecorded_sentences(category)
        if unrecorded:
            cur = unrecorded_indices.get(category, 0)
            unrecorded_indices[category] = max(0, cur - 1)
    return get_current_sentence_display(category)

def next_sentence(category):
    if category in state.sentences_by_category:
        unrecorded = get_unrecorded_sentences(category)
        if unrecorded:
            cur = unrecorded_indices.get(category, 0)
            unrecorded_indices[category] = min(len(unrecorded) - 1, cur + 1)
    return get_current_sentence_display(category)

def on_category_change(category):
    # Reset unrecorded index to 0 when category changes
    unrecorded_indices[category] = 0
    return get_current_sentence_display(category)

def save_new_audio(audio_data, category):
    try:
        if not category or category not in state.sentences_by_category:
            return "Please select a category.", get_current_sentence_display(category), None
            
        unrecorded = get_unrecorded_sentences(category)
        if not unrecorded:
            return "All sentences completed for this category.", get_current_sentence_display(category), None
            
        idx = unrecorded_indices.get(category, 0)
        if idx >= len(unrecorded):
            idx = max(0, len(unrecorded) - 1)
            unrecorded_indices[category] = idx

        if audio_data is None:
            return "Please record audio first.", get_current_sentence_display(category), None

        transcript = unrecorded[idx][0]
        clean_lang = state.get_clean_language_name(category)
        
        # Audio is TTS if it's an MP3 or comes from tts / tts_cache directories
        is_tts = False
        if isinstance(audio_data, str):
            abs_audio = os.path.abspath(audio_data).lower()
            norm_cache = os.path.abspath(state.TTS_CACHE_DIR).lower()
            norm_tts = os.path.abspath(state.TTS_AUDIO_DIR).lower()
            if norm_cache in abs_audio or norm_tts in abs_audio or "tts" in os.path.basename(abs_audio) or abs_audio.endswith(".mp3"):
                is_tts = True
                
        rel_path, save_path = state.save_audio_file(audio_data, is_tts=is_tts, language=clean_lang)
        state.record_audio_entry(rel_path, transcript, clean_lang, status="Ready", is_tts=is_tts)
        
        # After saving, get updated unrecorded list
        new_unrecorded = get_unrecorded_sentences(category)
        if idx >= len(new_unrecorded):
            unrecorded_indices[category] = max(0, len(new_unrecorded) - 1)
            
        remaining = len(new_unrecorded)
        total = len(state.sentences_by_category[category])
        return f"Saved! ({total - remaining}/{total} recorded)", get_current_sentence_display(category), save_path
        
    except Exception as e:
        error_msg = f"Crash: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return error_msg, get_current_sentence_display(category), None

def skip_sentence(category):
    if category and category in state.sentences_by_category:
        unrecorded = get_unrecorded_sentences(category)
        if unrecorded:
            cur = unrecorded_indices.get(category, 0)
            unrecorded_indices[category] = min(len(unrecorded) - 1, cur + 1)
    return "Skipped.", get_current_sentence_display(category), None

def get_edge_tts_voice(voice_type, gender):
    if voice_type == "English":
        return "en-US-AriaNeural" if gender == "Female" else "en-US-GuyNeural"
    elif voice_type in ["Bangla (BD)", "Chakma (BD)"]:
        return "bn-BD-NabanitaNeural" if gender == "Female" else "bn-BD-PradeepNeural"
    elif voice_type == "Bangla (IN)":
        return "bn-IN-TanishaaNeural" if gender == "Female" else "bn-IN-BashkarNeural"
    elif voice_type == "Pali (LK Sinhala style)":
        return "si-LK-ThiliniNeural" if gender == "Female" else "si-LK-SameeraNeural"
    elif voice_type == "Pali (IN Hindi style)":
        return "hi-IN-SwaraNeural" if gender == "Female" else "hi-IN-MadhurNeural"
    return "bn-BD-NabanitaNeural"

def generate_tts_audio_file(category, voice_type, gender):
    import subprocess
    import sys
    if not category or category not in state.sentences_by_category:
        raise Exception("Please select a category.")
    
    unrecorded = get_unrecorded_sentences(category)
    if not unrecorded:
        raise Exception("All sentences completed for this category.")
        
    idx = unrecorded_indices.get(category, 0)
    if idx >= len(unrecorded):
        idx = max(0, len(unrecorded) - 1)
        unrecorded_indices[category] = idx
    
    transcript, context = unrecorded[idx]
    
    tts_text = transcript
    if "Chakma" in category and ("Bangla" in voice_type or "Chakma" in voice_type):
        if context.startswith("(") and "|" in context:
            tts_text = context.split("|")[0].replace("(", "").strip()
    
    voice_id = get_edge_tts_voice(voice_type, gender)
    
    clean_lang = state.get_clean_language_name(category)
    lang_prefix = state.get_language_prefix(clean_lang)
    filename = f"preview_{lang_prefix}_{uuid.uuid4().hex[:10]}.mp3"
    save_path = os.path.join(state.TTS_CACHE_DIR, filename)
    
    edge_tts_path = os.path.join(os.path.dirname(sys.executable), "edge-tts")
    
    try:
        res = subprocess.run([edge_tts_path, "--text", tts_text, "--voice", voice_id, "--write-media", save_path], 
                             capture_output=True, text=True, encoding='utf-8')
        if res.returncode != 0:
            raise Exception(f"edge-tts failed: {res.stderr}")
    except Exception as e:
        raise Exception(str(e))
        
    return save_path

def handle_tts_action(action, category, voice_type, gender):
    if action == "Generate":
        try:
            save_path = generate_tts_audio_file(category, voice_type, gender)
            msg = "Auto-generated audio successfully. Click 'Submit & Next' to save."
            return "", save_path, msg, None
        except Exception as e:
            error_msg = f"Error generating voice: {str(e)}"
            print(error_msg.encode('utf-8', errors='replace').decode('utf-8'))
            return "", gr.update(), error_msg.encode('utf-8', errors='replace').decode('utf-8'), None
    elif action == "Clear Cache":
        deleted = state.clear_tts_cache()
        msg = f"🧹 TTS cache cleared ({deleted} temporary files removed)."
        return "", gr.update(), msg, None
    return "", gr.update(), gr.update(), None


def render():
    with gr.TabItem("1. Record New Sentences", id="tab-1"):
        gr.Markdown("Read the sentence below out loud and hit record. Audio is automatically normalized (volume boosted) upon saving.")
        
        categories = list(state.sentences_by_category.keys())
        default_cat = categories[0] if categories else None
        
        category_dropdown = gr.Dropdown(choices=categories, value=default_cat, label="Select Category / Language", scale=1, elem_classes=["category-dropdown"])
        
        with gr.Row(elem_classes=["main-sentence-row"]):
            prev_sent_btn = gr.Button("◀ Prev", scale=1, min_width=75, elem_classes=["sent-nav-btn", "prev-sent-btn"])
            with gr.Column(scale=8, elem_classes=["sentence-box"]):
                sentence_display = gr.Markdown(get_current_sentence_display(default_cat))
            next_sent_btn = gr.Button("Next ▶", scale=1, min_width=75, elem_classes=["sent-nav-btn", "next-sent-btn"])
        
        with gr.Row():
            audio_input = gr.Audio(type="filepath", label="Record your voice", sources=["microphone", "upload"])
            
        with gr.Row():
            tts_choices = ["Chakma (BD)", "Pali (LK Sinhala style)", "Pali (IN Hindi style)", "Bangla (BD)", "Bangla (IN)", "English"]
            tts_voice_dropdown = gr.Dropdown(choices=tts_choices, value="Bangla (BD)", label="TTS Language", scale=2)
            tts_gender = gr.Radio(choices=["Male", "Female"], value="Male", label="TTS Gender", scale=2)
            tts_action = gr.Radio(choices=["Generate", "Clear Cache"], label="TTS Voice", scale=2, elem_classes=["tts-action-buttons"])
                        
        read_audio_player = gr.HTML(visible=False)
            
        with gr.Row():
            submit_btn = gr.Button("Submit & Next", variant="primary")
            skip_btn = gr.Button("Skip")
        status_text = gr.Textbox(label="Status", interactive=False)
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Last Saved Recording")
                last_audio_playback = gr.Audio(label="Playback", interactive=False, type="filepath")

        category_dropdown.change(fn=on_category_change, inputs=[category_dropdown], outputs=[sentence_display])
        
        prev_sent_btn.click(fn=prev_sentence, inputs=[category_dropdown], outputs=[sentence_display])
        next_sent_btn.click(fn=next_sentence, inputs=[category_dropdown], outputs=[sentence_display])
        
        tts_action.change(
            fn=handle_tts_action,
            inputs=[tts_action, category_dropdown, tts_voice_dropdown, tts_gender],
            outputs=[read_audio_player, audio_input, status_text, tts_action]
        )
        
        submit_btn.click(
            fn=save_new_audio, 
            inputs=[audio_input, category_dropdown], 
            outputs=[status_text, sentence_display, last_audio_playback]
        ).then(
            fn=lambda: None, inputs=None, outputs=[audio_input]
        )
        
        skip_btn.click(
            fn=skip_sentence, 
            inputs=[category_dropdown], 
            outputs=[status_text, sentence_display, last_audio_playback]
        )
