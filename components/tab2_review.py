import os
import uuid
import sys
import subprocess
import gradio as gr
import scipy.io.wavfile as wavfile

import core.state as state

def get_edge_tts_voice(voice_type, gender):
    if voice_type == "English":
        return "en-US-AriaNeural" if gender == "Female" else "en-US-GuyNeural"
    elif voice_type in ["Bangla (BD)", "Chakma (BD)", "Bengali", "Chakma"]:
        return "bn-BD-NabanitaNeural" if gender == "Female" else "bn-BD-PradeepNeural"
    elif voice_type == "Bangla (IN)":
        return "bn-IN-TanishaaNeural" if gender == "Female" else "bn-IN-BashkarNeural"
    elif voice_type in ["Pali (LK Sinhala style)", "Pali"]:
        return "si-LK-ThiliniNeural" if gender == "Female" else "si-LK-SameeraNeural"
    elif voice_type == "Pali (IN Hindi style)":
        return "hi-IN-SwaraNeural" if gender == "Female" else "hi-IN-MadhurNeural"
    return "bn-BD-NabanitaNeural"

def generate_tts_audio_file_review(transcript, voice_type, gender, language_hint=None):
    if not transcript:
        raise Exception("Transcript is empty.")
    
    tts_text = transcript
    found_context = None

    import unicodedata
    def _norm(s):
        return unicodedata.normalize('NFC', s.replace(" ", "").strip())

    trans_norm = _norm(transcript)

    # Search for context corresponding to this transcript
    for cat_name, sents in state.sentences_by_category.items():
        for t, c in sents:
            if t.strip() == transcript.strip() or _norm(t) == trans_norm:
                found_context = c
                break
        if found_context:
            break

    # If voice is Bengali or Chakma, check for Bengali transliteration
    if "Bangla" in voice_type or "Chakma" in voice_type or "Bengali" in voice_type:
        if found_context and "(" in found_context and "|" in found_context:
            tts_text = found_context.split("|")[0].replace("(", "").strip()
    elif "English" in voice_type:
        # If the transcript itself is not English (e.g. Chakma/Bengali/Pali script), use English translation if available
        if found_context and "—" in found_context:
            tts_text = found_context.split("—")[-1].strip()
    elif "Pali" in voice_type:
        # For Pali, Sinhala or Hindi voices can read Pali Latin or Sinhala text
        if found_context and "(" in found_context and "|" in found_context:
            # Often first part in parenthesis is Bengali or Romanized Pali
            pass

    voice_id = get_edge_tts_voice(voice_type, gender)
    lang_prefix = state.get_language_prefix(voice_type)
    filename = f"preview_{lang_prefix}_{uuid.uuid4().hex[:10]}.mp3"
    save_path = os.path.join(state.TTS_CACHE_DIR, filename)
    
    try:
        cmd = [sys.executable, "-m", "edge_tts", "--text", tts_text, "--voice", voice_id, "--write-media", save_path]
        res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        if res.returncode != 0:
            raise Exception(f"edge-tts failed: {res.stderr}")
    except Exception as e:
        raise Exception(str(e))
    return save_path

def handle_tts_action_review(action, transcript, voice_type, gender, current_lang):
    if action == "Generate":
        try:
            save_path = generate_tts_audio_file_review(transcript, voice_type, gender, language_hint=current_lang)
            msg = "Auto-generated audio successfully. Click 'Overwrite Audio' below to save."
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

def get_sentence_choices():
    records = state.get_recorded_manifest()
    choices = []
    for i, rec in enumerate(records):
        choices.append(f"[{i}] {rec[1]}")
    return choices

def get_default_tts_voice_for_lang(lang):
    clean = state.get_clean_language_name(lang)
    if clean == "English":
        return "English"
    elif clean == "Chakma":
        return "Chakma (BD)"
    elif clean == "Pali":
        return "Pali (LK Sinhala style)"
    return "Bangla (BD)"

def load_selected_sentence(choice):
    if not choice:
        return None, "No selection", "", "Unknown", "Ready", gr.update()
    idx = int(choice.split("]")[0].replace("[", ""))
    records = state.get_recorded_manifest()
    if idx < len(records):
        rec = records[idx]
        path, trans, lang, rec_status = rec
        clean_lang = state.get_clean_language_name(lang)
        abs_path = os.path.join(state.PROJECT_ROOT, path)
        default_voice = get_default_tts_voice_for_lang(clean_lang)
        return abs_path, f"Selected: {trans}", trans, clean_lang, rec_status, default_voice
    return None, "Error loading", "", "Unknown", "Ready", gr.update()

