
import urllib.request, json
req = urllib.request.Request('http://127.0.0.1:8000/api/admin/accounts/acc1/verify', data=b'', headers={'Content-Type': 'application/json', 'X-Admin-Key': ''})
try:
    with urllib.request.urlopen(req) as response:
        print(response.read().decode())
except Exception as e:
    print('Error:', e)
    if hasattr(e, 'read'):
        print(e.read().decode())

