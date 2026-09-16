
import urllib.request, json
import sys

def req(url, method='GET', data=None):
    r = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json', 'X-Admin-Key': ''})
    r.get_method = lambda: method
    try:
        with urllib.request.urlopen(r) as response:
            print(f'OK {method} {url}: {response.status}')
    except urllib.error.HTTPError as e:
        body = b''
        try:
            body = e.read()
        except:
            pass
        print(f'ERR {method} {url}: {e.code}')
        if e.code == 500:
            print('  -> 500 BODY:', body.decode('utf-8', errors='ignore'))
    except Exception as e:
        print(f'ERR {method} {url}: {e}')

req('http://127.0.0.1:8000/api/admin/accounts/acc1/verify', 'POST', b'')
req('http://127.0.0.1:8000/api/admin/accounts/import-cookies', 'POST', json.dumps({'cookies': 'test'}).encode())
req('http://127.0.0.1:8000/api/admin/accounts/acc1/cookie', 'POST', json.dumps({'cookie': 'test'}).encode())
req('http://127.0.0.1:8000/api/admin/accounts', 'POST', json.dumps({'name': 'test1', 'email': 't@g.com', 'password': 'p', 'totp': ''}).encode())
req('http://127.0.0.1:8000/api/admin/accounts/acc1/login-browser', 'POST', b'')
req('http://127.0.0.1:8000/api/admin/accounts/test1', 'DELETE')

