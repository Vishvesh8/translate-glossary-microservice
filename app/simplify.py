def simplify(sent):
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
