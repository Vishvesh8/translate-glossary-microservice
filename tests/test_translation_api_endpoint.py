# api_integration_tests.py
"""
```bash
curl --location --request POST 'https://staging.vivatranslate.io/translate/' \
--header 'Content-Type: text/plain' \
--data-raw '{
  "text": "Me quedo mirando la pantalla todo el día, pero no me importa la computadora.",
  "source_language": "es",
  "target_language": "EN-US",
  "glossary_terms": [
    "pantalla"
  ]
}'
```
"""
import requests
from pathlib import Path


def good_response(resp):
    assert bool(resp.text)
    assert 200 <= resp.status_code < 300
    assert '400' not in resp.text
    assert '404' not in resp.text
    assert 'error' not in resp.text.lower()
    assert 'fault' not in resp.text.lower()
    assert 'undefined' not in resp.text.lower()
    return True


def test_translation(
        url='http://viva-btcvden.us-east-1.elasticbeanstalk.com/translate',
        host='viva-btcvden.us-east-1.elasticbeanstalk.com',
        path='translate'):
    # vish
    url = url or ("http://" + str(Path(host) / path))
    print(f"Testing {url}.")

    payload = dict(
        text="Hola",
        source_language="es",
        target_language="en-US",
        glossary_terms=[]
    )
    resp = requests.post(url=url, json=payload)
    assert resp.status_code == 200
    assert good_response(resp)

    resp.json()

    # john/chris
    payload = {
        "text": "Me quedo mirando la pantalla todo el día, pero no me importa la computadora.",
        "source_language": "es",
        "target_language": "EN-US",
        "glossary_terms": [
            "pantalla"
        ]
    }
    resp = requests.post(url=url, json=payload)
    assert good_response(resp)
    assert resp.status_code == 200
    return True
