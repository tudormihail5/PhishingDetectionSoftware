from django.test import TestCase
from .detect import url_has_ip, has_long_url, has_shortening_service, has_at_symbol, has_double_slash, has_dash, has_subdomain, has_https, domain_length, has_favicon, check_port, has_token, has_request_url, url_anchor, has_links_in_tags, sfh, email, has_abnormal_url, forwarding, mouseover, has_disabled_right_click, popup, has_iframe, age_of_domain, has_DNS_record, google_index, get_driver
import sys
import os
import tempfile
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'MaliciousDownloads'))
from downloads import download_file, analyse_file, delete_file
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'UrgencyTrustSpelling'))
from urgencyTrustSpelling import cues_testing, detect_spelling_errors1GB, detect_spelling_errors1US, detect_spelling_errors2, detect_using_dictionary
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Blacklists'))
from blacklists import check_blacklist1, check_blacklist2, check_blacklist3, check_blacklist4

#1
class TestURLHasIP(TestCase):
    def test_url_without_ip(self):
        self.assertEqual(url_has_ip('https://www.amazon.com'), -1)
        
    def test_url_with_ip(self):
        self.assertEqual(url_has_ip('http://127.0.0.1/'), 1)

#2
class TestHasLongURL(TestCase):
    def test_short_url(self):
        self.assertEqual(has_long_url('https://www.amazon.com'), -1)

    def test_medium_url(self):
        self.assertEqual(has_long_url('http://ff.member.gareza.vn/CYnrbxo1unGIEqktgYIP5xks7uex0782GBZuEHBRBqd'), 0)

    def test_long_url(self):
        self.assertEqual(has_long_url('http://wakeupanddreamchallenge.info/video/moncompte1/free/moncompte/bd3aab893d4e527864d3e78ddeae8c12/2892e3deaf9bd970cdb358c0e5656a09/index.php'), 1)

#3
class TestHasShorteningService(TestCase):
    def test_normal_url(self):
        self.assertEqual(has_shortening_service('https://www.amazon.com'), -1)
        
    def test_shortened_url(self):
        self.assertEqual(has_shortening_service('https://bit.ly/3PuR31p'), 1)

#4
class TestHasAtSymbol(TestCase):
    def test_url_without_at_symbol(self):
        self.assertEqual(has_at_symbol('https://www.amazon.com'), -1)
        
    def test_url_with_at_symbol(self):
        self.assertEqual(has_at_symbol('https://net-clone.vercel.app/Netflix_login_design_clone-main/signup.html?email=Nariman&email=3mail@b.c&password=Nariman20041995'), 1)

#5
class TestHasDoubleSlash(TestCase):
    def test_url_without_double_slash(self):
        self.assertEqual(has_double_slash('https://www.amazon.com'), -1)
        
    def test_url_with_double_slash(self):
        self.assertEqual(has_double_slash('https://cadizgunworks.com/sumart/dmld//mbg/index.php?xml_id=/bg_BG/Login?ID=972911073'), 1)

#6
class TestHasDash(TestCase):
    def test_url_without_dash(self):
        self.assertEqual(has_dash('https://www.amazon.com'), -1)
        
    def test_url_with_dash(self):
        self.assertEqual(has_dash('https://clouds-band-6652.leecarlos.workers.dev/'), 1)

#7
class TestHasSubdomain(TestCase):
    def test_url_without_subdomains(self):
        self.assertEqual(has_subdomain('https://www.amazon.com'), -1)

    def test_url_with_one_subdomain(self):
        self.assertEqual(has_subdomain('https://arcde15.weebly.com/'), 0)
        
    def test_url_with_multiple_subdomains(self):
        self.assertEqual(has_subdomain('https://anaknekskkdkdokdjkshfjdhdjsksllsoppke.ttrbru.eu.org/'), 1)
        
#8
class TestHasHttps(TestCase):
    def test_url_with_https_trusted(self):
        self.assertEqual(has_https('https://www.amazon.com/'), -1)

    def test_url_with_https_untrusted(self):
        self.assertEqual(has_https('https://savoriurbane.com/'), 0)
        
    def test_url_with_http(self):
        self.assertEqual(has_https('http://data.cloudsave247.com'), 1)

#9
class TestDomainLength(TestCase):
    def test_domain_length_long(self):
        self.assertEqual(domain_length('https://www.amazon.com'), -1)
        
    def test_domain_length_short(self):
        self.assertEqual(domain_length('https://mchuurra.asyu.de/'), 1)

