from flask import Flask, request, jsonify
from flask_cors import CORS

# summarization
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
from heapq import nlargest

app = Flask(__name__)
CORS(app) 

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

# Summarization function
def text_summarizer(text, percentage): 
    # pass the text into the nlp function
    doc= nlp(text)
    
    ## The score of each word is kept in a frequency table
    tokens=[token.text for token in doc]
    freq_of_word=dict()
    
    # Text cleaning and vectorization 
    for word in doc:
        if word.text.lower() not in list(STOP_WORDS):
            if word.text.lower() not in punctuation:
                if word.text not in freq_of_word.keys():
                    freq_of_word[word.text] = 1
                else:
                    freq_of_word[word.text] += 1
                    
    # Maximum frequency of word
    max_freq=max(freq_of_word.values())
    
    # Normalization of word frequency
    for word in freq_of_word.keys():
        freq_of_word[word]=freq_of_word[word]/max_freq
        
    # In this part, each sentence is weighed based on how often it contains the token.
    sent_tokens= [sent for sent in doc.sents]
    sent_scores = dict()
    for sent in sent_tokens:
        for word in sent:
            if word.text.lower() in freq_of_word.keys():
                if sent not in sent_scores.keys():                            
                    sent_scores[sent]=freq_of_word[word.text.lower()]
                else:
                    sent_scores[sent]+=freq_of_word[word.text.lower()]
    
    
    len_tokens=int(len(sent_tokens)*percentage)
    
    # Summary for the sentences with maximum score. Here, each sentence in the list is of spacy.span type
    summary = nlargest(n = len_tokens, iterable = sent_scores,key=sent_scores.get)
    
    # Prepare for final summary
    final_summary=[word.text for word in summary]
    
    #convert to a string
    summary=" ".join(final_summary)
    
    # Return final summary
    return summary


# Route for summarization API
@app.route("/summarize", methods=["POST"])
def summarize():
    data = request.get_json()
    text = data.get("text", "")
    summary = text_summarizer(text, 0.3)
    return jsonify({"summary": summary})

if __name__ == "__main__":
    app.run(debug=True)
