"""
data_request.py

Ivan Veliki
07/2022
"""
import requests
import os
language = 'en-gb'
OXFORD_ENDPOINT="https://od-api.oxforddictionaries.com/api/v2"
#OXFORD_APP_ID=os.environ.get("OXFORD_APP_ID")
OXFORD_APP_ID='e6287830'
#OXFORD_API_KEY=os.environ.get("OXFORD_API_KEY")
OXFORD_API_KEY='e289b15c155e0d68724652b7f9d626b5'

headers ={
  "Accept": "application/json",
  "app_id":OXFORD_APP_ID,
  "app_key":OXFORD_API_KEY
}

def translate_word(word):
  #Translate Word And make Dictionary
  def send_word_request(word_id):
    url = OXFORD_ENDPOINT+'/entries/'  + language + '/'  + word_id.lower()
    response = requests.get(url, headers = headers)

    word_data=response.json()
    results=word_data["results"][0]
    lexicalEntries=results["lexicalEntries"][0]
    lexicalCategory=lexicalEntries["lexicalCategory"]["text"]
    entries=lexicalEntries["entries"][0]
    audio_file=entries["pronunciations"][0]["audioFile"]
    senses=entries["senses"][0]
    definitions=senses["definitions"]
    examples=senses["examples"]

    return make_dictionary(word_id,lexicalCategory,definitions,examples,audio_file)

  #Make Dictionary From Translated Word
  def make_dictionary(word,part_speech,definition,example_sentence,audio_file):
    temp_dic={
      "part-speech":part_speech,
      "Definition":definition,
      "Example sentence":example_sentence,
      "audio-file":audio_file
    }
    return temp_dic
  return send_word_request(word)
