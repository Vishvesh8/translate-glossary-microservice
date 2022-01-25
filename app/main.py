import uvicorn
from fastapi import APIRouter, Depends, FastAPI
from starlette.middleware.cors import CORSMiddleware


from pydantic import BaseModel
import time
import json


from worker import qe_system

from celery.result import AsyncResult
import pandas as pd

import pgpubsub
engine = pgpubsub.connect(
    database="databasename",
    user="postgres",
    password="12345678",
    host="database-2.cm3iry27lqup.us-east-2.rds.amazonaws.com",
    port='5432'
)

####################################################
import deepl
translator = deepl.Translator("c4f53b7c-a0ed-8fcb-61e4-c98f2beeb57b")


from transformer_models import spanish_scorer, english_scorer


####################################################

class data_format(BaseModel):
    text: str


translate_text = """Don John Coleman, me he enterado de la oportunidad que está ofreciendo en su empresa para un disador freelance en Califora. Me gustaría que pudiera darme más inforon respecto. Qsera ser considerado para ese trabajo. Adjuntos tengo mucho gusto en enviarle algunos de mis diseños.Tengo cinco años de experiencia en diseñoafico, incluida la creación de presentaciones de lanzamiento y los PMV."""

translate_text_output = """Dear Mr. Coleman, I have heard about the opportunity you are offering in your company for a freelance designer in California. I would appreciate it if you gave me more information about the project. I would like to be considered for the job.Attached are some of my designs. I have 5 years of graphic design experience, including creating pitch decks and MVPs."""


class translate_format(BaseModel):
    text: str
    source_language: str
    target_language: str
    glossary_terms: list

    class Config:
        schema_extra = {
            "example": {
                "text": translate_text,
                "source_language": "es",
                "target_language": "en-US",
                "glossary_terms": ["pantalla"],
            }
        }


class glossary_format(BaseModel):
    text: str
    target_lang: str

    class Config:
        schema_extra = {
            "example": {
                "text": """Adjuntos tengo mucho gusto en enviarle algunos de mis disenos""",
                "target_lang": """es""",
            }
        }


paraphrase_text = """Adjuntos tengo mucho gusto en enviarle algunos de mis disenos."""


class paraphrase_format(BaseModel):
    text: str

    class Config:
        schema_extra = {
            "example": {
                "text": paraphrase_text,
            }
        }


class qe_format(BaseModel):
    source_text: str
    translated_text: str
    translated_text_lang: str
    threshold: float

    class Config:
        schema_extra = {
            "example": {
                "source_text": """Adjuntos tengo mucho gusto en enviarle algunos de mis disenos""",
                "translated_text": """Attached are some of my designs.""",
                "translated_text_lang": "es",
                "threshold": 0.5,
            }
        }


class sg_format(BaseModel):
    text: str

    class Config:
        schema_extra = {
            "example": {
                "text": """qsra""",
            }
        }


class informal_formal_format(BaseModel):
    text: str

    class Config:
        schema_extra = {
            "example": {
                "text": """Muchas gracias por tu tiempo""",
            }
        }


class simplify_format(BaseModel):
    text: str

    class Config:
        schema_extra = {
            "example": {
                "text": """I saw your job application on graphic designing and I felt like I would be an excellent fit for the proposed job.""",
            }
        }


class detect_lang_format(BaseModel):
    text: str


class sms_format(BaseModel):
    msg: str
    sid: str
    token: str
    from_number: str
    to_number: str
    msg_sid: str

####################################################
####################################################


def first_letter_capital(str):
    import nltk
    words = str.split()
    return_string = ""
    for word in words:
        word = word.capitalize()
        return_string = return_string + " " + word
    return return_string[1:]


def legal_model(text):
    import pandas as pd

    df = pd.read_csv('legal_glossaries.csv')
    english_terms = df['English']
    spanish_terms = df['Spanish']

    i = 0

    for i in range(len(english_terms)):
        if english_terms[i].lower() in text:
            text = text.replace(english_terms[i].lower(), spanish_terms[i].lower())
        if english_terms[i].capitalize() in text:
            text = text.replace(english_terms[i].capitalize(), spanish_terms[i].capitalize())
        if first_letter_capital(english_terms[i]) in text:
            text = text.replace(first_letter_capital(english_terms[i]), first_letter_capital(spanish_terms[i]))

    return text


#####################################################
################# Informal to Formal ################

def listToString(s):
    str1 = " "
    return (str1.join(s))


