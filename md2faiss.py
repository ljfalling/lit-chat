import typer
import os
from mistralai import Mistral
from langchain_community.document_loaders import TextLoader
from langchain_mistralai.embeddings import MistralAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter

def md_filepath_collector(parent_folder):
    md_filepaths = []
    for root, dirs, files in os.walk(parent_folder):
        for file in files:
            if file.endswith('.md') and not file.startswith('.'):
                md_filepaths.append(os.path.join(root, file))
    return md_filepaths

def remove_images_from_text(text: str) -> str:
    import re
    # Removes ![...](...) references
    return re.sub(r'!\[[^\]]*\]\([^\)]*\)', '', text)

def concatenate_md_files(md_filepaths):
    multiple_docs = []
    for file_path in md_filepaths:
        loader = TextLoader(file_path)
        docs = loader.load()
        for doc in docs:
            doc.page_content = remove_images_from_text(doc.page_content)
        multiple_docs.extend(docs)
    return multiple_docs

def split_text(doc_list):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=4000,  # smaller chunks if needed
        chunk_overlap=400,
        length_function=len  # using character count since tokenizer isn't working
    )
    snippets = text_splitter.split_documents(doc_list)
    return snippets

def main(parent_folder_path: str, output_folder_path: str):
    api_key = os.environ["MISTRAL_API_KEY"]
    filepaths = md_filepath_collector(parent_folder_path)
    doc_stack = concatenate_md_files(filepaths)
    snippets = split_text(doc_stack)
    embedding = MistralAIEmbeddings(model="mistral-embed", mistral_api_key=api_key)
    vector = FAISS.from_documents(snippets, embedding)
    vector.save_local(output_folder_path)

if __name__ == "__main__":
    typer.run(main)