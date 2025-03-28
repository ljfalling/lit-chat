'''
This script takes a parent folder as input and converts all .pdf files
not starting with . to markdown using Mistral OCR. 
Outputs are saved in a markdown-collector folder in the parent folder.
'''
import typer
import os
from mistralai import Mistral
import json
from mistralai.models import OCRResponse

def pdf_filepath_collector(parent_folder):
    pdf_filepaths = []
    for root, dirs, files in os.walk(parent_folder):
        for file in files:
            if file.endswith('.pdf') and not file.startswith('.'):
                pdf_filepaths.append(os.path.join(root, file))
    return pdf_filepaths

def retrieve_signed_urls(client, pdf_filepaths):
    signed_urls = {}
    for pdf_filepath in pdf_filepaths:
        print(f"Uploading {pdf_filepath}")
        filename = os.path.basename(pdf_filepath)
        uploaded_pdf = client.files.upload(
        file={
                "file_name": filename,
                "content": open(pdf_filepath, "rb"),
            },
            purpose="ocr"
        )
        client.files.retrieve(file_id=uploaded_pdf.id)
        signed_url = client.files.get_signed_url(file_id=uploaded_pdf.id)
        signed_urls[filename] = signed_url
    return signed_urls

def replace_images_in_markdown(markdown_str: str, images_dict: dict) -> str:
    for img_name, base64_str in images_dict.items():
        # Check if the base64_str already has a data URI prefix
        if not base64_str.startswith('data:image/'):
            # Add proper data URI format with MIME type
            data_uri = f"data:image/jpeg;base64,{base64_str}"
        else:
            data_uri = base64_str
        markdown_str = markdown_str.replace(f"![{img_name}]({img_name})", f"![{img_name}]({data_uri})")
    return markdown_str

def get_combined_markdown(ocr_response: OCRResponse) -> str:
  markdowns: list[str] = []
  for page in ocr_response.pages:
    image_data = {}
    for img in page.images:
      image_data[img.id] = img.image_base64
    markdowns.append(replace_images_in_markdown(page.markdown, image_data))
  return "\n\n".join(markdowns)


def pdf2markdown(client, urls, output_folder):
    for filename, url in urls.items():
        print(f"Processing {filename}")
        #print(f"URL: {url}")
        writeout_path = f"{output_folder}/" + filename + ".md"
        if os.path.exists(writeout_path):
            print(f"skipping {filename}, since it already exists")
            continue
        else:
            ocr_response = client.ocr.process(
                model="mistral-ocr-latest",
                include_image_base64=True,
                document={
                    "type": "document_url",
                    "document_url": url.url,
                }
            )
            print("ocr_response length: ", len(ocr_response.pages))
            markdown_content = get_combined_markdown(ocr_response)

            os.makedirs(os.path.dirname(writeout_path), exist_ok=True)
            with open(writeout_path, "w") as f:
                f.write(markdown_content)

def main(parent_folder_path: str, output_folder_path: str):
    api_key = os.environ["MISTRAL_API_KEY"]
    client = Mistral(api_key=api_key)
    pdf_filepaths = pdf_filepath_collector(parent_folder_path)
    urls = retrieve_signed_urls(client, pdf_filepaths)
    pdf2markdown(client, urls, output_folder_path)

if __name__ == "__main__":
    typer.run(main)