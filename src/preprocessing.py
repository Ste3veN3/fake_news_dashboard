# ================================================
# src/preprocessing.py
# Pipeline de preprocesamiento NLP
# Proyecto: Detección de Noticias Falsas - USFQ
# Autor: Steeven Quezada
# ================================================

import re
import string
import nltk
import spacy
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Descargar recursos necesarios
nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)

# Cargar modelo de spaCy
nlp = spacy.load('en_core_web_sm')

# Stopwords en inglés
STOP_WORDS = set(stopwords.words('english'))

def clean_text(text):
    """
    Paso 1: Limpieza básica del texto.
    Elimina URLs, menciones, hashtags, 
    números y puntuación.
    """
    if not isinstance(text, str):
        return ""
    
    # Convertir a minúsculas
    text = text.lower()
    
    # Eliminar URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text)
    
    # Eliminar menciones y hashtags
    text = re.sub(r'@\w+|#\w+', '', text)
    
    # Eliminar números
    text = re.sub(r'\d+', '', text)

    # Eliminar palabras de 1-2 caracteres (ruido)
    text = re.sub(r'\b\w{1,2}\b', '', text)
    
    # Eliminar puntuación
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Eliminar espacios múltiples
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def remove_stopwords(text):
    """
    Paso 2: Eliminar stopwords.
    Quita palabras que no aportan significado
    como 'the', 'is', 'at', 'on', etc.
    """
    tokens = word_tokenize(text)
    tokens = [t for t in tokens if t not in STOP_WORDS]
    return ' '.join(tokens)

def lemmatize_text(text):
    """
    Paso 3: Lematización con spaCy.
    Reduce palabras a su forma base:
    'running' → 'run', 'better' → 'good'
    """
    doc = nlp(text)
    tokens = [token.lemma_ for token in doc 
              if not token.is_space]
    return ' '.join(tokens)

def preprocess(text, lemmatize=True):
    """
    Pipeline completo de preprocesamiento.
    Combina todos los pasos en uno.
    
    Args:
        text: texto crudo de entrada
        lemmatize: si True aplica lematización
                  (más lento pero mejor calidad)
    
    Returns:
        texto limpio y procesado
    """
    text = clean_text(text)
    text = remove_stopwords(text)
    if lemmatize:
        text = lemmatize_text(text)
    return text


# ================================================
# TEST RÁPIDO - ejecutar directamente para verificar
# ================================================
if __name__ == "__main__":
    
    texto_prueba = """
    Donald Trump's AMAZING speech!! He said: 'We WILL win' 
    on December 31st, 2017... #MAGA https://t.co/abc123
    via @FoxNews. The president is running for re-election.
    """
    
    print("TEXTO ORIGINAL:")
    print(texto_prueba)
    print("\n" + "="*50)
    
    print("\nPASO 1 - Limpieza básica:")
    paso1 = clean_text(texto_prueba)
    print(paso1)
    
    print("\nPASO 2 - Sin stopwords:")
    paso2 = remove_stopwords(paso1)
    print(paso2)
    
    print("\nPASO 3 - Lematización:")
    paso3 = lemmatize_text(paso2)
    print(paso3)
    
    print("\n" + "="*50)
    print("RESULTADO FINAL (pipeline completo):")
    print(preprocess(texto_prueba))