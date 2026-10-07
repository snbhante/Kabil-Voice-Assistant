# Changelog

All notable changes to the **Kabil - Chakma and Pali Voice Assistant** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v0.1.1-alpha] - 2026-10-07

### Added
- **Global TTS UI Panel**: Added a unified, native-looking TTS generation panel (Language, Gender, and Actions) to both the "Record New Sentences" and "Review & Re-record" tabs.
- **Auto-Load Generated Audio**: In the Review tab, automatically loading generated TTS speech into the record buffer allows reviewers to instantly overwrite old audio with high-quality synthesized speech.

### Fixed
- **Chakma Script TTS Crashes**: Resolved a critical issue where passing native Chakma Unicode (𑄃𑄎𑄴𑄠𑄧) directly to Microsoft Edge TTS caused silent WebSocket failures. The system now parses and passes the Bangla transliteration string, allowing seamless generation.
- **Windows Encoding Crashes**: Prevented Gradio server crashes on Windows environments caused by `cp1252` encoding failures when printing Chakma characters to the terminal.

## [v0.1.0-alpha] - 2026-10-06

### Added
- **Repository Architecture:** Created the foundational directory structure (`api/`, `data/`, `docs/`, `embedded/`, `models/`, `scripts/`).
- **Core Documentation:**
  - `README.md`: Project introduction and capabilities.
  - `CONTRIBUTING.md`: Guidelines for open-source community contributors.
  - `CODE_OF_CONDUCT.md`: Contributor covenant to ensure a safe environment.
  - `.gitignore`: Configured for Python, ML models, and audio data.
- **Dataset Guidelines:**
  - `docs/dataset_guidelines/phoneme_mapping.md`: Initial draft for Chakma Bengali script to IPA (International Phonetic Alphabet) mapping.
- **Raw Data Corpus:**
  - `data/raw/texts.txt`: Added initial Chakma and Pali conversational sentences, formatted with a pipe (`|`) separator for UI context parsing.
- **Audio Data Collection App:** 
  - Built a multi-tab Gradio web app (`scripts/data_collection/app.py`) to record and review audio.
  - **Tab 1:** Records new sentences, applies automatic volume normalization, and saves raw audio along with transcripts to `manifest.csv`.
  - **Tab 2 (Data Dashboard):** Allows users to review all previously saved sentences, play back the audio, and overwrite recordings.
  - Added full support for processing browser-trimmed audio arrays via `scipy.io.wavfile`.
  - Implemented `allowed_paths` to comply with strict Gradio 4 local file-serving security policies.
  - Implemented URL query parameter parsing (`?id=X`) to support deep-linking directly to specific recordings in the Review tab.
- **Custom Frontend UI:**
  - `frontend/index.html`: Created a responsive, dark-mode Tailwind CSS interface for reviewing paginated recorded audio.
  - Implemented a custom multi-mode audio player (`off`, `play-all`, `repeat-one`, `shuffle`) defaulting to single-play mode.
  - Added an "Edit" deep-link button mapping UI elements directly to the Gradio backend for seamless re-recording workflows.
### Changed
- Refined `app.py` audio normalization to use peak normalization to help mitigate low microphone volume without introducing unstable external dependencies.
