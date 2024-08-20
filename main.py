import logging

from Helper import helper as hp
from Scrape import scrape as ytscrape
from Transcribe import transcribe as yttranscribe
from Translate import translate as yttranslate
from SpeechSynthesis import tts as ytspeechsynthesis
from Sync import sync as ytsync

def main():
    log_level = logging.DEBUG
    helper = hp.Helper(log_level)
    log = helper.log
    helper.create_unverified_https_context()
    work_dir = helper.fresh_work_dir(f'working_dir')
    delim = helper.define_delimiter()
     
    ######################################################
    # Replace video_link with the YouTube link of the video you want to transcribe: Streamlit UI?
    # video_link= "https://www.youtube.com/watch?v=mEsleV16qdo" # 30 hrs
    # video_link= "https://www.youtube.com/watch?v=PSNXoAs2FtQ" # 20 hrs
    # video_link= "https://www.youtube.com/watch?v=5rNk7m_zlAg" # 13 hrs
    #video_link= "https://www.youtube.com/watch?v=6nz8GXjxiHg" # 4 hrs
    #video_link= "https://www.youtube.com/watch?v=kCc8FmEb1nY" # 2 hrs
    # video_link= "https://www.youtube.com/watch?v=zjkBMFhNj_g" # 1 hr
    video_link= "https://www.youtube.com/watch?v=dN0lsF2cvm4&list=PLjRXclzlEk_M2SrV1N1RlujQJfAU5mtem&index=256&t=24s" # 4 mins
    #video_link = "https://www.youtube.com/watch?v=yzNG3NnF0YE" # 18 mins
    #video_link = "https://www.youtube.com/watch?v=ARMk955pGbg" # 42 mins
    #video_link = "https://www.youtube.com/watch?v=UUgloGXGZws&list=PLjRXclzlEk_M2SrV1N1RlujQJfAU5mtem&index=12&t=18s"
    ######################################################
    
    ######################################################
    # 1. Get the audio and video streams from the YouTube link
    ######################################################
    scraper = ytscrape.YouTubeScrape(helper)
    audio_f, video_f = scraper.get_av_stream_from_url(video_link, work_dir)

    # Convert the audio to wav format with a sample rate of 16000
    wav_f = scraper.convert_mp4_to_wav(audio_f, work_dir, 16000)

    ######################################################
    # 2. Transcribe the audio to text
    ######################################################
    transcriber = yttranscribe.HighPerfWhisper(helper)
    transcription_f = transcriber.transcribe_wav_to_text(wav_f, work_dir, 'small')

    # Separate each sentence into a new line
    prep_f = transcriber.prepare_for_translation(transcription_f, work_dir)
    
    ######################################################
    # 3. Translate the transcript from English to Korean
    ######################################################
    translator = yttranslate.Translate(helper)
    translation_f = translator.do_papago_translate(prep_f, work_dir, "en", "ko")
    
    ######################################################
    # 4. Speech Synthesis
    ######################################################
    speech_synthesizer = ytspeechsynthesis.SpeechSynthesis(helper)
    wav_f = speech_synthesizer.do_papago_tts(translation_f, work_dir, "ko")
    
    ######################################################
    # 5. Synchronize speeches with the original video
    ######################################################
    synchronizer = ytsync.Synchronizer(helper)
    sync_f = synchronizer.sync_audio_with_video(prep_f, wav_f, video_f, work_dir)
    
    
    log.info(f'All processes complete!\n')
    log.info(f'Out file: {work_dir}/{sync_f}\n')
    
    
    # Allow the user to download the synced video, the original video, and the original and translated transcript. : Streamlit UI?
    # and Summary.txt, and time_summary.txt
    # helper.zip_and_download(work_dir, "output.zip")
    
if __name__ == "__main__":
    main()