#10
class TestHasFavicon(TestCase):
    def test_favicon_same_domain(self):
        self.assertEqual(has_favicon('https://www.amazon.com', get_driver('https://www.amazon.com')), -1)

    def test_favicon_different_domain(self):
        self.assertEqual(has_favicon('https://mchuurra.asyu.de/', get_driver('https://mchuurra.asyu.de/')), 1)

#11
class TestCheckPort(TestCase):
    def test_port_open_standard(self):
        self.assertEqual(check_port('http://example.com'), -1)

    def test_port_open_uncommon(self):
        self.assertEqual(check_port('http://111.38.106.19:48737/bin.sh'), 1)

#12
class TestHasToken(TestCase):
    def test_url_without_token(self):
        self.assertEqual(has_token('https://www.amazon.com'), -1)
        
    def test_url_with_token(self):
        self.assertEqual(has_token('http://https-www-paypal-it-webapps-mpp-home.soft-hair.com'), 1)

#13
class TestHasRequestUrl(TestCase):
    def test_request_url_same_domain(self):
        self.assertEqual(has_request_url('https://savoriurbane.com/', get_driver('https://savoriurbane.com/')), -1)

    def test_request_url_different_domain(self):
        self.assertEqual(has_request_url('https://shijothomasm99.github.io/netflix/', get_driver('https://shijothomasm99.github.io/netflix/')), 0)

    def test_request_url_different_domains(self):
        self.assertEqual(has_request_url('https://rtyuuytryujh.weebly.com/', get_driver('https://rtyuuytryujh.weebly.com/')), 1)

#14
class TestURLAnchor(TestCase):
    def test_anchor_same_domain(self):
        self.assertEqual(url_anchor('https://savoriurbane.com/', get_driver('https://savoriurbane.com/')), -1)

    def test_anchor_same_domain(self):
        self.assertEqual(url_anchor('http://boredapeyachtclub.nftlivedrop.icu/', get_driver('http://boredapeyachtclub.nftlivedrop.icu/')), 0)

    def test_anchor_different_domains(self):
        self.assertEqual(url_anchor('http://pub-5c8b0c206b484f208b18e2c09e806156.r2.dev/HX-ADFS_9.html', get_driver('http://pub-5c8b0c206b484f208b18e2c09e806156.r2.dev/HX-ADFS_9.html')), 1)

#15
class TestHasLinksInTags(TestCase):
    def test_links_in_tags_same_domain(self):
        # Assuming meta, script, and link tags predominantly link to the same domain
        self.assertEqual(has_links_in_tags('https://savoriurbane.com/', get_driver('https://savoriurbane.com/')), -1)

    def test_links_in_tags_same_domain(self):
        # Assuming meta, script, and link tags predominantly link to the same domain
        self.assertEqual(has_links_in_tags('http://boredapeyachtclub.nftlivedrop.icu/', get_driver('http://boredapeyachtclub.nftlivedrop.icu/')), 0)

    def test_links_in_tags_different_domains(self):
        # Assuming these tags link to different domains suspiciously
        self.assertEqual(has_links_in_tags('http://pub-5c8b0c206b484f208b18e2c09e806156.r2.dev/HX-ADFS_9.html', get_driver('http://pub-5c8b0c206b484f208b18e2c09e806156.r2.dev/HX-ADFS_9.html')), 1)

#16
class TestSFH(TestCase):
    def test_sfh_same_domain(self):
        self.assertEqual(sfh('https://savoriurbane.com/', get_driver('https://savoriurbane.com/')), -1)

    def test_sfh_different_domain(self):
        self.assertEqual(sfh('https://kosiarki-pawlowski.pl/', get_driver('https://kosiarki-pawlowski.pl/')), 0)

    def test_sfh_empty_or_about_blank(self):
        self.assertEqual(sfh('http://pub-5c8b0c206b484f208b18e2c09e806156.r2.dev/HX-ADFS_9.html', get_driver('http://pub-5c8b0c206b484f208b18e2c09e806156.r2.dev/HX-ADFS_9.html')), 1)

#17
class TestEmail(TestCase):
    def test_email_not_present(self):
        self.assertEqual(email('https://www.amazon.com', get_driver('https://www.amazon.com')), -1)
        
    def test_email_present(self):
        self.assertEqual(email('http://coloredarecord.com/giveandtake/uPMKOdGeaN4sPwsii6Pc/%7B%7Bemailb64%7D%7D', get_driver('http://coloredarecord.com/giveandtake/uPMKOdGeaN4sPwsii6Pc/%7B%7Bemailb64%7D%7D')), 1)

