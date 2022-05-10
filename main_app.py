from flask import Flask
from flask import render_template, request, send_file
from gtts import gTTS
from gtts.lang import tts_langs
from os import remove
from time import sleep
from threading import Thread
from datetime import datetime, timedelta


app = Flask(__name__)

allowed_format = ['txt', 'pdf']
def check_valid_format(filename):
    if filename[-3:] in allowed_format:
        return True

d = tts_langs()
languages = { v:k  for k, v in d.items()}
 
old_file = []

@app.route('/', methods=['POST', 'GET'])
def main_page(): 
    if request.method == 'POST':

        file = request.files['name_file']
        file_lang = request.form['lang'] 

        if file:
            if check_valid_format(file.filename):
                try:
                    file_to_convert = file.read().decode("utf-8")
                    lang = languages[f'{file_lang}']

                    audio_file = gTTS(file_to_convert, lang=lang, slow=False)
                    audio_file_name = f'{file.filename[:-4]}.mp3'
                    audio_file.save(audio_file_name)

                    global old_file
                    if audio_file_name not in old_file:
                        old_file.append( (audio_file_name, datetime.now()) )

                    return render_template('index.html', languages=languages, audio_file_name=audio_file_name)
                except:
                    msg = 'An error occurred while converting. You may have mistakenly selected a scanned document.'
                    return render_template('index.html', languages=languages, msg=msg)
            else:
                msg = 'An error occurred while converting. You may have mistakenly selected a file with the wrong format.'
                return render_template('index.html', languages=languages, msg=msg)
        else:
            msg = 'You have not selected a file to convert.'
            return render_template('index.html', languages=languages, msg=msg)
    else:
        return render_template('index.html', languages=languages)


@app.route('/download/<audio_file_name>')
def download(audio_file_name):
    return send_file(audio_file_name, as_attachment=True)


def delete_old_files():
    global old_file

    while True:
        now = datetime.now()
        save_time = timedelta(minutes=1)
        for file, time in old_file:
            if (time + save_time) < now:
                remove(file)                    # delete from server
                old_file.remove((file, time))   # delete from list

        sleep(60)

another_thread = Thread(target=delete_old_files, args=())
another_thread.start()



if __name__ == '__main__':
    app.run(debug = True)


