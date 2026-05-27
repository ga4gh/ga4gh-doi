from logging import exception
import requests
from password import EMAIL, PASSWORD

def submit_doi(xml):
    url = "https://test.crossref.org/servlet/deposit"
    email = EMAIL
    password = PASSWORD
    try:   
        header= {"User-Agent": "Crossref depositing; mailto:chen.chen@ga4gh.org"
                }
        params = {"operation": "doMDUpload",
                  "login_id": email, 
                  "login_passwd": password}
                  
        file = {"fname": open(xml, "rb")}
        
        postRequest = requests.post(url, params=params, headers=header, files=file, timeout=100000000)

    except:
        raise exception("Submit request failed") 

    return postRequest.status_code, postRequest.text

print(submit_doi("testsubmit.xml"))