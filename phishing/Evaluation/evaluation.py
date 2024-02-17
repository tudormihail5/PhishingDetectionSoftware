import os
import requests

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_file_path = os.path.join(current_dir, 'evaluationDownload.txt')
    output_file_path = os.path.join(current_dir, 'resultsDownload.txt')
    api_endpoint = 'http://127.0.0.1:8000/store_url/'
    # Read the URLs file
    with open(input_file_path, 'r') as file:
        urls = file.readlines()
    for url in urls:
        # Remove the whitespace
        url = url.strip()
        result = post_url(api_endpoint, url)
        with open(output_file_path, 'a') as outfile:
            outfile.write(f"{result}\n")

def post_url(api_endpoint, url):
    data = {'url': url, 'isEnglish': 'false'}
    try:
        response = requests.post(api_endpoint, data=data)
        return str(response.json())
    except Exception as e:
        return e

if __name__ == "__main__":
    main()