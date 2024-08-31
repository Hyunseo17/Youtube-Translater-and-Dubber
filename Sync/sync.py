import os
import re

class Synchronizer:
    def __init__(self, helper):
        self.helper = helper
    
    def extract_line_number_with_specific_string(self, file, string, n_words, matching_vtt_line_num):
        with open(file, 'r') as f:
            lines = f.readlines()
            i = matching_vtt_line_num
            for i in range(i, len(lines)):
                if (i == 136):
                    print('I am here.')
                    
                line = lines[i-1]
                if i < len(lines)-2:
                    next_text_line = lines[i+2]
                else:
                    next_text_line = ''
                    
                if (len(line.split()) < n_words and not string in line) or re.search(r'-->', line):
                    continue
                
                if string in line:
                    return i, line
                
                #check if the line ended within the n_word of string
                #n_words = len(string.split())
                #for n in range(n_words-1):
                for n in range(len(string.split())):
                    partial_match = re.search(rf'{string.split()[n]}\n$', line)
                    if partial_match == None:
                        matched_word = ''
                    elif n == 0:
                        matched_word = string.split()[0]
                    else:
                        matched_word = f'{string.split()[0]} {string.split()[1]}'
                    
                    if partial_match:
                        #check if the next_text_line begins with next word
                        #cutoff_string = f'{matched_word} {string[len(partial_match.group(0)):]}'
                        cutoff_string = f'{string[len(matched_word.strip()):]}'
                        cutoff_string = f' {cutoff_string.strip()}'
                        if (next_text_line.startswith(cutoff_string)):
                            return i, line
                # text_match = not (re.search(r'-->', line))
                # if text_match and not partial_match:
                #     raise ValueError(f'No line with {string} found in {file}')
                    
    def extract_line_at_line_number(self, file, line_number):
        with open(file, 'r') as f:
            lines = f.readlines()
            return lines[line_number-1]

    def extract_first_n_words_from_line(self, line, n):
        words = line.split()
        return ' '.join(words[:n])

    def convert_time_to_ms(self, time):
        #time = "00:00:24.350"
        time = time.split(':')
        hour = time[0]
        minute = time[1]
        second = time[2].split('.')[0]
        milisecond = time[2].split('.')[1]

        hours = int(hour)
        minutes = int(minute)
        seconds = int(second)
        miliseconds = float(milisecond)/1000

        time_ms = int(round(((hours * 3600 + minutes * 60 + seconds + miliseconds) * 1000), 0))
        return time_ms

    def get_sentence_start_time(self, time, line, str):
        s_ms = self.convert_time_to_ms(time.split(' --> ')[0])
        e_ms = self.convert_time_to_ms(time.split(' --> ')[1])
        line_length = len(line)
        
        m = re.match(rf'.*{str}', line)
        m_first_word = re.match(rf'.*{str.split()[0]}\n$', line)
        if len(str.split()) > 1:
            m_second_word = re.match(rf'.*{str.split()[1]}\n$', line)
        
        if m :
            str_length = (m.span()[1] -1) - len(str)
        elif m_first_word:
            str_length = m_first_word.span()[1] - len(str.split()[0])
        elif m_second_word:
            str_length = m_second_word.span()[1] - (len(str.split()[1]) + len(str.split()[0])+1)

        duration = e_ms - s_ms
        
        start_time = round(s_ms + (duration * (str_length / line_length)))
        
        return start_time

    def put_to_start_time_file(self, start_time, sentence, sent_num, start_time_file):
        with open(start_time_file, 'a') as f:
            f.write(f'{sent_num}:{start_time}: {sentence}')
            self.helper.log.info(f'Wrote to start_time_file: {sent_num}:{start_time}: {sentence}')

    def compose_mixing_command(self, video, start_time_file, work_dir):
        cmd = f'ffmpeg -y -i {video} '
        audios = ''
        filters = ''
        mixes = ''
        maps = '' 
        
        with open(start_time_file, 'r') as f:
            lines = f.readlines()
            for n, line in enumerate(lines, start = 1):
                audios = audios + f' -i {work_dir}/out_{n}.wav'

                start_time = int(line.split(":")[1])
                
                filters = filters + f' [{n}:a] adelay={start_time}|{start_time} [voice{n}];'
                
                mixes = mixes + f'[voice{n}]'       
        
        maps = maps + f' -map 0:v -map \"[audio_out]\" -c:v copy -c:a aac {work_dir}/out_video.mp4'
        myCmd = cmd + audios + f' -filter_complex \"' + filters + mixes + f' amix=inputs={n}:duration=longest [audio_out]\" ' + maps
        
        with open(f'{work_dir}/mix_cmd.sh', 'w') as f:
            f.write(myCmd)
            
        os.chmod(f'{work_dir}/mix_cmd.sh', 0o755)
        self.helper.log.info(f'Wrote to mix_cmd.sh: {work_dir}/mix_cmd.sh')
        
        
    def sync_audio_with_video(self, prep_f: str, audio_f: str, video_f: str, work_dir: str):
        self.helper.log.info(f'Synchronizing audio with video...\n')
        n_words = 3
        matching_vtt_line_num = 1
        org_vtt_file = f'{work_dir}/Org_audio.vtt'
        start_time_file = f'{work_dir}/start_times.txt'
        
        with open(prep_f, 'r') as f:
            sentences = f.readlines()
            for sent_num, sentence in enumerate(sentences, start=1):
                if sent_num == 50:
                    print('I am here.')

                my_str = self.extract_first_n_words_from_line(sentence, n_words)
                
                my_line_num, my_line = self.extract_line_number_with_specific_string(org_vtt_file, my_str, n_words, matching_vtt_line_num)
                
                matching_vtt_line_num = my_line_num
                
                my_time = self.extract_line_at_line_number(org_vtt_file, my_line_num - 1)
                
                start_time = self.get_sentence_start_time(my_time, my_line, my_str)
                
                self.put_to_start_time_file(start_time, sentence, sent_num, start_time_file)
        
        video = f'{work_dir}/Org_video.mp4'
        self.compose_mixing_command(video, start_time_file, work_dir)
        self.helper.log.info(f'Running composed mixing command: {work_dir}/mix_cmd.sh')
        os.system(f'{work_dir}/mix_cmd.sh')



        self.helper.log.info(f'Audio synchronized with video: ..\n')
        return "output.mp4"