# Chat with your scientific literature (PDFs) using Mistral AI

This depository offers some scripts to 

  - convert PDFs to markdown files, with Mistral's OCR model
  - rename markdown files, with Mistral's latest large model
  - ask questions that are answered with Langchain and Mistral's latest large model
  - print history of questions

## How to use:
Clone repository
```
git clone https://github.com/ljfalling/lit-chat.git
cd lit-chat
```
### Run with UV
The depository is a [uv](https://github.com/astral-sh/uv) project folder, so if you have uv installed (use standalone installer following the link on the left) you can run the scripts and uv will take care of dependencies. You can run scripts with
```
uv run script.py
```
If there are further inputs needed in the call, typer will alert you.
You can also get help on what is needed by
```
uv run script.py --help
```
For example, you can run the conversion of PDFs in a folder named pdf-collection with
```
uv run pdf2markdown.py "pdf-collection" "markdown-collection"
```
where markdown-collection is the output path.


### Run without uv, for example using venv
Create a virtual environment using python 3.11 with,for example 
```
python3.11 -m venv .venv
```
and activate it
```
source .venv/bin/activate
```
and install dependencies listed in the pyproject.toml and uv.lock using pip:
```
pip install -e .
```
and run the script via
```
python pdf2markdown.py "pdf-collection" "markdown-collection"
```
