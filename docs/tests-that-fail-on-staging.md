# tests that fail

## Translate

```python
data_dict = {
    "text": "Yo quiero las uvas mucho.",
    "source_language": "ES",
    "target_language": "EN-US",
    "glossary_terms": {"pantalla": "screen"}
}
resp = requests.post('https://staging.vivatranslate.io/translate', 
    json=json.dumps(data_dict))
resp
# 500
```

## Glossary

```python
resp = requests.post('https://staging.vivatranslate.io/glossary', 
    json='"Miro mi pantalla todo el día"')
resp
# 404
```
