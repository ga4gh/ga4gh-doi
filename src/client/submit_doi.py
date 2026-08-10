import io
import os

import requests
from src.config.password import EMAIL, PASSWORD

def submitDoi(xml):
    """Submit a DOI batch XML to Crossref.

    `xml` may be a path to an XML file, or the raw XML content as a string.
    """
    url = "https://test.crossref.org/servlet/deposit"
    email = EMAIL
    password = PASSWORD
    try:
        header= {"User-Agent": "Crossref depositing; mailto:chen.chen@ga4gh.org"
                }
        params = {"operation": "doMDUpload",
                  "login_id": email,
                  "login_passwd": password}

        if isinstance(xml, str) and os.path.isfile(xml):
            fname = open(xml, "rb")
        else:
            content = xml.encode("utf-8") if isinstance(xml, str) else xml
            fname = io.BytesIO(content)

        file = {"fname": fname}

        postRequest = requests.post(url, params=params, headers=header, files=file, timeout=100000000)

    except Exception as e:
        raise Exception("Submit request failed")

    return postRequest.status_code, postRequest.text

#print(submit_doi("testsubmit.xml"))