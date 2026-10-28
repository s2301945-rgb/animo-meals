"""Trigger the private frontend deploy hook without logging its secret URL."""
import json
import os
import sys
import urllib.request
from urllib.parse import urlsplit


def main():
    hook = os.environ.get('VERCEL_DEPLOY_HOOK', '')
    if not hook:
        print('Deployment stopped: configure the VERCEL_DEPLOY_HOOK repository secret.')
        return 1
    parsed = urlsplit(hook)
    if parsed.scheme != 'https' or parsed.hostname != 'api.vercel.com':
        print('Deployment stopped: the hook must be an official HTTPS Vercel deploy hook.')
        return 1
    try:
        request = urllib.request.Request(hook, data=b'', method='POST')
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.load(response)
            if not isinstance(payload, dict) or 'job' not in payload:
                raise ValueError('Unexpected hook response')
    except Exception:
        print('Vercel deployment trigger failed. Secret URL and provider response are not logged.')
        return 1
    print('Vercel accepted the deployment job. Verify completion in the Vercel dashboard.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
