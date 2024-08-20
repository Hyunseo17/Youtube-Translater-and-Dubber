import os
import json
import urllib.request

class Translate:
    def __init__(self, helper):
        self.helper = helper
        
    def do_papago_translate_line(self, in_text: str, src_lang: str, target_lang: str):
        client_id = os.getenv("PAPAGO_CLIENT_ID")
        client_secret = os.getenv("PAPAGO_CLIENT_SECRET")
        encText = urllib.parse.quote(in_text)
        url = "https://naveropenapi.apigw.ntruss.com/nmt/v1/translation"
        
        data = f'source=en&target={target_lang}&text=' + encText
        itxt = in_text.strip()
        self.helper.log.info(f'{itxt}')
        
        request = urllib.request.Request(url)
        request.add_header("X-NCP-APIGW-API-KEY-ID",client_id)
        request.add_header("X-NCP-APIGW-API-KEY",client_secret)
        response = urllib.request.urlopen(request, data=data.encode("utf-8"))
        rescode = response.getcode()

        if rescode == 200:
            response_body = response.read()
            response_decode = response_body.decode('utf-8')
            data_dict = json.loads(response_decode)
            translated_text = data_dict['message']['result']['translatedText']
            self.helper.log.info(f'{translated_text}\n')
        else:
            self.helper.log.error("Error Code:", rescode)

        return translated_text
    
    def do_papago_translate(self, in_f: str, out_f: str, src_lang: str, target_lang: str):
        self.helper.log.info(f'Translating the transcript with Papago...\n')
        out_file = f'{out_f}/Translatedd_Text_Papago.txt'
        with open(f'{in_f}', 'r') as src_f:
            lines = src_f.readlines()
            with open(f'{out_file}', 'w') as dst_f:
                for line in lines:
                    translated = self.do_papago_translate_line(line, src_lang, target_lang)
                    dst_f.write(f'{translated}\n')
        self.helper.log.info(f"Translation done with Papago: {out_file}\n\n")
        return f'{out_file}'