'''
This script takes a parent folder as input and renames all .md files
in that folder and its subfolders to a citation ID format.
'''
import typer
import re
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from md2faiss import remove_images_from_text

def sanitize_filename(filename: str, max_length: int = 80) -> str:
    """
    Remove special characters from the filename and limit its length.
    """
    # Only keep letters, digits, underscore, and hyphen
    sanitized = re.sub(r'[^A-Za-z0-9_\-]', '', filename)
    # Truncate if it exceeds max_length
    return sanitized[:max_length]

def generate_filename(file_path, api_key):
    """
    Generate a citation ID in the format FirstAuthor_YearOfPublication_FullTitle
    by analyzing the first 3000 characters of a document.
    """

    model = ChatMistralAI(
        mistral_api_key=api_key,
        model="mistral-large-latest"
        )
    
    # Read the document content
    with open(file_path, "r", encoding="latin-1") as f:
        content = f.read()
        # Remove images from content
        content = remove_images_from_text(content)    
    
    # Take first 3000 characters
    preview_text = content[:3000]

    # Escape curly braces to prevent template interpretation issues
    escaped_text = preview_text.replace("{", "{{").replace("}", "}}")

    system_message = """You are an academic citation specialist. Analyze the beginning of an academic document 
    and fill in the information about First Author, Year, and Title in the following format, no explanations, please:

    First Author: [Last Name only]
    Year of Publication: [4-digit year, if not found use "YEAR"]
    Title: [Title of the document]
    """

    user_message = f"Compile the information for the following document:\n\n{escaped_text}"
    
    citation_prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        ("user", user_message)
    ])
    
    # Call the model
    chain = citation_prompt | model
    response = chain.invoke({})

    info_compilation = response.content
    # print(f"Info Compilation: \n{info_compilation}")

    # Format info compilation into a filename
    lines = info_compilation.split("\n")
    filename_parts = []
    for line in lines:
        if line.strip():
            if "First Author" in line:
                filename_parts.append(line.split(":")[1].strip())
            elif "Year of Publication" in line:
                filename_parts.append(line.split(":")[1].strip())
            elif "Title" in line:
                raw_title = line.split(":")[1].strip()
                title = raw_title.strip().replace(" ", "-").replace(":", "").replace(",", "")
                filename_parts.append(title)
    filename = "_".join(filename_parts)
    return filename

def process_and_rename_files(parent_folder:str, api_key:str):
    for root, dirs, files in os.walk(parent_folder):
        for file in files:
            if file.endswith(".md") and not file.startswith("."):
                file_path = os.path.join(root, file)
                generated_filename = generate_filename(file_path, api_key)
                generated_filename = sanitize_filename(generated_filename)
                # Rename the file
                new_file_name = generated_filename + ".md"
                new_file_path = os.path.join(root, new_file_name)
                
                # Check if the destination file already exists
                if os.path.exists(new_file_path):
                    print(f"Warning: Destination file already exists. Adding unique suffix to {new_file_name}")
                    new_file_name = f"{generated_filename}_1.md"
                    new_file_path = os.path.join(root, new_file_name)
                
                os.rename(file_path, new_file_path)
                print(f"Renamed {file_path} to \n ---> {new_file_path}")

def main(parent_folder_path: str):
    api_key = os.environ["MISTRAL_API_KEY"]
    process_and_rename_files(parent_folder_path, api_key)

if __name__ == "__main__":
    typer.run(main)