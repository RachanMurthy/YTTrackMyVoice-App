import time
from pyannote.audio import Pipeline
from yttrackmyvoice.utils import get_key

print("\n\npart 1\n\n")
# Load the pre-trained diarization pipeline (ensure the token is valid and has required access)
pipeline = Pipeline.from_pretrained('pyannote/speaker-diarization-3.1', use_auth_token=get_key('SECRET_KEY_PYANNOTE'))

# Path to your audio file
audio_file = get_key('TEMP_AUDIO_FILE_PATH')

# Record the start time before processing
start_time = time.time() 
print("\n\npart 2\n\n")
# Apply diarization
diarization, embeddings = pipeline(audio_file, return_embeddings=True)

print("\n\npart 3\n\n")
# Get the list of unique speakers from the diarization labels
speakers = diarization.labels()

# Print each speaker's start/end times and corresponding embedding
for idx, speaker in enumerate(speakers):
    print(f"\nSpeaker {speaker}'s embedding:\n{embeddings[idx]}\n")
    for segment, track, spkr in diarization.itertracks(yield_label=True):
        if spkr == speaker:
            segment_start = segment.start  # Use a different variable name
            segment_end = segment.end      # Use a different variable name
            print(f"Speaker {speaker} speaks from {segment_start:.1f}s to {segment_end:.1f}s")

# Record the end time after processing
end_time = time.time() 
elapsed_time = end_time - start_time
print(f"Function execution time: {elapsed_time:.6f} seconds")

