import time
import requests


def response(url, headers, delay=0, save_html=False):
    time.sleep(delay)
    t0 = time.time()
    while True:
        print('[GET]')
        r = None
        while not r:
            print('...')
            try:
                r = requests.get(url, headers=headers)
            except ConnectionError as ex:
                print(ex)
                print('[WARNING] Проблема с соединением')
                time.sleep(1)
        if r.status_code == 200:
            if save_html:
                with open('page.html', 'w', encoding='utf8') as html_file:
                    html_file.write(r.text)
            print(time.time()-t0)
            return r