def update_voice_details(choice, new_trans, new_lang, new_status):
    if not choice:
        return "No track selected."
    try:
        idx = int(choice.split("]")[0].replace("[", ""))
        records = state.get_recorded_manifest()
        if idx < len(records):
            records[idx][1] = new_trans
            records[idx][2] = new_lang
            records[idx][3] = new_status
            state.save_manifest(records)
            gr.Info("✅ Updated successfully!")
            return f"✅ Updated successfully! (Track {idx})"
    except Exception as e:
        return f"❌ Error updating: {str(e)}"
    return "Failed to update."

def overwrite_audio(choice, new_audio):
    if not choice or new_audio is None:
        return "Please select a sentence and record new audio."
    try:
        idx = int(choice.split("]")[0].replace("[", ""))
        records = state.get_recorded_manifest()
        if idx < len(records):
            old_rel_path, trans, lang, current_status = records[idx]
            
            is_tts = False
            if isinstance(new_audio, str):
                abs_audio = os.path.abspath(new_audio).lower()
                norm_cache = os.path.abspath(state.TTS_CACHE_DIR).lower()
                norm_tts = os.path.abspath(state.TTS_AUDIO_DIR).lower()
                if norm_cache in abs_audio or norm_tts in abs_audio or "tts" in os.path.basename(abs_audio) or abs_audio.endswith(".mp3"):
                    is_tts = True
                    
            new_rel_path, new_abs_path = state.save_audio_file(new_audio, is_tts=is_tts, language=lang)
            state.record_audio_entry(new_rel_path, trans, lang, status=current_status, is_tts=is_tts)
            
            return f"Successfully overwritten audio for: {trans}"
    except Exception as e:
        return f"Error: {str(e)}"
    return "Failed to overwrite."

def render():
    with gr.TabItem("2. Review & Re-record", id="tab-2"):
        gr.Markdown("Select a previously recorded sentence to listen to it, edit its details, or overwrite its audio.")
        
        with gr.Row():
            sentence_dropdown = gr.Dropdown(choices=get_sentence_choices(), label="Select Recorded Sentence", scale=3)
        
        with gr.Row():
            existing_audio_playback = gr.Audio(label="Current Audio", interactive=False, type="filepath")
        
        gr.Markdown("### Edit Voice Details")
        with gr.Row():
            edit_transcript = gr.Textbox(label="Transcript", scale=2)
            edit_language = gr.Dropdown(choices=["Chakma", "Pali", "Bengali", "English", "Unknown"], label="Language", scale=1)
            edit_status = gr.Dropdown(choices=["Ready", "Needs Review", "Rejected"], label="Status", scale=1)
        update_details_btn = gr.Button("Update Details")
            
        with gr.Row():
            tts_choices = ["Chakma (BD)", "Pali (LK Sinhala style)", "Pali (IN Hindi style)", "Bangla (BD)", "Bangla (IN)", "English"]
            tts_voice_dropdown = gr.Dropdown(choices=tts_choices, value="Bangla (BD)", label="TTS Language", scale=2)
            tts_gender = gr.Radio(choices=["Male", "Female"], value="Male", label="TTS Gender", scale=2)
            tts_action = gr.Radio(choices=["Generate", "Clear Cache"], label="TTS Voice", scale=2, elem_classes=["tts-action-buttons"])
                        
        read_audio_player = gr.HTML(visible=False)

        gr.Markdown("### Re-record (Overwrite Audio)")
        with gr.Row():
            rerecord_input = gr.Audio(type="filepath", label="Record New Version")
        with gr.Row():
            overwrite_btn = gr.Button("Overwrite Audio", variant="stop")
        
        review_status = gr.Textbox(label="Status", interactive=False)
        
        sentence_dropdown.change(
            fn=load_selected_sentence, 
            inputs=[sentence_dropdown], 
            outputs=[existing_audio_playback, review_status, edit_transcript, edit_language, edit_status, tts_voice_dropdown]
        )
        
        update_details_btn.click(
            fn=update_voice_details,
            inputs=[sentence_dropdown, edit_transcript, edit_language, edit_status],
            outputs=[review_status]
        )
        
        tts_action.change(
            fn=handle_tts_action_review,
            inputs=[tts_action, edit_transcript, tts_voice_dropdown, tts_gender, edit_language],
            outputs=[read_audio_player, rerecord_input, review_status, tts_action]
        )
        
        overwrite_btn.click(
            fn=overwrite_audio, 
            inputs=[sentence_dropdown, rerecord_input], 
            outputs=[review_status]
        ).then(
            fn=lambda: None, inputs=None, outputs=[rerecord_input]
        ).then(
            fn=load_selected_sentence, 
            inputs=[sentence_dropdown], 
            outputs=[existing_audio_playback, review_status, edit_transcript, edit_language, edit_status, tts_voice_dropdown]
        )
        
    return sentence_dropdown

