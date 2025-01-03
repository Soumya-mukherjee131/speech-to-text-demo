
import gradio as gr
import requests
import nltk
from nltk.corpus import cmudict
import re
import csv
import tempfile

# Ensure CMU Pronouncing Dictionary is downloaded
nltk.download("cmudict")
cmu_dict = cmudict.dict()

# Hugging Face API Key and Endpoints
API_KEY = "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"
WHISPER_URL = "https://api-inference.huggingface.co/models/openai/whisper-large"
FALCON_URL = "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct"
REPHRASER_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"

headers = {"Authorization": f"Bearer {API_KEY}"}

# Function to transcribe audio
def transcribe_audio(audio_file):
    try:
        with open(audio_file, "rb") as f:
            response = requests.post(WHISPER_URL, headers=headers, data=f)
        result = response.json()
        print("Whisper API Response:", result)
        if "text" in result:
            return result["text"]
        else:
            return f"Error in transcription: {result}"
    except Exception as e:
        return f"Transcription error: {str(e)}"

# Function to correct grammar
def correct_text(raw_text):
    prompt = f"Correct this text for grammar, punctuation, and clarity:\n\n{raw_text}"
    payload = {"inputs": prompt}

    try:
        response = requests.post(FALCON_URL, headers=headers, json=payload)
        result = response.json()
        print("Falcon API Response:", result)
        if isinstance(result, list) and "generated_text" in result[0]:
            return result[0]["generated_text"].split("\n\n")[-1].strip()
        return f"Error in correction: {result}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

# Function to rephrase the text
def rephrase_text(raw_text):
    prompt = f"Rephrase this text in a formal, coherent, and concise manner:\n\n{raw_text}"
    payload = {"inputs": prompt}

    try:
        response = requests.post(REPHRASER_URL, headers=headers, json=payload)
        result = response.json()
        print("Rephraser API Response:", result)
        if isinstance(result, list) and "summary_text" in result[0]:
            return result[0]["summary_text"]
        return f"Error in rephrasing: {result}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

# Function to extract phonemes
def extract_phonemes(text):
    words = re.findall(r'\b\w+\b', text.lower())
    phoneme_data = []

    for word in words:
        if word in cmu_dict:
            phonemes = " ".join(cmu_dict[word][0])
            phoneme_data.append({"word": word, "phonemes": phonemes})
        else:
            phoneme_data.append({"word": word, "phonemes": "[Not found]"})

    return phoneme_data

# Function to compare phonemes
def compare_phonemes(raw_phonemes, corrected_phonemes):
    comparison_data = []
    for raw, corrected in zip(raw_phonemes, corrected_phonemes):
        match = raw["phonemes"] == corrected["phonemes"]
        comparison_data.append({
            "word": raw["word"],
            "raw_phoneme": raw["phonemes"],
            "corrected_phoneme": corrected["phonemes"],
            "match": match
        })
    return comparison_data

# Function to generate downloadable CSV
def generate_csv(comparison_data):
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    with open(temp_file.name, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Word", "Raw Phoneme", "Corrected Phoneme", "Match"])

        for data in comparison_data:
            writer.writerow([
                data["word"],
                data["raw_phoneme"],
                data["corrected_phoneme"],
                "Yes" if data["match"] else "No"
            ])

    return temp_file.name

# Gradio handler
def handle_request(audio_file):
    try:
        yield "Processing audio...", "", "Processing, please wait...", "", None
        raw_transcription = transcribe_audio(audio_file)
        if "Error" in raw_transcription:
            yield raw_transcription, "", "", "Error in transcription", None
            return

        yield raw_transcription, "Processing grammar correction...", "Correcting grammar...", "", None
        corrected_transcription = correct_text(raw_transcription)
        if "Error" in corrected_transcription:
            yield raw_transcription, corrected_transcription, "", "Error in text correction", None
            return

        yield raw_transcription, corrected_transcription, "Rephrasing text...", "", None
        enhanced_text = rephrase_text(raw_transcription)
        if "Error" in enhanced_text:
            yield raw_transcription, corrected_transcription, "", "Error in rephrasing", None
            return

        raw_phonemes = extract_phonemes(raw_transcription)
        corrected_phonemes = extract_phonemes(corrected_transcription)
        comparison_data = compare_phonemes(raw_phonemes, corrected_phonemes)

        csv_path = generate_csv(comparison_data)

        yield raw_transcription, corrected_transcription, enhanced_text, "Processing complete!", csv_path

    except Exception as e:
        yield "", "", "", f"An error occurred: {str(e)}", None

# Gradio Interface
interface = gr.Interface(
    fn=handle_request,
    inputs=gr.Audio(type="filepath", label="Upload Audio"),
    outputs=[
        gr.Textbox(label="Raw Transcription"),
        gr.Textbox(label="Corrected Transcription"),
        gr.Textbox(label="Enhanced Text"),
        gr.Textbox(label="Status"),
        gr.File(label="Download CSV"),
    ],
    live=True,
    title="Speech-to-Text with Grammar, Rephrasing, and Phoneme Correction",
    description="Upload an audio file to get transcription, corrected text, enhanced rephrasing, and a downloadable CSV for phoneme comparison.",
)

if __name__ == "__main__":
    interface.launch(share=True)