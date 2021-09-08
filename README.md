# requestium-automation-demo
**Name:** requestium-automation-demo  
**Description:** Example of booking automation with [Requestium](https://github.com/tryolabs/requestium) Python library on https://bezkolejki.eu/suw  
**GitHub:** https://github.com/korniichuk/requestium-automation-demo  
**Owner:** Ruslan Korniichuk

## Table of Contents
* **[Portability](#portability)**
* **[How to run](#how-to-run)**
  * **[Python script](#python-script)**
* **[FAQ](#faq)**

## Portability
`requestium-automation-demo` checked on Ubuntu Desktop 18.04 LTS operating system.

## How to run
### Python script
**Step 1:** Install operating system packages:
```sh
$ sudo apt update
$ sudo apt install google-chrome-stable
$ sudo apt install chromium-chromedriver
```

**Step 2:** Create `var/log/booking` folder for logger:
```sh
$ sudo mkdir /var/log/booking
$ sudo chown $USER:$USER /var/log/booking
```

**Step 3:** Install Python packages:
```sh
$ pip3 install --upgrade --user --requirement requirements.txt
```

**Note:** You can install Python packages using virtual environments (recommended). Example:
```sh
$ pipenv --python 3.6
$ pipenv shell
$ pipenv install
```

**Step 4:** Run Python script:
```sh
$ python3 booking_auto_example.py
```

[![demo_0001_youtube.png](img/demo_0001_youtube.png "See demo on YouTube")](https://youtu.be/hroRpT8mq6M)

## FAQ
**1. How to get bezkolejki.eu security token:**
```python3
import requests

url = 'https://bezkolejki.eu/api/Authentication/GetEmptyToken/suw'
r = requests.get(url)
token = r.json()['token']
print(f"token: '{token}'")
```

**2. How to get recaptcha token:**
```python3
import re

import requests

recaptcha_regex = re.compile(r'<input type="hidden" id="recaptcha-token" value="([^"]+)">')

k = '6LeCXbUUAAAAALp9bXMEorp7ONUX1cB1LwKoXeUY'
co = 'aHR0cHM6Ly9iZXprb2xlamtpLmV1OjQ0Mw..'
v = 'wxAi4AKLXL2kBAvXqI4XLSWS'
cb = '123456789'  # TODO
url = f'https://www.google.com/recaptcha/api2/anchor?ar=1&k={k}&co={co}&hl=en&v={v}&size=invisible&cb={cb}'
r = requests.get(url)
recaptcha_token  = recaptcha_regex.search(r.text).group(1)
print(f"recaptcha token: '{recaptcha_token}'")
```

**3. How to get solved recaptcha token for bezkolejki.eu:**
```python3
import json

import requests

prefix = ")]}'"

k = '6LeCXbUUAAAAALp9bXMEorp7ONUX1cB1LwKoXeUY'
url = f'https://www.google.com/recaptcha/api2/reload?k={k}'
data = {"reason": "q", "c": recaptcha_token}
r = requests.post(url, data=data)
text = r.text
if text.startswith(prefix):
    text = text[len(prefix):]
solved_recaptcha_token = json.loads(text)[1]
print(f"solved recaptcha token: {solved_recaptcha_token}")
```
