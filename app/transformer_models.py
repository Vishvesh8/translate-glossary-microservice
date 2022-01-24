from bert_score import BERTScorer

spanish_scorer = BERTScorer(lang="es", rescale_with_baseline=True)
english_scorer = BERTScorer(lang="en", rescale_with_baseline=True)

refs = [["hello john."]]

hyps = ["holls juan."]
P, R, F1 = spanish_scorer.score(hyps, refs)

# print(P, R, F1)
print('done')
