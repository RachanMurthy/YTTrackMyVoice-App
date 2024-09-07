## YTTrackMyVoice (ONGOING)

**YTTrackMyVoice** is a Python-based application that processes YouTube videos or playlists and performs voice diarization to label and track individual speakers across multiple videos. The app leverages cutting-edge machine learning and speech processing technologies to accurately diarize audio and manage speaker identification efficiently.

## Features

- **YouTube Integration**: Accepts input as individual YouTube video URLs or entire playlists.
- **Audio Extraction**: Extracts audio from the video using `pytube` and supports `.webm` formats.
- **Voice Diarization**: Uses audio embeddings and diarization techniques to identify different speakers in the videos.
- **Multi-Video Consistency**: Track and label speakers consistently across multiple videos in a playlist.
- **Speech-to-Text**: Integrates with services like **AssemblyAI** to transcribe extracted audio and identify speaker dialogues.
- **Speaker Labeling**: Semi-supervised machine learning models cluster and label each speaker based on voice embeddings.

## How It Works

The workflow of the application is as follows:

1. **Input: YouTube URLs or Playlist**
    - The user provides a list of URLs or a YouTube playlist.
    - `pytube` is used to extract audio from the provided videos.

2. **Audio Processing**:
    - Audio is extracted and converted into a `.webm` format.
    - Audio embeddings (video ID, timestamps, and embeddings) are created for each video.

3. **Database Storage**:
    - All relevant data such as video IDs, timestamps, embeddings, extracted texts, and voice labels are stored in a DBMS for future retrieval and analysis.

4. **Audio Segmentation**:
    - The extracted audio is segmented using timestamps for more accurate voice labeling and text extraction.

5. **Speech-to-Text**:
    - Audio segments are sent to **AssemblyAI** (or other speech-to-text services) to generate transcriptions of the content.
    - Extracted texts are associated with corresponding timestamps for easy reference.

6. **Machine Learning Model**:
    - A machine learning model processes the extracted audio embeddings and text.
    - Clustering and semi-supervised learning techniques are used to label and group different speakers across the videos.

7. **Output**:
    - The final output includes labeled speakers and transcribed text for the entire video playlist, which can be visualized or exported.

## Technologies Used

- **pytube**: For extracting audio from YouTube videos.
- **pydub**: For processing and segmenting audio.
- **AssemblyAI**: For speech-to-text conversion.
- **Machine Learning**: Semi-supervised learning for speaker labeling.
- **Python**: Core language for developing the application.
