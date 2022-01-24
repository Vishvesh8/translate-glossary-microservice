from pathlib import Path
import time
import requests


def good_response(resp):
    assert bool(resp.text)
    assert 200 <= resp.status_code < 300
    assert '400' not in resp.text
    assert '404' not in resp.text
    assert 'error' not in resp.text.lower()
    assert 'fault' not in resp.text.lower()
    assert 'undefined' not in resp.text.lower()
    return True


url = 'http://viva-btcvden.us-east-1.elasticbeanstalk.com/translate'
host = 'viva-btcvden.us-east-1.elasticbeanstalk.com'
path = 'translate'
url = url or ("http://" + str(Path(host) / path))

print(f"Testing {url}.")

payload = dict(
    text="Hola",
    source_language="es",
    target_language="en-US",
    glossary_terms=[]
)
# john/chris
payload = {
    "text": "Me quedo mirando la pantalla todo el día, pero no me importa la computadora.",
    "source_language": "es",
    "target_language": "EN-US",
    "glossary_terms": [
        "pantalla"
    ]
}

wait_times = [10, 1, .1, .01]
experiments = {}

for wait_time in wait_times:
    response_times = []
    for requestnum in range(20):
        t0 = time.time()
        try:
            resp = requests.post(url=url, json=payload)
            t1 = time.time()
            print(resp.text)
            assert resp.status_code == 200
            assert good_response(resp)
            response_times.append((t1 - t0, resp))
        except Exception:
            break
        while time.time() - t0 < wait_time:
            time.sleep(wait_time / 10)
    experiments[wait_time] = response_times


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
