from django.test import TestCase
from django.urls import reverse
from .models import UrlRecord
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'MaliciousDownloads'))
from downloads import virustotal
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'UrgencyTrustSpelling'))
from urgencyTrustSpelling import urgency_trust_spelling
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Blacklists'))
from blacklists import check_blacklists
from .detect import random_forest

class URLCheckboxDownloads(TestCase):
    def test_url_submission_with_checkbox_true(self):
        submission_url = reverse('store_url')
        form_data = {
            'url': 'http://117.220.151.43:59517/bin.sh',
            'isEnglish': 'true',
        }
        response = self.client.post(submission_url, form_data)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {
                'status': 'success',
                'result_count': 1,
                'detailed_results': [
                    ['malicious files', 'P'], 
                ]
            }
        )
        self.assertTrue(UrlRecord.objects.filter(url='http://117.220.151.43:59517/bin.sh').exists())

    def test_url_submission_with_checkbox_true(self):
        submission_url = reverse('store_url')  
        form_data = {
            'url': 'https://www.amazon.com',
            'isEnglish': 'true',
        }
        response = self.client.post(submission_url, form_data)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {
                'status': 'success',
                'result_count': 3, 
                'detailed_results': [
                    ['random forest', 'L'], 
                    ['cues and spelling', 'L'], 
                    ['blacklists', 'L'] 
                ]
            }
        )
        self.assertTrue(UrlRecord.objects.filter(url='https://www.amazon.com').exists())

    def test_url_submission_with_checkbox_false(self):
        submission_url = reverse('store_url')
        form_data = {
            'url': 'https://www.amazon.com',
            'isEnglish': 'false',
        }
        response = self.client.post(submission_url, form_data)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {
                'status': 'success',
                'result_count': 2, 
                'detailed_results': [
                    ['random forest', 'L'], 
                    ['blacklists', 'L'] 
                ]
            }
        )
        self.assertTrue(UrlRecord.objects.filter(url='https://www.amazon.com').exists())

class TestDownloads(TestCase):
    def test_no_download(self):
        self.assertEqual(virustotal('https://www.amazon.com'), 'L')

    def test_safe_download(self):
        self.assertEqual(virustotal('https://menstreamlive.co.za/tawSylDrz27.bin'), 'D')

    def test_malicious_download(self):
        self.assertEqual(virustotal('http://115.49.64.169:48461/bin.sh'), 'P')

class TestRandomForest(TestCase):
    def test_legitimate(self):
        self.assertEqual(random_forest('https://www.amazon.com'), -1)

    def test_phishing(self):
        self.assertEqual(random_forest('http://telegrom-wk.com/'), 1)

class TestCuesSpelling(TestCase):
    def test_legitimate(self):
        self.assertEqual(urgency_trust_spelling('https://www.amazon.com'), 'L')

    def test_phishing(self):
        self.assertEqual(urgency_trust_spelling('http://att-service-105697.weeblysite.com/'), 'P')

class TestBlacklists(TestCase):
    def test_legitimate(self):
        self.assertEqual(check_blacklists('https://www.amazon.com'), 'L')

    def test_phishing(self):
        self.assertEqual(check_blacklists('http://61.53.87.148:37374/i'), 'P')