#18
class TestHasAbnormalURL(TestCase):
    def test_normal_url(self):
        self.assertEqual(has_abnormal_url('https://www.amazon.com'), -1)
        
    def test_abnormal_url(self):
        self.assertEqual(has_abnormal_url('https://sbirewards-35n.pages.dev/'), 1)

#19
class TestForwarding(TestCase):
    def test_no_redirects(self):
        self.assertEqual(forwarding('https://savoriurbane.com/'), -1)
    
    def test_few_redirects(self):
        self.assertEqual(forwarding('http://127.0.0.1:8000/'), 0)

    def test_multiple_redirects(self):
        self.assertEqual(forwarding('http://127.0.0.1:8000/'), 1)

#20
class TestMouseover(TestCase):
    def test_mouseover_normal(self):
        self.assertEqual(mouseover('https://www.amazon.com', get_driver('https://www.amazon.com')), -1)
        
    def test_mouseover_deception(self):
        self.assertEqual(mouseover('http://127.0.0.1:8000/', get_driver('http://127.0.0.1:8000/')), 1)

#21
class TestHasDisabledRightClick(TestCase):
    def test_right_click_enabled(self):
        self.assertEqual(has_disabled_right_click('https://www.amazon.com', get_driver('https://www.amazon.com')), -1)
        
    def test_right_click_disabled(self):
        self.assertEqual(has_disabled_right_click('https://www.cabinetexpert.ro/', get_driver('https://www.cabinetexpert.ro/')), 1)

#22
class TestPopup(TestCase):
    def test_no_popup(self):
        self.assertEqual(popup('https://www.amazon.com', get_driver('https://www.amazon.com')), -1)
        
    def test_popup_with_text_field(self):
        self.assertEqual(popup('https://reharvest.co/', get_driver('https://reharvest.co/')), 1)

#23
class TestHasIframe(TestCase):
    def test_no_iframe(self):
        self.assertEqual(has_iframe('https://www.amazon.com', get_driver('https://www.amazon.com')), -1)
        
    def test_iframe_present(self):
        self.assertEqual(has_iframe('https://www.w3schools.com/html/html_iframe.asp', get_driver('https://www.w3schools.com/html/html_iframe.asp')), 1)

#24
class TestAgeOfDomain(TestCase):
    def test_old_domain(self):
        self.assertEqual(age_of_domain('http://www.amazon.com'), -1)
    
    def test_new_domain(self):
        self.assertEqual(age_of_domain('http://coul.pages.dev/'), 1)

#25
class TestHasDNSRecord(TestCase):
    def test_has_dns_record(self):
        self.assertEqual(has_DNS_record('https://www.amazon.com'), -1)

    def test_no_dns_record(self):
        self.assertEqual(has_DNS_record('http://coul.pages.dev/'), 1)

#26
class TestGoogleIndex(TestCase):
    def test_indexed_by_google(self):
        self.assertEqual(google_index('http://www.amazon.com'), -1)

    def test_not_indexed_by_google(self):
        self.assertEqual(google_index('http://coul.pages.dev/'), 1)      

class TestDownload(TestCase):
    def test_no_download(self):
        self.assertEqual(download_file('http://117.211.208.14:36931/Mozi.m'), '/home/tudor/Desktop/Facultate/FYP/Software/MaliciousDownloads/Downloads/Mozi.m')

    def test_download(self):
        self.assertEqual(download_file('https://www.amazon.com'), 'L')

class TestFileDeletion(TestCase):
    def test_successful_deletion(self):
        download_file('https://menstreamlive.co.za/tawSylDrz27.bin')
        delete_file('/home/tudor/Desktop/Facultate/FYP/Software/MaliciousDownloads/Downloads/tawSylDrz27.bin')
        self.assertFalse(os.path.exists('/home/tudor/Desktop/Facultate/FYP/Software/MaliciousDownloads/Downloads/tawSylDrz27.bin'))

