import gradio as gr
import os
import uuid
import csv
import shutil
import numpy as np
import scipy.io.wavfile as wavfile
import traceback

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
TEXTS_FILE = os.path.join(PROJECT_ROOT, "data", "raw", "texts.txt")
AUDIO_DIR = os.path.join(PROJECT_ROOT, "data", "raw", "audio")
METADATA_FILE = os.path.join(PROJECT_ROOT, "data", "metadata", "manifest.csv")

os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(os.path.dirname(METADATA_FILE), exist_ok=True)

# Load sentences
sentences = []
if os.path.exists(TEXTS_FILE):
    with open(TEXTS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                if ". " in line[:4]:
                    line = line.split(". ", 1)[1]
                if "|" in line:
                    transcript, context = line.split("|", 1)
                    sentences.append((transcript.strip(), context.strip()))
                else:
                    sentences.append((line, ""))
else:
    sentences = [("Error: texts.txt not found.", "")]

# Helper: Audio Normalization to fix low volume
def normalize_audio(filepath_or_tuple):
    # Reads, normalizes volume to max, and returns (sr, data)
    if isinstance(filepath_or_tuple, str):
        sr, data = wavfile.read(filepath_or_tuple)
    else:
        sr, data = filepath_or_tuple
        
    if data.dtype == np.int16:
        data = data.astype(np.float32)
        max_val = np.max(np.abs(data))
        if max_val > 0:
            data = data / max_val * 32767.0
        data = data.astype(np.int16)
    elif data.dtype in (np.float32, np.float64):
        max_val = np.max(np.abs(data))
        if max_val > 0:
            data = data / max_val
    return sr, data

# State for Tab 1
current_index = 0

def get_current_sentence_display():
    if not sentences:
        return "No sentences available."
    if current_index >= len(sentences):
        return "🎉 You have completed all sentences!"
    transcript, context = sentences[current_index]
    if context:
        return f"### {transcript}\n\n*(Context: {context})*"
    return f"### {transcript}"

def save_new_audio(audio_data):
    global current_index
    try:
        if audio_data is None:
            return "Please record audio first.", get_current_sentence_display(), None
        if current_index >= len(sentences):
            return "All sentences completed.", get_current_sentence_display(), None

        filename = f"sample_{uuid.uuid4().hex[:8]}.wav"
        save_path = os.path.join(AUDIO_DIR, filename)
        
        # Normalize and save
        sr, data = normalize_audio(audio_data)
        wavfile.write(save_path, sr, data)
        
        transcript = sentences[current_index][0]
        file_exists = os.path.isfile(METADATA_FILE)
        
        with open(METADATA_FILE, "a", encoding="utf-8", newline='') as csvfile:
            writer = csv.writer(csvfile)
            if not file_exists:
                writer.writerow(["file_path", "transcript"])
            writer.writerow([os.path.join("data", "raw", "audio", filename), transcript])
        
        current_index += 1
        return f"Saved! ({current_index}/{len(sentences)})", get_current_sentence_display(), save_path
        
    except Exception as e:
        error_msg = f"Crash: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return error_msg, get_current_sentence_display(), None

def skip_sentence():
    global current_index
    current_index += 1
    return "Skipped.", get_current_sentence_display(), None

# --- TAB 2 LOGIC ---
def get_recorded_manifest():
    records = []
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None) # skip header
            for row in reader:
                if len(row) == 2:
                    records.append((row[0], row[1]))
    return records

def get_sentence_choices():
    records = get_recorded_manifest()
    choices = []
    for i, (path, trans) in enumerate(records):
        choices.append(f"[{i}] {trans}")
    return choices

def load_selected_sentence(choice):
    if not choice:
        return None, "No selection"
    idx = int(choice.split("]")[0].replace("[", ""))
    records = get_recorded_manifest()
    if idx < len(records):
        path, trans = records[idx]
        abs_path = os.path.join(PROJECT_ROOT, path)
        return abs_path, f"Selected: {trans}"
    return None, "Error loading"

