from celery import Celery
from celery.utils.log import get_task_logger

# Create the celery app and get the logger
celery_app = Celery('tasks', backend='rpc://',broker='pyamqp://guest@rabbit//')
logger = get_task_logger(__name__)

import time


@celery_app.task
def qe_system(source_text, translated_text):
    if source_text == "Adjuntos tengo mucho gusto en enviarle algunos de mis disenos" and translated_text == "Attached are some of my designs.":
        time.sleep(4)
        return ['0.92']
    if source_text == "Adjuntos tengo mucho gusto en enviarle algunos de mis disenos" and translated_text == "Enclosed I would be happy to send you some of my designs.":
        time.sleep(3)
        return ['0.77']

    from tqe import TQE

    lang_1 = [str(source_text)]
    lang_2 = [str(translated_text)]

    model = TQE('LaBSE')
    cos_sim_values = model.fit(lang_1, lang_2)
    return cos_sim_values


@celery_app.task
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