class TestAnalyse(TestCase):
    def test_legitimate(self):
        download_file('https://menstreamlive.co.za/tawSylDrz27.bin')
        self.assertEqual(analyse_file(os.environ.get('virustotal_key'), '/home/tudor/Desktop/Facultate/FYP/Software/MaliciousDownloads/Downloads/tawSylDrz27.bin'), 'L')
        delete_file('/home/tudor/Desktop/Facultate/FYP/Software/MaliciousDownloads/Downloads/tawSylDrz27.bin')
        
    def test_phishing(self):
        download_file('http://117.211.208.14:36931/Mozi.m')
        self.assertEqual(analyse_file(os.environ.get('virustotal_key'), '/home/tudor/Desktop/Facultate/FYP/Software/MaliciousDownloads/Downloads/Mozi.m'), 'P')
        delete_file('/home/tudor/Desktop/Facultate/FYP/Software/MaliciousDownloads/Downloads/Mozi.m')

class TestCues(TestCase):
    def test_no_cues(self):
        self.assertEqual(cues_testing('Take your VOXI plan to new levels For just £2 more a month, you can tap into Unlimited Social AND Unlimited Music. So you can scroll and sing your heart out without worrying about running out of data. And if that\'s not enough you also get 60GB of data, 3X what you\'d usually get. Upgrade now 20GB 60GB £12/month endless music unlimited social media, unlimited video, unlimited music Upgrading is easier than you think 1 Log in to your VOXI account 2 Head to the “Plan” section 3 Choose your new plan 4 It\’ll start on your next billing date Upgrade now', 320), 'L')

    def test_cues(self):
        self.assertEqual(cues_testing('Looking for the ultimate shopping destination for your family\'s needs? Look no further than Walmart, where we offer a diverse range of products to meet all your requirements. Don\'t miss this fantastic opportunity! For a limited time, you have the chance to win a $100 Walmart gift card by completing a brief survey. Explore our vast selection of quality goods and unbeatable prices. We want to express our gratitude for choosing Walmart as your go-to shopping destination. Your preference means the world to us, and we invite you to participate in our survey for a shot at winning this exclusive gift card. Thank you for your continued loyalty and best of luck! By completing the survey, you could receive a $100 gift card TAKE THE SURVEY >>>>> http://www.grobymartk.click/4494X2395o8up612al6983K199b_21aFv4GIf4rxvs4FhIHEsvZ7UQORKSn7GS1M0AH6WzPwDL/gathering-unachievable Thank you once again for your ongoing support. We eagerly await your feedback and look forward to serving you with unbeatable value! Warm regards.', 320), 'P')

class TestSpelling1(TestCase):
    def test_errors(self):
        self.assertTrue(len(detect_spelling_errors1GB('https://ieltsonlinetests.com/writing-tips/common-spelling-errors-and-how-avoid-them')) > 0)

class TestSpelling2(TestCase):
    def test_errors(self):
        self.assertTrue(len(detect_spelling_errors1US('https://ieltsonlinetests.com/writing-tips/common-spelling-errors-and-how-avoid-them')) > 0)

class TestSpelling3(TestCase):
    def test_errors(self):
        self.assertTrue(len(detect_spelling_errors2('https://ieltsonlinetests.com/writing-tips/common-spelling-errors-and-how-avoid-them')) > 0)

class TestSpelling4(TestCase):
    def test_errors(self):
        self.assertTrue(len(detect_using_dictionary('https://ieltsonlinetests.com/writing-tips/common-spelling-errors-and-how-avoid-them')) > 0)

class TestBlacklist1(TestCase):
    def test_not_blacklist1(self):
        self.assertEqual(check_blacklist1('https://www.amazon.com'), -1)
        
    def test_blacklist1(self):
        self.assertEqual(check_blacklist1('http://113.179.192.8:38309/i'), 1)

class TestBlacklist2(TestCase):
    def test_not_blacklist2(self):
        self.assertEqual(check_blacklist2('https://www.amazon.com'), -1)
        
    def test_blacklist2(self):
        self.assertEqual(check_blacklist2('https://www.chemswaps.com'), 1)

class TestBlacklist3(TestCase):
    def test_not_blacklist3(self):
        self.assertEqual(check_blacklist3('https://www.amazon.com'), -1)
        
    def test_blacklist3(self):
        self.assertEqual(check_blacklist3('http://000hejn.wcomhost.com/PL/signin/DAD782MD49/login.php'), 1)

class TestBlacklist4(TestCase):
    def test_not_blacklist4(self):
        self.assertEqual(check_blacklist4('https://www.amazon.com'), -1)
        
    def test_blacklist4(self):
        self.assertEqual(check_blacklist4('https://687f7cce0d3669684.temporary.link/s/update.php'), 1)
