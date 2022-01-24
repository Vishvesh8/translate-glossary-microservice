from pathlib import Path
import time
import requests

test_start = time.time()

def run_tests(url):

    def good_response(resp):
        assert bool(resp.text)
        assert 200 <= resp.status_code < 300
        assert '400' not in resp.text
        assert '404' not in resp.text
        assert 'error' not in resp.text.lower()
        assert 'fault' not in resp.text.lower()
        assert 'undefined' not in resp.text.lower()
        return True

    print(f"Testing {url}.")

    payload = {
        "text": "Me quedo mirando la pantalla todo el día, pero no me importa la computadora.",
        "target_lang": "en-US"
    }

    wait_times = [10, 1, .1, .01]
    experiments = {}

    for wait_time in wait_times:
        test_wait_time_start = time.time()
        response_times = []
        for requestnum in range(20):
            t0 = time.time()
            request_time_start = time.time()

            try:
                resp = requests.post(url=url, json=payload)
                t1 = time.time()
                print(resp.text)
                assert resp.status_code == 200
                assert good_response(resp)
                response_times.append((t1 - t0, resp))

                request_time_end = time.time()
                request_time = request_time_end - request_time_start
                print(f'request time = { request_time }')

            except Exception:
                break

            while time.time() - t0 < wait_time:
                time.sleep(wait_time / 10)
            print(f'time for test {requestnum} with wait_time = {wait_time} ')
        experiments[wait_time] = response_times

        test_wait_time_end = time.time()
        total_wait_time_test = test_wait_time_end - test_wait_time_start
        print(f'total time for 20 tests with wait_time {wait_time} = { total_wait_time_test }')

    resp = requests.post(url=url, json=payload)
    resp.json()

    assert good_response(resp)
    assert resp.status_code == 200
    print(True)

    test_finish = time.time()
    total_time = test_finish - test_start
    print(f'total test time = { total_time }')
    print(experiments)


url = 'http://api.vivatranslate.io/glossary/remote-work/'
run_tests(url)
