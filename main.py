from yttrackmyvoice import yyt, urls, playlist, download_audio, segment_audio

if __name__ == "__main__":
    yyt("first")
    urls("first", ["https://www.youtube.com/watch?v=gpAC_yIDljg"])
    download_audio("first")
    segment_audio("first")