from yttrackmyvoice import yyt, urls, playlist, download_audio, segment_audio, store_embedding_and_timestamp, retrieve_embeddings, embedd_audio

if __name__ == "__main__":
    yyt("first")
    urls("first", ["https://www.youtube.com/watch?v=xooyDuq0emI"])
    download_audio("first")
    segment_audio("first")
    embedd_audio("first")
