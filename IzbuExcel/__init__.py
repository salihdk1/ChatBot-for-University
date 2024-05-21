from flask import Flask, render_template, request, session
import markupsafe
import pandas as pd
import difflib
import nltk
from nltk.corpus import stopwords
import secrets
import re
from openpyxl import load_workbook

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

df = pd.read_excel('veritabani_tr.xls')
nltk.download('stopwords')
stop_words = set(stopwords.words('turkish'))

@app.route('/')
def home():
    global df

    selected_language = request.args.get('language', session.get('language', 'tr'))
    session['language'] = selected_language

    if selected_language == 'tr':
        df = pd.read_excel('veritabani_tr.xls')
    else:
        df = pd.read_excel('veritabani_en.xls')

    return render_template('index.html', messages=session.get('messages', []), language=selected_language)


@app.route('/handle_form', methods=['POST'])
def handle_form():
    if request.method == 'POST':
        user_question = request.form['question']

        answer = find_answer(user_question, df, session.get('language', 'tr'))

        messages = session.get('messages', [])
        messages.append({'sender': 'user', 'text': user_question})
        messages.append({'sender': 'bot', 'text': answer})

        session['messages'] = messages

        return render_template('index.html', messages=messages)


@app.route('/clear_messages', methods=['POST'])
def handle_clear_button():
    if request.method == 'POST':
        session.pop('messages', None)
        return 'Messages cleared successfully'


def preprocess_question_text(question):
    question_str = str(question)
    words = [word for word in question_str.split() if word.lower() not in stop_words]
    return ' '.join(words)

def make_links_clickable(text):
    # Metindeki linkleri tıklanabilir yap
    clickable_text = re.sub(r'(https?://\S+)', r'<a href="\1" target="_blank">\1</a>', text)
    return markupsafe.Markup(clickable_text)

def find_answer(question, dataframe, language):
    similarity_scores = dataframe['question'].apply(
        lambda x: difflib.SequenceMatcher(None, preprocess_question_text(x), preprocess_question_text(question)).ratio())

    max_similarity_index = similarity_scores.idxmax()
    max_similarity_score = similarity_scores[max_similarity_index]

    threshold = 0.6

    if max_similarity_score > threshold:
        answer_column_name = f'answer'
        try:
            answer = dataframe.loc[max_similarity_index, answer_column_name]
            answer = make_links_clickable(answer)

        except KeyError:
            answer = f"No '{answer_column_name}' column found in the DataFrame."
    else:
        if language == 'tr':
            answer = "Sorunuza uygun bir cevap veremiyorum."
        else:  
            answer = "I cannot provide a suitable answer for your question."

    return answer


if __name__ == '__main__':
    app.run(debug=True)
