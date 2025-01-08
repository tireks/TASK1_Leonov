#!/usr/bin/env python3
import sys
import os
import urllib.parse
import http.client
import threading
import time

stop_event = threading.Event()  
downloaded_bytes = 0           
lock = threading.Lock()         

def download_file(url):
    global downloaded_bytes

    parsed_url = urllib.parse.urlparse(url)
    if parsed_url.scheme == "https":
        conn = http.client.HTTPSConnection(parsed_url.netloc)
    else:
        conn = http.client.HTTPConnection(parsed_url.netloc)

    path = parsed_url.path if parsed_url.path else "/"
    
    conn.request("GET", path)
    response = conn.getresponse()
    
    if response.status != 200:
        print(f"Ошибка при загрузке: {response.status} - {response.reason}")
        stop_event.set()
        conn.close()
        return
    
    filename = os.path.basename(path)
    if not filename:
        filename = "downloaded_file"

    print(f"Начинаем загрузку: {filename}")

    with open(filename, "wb") as f:
        while not stop_event.is_set():
            data = response.read(4096)  # читаем блоками по 4 КБ
            if not data:
                # Конец данных
                break
            f.write(data)
            with lock:
                downloaded_bytes += len(data)

    conn.close()
    stop_event.set()


def print_progress():
    while not stop_event.is_set():
        time.sleep(0.1)
        with lock:
            if downloaded_bytes != 0 :
                print(f"Скачано: {downloaded_bytes} байт")


def main():

    url = sys.argv[1]

    t_download = threading.Thread(target=download_file, args=(url,))
    t_progress = threading.Thread(target=print_progress)

    t_download.start()
    t_progress.start()

    t_download.join()
    stop_event.set()
    
    t_progress.join()

    print("Загрузка завершена.")

if __name__ == "__main__":
    main()
