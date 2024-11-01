# Install

Create a venv:

```
python3 -m venv .venv
source .venv/bin/activate
```

Install requirements:

```
pip3 install -r requirements.txt
```

Use your local package manager to install binary and development packages of the
tools and libararies which you lack.

# Prepare

Put `doc.pdf` next to the script.

Open one of the pages and snip out an image you will be searching. Name it `part-1.png`
and put it next to the script.

# Run

Run the script:

```
python3 find.py
```

It will print ton of useless debug information. In the last few lines it will tell you
if the template was found. Check found_doc.png with the image of page and light
rectangle in the place where the template was found.

See the top of the script for some parameters of the script which might help understand
why the template was not found. Also, try to render one of the pages to check whether
you favorite pdf viewer shows you the same thing which python sees.