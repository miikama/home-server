import time
from typing import List
import os
import requests
import asyncio
import base64
from homeserver import logger

from homeserver.voice_control.sound_utilities import record_audio, play_back_audio
from homeserver.voice_control import VOICE_CONTROL_DIR



MODEL_DIR = "models"
SNOWBOY_API_ENDPOINT = "https://snowboy.kitt.ai/api/v1/train/"
VOICE_SAMPLE_LENGTH = 3

class QueryParamaters:
    
    class Gender:
        MALE = 'M'
        FEMALE = 'F'
        

    class AgeGroups:
        ages = ['0_9', '10_19', '20_29', '30_39', '40_49', '50_59', '60+']

    class Languages:
        langs = ['Arabic',
                'Chinese',
                'Dutch',
                'English',
                'French',
                'German',
                'Hindi',
                'Italian',
                'Japanese',
                'Korean',
                'Persian',
                'Polish',
                'Portuguese',
                'Russian',
                'Spanish',
                'Other']

        lang_codes = ['ar',
                'ch',
                'du',
                'en',
                'fr',
                'de',
                'hi',
                'it',
                'ja',
                'ko',
                'fa',
                'pl',
                'pt',
                'ru',
                'es',
                'ot']





def get_model_folder() -> str:

    # the absolute directory of this python file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_dir = os.path.join(script_dir, MODEL_DIR)

    return model_dir


    
def available_models(path_type="relative") -> List[str]:

    assert(path_type in ('relative', 'absolute'))

    models = []

    model_dir = get_model_folder()

    # walk the files in the model directory
    files_in_model_dir = os.listdir(model_dir)

    for possible_model_file in files_in_model_dir:

        if possible_model_file.endswith("pmdl"):

            models.append(possible_model_file)

    # return absolute model paths
    if path_type == "absolute":
        models = [os.path.join(model_dir, model) for model in models]

    return models

def print_available_models():
    model_dir = get_model_folder()
    models = available_models()    

    print("Following models are available in directory {}:".format(model_dir))
    print("")
    for mfile in models:
        print("{}".format(mfile))
    print("")



def get_wave(fname):
    with open(fname, 'rb') as infile:
        return base64.b64encode(infile.read()).decode('utf-8')

def get_api_token():    
    key = os.environ.get('SNOWBOY_API_KEY')
    if not key:
        print("""No snowboy api key. 
        
Go to {} 
for instructions where to get the key.
        
Then store the key in your shell environment variable,         
e.g. SNOWBOY_API_KEY=thelonglistofnumbers""".format("http://docs.kitt.ai/snowboy/#restful-api-calls"))

        return ""

    return key



def train_new_model(wav_files=[],
                    gender=QueryParamaters.Gender.MALE, \
                    age_group=QueryParamaters.AgeGroups.ages[2], \
                    language=QueryParamaters.Languages.lang_codes[-1]):



    logger.info("Training new model")

     # get the Snowboy api token
    api_key = get_api_token()
    if not api_key:
        return

    model_name = input("""    
What should the model be named?
...
""")

    if len(wav_files) != 3:
        print("Training requires 3 voice samples, press Enter to start recording the first one.")    
        wav_files = []

        # record 3 samples
        for index in range(1,4):
            input("Start the recording of sample {}...".format(index))
            audio_file = os.path.join(VOICE_CONTROL_DIR, 'resources', 'voiceque{}.wav'.format(index))
            wav_files.append(audio_file)
            record_audio(VOICE_SAMPLE_LENGTH, audio_file)

        logger.info("Succefully recorded 3 samples")

    # parse the model name
    parsed_name = "my_model"
    try:
        parsed_name = str(model_name).strip()
        if parsed_name.endswith('.umdl'):
            parsed_name = parsed_name[0:-5]
    except:
        pass
    
    
    data = {
        "name": parsed_name,
        "language": language,
        "age_group": age_group,
        "gender": gender,        
        "token": api_key,
        "microphone": "default",
        "voice_samples": [
            {"wave": get_wave(wav_files[0])},
            {"wave": get_wave(wav_files[1])},
            {"wave": get_wave(wav_files[2])}
        ]
    }

    # where to put the ready model
    model_name = parsed_name + '.pmdl'
    model_dir = get_model_folder()    
    model_file = os.path.join(model_dir, model_name)

    response = requests.post(SNOWBOY_API_ENDPOINT, json=data)
    if response.ok:
        with open(model_file, "wb") as outfile:
            outfile.write(response.content)
        logger.info("Created model saved to {}.".format(model_file))
    else:
        logger.info("Creating hotword failed.")
        logger.info(response.text)

    
    
    






