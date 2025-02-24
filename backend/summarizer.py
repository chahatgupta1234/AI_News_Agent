from transformers import pipeline

# Initialize the summarization pipeline with PyTorch
summarizer = pipeline("summarization", model="facebook/bart-large-cnn", framework="pt")

def summarize(text):
    try:
        summary = summarizer(text, max_length=130, min_length=30, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        print(f"Summarization error: {e}")
        return "Summary not available."