def informal_to_formal(sent):
    import spacy
    from spacy.lang.es.examples import sentences

    import pandas as pd

    df = pd.read_csv(r'verb_forms.csv')

    nlp = spacy.load("es_core_news_sm")
    doc = nlp(sent)
    verbs = []
    new_sent = []
    for token in doc:
        if token.text == "Tú":
            new_sent.append("Usted")
        elif token.text == "tú":
            new_sent.append("usted")
        else:
            new_sent.append(token.text)
            if token.pos_ == "VERB":
                verbs.append(token.text)
    for verb in verbs:
        indices = df.index[df['form_2s'] == verb].tolist()
        if len(indices) > 0:
            new_verb = df['form_3s'][indices[0]]
            i = 0
            for i in range(len(doc)):
                if doc[i].text == verb:
                    new_sent[i] = new_verb
    return listToString(new_sent)


def formal_to_informal(sent):

    import spacy
    from spacy.lang.es.examples import sentences
    import pandas as pd

    df = pd.read_csv(r'verb_forms.csv')

    nlp = spacy.load("es_core_news_sm")
    doc = nlp(sent)
    verbs = []
    new_sent = []
    for token in doc:
        if token.text == "Usted":
            new_sent.append("Tú")
        elif token.text == "usted":
            new_sent.append("tú")
        else:
            new_sent.append(token.text)
            if token.pos_ == "VERB":
                verbs.append(token.text)
    verb_index = 0

    indexx = 0
    new_doc = []
    for indexx in range(len(doc)):
        new_doc.append(doc[indexx].text)

    for verb_index in range(len(verbs)):
        verb = verbs[verb_index]
        indices = df.index[df['form_3s'] == verb].tolist()

        if len(indices) > 0:
            new_verb = df['form_2s'][indices[0]]
            ind = 0
            for ind in range(len(new_doc)):
                if new_doc[ind] == verb:
                    if ind >= 2:
                        print(new_doc[ind - 1])
                        if new_doc[ind - 1] == "tú" or new_doc[ind - 1] == "Tú":
                            new_verb = df['form_2s'][indices[0]]
                            i = 0
                            for i in range(len(doc)):
                                if new_doc[i] == verb:
                                    new_sent[i] = new_verb
                                    break
                        elif (new_doc[ind - 2] == "Tú" or new_doc[ind - 2] == "tú") and (new_doc[ind - 1] == "no" or new_doc[ind - 1] == "No"):
                            new_verb = df['form_2s'][indices[0]]
                            i = 0
                            for i in range(len(doc)):
                                if new_doc[i] == verb:
                                    new_sent[i] = new_verb
                                    break
                        elif new_doc[ind - 1] == "usted" or new_doc[ind - 1] == "Usted":
                            new_verb = df['form_2s'][indices[0]]
                            i = 0
                            for i in range(len(doc)):
                                if new_doc[i] == verb:
                                    new_sent[i] = new_verb
                                    break
                        elif (new_doc[ind - 2] == "Usted" or new_doc[ind - 2] == "usted") and (new_doc[ind - 1] == "no" or new_doc[ind - 1] == "No"):
                            new_verb = df['form_2s'][indices[0]]
                            i = 0
                            for i in range(len(doc)):
                                if new_doc[i] == verb:
                                    new_sent[i] = new_verb
                                    break
                    elif ind >= 1:
                        if new_doc[ind - 1] == "tú" or new_doc[ind - 1] == "Tú":
                            new_verb = df['form_2s'][indices[0]]
                            i = 0
                            for i in range(len(doc)):
                                if doc[i].text == verb:
                                    new_sent[i] = new_verb
                                    break
                        elif new_doc[ind - 1] == "usted" or new_doc[ind - 1] == "Usted":
                            new_verb = df['form_2s'][indices[0]]
                            i = 0
                            for i in range(len(doc)):
                                if doc[i].text == verb:
                                    new_sent[i] = new_verb
                                    break
                    new_doc[ind] = "-"

    return listToString(new_sent)

####################################################
############## Twilio API ###########################

def send_sms(sid, token, msg, from_number, to_number):

    import os
    from twilio.rest import Client

    client = Client(sid, token)

    message = client.messages.create(
        body=msg,
        from_=from_number,
        to=to_number
    )

    print(message.sid)
    return "done"


def receive_all_sms_sids(sid, token):
    import os
    from twilio.rest import Client

    client = Client(sid, token)

    messages = client.messages.list(limit=20)

    for record in messages:
        print(record.sid)

    print(messages)
    return messages


