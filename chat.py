import typer
import os
from langchain_mistralai.embeddings import MistralAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import RetrievalQA
import pickle
from datetime import datetime


def load_faiss(faiss_folder, embedding):
    # Define a retriever interface
    loaded_vector = FAISS.load_local(
        faiss_folder, 
        embedding, 
        allow_dangerous_deserialization=True
    )
    return loaded_vector.as_retriever() # defaults to k = 4 documents based on cosine similarity

def prompt_llm(api_key, retriever, question):
    model = ChatMistralAI(mistral_api_key=api_key, model="mistral-large-latest")
    prompt = ChatPromptTemplate.from_template("""Answer the following question based only on the provided context:

    <context>
    {context}
    </context>

    Question: {question}""")

    # Create a chain that can cite the source(s) of the answer
    chain = RetrievalQA.from_chain_type(
        llm=model,
        retriever=retriever,
        chain_type="stuff",
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt}
    )
    result = chain.invoke({"query": question})
    return result

def format_citation(filepath):
    filename = os.path.basename(filepath)
    # Remove extensions (.pdf.md)
    filename = filename.replace(".pdf.md", "")
    return filename

def get_answer_with_citations(result):
    # Extract the source documents and format them as citations
    answer = result["result"]
    sources = [doc.metadata["source"] for doc in result["source_documents"]]
    unique_sources = list(set(sources))
    references = []
    for i, source in enumerate(unique_sources, 1):
        citation = format_citation(source)
        references.append(f"[{i}] {citation}")
    answer_with_citations = answer + "\n\nReferences:\n" + "\n".join(references)
    return answer_with_citations

def load_history(file_path: str) -> dict:
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return pickle.load(f)
    return {}

def pickle_history(question: str, answer_with_citations: str) -> None:
    history_file = "qa_history.pkl"
    history = load_history(history_file)
    history[str(datetime.now())] = {"question": question, "answer": answer_with_citations}
    with open(history_file, "wb") as f:
        pickle.dump(history, f)

def main(faiss_source_folder: str, question: str):
    api_key = os.environ["MISTRAL_API_KEY"]
    embedding = MistralAIEmbeddings(model="mistral-embed", mistral_api_key=api_key)
    retriever = load_faiss(faiss_source_folder, embedding)
    result = prompt_llm(api_key, retriever, question)
    answer_with_citations = get_answer_with_citations(result)
    pickle_history(question, answer_with_citations)
    print(answer_with_citations)

if __name__ == "__main__":
    typer.run(main)