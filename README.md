# Kabil - Chakma and Pali Voice Assistant

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Version](https://img.shields.io/badge/version-v0.1.0--alpha-orange.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)

**Kabil** is a comprehensive, open-source AI Voice Assistant designed specifically to bridge the gap in low-resource language technologies. Built from the ground up, Kabil focuses on **Chakma** and **Pali** (essential for Buddhist monastic studies and Tripitaka research), alongside Bengali and English. 

Currently, no fully functional Speech Recognition (ASR) or Speech Synthesis (TTS) systems exist for Chakma. Our mission is to build robust, community-driven models capable of understanding, translating, generating text, and speaking across these four languages. 

Whether it's for multi-platform software applications or embedded edge devices (like Raspberry Pi and ESP32), Kabil is built to be scalable, efficient, and deeply rooted in open-source principles.

## Core Capabilities
1. **Multilingual ASR:** Transcribe spoken Chakma, Pali, Bengali, and English into precise Unicode text.
2. **Multilingual TTS:** Read Unicode text in these 4 languages with natural, highly expressive human-like voice synthesis.
3. **NLP/NLU Logic:** A conversational engine designed for complex query processing, multi-way translation, and semantic search within historical databases (e.g., Tripitaka, Chakma dictionaries).
4. **Embedded System Ready:** Optimized models (TFLite/ONNX/Quantization) optimized for microcontrollers and edge deployments.

## Repository Structure Overview
```text
Kabil-Voice-Assistant/
├── api/             # FastAPI/Flask backend for NLP and model serving
├── data/            # Raw audio, processed datasets, and metadata
├── docs/            # Architecture diagrams, API specs, and project guidelines
├── embedded/        # Edge AI deployments (ESP32, Raspberry Pi, TFLite models)
├── frontend/        # Custom web UI dashboards (e.g., dataset review audio player)
├── models/          # Model weights and configs (ASR, TTS, NLP)
└── scripts/         # Utility scripts for data collection and training pipelines
```

## Quick Start & Setup
For detailed step-by-step setup, running the application, corpus expansion, and contribution rules, check out our **[SETUP&GUIDELINE.md](SETUP&GUIDELINE.md)**.

## Getting Involved
This project is fully open-source and we welcome contributors of all backgrounds—whether you are a native Chakma speaker, a Pali scholar, a Data Scientist, or a hardware enthusiast!
Please refer to our [CONTRIBUTING.md](CONTRIBUTING.md) and [SETUP&GUIDELINE.md](SETUP&GUIDELINE.md) for details on how to get started.

