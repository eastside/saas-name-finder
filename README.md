# How to install

You'll need Python3 installed. :)

Download the script. (Go to "Code" then "Download." Unpack the zip and remember where it is.)

Open up terminal. Change directory to where-ever you unpacked the zip.

Activate a Python3 virtual environment and install requirements...

    python3 -m venv venv
    source ./venv/bin/activate
    pip install -r requirements.txt

# How to use

Run the script with...

    python3 script.py .app app.com .tech tech.com < words.txt

This'll check for all domains with an English prefix that are available with the given suffix.

So, like, right now, wheat.app is available! Grab it quick!
