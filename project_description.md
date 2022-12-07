# Norwegian ParlaSpeech project description
## Introduction
This document describes the planned procedure for making a Norwegian ParlaSpeech corpus (*ParlaSpeech-NO*), modelled on the [Croatian ParlaSpeech corpus](https://www.clarin.si/repository/xmlui/handle/11356/1494), a large speech corpus of parliamentary speech in Norwegian intended for ASR training and testing. ParlaSpeech-NO will consist of audio recordings extracted from the video recordings of Stortinget, the Norwegian parliament. These are segmented and aligned segment per segment with the corresponding text in the Norwegian subcorpus of [ParlaMint](https://www.clarin.eu/parlamint), consisting of the official proceedings from Stortinget and corresponding metadata. ParlaSpeech-NO is developed by the [Language Bank](https://www.nb.no/sprakbanken/en/sprakbanken/) and the [AI lab](https://ai.nb.no/) at the National Library of Norway. The corpus will be released with an open license in the repository of the Language Bank.

There is a closely related corpus for Norwegian, the Norwegian Parliamentary Speech Corpus (NPSC), which was released by the Language Bank in 2021. This corpus consists of about 126 hours of manually transcribed audio from Storinget. In the NPSC project, the transcriptions were purpose-made and not extracted from the official proceedings. It has been shown, e.g. by the Croatian ParlaSpeech project and [OpenAI's Whisper](https://openai.com/blog/whisper/), that it is possible to train ASR systems with state-of-the-art performance on non-verbatim transcriptions, but that it requires more data. By extracting transcriptions from the official proceedings, it is possible to create a much larger dataset than the NPSC automatically.

After having collected the audio data and textual data, we plan to segment the audio files with Voice Activity Detection (VAD) to obtain speech segments. These speech segments will be run through a Norwegian SST system. The ASR output of each segment will be aligned with the official transcripts. In order to do this, we need to produce a normalized version of the transcripts which resembles the ASR output as much as possible. We can then extract the transcriptions for the speech segments, in addition to metadata about the speaker of the particular segment registered in ParlaMint. The dataset can be released, and we can train and release ASR models trained on it.

Note that there has been a similar initiative for Danish, [FT Speech](https://ftspeech.github.io/), which may serve as a source of inspiration for the current project in addition to the Croatian project.

## Data collection
At the time of writing (October 2022), this step is mostly completed.

We parsed the website of the Stortinget video archive and found the links to all the mp4 files. We then downloaded the files using Wget. The video files were subsequently converted to wav with a sample rate of 16kHz. We also kept the unmodified audio track of each video.

The videos are from meetings at Stortinget from 2010 to 2022. The duration is 6689 hours. If we assume that about 90% percent of the audio contains speech (as it did in the NPSC), we have about 6020 hours of speech. We will not be able to extract transcriptions for all the speech segments, but we will still most likely end up with a transcribed dataset which is several times larger than all the open, Norwegian speech datasets that exist today taken together.

For the textual data, we will use the xml files in the Norwegian subcorpus of ParlaMint, which will be released in November 2022. This corpus consists of all the proceedings from Stortinget dating back to the late 90-ies.

## Pilot and full-scale version
We need to run the segmentation-ASR-matching pipeline in an environment which can handle the large quantity of long audio files, and we probably should use some kind of multiprocessing. Before setting this up, we will test and develop a pilot version og the pipeline with a smaller quantity of audio files, which can be run on standard hardware with one GPU. When we have a working system, we will look into how we can scale it up.

## Segmentation and initial ASR
For the segmentation, we will use [Silero VAD](https://github.com/snakers4/silero-vad), and merge shorter segments into larger segments using resegmentation code from the Croatian ParlaSpeech project. Segments will have a maximum length of 30 segments. The ParlaSpeech code has functionality for splitting up segments from the VAD which are longer than 30 seconds. 

The audio segments will be transcribed with the [Bokmål wav2vec model](https://huggingface.co/NbAiLab/nb-wav2vec2-1b-bokmaal) trained on the NPSC by the AI lab at the National Library of Norway. It might be necessary with a second transcription with the [Nynorsk model](https://huggingface.co/NbAiLab/nb-wav2vec2-300m-nynorsk), in order to get a better matching of segments written in Nynorsk in the proceedings.

## XML parsing
The text from the proceedings should be extracted from the ParlaMint-NO XML files, using e.g. BeautifulSoup. If we need the timestamps for the matching, we should extract those (see below). We need to look into what kind of segmentation we need, either sentences or words.

## Normalization
Even in the case of correct transcriptions, the ASR output and the proceedings do not always correspond. Firstly, the ASR output contains transcriptions of hesitations and other non-language verbal sounds, which the proceedings do not. These must be removed before matching. Secondly, the ASR transcriptions have what we might call a verbalized form: numbers are written with letters as they are pronunced ("ett hundre" not "100"), dates are similarly written with letters, and abbreviations are not used. The proceedings, on the other hand, have a regular, written form. In order for the matching to be as successful as possible, we should either produce written forms from the ASR output, so-called *inverse normalization*, or produce verbalized forms from the proceedings, called *normalization*. It probably makes the most sense to do inverse normalization in this case, as the mapping from written form to verbalized form may be a one-to-many mapping in some cases. 

We will make Norwegian inverse normalization grammars for [NVIDIA's NeMo toolkit](https://github.com/NVIDIA/NeMo/tree/main/). Since we probably want to produce verbalized forms of the final corpus too, and since it may be a useful resource for others, we will also make Norwegian normalization grammars. 

## Matching
After normalization, we can try to match segments in the ASR output with the corresponding segments in the proceedings, and by consequence audio segments with proceedings text segments. For this, we can either use a rule-based system, e.g. that of the Croatian ParlaSpeech project, or use some kind of ML-based method. Some of the proceedings come with turn-level (?) timestamps, and it is possible that these can be exploited to narrow the search space. In the FT Speech project, they used a similar alignment method to LibriSpeech, which is also worth looking into.

## Output formats
The output of the project will be in a JSONL format, where the audio file, the proceedings text, timestamps and various metadata about the speaker, audio formats etc. are recorded. It will be easy to convert this format to any other format which may be useful, such as csv or Huggingface datasets. We will decide whether to release the corpus with the full audio files of the parliamentary meetings or segmented audio files of the transcribed segments. If we do the former, it will be easy for users to extract the segmented files from the timestamps. 


## ASR experiments
Once the corpus is made, we will make canonical data splits and train and evaluate ASR models on the data. Using the normalization grammars developed in the project, we can make versions of the dataset in verbalized form and train models both on written form and verbalized form transcriptions.
