import os
import csv
import uuid
import traceback
import gradio as gr
import scipy.io.wavfile as wavfile

import core.state as state

# Track current index in unrecorded list per category
unrecorded_indices = {}

def get_default_category():
    categories = list(state.sentences_by_category.keys())
    return categories[0] if categories else None

def resolve_category(category):
    if category and category in state.sentences_by_category:
        return category
    return get_default_category()

def get_tts_language_for_category(category=None):
    category = resolve_category(category)
    if not category:
        return "Bangla (BD)"
    clean = state.get_clean_language_name(category)
    if clean == "English":
        return "English"
    elif clean == "Chakma":
        return "Chakma (BD)"
    elif clean == "Pali":
        return "Pali (LK Sinhala style)"
    elif clean == "Bengali":
        return "Bangla (BD)"
        
    cat_lower = str(category).lower()
    if "chakma" in cat_lower or "𑄌𑄇𑄴𑄟" in cat_lower:
        return "Chakma (BD)"
    elif "pali" in cat_lower or "pāḷi" in cat_lower or "পাল়ি" in cat_lower or "𑄛𑅄𑄨" in cat_lower:
        return "Pali (LK Sinhala style)"
    elif "english" in cat_lower:
        return "English"
    elif "bangla" in cat_lower or "bengali" in cat_lower or "বাংলা" in cat_lower:
        return "Bangla (BD)"
    return "Bangla (BD)"


def get_unrecorded_sentences(category=None):
    category = resolve_category(category)
    if not category or category not in state.sentences_by_category:
        return []
    all_sents = state.sentences_by_category[category]
    recorded = state.get_recorded_manifest(verify_local_storage=True)
    clean_lang = state.get_clean_language_name(category)
    
    # A sentence is treated as recorded ONLY IF:
    # 1. It is recorded in the metadata manifest for this language, AND
    # 2. The audio file physically exists locally on disk
    # If any file or sentence is deleted from local storage, it immediately reappears.
    recorded_transcripts = {
        r[1].strip() for r in recorded 
        if len(r) > 1 and r[1] and (r[2] == clean_lang or r[2] == "Unknown")
    }
    
    unrecorded = [s for s in all_sents if s[0].strip() not in recorded_transcripts]
    return unrecorded


def get_current_sentence_display(category=None):
    category = resolve_category(category)
    if not category or category not in state.sentences_by_category:
        return "<div style='text-align: center; width: 100%;'>No category available.</div>"
    
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

def prev_sentence(category=None):
    category = resolve_category(category)
    if category in state.sentences_by_category:
        unrecorded = get_unrecorded_sentences(category)
        if unrecorded:
            cur = unrecorded_indices.get(category, 0)
            unrecorded_indices[category] = max(0, cur - 1)
    return get_current_sentence_display(category)

def next_sentence(category=None):
    category = resolve_category(category)
    if category in state.sentences_by_category:
        unrecorded = get_unrecorded_sentences(category)
        if unrecorded:
            cur = unrecorded_indices.get(category, 0)
            unrecorded_indices[category] = min(len(unrecorded) - 1, cur + 1)
    return get_current_sentence_display(category)

def on_category_change(category=None):
    category = resolve_category(category)
    # Reset unrecorded index to 0 when category changes
    unrecorded_indices[category] = 0
    tts_lang = get_tts_language_for_category(category)
    return get_current_sentence_display(category), gr.update(value=tts_lang)

def on_tab1_select(category=None):
    category = resolve_category(category)
    tts_lang = get_tts_language_for_category(category)
    return get_current_sentence_display(category), gr.update(value=tts_lang)

def save_new_audio(audio_data, category=None):
    try:
        category = resolve_category(category)
        if not category or category not in state.sentences_by_category:
            return "No category available.", get_current_sentence_display(category), None
            
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

def skip_sentence(category=None):
    category = resolve_category(category)
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
    category = resolve_category(category)
    if not category or category not in state.sentences_by_category:
        raise Exception("No category available.")
    
    # Automatically match voice_type with category if missing or invalid
    if not voice_type or voice_type not in ["Chakma (BD)", "Pali (LK Sinhala style)", "Pali (IN Hindi style)", "Bangla (BD)", "Bangla (IN)", "English"]:
        voice_type = get_tts_language_for_category(category)
        
    unrecorded = get_unrecorded_sentences(category)
    if not unrecorded:
        raise Exception("All sentences completed for this category.")
        
    idx = unrecorded_indices.get(category, 0)
    if idx >= len(unrecorded):
        idx = max(0, len(unrecorded) - 1)
        unrecorded_indices[category] = idx
    
    transcript, context = unrecorded[idx]
    
    tts_text = state.resolve_tts_spoken_text(
        transcript, 
        context=context, 
        voice_type=voice_type, 
        category_or_lang=category
    )
    
    voice_id = get_edge_tts_voice(voice_type, gender)
    
    clean_lang = state.get_clean_language_name(category)
    lang_prefix = state.get_language_prefix(clean_lang)
    filename = f"preview_{lang_prefix}_{uuid.uuid4().hex[:10]}.mp3"
    save_path = os.path.join(state.TTS_CACHE_DIR, filename)
    
    try:
        cmd = [sys.executable, "-m", "edge_tts", "--text", tts_text, "--voice", voice_id, "--write-media", save_path]
        res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        if res.returncode != 0:
            err = res.stderr.strip()
            if "NoAudioReceived" in err and not tts_text.isascii():
                fallback_text = state.chakma_to_bengali(transcript)
                fallback_cmd = [sys.executable, "-m", "edge_tts", "--text", fallback_text, "--voice", "bn-BD-PradeepNeural", "--write-media", save_path]
                res2 = subprocess.run(fallback_cmd, capture_output=True, text=True, encoding='utf-8')
                if res2.returncode == 0:
                    return save_path
            raise Exception(f"edge-tts failed: {err}")
    except Exception as e:
        raise Exception(str(e))
        
    return save_path

