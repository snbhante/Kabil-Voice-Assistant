# Changelog

All notable changes to the **Kabil - Chakma and Pali Voice Assistant** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

### Changed
- Refined `app.py` audio normalization to use peak normalization to help mitigate low microphone volume without introducing unstable external dependencies.
