# -*- coding: utf-8 -*-
"""
Created on Fri Aug 22 12:04:59 2025

@author: Jegou
"""

from flask import Flask, render_template, request
from functions import *

app = Flask(__name__)

    
@app.route("/")
def index():
    original_story = load_file(name=1)
    return render_template("home.html", original_story = original_story)

@app.route("/write/", methods=['POST'])
def move_forward():
    #0 means it selects a random story
    num_story = select_file(0)
    #The number of printed sentences is 3 only editable in the function file.
    sen = get_last_sentences(name = num_story)

    return render_template('write.html', num_story = str(num_story), phrase_1 = sen[0], phrase_2 = sen[1],phrase_3 = sen[2]);

# @app.route("/save/", methods=['POST'])
# def save_story():
#     #If the submit button is pressde
#     if request.method == 'POST':
#         # Retrieve the text from the textarea
#         num_story = request.form.get("num_story") 
#         text = request.form.get("story")
#         if text is None:
#             print('Not passed')
#         elif len(text) > 30:
#             print('passed')
#             write_file(num_story, text)
            
#     return render_template('Merci.html');

@app.route("/save/", methods=['POST'])
def save_story():
    #If the submit button is pressde
    if request.method == 'POST':
        # Retrieve the text from the textarea
        num_story = request.form.get("num_story") 
        sen = get_last_sentences(name = num_story)
        text = request.form.get("story")
        n_sentences = get_n_sentences(name = None, text = text)
        if n_sentences < 5:
            print('Not passed')
            return render_template('write_bis.html', num_story = str(num_story), phrase_1 = sen[0], phrase_2 = sen[1],phrase_3 = sen[2], prev_text = text, n_sentences = n_sentences)
        else:
            print('passed')
            write_file(num_story, text)
            return render_template('Merci.html');


if __name__ == '__main__':
   app.run()
   #app.run(host="0.0.0.0", port=80)