def handle_tts_action(action, category, voice_type, gender):
    category = resolve_category(category)
    if not voice_type:
        voice_type = get_tts_language_for_category(category)
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

def get_current_sentence_data(category=None):
    category = resolve_category(category)
    if not category or category not in state.sentences_by_category:
        return "", ""
    unrecorded = get_unrecorded_sentences(category)
    if not unrecorded:
        return "", ""
    idx = unrecorded_indices.get(category, 0)
    if idx >= len(unrecorded):
        idx = max(0, len(unrecorded) - 1)
        unrecorded_indices[category] = idx
    elif idx < 0:
        idx = 0
        unrecorded_indices[category] = 0
    return unrecorded[idx]

def open_proof_modal(category=None):
    category = resolve_category(category)
    trans, ctx = get_current_sentence_data(category)
    if not trans:
        return gr.update(visible=False), "", "", "", "No sentence available to edit."
    return gr.update(visible=True), trans, ctx, trans, "Editing sentence in pop-up..."

def close_proof_modal():
    return gr.update(visible=False)

def save_proof_modal(category, orig_trans, new_trans, new_ctx):
    category = resolve_category(category)
    if not orig_trans:
        return gr.update(visible=False), get_current_sentence_display(category), "Error: Original sentence not found."
    success, msg = state.update_raw_sentence(category, orig_trans, new_trans, new_ctx)
    if success:
        return gr.update(visible=False), get_current_sentence_display(category), msg
    else:
        return gr.update(visible=True), get_current_sentence_display(category), f"Failed: {msg}"


def render():
    with gr.TabItem("1. Record New Sentences", id="tab-1") as tab1_item:
        gr.Markdown("Read the sentence below out loud and hit record. Audio is automatically normalized (volume boosted) upon saving.")
        
        categories = list(state.sentences_by_category.keys())
        default_cat = get_default_category()
        default_tts_lang = get_tts_language_for_category(default_cat)
        
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
            tts_voice_dropdown = gr.Dropdown(choices=tts_choices, value=default_tts_lang, label="TTS Language", scale=2)
            tts_gender = gr.Radio(choices=["Male", "Female"], value="Male", label="TTS Gender", scale=2)
            tts_action = gr.Radio(choices=["Generate", "Clear Cache"], label="TTS Voice", scale=2, elem_classes=["tts-action-buttons"])
                        
        read_audio_player = gr.HTML(visible=False)
            
        with gr.Row():
            proof_btn = gr.Button("Proof Text", variant="secondary", scale=2)
            skip_btn = gr.Button("Skip", variant="secondary", scale=1)
            submit_btn = gr.Button("Submit & Next", variant="primary", scale=2)
        status_text = gr.Textbox(label="Status", interactive=False)
        
        # Pop-up modal for Proofing / Editing Sentence
        with gr.Group(visible=False, elem_id="proof_modal_container", elem_classes=["modal-overlay"]) as proof_modal:
            with gr.Column(elem_classes=["modal-card"]):
                with gr.Row(elem_classes=["modal-header"]):
                    gr.Markdown("### Proof & Edit Sentence")
                gr.Markdown("Correct any errors in the primary sentence transcript or context below. Saving will permanently update the local raw `*.txt` file.")
                proof_transcript_input = gr.Textbox(
                    label="Sentence / Transcript (Spoken Text)", 
                    lines=1,
                    max_lines=1,
                    interactive=True,
                    placeholder="Enter corrected sentence transcript..."
                )
                proof_context_input = gr.Textbox(
                    label="Context / Transliteration / Meaning", 
                    lines=3, 
                    interactive=True,
                    placeholder="Enter corrected context, transliteration, or translation..."
                )
                with gr.Row():
                    proof_save_btn = gr.Button("Save & Update", variant="primary", scale=2)
                    proof_cancel_btn = gr.Button("Cancel", variant="secondary", scale=1)

        orig_trans_state = gr.State(value="")
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Last Saved Recording")
                last_audio_playback = gr.Audio(label="Playback", interactive=False, type="filepath")

        category_dropdown.change(
            fn=on_category_change, 
            inputs=[category_dropdown], 
            outputs=[sentence_display, tts_voice_dropdown]
        )
        
        prev_sent_btn.click(fn=prev_sentence, inputs=[category_dropdown], outputs=[sentence_display])
        next_sent_btn.click(fn=next_sentence, inputs=[category_dropdown], outputs=[sentence_display])
        
        tts_action.change(
            fn=handle_tts_action,
            inputs=[tts_action, category_dropdown, tts_voice_dropdown, tts_gender],
            outputs=[read_audio_player, audio_input, status_text, tts_action]
        )
        
        proof_btn.click(
            fn=open_proof_modal,
            inputs=[category_dropdown],
            outputs=[proof_modal, proof_transcript_input, proof_context_input, orig_trans_state, status_text]
        )
        
        proof_cancel_btn.click(
            fn=close_proof_modal,
            inputs=None,
            outputs=[proof_modal]
        )
        
        proof_save_btn.click(
            fn=save_proof_modal,
            inputs=[category_dropdown, orig_trans_state, proof_transcript_input, proof_context_input],
            outputs=[proof_modal, sentence_display, status_text]
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
        
        tab1_item.select(
            fn=on_tab1_select, 
            inputs=[category_dropdown], 
            outputs=[sentence_display, tts_voice_dropdown]
        )
        
        return category_dropdown, sentence_display, tts_voice_dropdown