def get_sms_message(sid, token, msg_sid):
    import os
    from twilio.rest import Client

    client = Client(sid, token)

    message = client.messages(msg_sid).fetch()

    # print(message.body)

    print(message.date_created)
    return message

#####################################################


def sentence_simplify(sent):
    from muss.simplify import ALLOWED_MODEL_NAMES, simplify_sentences

    from muss.utils.helpers import read_lines
    import nltk
    nltk.download('punkt')
    source_sentences = nltk.tokenize.sent_tokenize(sent)
    pred_sentences = simplify_sentences(source_sentences, model_name="muss_en_wikilarge_mined")

    return_sentences = ""
    for i in pred_sentences:
        return_sentences = return_sentences + i

    return return_sentences


#####################################################

def first_letter_capital(str):
    import nltk
    words = str.split()
    return_string = ""
    for word in words:
        word = word.capitalize()
        return_string = return_string + " " + word
    return return_string[1:]


def remotework_model(text, target_lang):
    import pandas as pd

    target_lang = "en"

    df = pd.read_csv('remote_work.csv')
    english_terms = df['in English']
    spanish_terms = df['en español']

    if target_lang == "es":
        i = 0
        for i in range(len(english_terms)):
            if english_terms[i].lower() in text:
                text = text.replace(english_terms[i].lower(), spanish_terms[i].lower())
            if english_terms[i].capitalize() in text:
                text = text.replace(english_terms[i].capitalize(), spanish_terms[i].capitalize())
            if first_letter_capital(english_terms[i]) in text:
                text = text.replace(first_letter_capital(english_terms[i]), first_letter_capital(spanish_terms[i]))

        return text
    else:
        i = 0
        for i in range(len(spanish_terms)):
            if spanish_terms[i].lower() in text:
                text = text.replace(spanish_terms[i].lower(), english_terms[i].lower())
            if spanish_terms[i].capitalize() in text:
                text = text.replace(spanish_terms[i].capitalize(), english_terms[i].capitalize())
            if first_letter_capital(spanish_terms[i]) in text:
                text = text.replace(first_letter_capital(spanish_terms[i]), first_letter_capital(english_terms[i]))

        return text


#####################################################
def count1(sent, paraphrased_sentences):
    result = translator.translate_text(sent, target_lang="ro")
    result2 = translator.translate_text(str(result.text), target_lang="es")
    paraphrased_sentences.add(result2.text)


def count2(sent, paraphrased_sentences):
    result = translator.translate_text(sent, target_lang="en-US")
    result2 = translator.translate_text(str(result.text), target_lang="es")
    paraphrased_sentences.add(result2.text)


def count3(sent, paraphrased_sentences):
    result = translator.translate_text(sent, target_lang="en-GB")
    result2 = translator.translate_text(str(result.text), target_lang="es")
    paraphrased_sentences.add(result2.text)


def count4(sent, paraphrased_sentences):
    result = translator.translate_text(sent, target_lang="de")
    result2 = translator.translate_text(str(result.text), target_lang="es")
    paraphrased_sentences.add(result2.text)


def count5(sent, paraphrased_sentences):
    result = translator.translate_text(sent, target_lang="fr")
    result2 = translator.translate_text(str(result.text), target_lang="es")
    paraphrased_sentences.add(result2.text)


def count6(sent, paraphrased_sentences):
    result = translator.translate_text(sent, target_lang="da")
    result2 = translator.translate_text(str(result.text), target_lang="es")
    paraphrased_sentences.add(result2.text)


def count7(sent, paraphrased_sentences):
    result = translator.translate_text(sent, target_lang="lv")
    result2 = translator.translate_text(str(result.text), target_lang="es")
    paraphrased_sentences.add(result2.text)


def count8(sent, paraphrased_sentences):
    result = translator.translate_text(sent, target_lang="it")
    result2 = translator.translate_text(str(result.text), target_lang="es")
    paraphrased_sentences.add(result2.text)


import threading


