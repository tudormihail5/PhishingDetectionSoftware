from django.shortcuts import render
from django.views.decorators.http import require_POST
from .models import UrlRecord
from django.http import JsonResponse
from .detect import random_forest
import os
import sys
downloads_path = os.path.join(os.path.dirname(__file__), '..', 'MaliciousDownloads')
sys.path.append(downloads_path)
from downloads import virustotal
blacklists_path = os.path.join(os.path.dirname(__file__), '..', 'Blacklists')
sys.path.append(blacklists_path)
from blacklists import check_blacklists
urgencyTrustSpelling_path = os.path.join(os.path.dirname(__file__), '..', 'UrgencyTrustSpelling')
sys.path.append(urgencyTrustSpelling_path)
from urgencyTrustSpelling import urgency_trust_spelling
from concurrent.futures import ProcessPoolExecutor, as_completed
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt

def display(request):
    return render(request, 'home.html')

def history(request):
    return render(request, 'history.html')

def help(request):
    return render(request, 'help.html')

# @csrf_exempt
@require_POST
def store_url(request):
    url = request.POST.get('url').replace(' ', '').replace('\t', '')
    is_english = request.POST.get('isEnglish') == 'true'
    detailed_results = []
    try:
        result1 = virustotal(url)
        if result1 == 'P':
            result = '<span class="negative">P (MD)</span>'
            detailed_results.append(('malicious files', 'P'))
        elif result1 == 'D':
            result = '<span class="positive">L (SD)</span>'
            detailed_results.append(('malicious files', 'L'))
        else:
            if is_english:
                # Use parallel execution to speed up the analysis
                with ProcessPoolExecutor(max_workers=3) as executor:
                    # Submit tasks for execution
                    future_random_forest = executor.submit(random_forest, url)
                    future_urgency_trust = executor.submit(urgency_trust_spelling, url)
                    future_check_blacklists = executor.submit(check_blacklists, url)            
                    # Collect results as they complete
                    for future in as_completed([future_random_forest, future_urgency_trust, future_check_blacklists]):
                        if future == future_random_forest:
                            result2 = future.result()
                        elif future == future_urgency_trust:
                            result3 = future.result()
                        elif future == future_check_blacklists:
                            result4 = future.result()
                if result2 == 1:
                    result2 = '<span class="negative">P</span>'
                    detailed_results.append(('random forest', 'P'))
                else:
                    result2 = '<span class="positive">L</span>'
                    detailed_results.append(('random forest', 'L'))
                if result3 == 'P':
                    result3 = '<span class="negative">P</span>'
                    detailed_results.append(('cues and spelling', 'P'))
                else:
                    result3 = '<span class="positive">L</span>'
                    detailed_results.append(('cues and spelling', 'L'))
                if result4 == 'P':
                    result4 = '<span class="negative">P</span>'
                    detailed_results.append(('blacklists', 'P'))
                else:
                    result4 = '<span class="positive">L</span>'
                    detailed_results.append(('blacklists', 'L'))
                result = result2 + ' | ' + result3 + ' | ' + result4
            else:
                # Speed up the analysis
                with ProcessPoolExecutor(max_workers=2) as executor:
                    # Submit tasks for execution
                    future_random_forest = executor.submit(random_forest, url)
                    future_check_blacklists = executor.submit(check_blacklists, url)            
                    # Collect results as they complete
                    for future in as_completed([future_random_forest, future_check_blacklists]):
                        if future == future_random_forest:
                            result2 = future.result()
                        elif future == future_check_blacklists:
                            result4 = future.result()
                if result2 == 1:
                    result2 = '<span class="negative">P</span>'
                    detailed_results.append(('random forest', 'P'))
                else:
                    result2 = '<span class="positive">L</span>'
                    detailed_results.append(('random forest', 'L'))
                if result4 == 'P':
                    result4 = '<span class="negative">P</span>'
                    detailed_results.append(('blacklists', 'P'))
                else:
                    result4 = '<span class="positive">L</span>'
                    detailed_results.append(('blacklists', 'L'))
                result = result2 + ' | ' + result4
        UrlRecord.objects.create(url=url, result=result)
        return JsonResponse({'status': 'success', 'result_count': len(detailed_results), 'detailed_results': detailed_results})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

def csrf_token(request):
    return JsonResponse({'csrfToken': get_token(request)})

def list_history(request):
    urls = UrlRecord.objects.all()
    return render(request, 'history.html', {'urls': urls})

def search_view(request):
    query = request.GET.get('search', '')
    if query:
        results = UrlRecord.objects.filter(url__icontains=query)
    else:
        results = UrlRecord.objects.all()
    return render(request, 'history.html', {'urls': results})
