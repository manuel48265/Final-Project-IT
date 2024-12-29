import PyPDF2
from transformers import pipeline

# Extraer texto del PDF
def extract_text_from_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text

# Configurar el modelo de preguntas y respuestas
qa_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")

# Texto extraído del PDF
pdf_text = extract_text_from_pdf("example.pdf")

# Pregunta
question = "What is the main topic of the document?"

# Responder la pregunta
answer = qa_pipeline({
    "question": question,
    "context": pdf_text
})

print("Answer:", answer["answer"])




def extract_text_from_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    


def chunk_text(text, chunk_size=1000):
    words = text.split()
    return [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]



def find_relevant_chunks(chunks, question):
    relevant_chunks = [chunk for chunk in chunks if any(word in chunk.lower() for word in question.lower().split())]
    return relevant_chunks[:3]  # Limitar a los 3 fragmentos más relevantes

# Configurar pipeline de preguntas y respuestas
qa_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")

def answer_question(chunks, question):
    answers = []
    for chunk in chunks:
        result = qa_pipeline({"question": question, "context": chunk})
        answers.append(result["answer"])
    return answers



# Archivo PDF
file_path = "example.pdf"
text = extract_text_from_pdf(file_path)

# Dividir texto en fragmentos
chunks = chunk_text(text)

# Pregunta del usuario
question = "What is the main topic of the document?"

# Buscar fragmentos relevantes
relevant_chunks = find_relevant_chunks(chunks, question)

# Responder la pregunta
answers = answer_question(relevant_chunks, question)
print("Answers:", answers)





