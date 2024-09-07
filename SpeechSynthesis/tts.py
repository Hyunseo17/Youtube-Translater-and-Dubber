import os
import urllib.request
import moviepy.editor as mp

class SpeechSynthesis:
    def __init__(self, helper):
        self.helper = helper
    
    def merge_audio_files(self, audio_files, output_file):
        self.helper.log.info(f'Merging audio files: {audio_files}\n')
        audio_clips = [mp.AudioFileClip(f) for f in audio_files]
        audio = mp.concatenate_audioclips(audio_clips)
        # save audio to disk
        audio.write_audiofile(f'{output_file}')

        self.helper.log.info(f'Audio files merged: {output_file}\n')
        
    def do_papago_tts(self, in_file: str, working_dir, target_lang: str):
        self.helper.log.info(f'Speech Synthesizer: NaverCloudPlatform\n')

        client_id = os.getenv("CLOVA_VOICE_CLIENT_ID")
        client_secret = os.getenv("CLOVA_VOICE_API_KEY")
        
        with open (f'{in_file}', encoding='utf8') as f:
            n = 0
            lines = f.readlines()
            line_length = len(lines)
            for line in lines:
                n += 1
                print(line)
                encText = urllib.parse.quote(line)
                #data = "speaker=nara&volume=0&speed=0&pitch=0&format=mp3&text=" + encText
                #data = "speaker=nara&volume=0&speed=0&pitch=0&format=wav&text=" + encText
                #data = "speaker=nreview&volume=0&speed=-2&pitch=0&emotion=0&emotion-strength=0&alpha=0&end-pitch=0&format=wav&text=" + encText
                data = "speaker=nminsang&volume=4&speed=-2&pitch=0&emotion=0&emotion-strength=0&alpha=0&end-pitch=0&format=wav&text=" + encText
                url = "https://naveropenapi.apigw.ntruss.com/tts-premium/v1/tts"
                request = urllib.request.Request(url)
                request.add_header("X-NCP-APIGW-API-KEY-ID",client_id)
                request.add_header("X-NCP-APIGW-API-KEY",client_secret)
                
                response = urllib.request.urlopen(request, data=data.encode('utf-8'))
                rescode = response.getcode()
                if(rescode==200):
                    response_body = response.read()
                    out_file = f'{working_dir}/out_{n}.wav'
                    with open(f'{out_file}', 'wb') as f:
                        f.write(response_body)
                else:
                    print("Error Code:" + rescode)
        
        # merge audio files
        merged_audio = f'{working_dir}/out_all.wav'
        audio_files = [f'{working_dir}/out_{n}.wav' for n in range(1, line_length +1)]
        self.merge_audio_files(audio_files, merged_audio)
        
        return merged_audio