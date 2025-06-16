# YTTrackMyVoice

YTTrackMyVoice is a Python tool that extracts audio from YouTube videos and diarizes speech to identify and track individual speakers across a playlist. The project integrates audio processing, machine learning, and speech-to-text services to generate labeled, searchable audio segments.

## Quick Start

1. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the main script to create a project and process a YouTube URL:
   ```bash
   python main.py
   ```
   Edit `main.py` to customize URLs, playlist handling, or other settings.

Full feature details are available in [docs/README.md](docs/README.md).

## Key Features

- **YouTube Integration** – download audio from individual videos or entire playlists.
- **Segmentation and Embeddings** – split audio into segments and compute embeddings for speaker diarization.
- **Speaker Labeling and Transcription** – cluster embeddings to label speakers and transcribe segments for text search.

## Technologies

This project relies on `pytube`, `pydub`, various machine learning libraries, and Python 3. See `requirements.txt` for the full list of packages.

## Resume Summary

- Designed and implemented an end-to-end pipeline for YouTube audio diarization.
- Leveraged machine learning and speech-to-text APIs to label speakers across large playlists.
- Built CLI-style utilities for downloading, segmenting, embedding, and transcribing audio.
