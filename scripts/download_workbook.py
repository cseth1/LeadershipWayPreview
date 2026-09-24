#!/usr/bin/env python3
"""Download the shared workbook without printing credentials or sharing URLs."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
from http.cookiejar import CookieJar
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse, parse_qsl, urlunparse, quote
from urllib.request import Request, build_opener, HTTPRedirectHandler, HTTPCookieProcessor
import zipfile

MAX_BYTES=10_000_000

class HTTPSRedirects(HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        if urlparse(newurl).scheme!='https':raise ValueError('The workbook redirected to an insecure address')
        redirected=super().redirect_request(req,fp,code,msg,headers,newurl)
        if redirected and urlparse(newurl).netloc!=urlparse(req.full_url).netloc:
            redirected.remove_header('Authorization')
        return redirected

def request(url,headers=None,data=None):
    req=Request(url,data=data,headers={'User-Agent':'LeadershipWorkbookSync/1.0',**(headers or {})})
    with build_opener(HTTPSRedirects(),HTTPCookieProcessor(CookieJar())).open(req,timeout=60) as response:
        result=response.read(MAX_BYTES+1)
    if len(result)>MAX_BYTES:raise ValueError('The workbook exceeds the 10 MB download limit')
    return result

def acquire():
    shared=os.environ.get('LEADERSHIP_WORKBOOK_URL','').strip()
    if shared:
        parsed=urlparse(shared)
        if parsed.scheme!='https' or not (parsed.hostname.endswith('.sharepoint.com') or parsed.hostname=='1drv.ms'):
            raise ValueError('LEADERSHIP_WORKBOOK_URL must be an HTTPS OneDrive or SharePoint workbook link')
        if '/:f:/' in parsed.path:raise ValueError('Use the workbook file link, not the shared folder link')
        query=dict(parse_qsl(parsed.query,keep_blank_values=True));query['download']='1'
        return request(urlunparse(parsed._replace(query=urlencode(query))))
    keys=['MS_TENANT_ID','MS_CLIENT_ID','MS_CLIENT_SECRET','MS_DRIVE_ID','MS_ITEM_ID']
    if any(not os.environ.get(k) for k in keys):
        raise ValueError('Configure a downloadable workbook link, or the five Microsoft Graph connection secrets')
    tenant=os.environ['MS_TENANT_ID']
    if not all(c.isalnum() or c in '-.' for c in tenant):raise ValueError('Invalid Microsoft tenant ID')
    payload=urlencode({'client_id':os.environ['MS_CLIENT_ID'],'client_secret':os.environ['MS_CLIENT_SECRET'],'grant_type':'client_credentials','scope':'https://graph.microsoft.com/.default'}).encode()
    token=json.loads(request(f'https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token',{'Content-Type':'application/x-www-form-urlencoded'},payload))['access_token']
    drive=quote(os.environ['MS_DRIVE_ID'],safe='');item=quote(os.environ['MS_ITEM_ID'],safe='')
    return request(f'https://graph.microsoft.com/v1.0/drives/{drive}/items/{item}/content',{'Authorization':'Bearer '+token})

def main():
    parser=argparse.ArgumentParser();parser.add_argument('output',type=Path);args=parser.parse_args()
    data=acquire()
    if not zipfile.is_zipfile(io.BytesIO(data)):
        raise ValueError('Microsoft returned a sign-in page or another non-Excel response. Use an authorized file download link or configure Microsoft Graph access.')
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        if 'xl/workbook.xml' not in z.namelist():raise ValueError('The downloaded file is not an Excel workbook')
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_bytes(data)
    print('Downloaded the shared Excel workbook successfully.')
    print('Workbook SHA256: '+hashlib.sha256(data).hexdigest())

if __name__=='__main__':
    try:main()
    except HTTPError as e:raise SystemExit(f'Microsoft download failed (HTTP {e.code}). Check workbook access and connection settings.') from None
    except URLError:raise SystemExit('Microsoft download failed. Check connectivity and the connection settings.') from None
    except (ValueError,KeyError,zipfile.BadZipFile) as e:raise SystemExit(str(e)) from None