def overwrite_audio(choice, new_audio):
    if not choice or new_audio is None:
        return "Please select a sentence and record new audio."
    try:
        idx = int(choice.split("]")[0].replace("[", ""))
        records = get_recorded_manifest()
        if idx < len(records):
            old_rel_path, trans = records[idx]
            abs_path = os.path.join(PROJECT_ROOT, old_rel_path)
            
            # Normalize and Overwrite the exact same file
            sr, data = normalize_audio(new_audio)
            wavfile.write(abs_path, sr, data)
            
            return f"Successfully overwritten audio for: {trans}"
    except Exception as e:
        return f"Error: {str(e)}"
    return "Failed to overwrite."

def load_from_url(request: gr.Request):
    # Parse "?id=X" from the query params if available
    if request and hasattr(request, 'query_params'):
        item_id = request.query_params.get("id")
        if item_id is not None:
            try:
                idx = int(item_id)
                choices = get_sentence_choices()
                if idx < len(choices):
                    # Switch to tab-2 and select the given choice
                    return gr.update(selected="tab-2"), gr.update(value=choices[idx], choices=choices)
            except ValueError:
                pass
    # Default behavior if no id or invalid id: stay on tab-1
    return gr.update(selected="tab-1"), gr.update(choices=get_sentence_choices())

# --- UI ---
with gr.Blocks(title="Kabil Data Collector") as demo:
    gr.Markdown("# 🎙️ Kabil Audio Data Collection")
    
    with gr.Tabs() as tabs:
        with gr.TabItem("1. Record New Sentences", id="tab-1"):
            gr.Markdown("Read the sentence below out loud and hit record. Audio is automatically normalized (volume boosted) upon saving.")
            sentence_display = gr.Markdown(get_current_sentence_display())
            with gr.Row():
                audio_input = gr.Audio(type="filepath", label="Record your voice")
            with gr.Row():
                submit_btn = gr.Button("Submit & Next", variant="primary")
                skip_btn = gr.Button("Skip")
            status_text = gr.Textbox(label="Status", interactive=False)
            gr.Markdown("### Last Saved Recording")
            last_audio_playback = gr.Audio(label="Playback", interactive=False, type="filepath")
            
            submit_btn.click(fn=save_new_audio, inputs=[audio_input], outputs=[status_text, sentence_display, last_audio_playback]).then(fn=lambda: None, inputs=None, outputs=[audio_input])
            skip_btn.click(fn=skip_sentence, inputs=None, outputs=[status_text, sentence_display, last_audio_playback])
            
        with gr.TabItem("2. Review & Re-record", id="tab-2"):
            gr.Markdown("Select a previously recorded sentence to listen to it, or record a new version to overwrite it.")
            
            refresh_btn = gr.Button("Refresh List")
            sentence_dropdown = gr.Dropdown(choices=get_sentence_choices(), label="Select Recorded Sentence")
            
            with gr.Row():
                existing_audio_playback = gr.Audio(label="Current Audio", interactive=False, type="filepath")
            
            gr.Markdown("### Re-record (Overwrite)")
            rerecord_input = gr.Audio(type="filepath", label="Record New Version")
            overwrite_btn = gr.Button("Overwrite Audio", variant="stop")
            review_status = gr.Textbox(label="Status", interactive=False)
            
            refresh_btn.click(fn=lambda: gr.update(choices=get_sentence_choices()), inputs=None, outputs=[sentence_dropdown])
            sentence_dropdown.change(fn=load_selected_sentence, inputs=[sentence_dropdown], outputs=[existing_audio_playback, review_status])
            overwrite_btn.click(fn=overwrite_audio, inputs=[sentence_dropdown, rerecord_input], outputs=[review_status]).then(fn=lambda: None, inputs=None, outputs=[rerecord_input]).then(fn=load_selected_sentence, inputs=[sentence_dropdown], outputs=[existing_audio_playback, review_status])
            
    demo.load(fn=load_from_url, inputs=None, outputs=[tabs, sentence_dropdown])

if __name__ == "__main__":
    print("Starting Kabil Data Collector...")
    demo.launch(allowed_paths=[PROJECT_ROOT])
