import subprocess
import sys
import uuid
import os
import gradio as gr

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

def generate_tts_audio_file_review(choice, transcript, voice_type, gender, state):
    if not transcript:
        raise Exception("Transcript is empty.")
    
    tts_text = transcript
    
    if "Chakma" in voice_type or "Bangla" in voice_type:
        for cat_name, sents in state.sentences_by_category.items():
            for t, c in sents:
                if t == transcript:
                    if c and c.startswith("(") and "|" in c:
                        tts_text = c.split("|")[0].replace("(", "").strip()
                    break

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

def handle_tts_action_review(action, choice, transcript, voice_type, gender, state):
    if action == "Read":
        try:
            save_path = generate_tts_audio_file_review(choice, transcript, voice_type, gender, state)
            filename = os.path.basename(save_path)
            html_player = f'<audio autoplay src="/data/raw/audio/{filename}"></audio>'
            return html_player, gr.update(), gr.update(), None
        except Exception as e:
            safe_err = f"Error reading voice: {str(e)}"
            print(safe_err.encode('utf-8', errors='replace').decode('utf-8'))
            return "", gr.update(), gr.update(), None
    elif action == "Generate":
        try:
            save_path = generate_tts_audio_file_review(choice, transcript, voice_type, gender, state)
            msg = "Auto-generated audio successfully."
            return "", save_path, msg, None
        except Exception as e:
            error_msg = f"Error generating voice: {str(e)}"
            print(error_msg.encode('utf-8', errors='replace').decode('utf-8'))
            return "", gr.update(), error_msg.encode('utf-8', errors='replace').decode('utf-8'), None
    return "", gr.update(), gr.update(), None
