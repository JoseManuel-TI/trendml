"""Download the public UCI Online Retail archive, retaining an existing local copy."""
from pathlib import Path
import hashlib
import urllib.request

URL = 'https://archive.ics.uci.edu/static/public/352/online%2Bretail.zip'

if __name__ == '__main__':
    target = Path('work/uci/online-retail.zip')
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        temporary = target.with_suffix('.download')
        urllib.request.urlretrieve(URL, temporary)
        temporary.replace(target)
    print(target)
    print('SHA256:', hashlib.sha256(target.read_bytes()).hexdigest())
