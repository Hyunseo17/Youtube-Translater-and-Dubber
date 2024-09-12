import os
import urllib.parse as urlparse
from pytube import YouTube
import logging

class YouTubeScrape:
    def __init__(self, helper):
        self.helper = helper
    
    def get_video_id(url: str) -> str:
        """
        Extract the video ID from a YouTube URL.
        This function supports various YouTube link formats:
        - http://youtu.be/{video_id}
        - http://www.youtube.com/watch?v={video_id}
        - http://www.youtube.com/embed/{video_id}
        - http://www.youtube.com/v/{video_id}?version=3&hl=en_US
        """
        query = urlparse.urlparse(url)
        if query.hostname == 'youtu.be':
            return query.path[1:]
        elif query.hostname in ('www.youtube.com', 'youtube.com'):
            if query.path == '/watch':
                params = urlparse.parse_qs(query.query)
                return params['v'][0]
            elif query.path.startswith('/embed/'):
                return query.path.split('/')[2]
            elif query.path.startswith('/v/'):
                return query.path.split('/')[2]
        # If none of the above cases match, return None
        return None
    
    def get_av_stream_from_url(self, video_link: str, out_f: str):
        yt = YouTube(video_link)
        self.helper.log.debug(f'\nVideo title: {yt.title}')
        self.helper.log.debug(f'\nVideo Link: {yt.watch_url}')
        self.helper.log.info(f'\nExtracting Video and Audio from URL..\n')

        # Get the highest quality audio/video stream
        audio = yt.streams.filter(only_audio=True).first()
        video = yt.streams.filter(only_video=True).first()
        audio.download(output_path=f'{out_f}', filename="Org_audio.mp4")
        video.download(output_path=f'{out_f}', filename="Org_video.mp4")
        org_audio_file = f'{out_f}/Org_audio.mp4'
        org_video_file = f'{out_f}/Org_video.mp4'

        self.helper.log.info(f'\nAudio file: {org_audio_file}')
        self.helper.log.info(f'\nVideo file: {org_video_file}\n')
        
        return org_audio_file, org_video_file
    
    def convert_mp4_to_wav(self, audio_file: str, out_f: str, sample_rate):
        audio_file_wav = f'{out_f}/Org_audio.wav'
        os.system(f'ffmpeg -i {audio_file} -vn -acodec pcm_s16le -ar {sample_rate} -ac 2 {audio_file_wav}')
        self.helper.log.info(f"Audio wav file: {audio_file_wav}\n")
        return audio_file_wav