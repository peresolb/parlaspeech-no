# Replicating the process on Južne Vesti corpus

Main project repo: https://github.com/5roop/task13/

Južne vesti were crawled with [this notebook - text](https://github.com/5roop/task13/blob/main/006_crawler_preparations.ipynb) and [this script - youtube videos](https://github.com/5roop/task13/blob/main/006_downloading_audio_script.py).

From this stage the audio has been saved in /audio directory, while the transcripts were saved in a csv format [here](https://github.com/5roop/task13/blob/main/006_crawling_juznevesti.csv). The columns were `url,yt_hash,transcript,exists,path`, the most important of course being yt_hash and transcript.
At this point the paragraph structure is intact, including the prefix, indicating the prefix indicating the anchor, asking a question (i.e. `JV: `).  For subsequent tasks the unneeded whitespace and the `JV: ` tokens were removed.

Audio has been converted to mono 16kHz wav files.


The rest of the processing followed Danijel's pipeline closely:

- In notebook nr. 013 we perform the VAD, splitting, and ASR. The code used deviates from Danijel's a little; I implemented a fix that would not crash the pipeline if the splitting could not be successully performed, but would merely discard that segmend.
- Afterwards the results were filtered; instances where segmentation and transcription failed were dropped.
- The [resulting dataset](https://github.com/5roop/task13/blob/main/014_filtered_df.json) and audio files were then transfered to another server where Kaldi was installed.
- Danijel's code for Kaldi sequence matching was then adapted to work on one video at a time, matching only transcriptions from that video with the ASR results. Anchor prompts (`JV: `) were removed from transcripts to allow for better matching.
- The results were extracted from files produced as a result of Danijel's pipeline and saved alongside the filtered dataset.
- Again a pass-over was performed to filter out any instances where the pipeline failed, and the final result is the file [here](https://github.com/5roop/task13/blob/main/018_juzne_vesti.jsonl)

[Dataset](https://github.com/5roop/task13/blob/main/018_juzne_vesti.jsonl) attributes:
+ 'file': the origin of the audio data, i.e. audio file as it exists on YouTube, 
+ 'start': seconds in original file where the instance speech starts,
+ 'end': mutatis mutandis, seconds in original file where the instance speech ends, 
+ 'asr_transcription': results obtained as a result of Wav2Vec model transcription, 
+ 'webpage_transcript': results of initial alignment, reliable in the beginning, but diverging with time,
+ 'ratio': a simmilarity metric between the asr_transcription and webpage_transcript, higher is better, 
+ 'text': a moot copy of asr_transcription, need for danijel's pipeline, 
+ 'kaldi_transcript': web page transcription, aligned with Kaldi, 
+ 'kaldi_words': a list of words as aligned by Kaldi, 
+ 'kaldi_word_starts': starting timestamps of the words (above), starting at the beginning of the recording, not instance!,
+ 'kaldi_word_ends': as above, but for word ends,  
+ 'segment_file: file, containing the audio, corresponding to the instance.'

# [Dataset in ParlaSpeech-HR.v1.0 form](JuzneVesti-SR.v1.0.jsonl)

The dataset is also encoded in another form in order to match original ParlaSpeech-HR encoding as closely as possible:


* `path`: path to the segment
* `orig_file`: path to full length audio (youtube_hash + `.wav`)
* `start`: start time in seconds since the beginning of the full length audio
* `end`: end time in in seconds since the beginning of the full length audio
* `words`: raw transcript, word delimited, contains numerals, punctuation, `JV:` separators...
* `norm_words`: kaldi alignment, word delimited, with normalized, lowercased Kaldi output. Host questions are delimited with `<anchor_start>` and `<anchor_end>`.
* `norm_words_start_times`: timestamps of `norm_words` starts
* `utterance_id_start`: moot, kept for consistency with ParlaSpeech-HR.v1.0
* `utterance_id_end`: see above
* `speaker_info`: dictionary, containing keys `guest_name`, `guest_description`, `host`, and `speaker_breakdown`
* `split`: to which split the instance belongs (test (10%), dev (10%), or train (80%))

Only the instances that have been correctly transcribed are included in this dataset (this was identified by comparing `words` and `norm_words`).