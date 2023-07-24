
from django.conf import settings
import vt
from vt import APIError
from main.helper import get_sleep_time_for_vt_check, is_reported, timestamp_to_datetime
from django_cron import CronJobBase, Schedule
from selfurl.models import ReportMalicious, Shortener
import time
from django.db.models import Q, F, When, Case
from django.utils import timezone

def get_checked_result(long_url, vt_client):   
    
    """
    Get the checked result for a given URL from the VirusTotal (VT) API or stored data.

    Args:
        long_url (str): The long URL to check for malicious activity.
        vt_client: The VirusTotal client object used to make API calls.

    Returns:
        tuple: A tuple containing checked_time (datetime), malicious (bool), suspicious (bool),
        and check_decision (str) representing the result of the URL scan.
    """
    
    try: 
        try:  
            # As per documention VT needs url_id to check            
            url_id = vt.url_id(long_url)
            url = vt_client.get_object(f"/urls/{url_id}")   
            
            timestamp = url.times_submitted
            last_analysis_stats = url.last_analysis_stats
        except APIError:    
            # if no result for the url then we will analysis the url and will wait for result.    
            url_report = (vt_client.scan_url(long_url, wait_for_completion=True)).to_dict() 
            
            timestamp = url_report['attributes']['date']                    
            last_analysis_stats = url_report['attributes']['stats'] 
                       
        checked_time = timestamp_to_datetime(timestamp)
        malicious = last_analysis_stats['malicious']
        suspicious = last_analysis_stats['suspicious']
        
    except (KeyError, APIError):
        # If there is an error in getting data from VirusTotal, mark the result as clean.
        checked_time = timestamp_to_datetime(0)
        malicious = 0
        suspicious = 0
    
    if malicious:
        check_decision = 'malicious'
    elif suspicious:
        check_decision = 'suspicious'
    elif suspicious and malicious:
        check_decision = 'suspicious and malicious'
    else:
        check_decision = settings.CLEAN_DECISION   
    
    return checked_time, malicious, suspicious, check_decision
        


def check_reported_url():
    """
    Check reported URLs for malicious activity using VirusTotal API.

    This function iterates through the reported URLs that have not been checked yet and
    updates the corresponding Shortener and ReportMalicious objects based on the scan result.
    """
    vt_client = vt.Client(settings.VT_API_KEY)
    
    long_urls = ReportMalicious.objects.filter(checked=False).values('url__long_url').distinct() 
    
    if long_urls.exists():
        for long_url in long_urls:          
                               
            checked_time, malicious, suspicious, check_decision = get_checked_result(long_url['url__long_url'], vt_client)
                        
            shorteners = Shortener.objects.filter(long_url = long_url['url__long_url'])
          
            for shortener in shorteners:
                if is_reported(shortener.long_url):
                    if (malicious or suspicious) and (shortener.expires_at == None or shortener.expires_at < timezone.now()):
                        shortener.active = False
                    else:
                        shortener.active = True                
            Shortener.objects.bulk_update(shorteners, ['active']) 
            
            reported_urls = ReportMalicious.objects.filter(url__in = shorteners)  
            
            reported_urls.update(checked=True, check_decision=check_decision, checked_at=checked_time)
             
            vt_client.close()
            time.sleep(get_sleep_time_for_vt_check())

    return None

class SelfCronJob(CronJobBase):
    RUN_EVERY_MINS = 120 # every 2 hours

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'main.cron_job'    # a unique code

    def do(self):
        check_reported_url()

            
            
            
        
    
    