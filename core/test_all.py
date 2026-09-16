
import urllib.request, json

def req(url, data=None):
    r = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    if data is None:
        r.get_method = lambda: 'POST'
    try:
        with urllib.request.urlopen(r) as response:
            print(f'OK {url}:', response.read().decode())
    except Exception as e:
        print(f'ERR {url}:', e)
        if hasattr(e, 'read'):
            print(e.read().decode())

print('Testing verify')
req('http://127.0.0.1:8000/api/admin/accounts/acc1/verify')
print('Testing import')
req('http://127.0.0.1:8000/api/admin/accounts/import-cookies', json.dumps({'cookies': 'test'}).encode())
print('Testing login-browser')
req('http://127.0.0.1:8000/api/admin/accounts/acc1/login-browser')

