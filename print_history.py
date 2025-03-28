import pickle
import typer

def display_history(history: dict) -> None:
    for timestamp, qa in history.items():
        question = qa["question"]
        answer = qa["answer"]
        print(f"Timestamp: {timestamp}\nQuestion: {question}\nAnswer: {answer}\n---")

def main():
    history_file = "qa_history.pkl"
    try:
        with open(history_file, "rb") as f:
            history = pickle.load(f)
        display_history(history)
    except FileNotFoundError:
        print(f"History file '{history_file}' not found.")

if __name__ == "__main__":
    typer.run(main)