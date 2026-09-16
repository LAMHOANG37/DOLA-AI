
import urllib.request, json
import sys

r = urllib.request.Request('http://127.0.0.1:8000/api/admin/accounts', data=json.dumps({'name': 'test1', 'email': 't@g.com', 'password': 'p', 'totp': ''}).encode(), headers={'Content-Type': 'application/json', 'X-Admin-Key': ''})
r.get_method = lambda: 'POST'
try:
    with urllib.request.urlopen(r) as response:
        print('OK')
except Exception as e:
    if hasattr(e, 'read'):
        print(e.read().decode())
    else:
        print(e)

