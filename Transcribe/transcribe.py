import os
import time
import re

class HighPerfWhisper:
    def __init__(self, helper):
        self.helper= helper
        
    def transcribe_wav_to_text(self, wav_file: str, out_f: str, model: str):
        self.helper.log.info(f'Transcribing the audio to text...\n')
        start_time = time.time()
        
        whisper_dir = f'{out_f}/../Transcribe/whisper.cpp'
        transcript = f'{out_f}/Org_audio'
        os.chdir(f'{whisper_dir}')
        command = f'./main -m models/ggml-{model}.en.bin -f {wav_file} -ovtt -otxt -of {transcript}'   
        os.system(command)
        # os.chdir(f'..')
        end_time = time.time()
        
        self.helper.log.info(f'Transcription complete!\n')
        self.helper.log.info(f'Transcription time: {end_time - start_time} seconds\n')
        self.helper.log.info(f'Transcription file: {transcript}.txt\n')
        return f'{transcript}.txt'
        
    def prepare_for_translation(self, in_f: str, out_f: str):
        self.helper.log.info(f'Preparing the transcript for translation...\n')
        in_file = f'{in_f}'
        out_file = f'{out_f}/Prep_audio.txt'
        
        with open(in_file, 'r') as src_f:
            lines = src_f.readlines()
            lines = [line for line in lines if line.strip()]
            with open(f'{out_file}', 'w') as prep_f:
                for line in lines:
                    line = line.replace("\n", " ")
                    line = line.replace('. ', ".\n")
                    line = re.sub('^ ', "", line)
                    prep_f.write(f'{line}')
        
        self.helper.log.info(f"Prepared translation file: {out_file}\n")
        return f'{out_file}'