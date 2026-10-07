import os
import csv
import uuid
import traceback
import gradio as gr
import scipy.io.wavfile as wavfile

import core.state as state

def get_current_sentence_display(category):
    if not category or category not in state.sentences_by_category:
        return "Please select a category."
    
    sents = state.sentences_by_category[category]
    idx = state.category_indices[category]
    
    if idx >= len(sents):
        return f"🎉 You have completed all {category} sentences!"
    
    transcript, context = sents[idx]
    if context:
        return f"### {transcript}\n\n*(Context: {context})*"
    return f"### {transcript}"

def save_new_audio(audio_data, category):
    try:
        if not category or category not in state.sentences_by_category:
            return "Please select a category.", get_current_sentence_display(category), None
            
        sents = state.sentences_by_category[category]
        idx = state.category_indices[category]
        
        if audio_data is None:
            return "Please record audio first.", get_current_sentence_display(category), None
        if idx >= len(sents):
            return "All sentences completed for this category.", get_current_sentence_display(category), None

        filename = f"sample_{uuid.uuid4().hex[:8]}.wav"
        save_path = os.path.join(state.AUDIO_DIR, filename)
        
        # Normalize and save
        sr, data = state.normalize_audio(audio_data)
        wavfile.write(save_path, sr, data)
        
        transcript = sents[idx][0]
        file_exists = os.path.isfile(state.METADATA_FILE)
        
        with open(state.METADATA_FILE, "a", encoding="utf-8", newline='') as csvfile:
            writer = csv.writer(csvfile)
            if not file_exists:
                writer.writerow(["file_path", "transcript", "language", "status"])
            writer.writerow([os.path.join("data", "raw", "audio", filename), transcript, category, "Ready"])
        
        state.category_indices[category] += 1
        return f"Saved! ({state.category_indices[category]}/{len(sents)})", get_current_sentence_display(category), save_path
        
    except Exception as e:
        error_msg = f"Crash: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return error_msg, get_current_sentence_display(category), None

def skip_sentence(category):
    if category and category in state.category_indices:
        state.category_indices[category] += 1
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
    
    sents = state.sentences_by_category[category]
    idx = state.category_indices[category]
    if idx >= len(sents):
        raise Exception("All sentences completed for this category.")
    
    transcript, context = sents[idx]
    
    tts_text = transcript
    if "Chakma" in category and ("Bangla" in voice_type or "Chakma" in voice_type):
        if context.startswith("(") and "|" in context:
            tts_text = context.split("|")[0].replace("(", "").strip()
    
    voice_id = get_edge_tts_voice(voice_type, gender)
    
    filename = f"tts_sample_{uuid.uuid4().hex[:8]}.mp3"
    save_path = os.path.join(state.AUDIO_DIR, filename)
    
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
    if action == "Read":
        try:
            save_path = generate_tts_audio_file(category, voice_type, gender)
            filename = os.path.basename(save_path)
            html_player = f'<audio autoplay src="/data/raw/audio/{filename}"></audio>'
            return html_player, gr.update(), gr.update(), None
        except Exception as e:
            safe_err = f"Error reading voice: {str(e)}"
            print(safe_err.encode('utf-8', errors='replace').decode('utf-8'))
            return "", gr.update(), gr.update(), None
    elif action == "Generate":
        try:
            save_path = generate_tts_audio_file(category, voice_type, gender)
            msg = "Auto-generated audio successfully. Click 'Submit & Next' to save."
            return "", save_path, msg, None
        except Exception as e:
            error_msg = f"Error generating voice: {str(e)}"
            print(error_msg.encode('utf-8', errors='replace').decode('utf-8'))
            return "", gr.update(), error_msg.encode('utf-8', errors='replace').decode('utf-8'), None
    return "", gr.update(), gr.update(), None


def render():
    with gr.TabItem("1. Record New Sentences", id="tab-1"):
        gr.Markdown("Read the sentence below out loud and hit record. Audio is automatically normalized (volume boosted) upon saving.")
        
        categories = list(state.sentences_by_category.keys())
        default_cat = categories[0] if categories else None
        
        category_dropdown = gr.Dropdown(choices=categories, value=default_cat, label="Select Category / Language", scale=1)
        
        sentence_display = gr.Markdown(get_current_sentence_display(default_cat))
        
        with gr.Row():
            audio_input = gr.Audio(type="filepath", label="Record your voice", sources=["microphone", "upload"])
            
        with gr.Row(variant="panel"):
            tts_choices = ["Chakma (BD)", "Pali (LK Sinhala style)", "Pali (IN Hindi style)", "Bangla (BD)", "Bangla (IN)", "English"]
            tts_voice_dropdown = gr.Dropdown(choices=tts_choices, value="Bangla (BD)", label="TTS Language", scale=2)
            tts_gender = gr.Radio(choices=["Male", "Female"], value="Male", label="TTS Gender", scale=2)
            tts_action = gr.Radio(choices=["Read", "Generate"], label="TTS Voice", scale=2)
                        
        read_audio_player = gr.HTML(visible=False)
            
        with gr.Row():
            submit_btn = gr.Button("Submit & Next", variant="primary")
            skip_btn = gr.Button("Skip")
        status_text = gr.Textbox(label="Status", interactive=False)
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Last Saved Recording")
                last_audio_playback = gr.Audio(label="Playback", interactive=False, type="filepath")

        category_dropdown.change(fn=get_current_sentence_display, inputs=[category_dropdown], outputs=[sentence_display])
        
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

