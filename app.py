import os
import io
import json
import os
import base64
import requests

from elevenlabslib.helpers import *
from elevenlabslib import *
import openai
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")


@app.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        question = request.form["question"]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=generate_prompt(question),
            temperature=0.8,
            max_tokens=60,
        )
        audio_js = audio(response.choices[0].message.content)

        #choices_text = [choice.text for choice in response.choices]
        return redirect(url_for("index", result=response.choices[0].message.content,audio_js=audio_js))

    #load html without user entery(first time run)
    result = request.args.get("result")
    audio_js = request.args.get("audio_js")
    return render_template("index.html", result=result,audio_js=audio_js)



def audio(GenPrompt):
    apiKey = ""


    #Create the user object
    user = ElevenLabsUser(apiKey)

    if user.get_voice_clone_available():
        audio_data = user.get_voices_by_name("jrogan")[0].generate_audio_bytes(prompt=GenPrompt)

        # Encode the audio data as a Base64-encoded string
        audio_base64 = base64.b64encode(audio_data).decode('ascii')

        # Generate a data URL for the audio data
        audio_url = f"data:audio/mpeg;base64,{audio_base64}"

        # Set the MIME type of the audio content
        audio_mime_type = "audio/mpeg"

        # Define a JavaScript function to create the audio player
        audio_js = f'''
        <script>
        window.onload = function() {{
          var audio = document.createElement('audio');
          var source = document.createElement('source');
          source.src = "{audio_url}";
          source.type = "{audio_mime_type}";
          audio.appendChild(source);
          audio.autoplay = true;
          audio.controls = false;
          document.body.appendChild(audio);
        }};
        </script>
        '''

        return audio_js
    
def generate_prompt(question):
    return [{"role": "user", "content": """Question: {} \n\n Answer this question in Joe Rogan's tone and his speaking style within 50 words. If you don't have an answer, reply in the same tone, stating "I cant provide you with an answer". Do not mention that you are an AI language model, Do not mention you are a language model.""".format(question.capitalize())}]