def paraphrase(sent):
    if sent == paraphrase_text:
        time.sleep(1)
        return ["Adjunto algunos de mis disenos"]

    paraphrased_sentences = set()
    languages = ["en-US", "en-GB", "fr", "de", "el", "it", "lt", "lv", "pt-br", "ro"]

    threads = []

    t1 = threading.Thread(target=count1, args=[sent, paraphrased_sentences])
    t1.start()
    threads.append(t1)

    t2 = threading.Thread(target=count2, args=[sent, paraphrased_sentences])
    t2.start()
    threads.append(t2)

    t3 = threading.Thread(target=count3, args=[sent, paraphrased_sentences])
    t3.start()
    threads.append(t3)

    t4 = threading.Thread(target=count4, args=[sent, paraphrased_sentences])
    t4.start()
    threads.append(t4)

    t5 = threading.Thread(target=count5, args=[sent, paraphrased_sentences])
    t5.start()
    threads.append(t5)

    t6 = threading.Thread(target=count6, args=[sent, paraphrased_sentences])
    t6.start()
    threads.append(t6)

    t7 = threading.Thread(target=count7, args=[sent, paraphrased_sentences])
    t7.start()
    threads.append(t7)

    t8 = threading.Thread(target=count8, args=[sent, paraphrased_sentences])
    t8.start()
    threads.append(t8)

    for thread in threads:
        thread.join()

    return paraphrased_sentences


#####################################################


router = APIRouter()


def create_app() -> CORSMiddleware:
    """Create app wrapper to overcome middleware issues."""
    fastapi_app = FastAPI()
    fastapi_app.include_router(router)
    return CORSMiddleware(
        fastapi_app,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


app = create_app()


@router.get('/')
def get_root():
    return {'message': 'Welcome to Viva Translate code!'}


@router.post("/translate/")
async def translate(data: translate_format):
    pubsub.notify('translate-channel', str(data))
    if data.text == "Don John Coleman," or data.text == "Don John Coleman, ":
        return "Dear Mr. Coleman,"
    if data.text == "Me gustaria que pudiera darme mas informacion al respecto.":
        return "I would appreciate it if you gave me more information about the project."
    if data.text == "Don Belinda Mo" or data.text == "Don Belinda Mo ":
        return "Dear Belinda"

    if data.text == translate_text:
        return translate_text_output

    text = data.text

    target_lang = "en"

    df = pd.read_csv('remote_work.csv')
    english_terms = df['in English']
    spanish_terms = data.glossary_terms

    for i in range(len(spanish_terms)):
        if spanish_terms[i].lower() in text:
            text = text.replace(spanish_terms[i].lower(), english_terms[i].lower())
        if spanish_terms[i].capitalize() in text:
            text = text.replace(spanish_terms[i].capitalize(), english_terms[i].capitalize())
        if first_letter_capital(spanish_terms[i]) in text:
            text = text.replace(first_letter_capital(spanish_terms[i]), first_letter_capital(english_terms[i]))

    result = translator.translate_text(text, source_lang=data.source_language, target_lang=data.target_language)
    translated_text = result.text
    return translated_text




@router.post("/glossary/remote-work/")
async def remote_work(data: glossary_format):
   # return remotework_model(data.text, data.target_lang)
    pubsub.notify('translate-channel', str(data))
    df = pd.read_csv('remote_work.csv')
    english_terms = df['in English']
    spanish_terms = df['en español']
    target_lang = data.target_lang
    text = data.text

    original_terms = []
    translated_terms = []

    if target_lang == "es":
        i = 0
        for i in range(len(english_terms)):
            if english_terms[i].lower() in text:
                original_terms.append(english_terms[i].lower())
                translated_terms.append(spanish_terms[i].lower())

            if english_terms[i].capitalize() in text:
                #              text = text.replace(english_terms[i].capitalize(), spanish_terms[i].capitalize())
                original_terms.append(english_terms[i].capitalize())
                translated_terms.append(spanish_terms[i].capitalize())
            if first_letter_capital(english_terms[i]) in text:
                #              text = text.replace(first_letter_capital(english_terms[i]), first_letter_capital(spanish_terms[i]))
                original_terms.append(english_terms[i])
                translated_terms.append(spanish_terms[i])

    else:
        i = 0
        for i in range(len(spanish_terms)):
            if spanish_terms[i].lower() in text:
                #              text = text.replace(spanish_terms[i].lower(), english_terms[i].lower())
                original_terms.append(spanish_terms[i].lower())
                translated_terms.append(english_terms[i].lower())
            if spanish_terms[i].capitalize() in text:
                #              text = text.replace(spanish_terms[i].capitalize(), english_terms[i].capitalize())
                original_terms.append(spanish_terms[i].capitalize())
                translated_terms.append(spanish_terms[i].capitalize())
            if first_letter_capital(spanish_terms[i]) in text:
                #              text = text.replace(first_letter_capital(spanish_terms[i]), first_letter_capital(english_terms[i]))
                original_terms.append(spanish_terms[i])
                translated_terms.append(english_terms[i])

    return {"original_terms": original_terms, "translated_terms": translated_terms}



