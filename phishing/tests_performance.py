import requests
import time

def measure_response_time(data):
    start_time = time.time()
    response = requests.post('http://127.0.0.1:8000/store_url/', data=data)
    end_time = time.time()
    return end_time - start_time, response.status_code

urls = {'http://182.126.113.75:47322/i', 'http://123.133.172.33:40090/bin.sh', 'http://42.179.5.103:38726/bin.sh', 'http://222.139.63.108:57892/i', 'http://182.126.107.39:56791/bin.sh', 'http://123.8.52.52:45248/i', 'http://117.206.190.79:40474/Mozi.m', 'http://182.127.128.75:38439/Mozi.m', 'http://115.51.92.11:46405/Mozi.m', 'http://112.248.185.172:54383/i'}
for url in urls:
    response_time, status_code = measure_response_time({'url': url, 'isEnglish': 'false'})
    print(f"Response Time: {response_time} seconds, Status Code: {status_code}")
