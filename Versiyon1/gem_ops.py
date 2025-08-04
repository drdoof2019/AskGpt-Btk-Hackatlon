import google.generativeai as genai
import time
import os
from dotenv import load_dotenv

# --- .env Dosyası ve API Anahtarı Kontrolü ---
if not os.path.exists('.env'):
    raise FileNotFoundError(".env dosyası bulunamadı! Lütfen API anahtarınızı içeren bir .env dosyası oluşturun.")
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY ortam değişkeni .env dosyasında bulunamadı veya ayarlanmamış.")

# --- YENİ: SİSTEM TALİMATI (BASE PROMPT) ---
# Bu prompt, modelin genel davranışını ve kişiliğini belirler.
SYSTEM_PROMPT = """
You are a highly capable and friendly personal desktop assistant. 
Your primary goal is to help the user with their tasks by analyzing screenshots and text prompts.
Key instructions:
1.  **Language:** Always respond in the same language the user uses in their prompt. If the user asks in Turkish, you MUST answer in Turkish. If they ask in English, answer in English.
2.  **Persona:** Be helpful, concise, and professional.
3.  **Context:** You have a chat history. Use the context from previous interactions to provide more relevant answers.
4.  **Formatting:** Use Markdown for formatting your answers to improve readability (e.g., use headings, bold text, bullet points, code blocks).
5.  **Analysis:** When analyzing an image, be objective and describe what you see, then answer the user's specific question about it.
"""

# --- İstemciyi Başlatma (DEĞİŞİKLİK) ---
genai.configure(api_key=GOOGLE_API_KEY)
# Modeli, sistem talimatı ile birlikte başlatıyoruz.
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash", 
    system_instruction=SYSTEM_PROMPT
)
# Sohbeti başlat
chat = model.start_chat(history=[])


def upload_file(path, name):
    """Verilen yoldaki dosyayı Google AI platformuna yükler."""
    try:
        file = genai.upload_file(path=path, display_name=name)
        print(f"Yüklendi: '{file.display_name}' URI: {file.uri}")
        return file
    except Exception as e:
        print(f"Dosya yüklenirken hata oluştu: {e}")
        return None

def generate_content(file, prompt):
    """Görüntü dosyası ve metin prompt'u ile içerik üretir."""
    # Sistem talimatı modelde zaten tanımlı olduğu için ekstra bir şey yapmaya gerek yok.
    try:
        response = chat.send_message([prompt, file])
        return response.text
    except Exception as e:
        print(f"İçerik üretilirken hata: {e}")
        return None

def generate_text_content(answer, prompt):
    """Sadece metin tabanlı devam eden sohbetler için içerik üretir."""
    # Sistem talimatı modelde zaten tanımlı.
    # Önceki cevabı ve yeni soruyu göndermek yerine, sadece yeni soruyu göndermemiz yeterli.
    # `chat` nesnesi zaten geçmişi tutuyor.
    try:
        # text = f"Previous context: {answer}\nNew question: {prompt}" # Bu yaklaşıma gerek yok, chat objesi geçmişi biliyor.
        response = chat.send_message(prompt)
        return response.text
    except Exception as e:
        print(f"Metin içeriği üretilirken hata: {e}")
        return None

def reset_chat():
    """Sohbet geçmişini sıfırlar."""
    global chat
    # Modeli yeniden başlatmaya gerek yok, sadece yeni ve boş bir sohbet oturumu başlatmak yeterli.
    chat = model.start_chat(history=[])
    print("Sohbet geçmişi sıfırlandı.")

def delete_file(file_obj):
    """Verilen dosya nesnesini siler."""
    try:
        genai.delete_file(name=file_obj.name)
        print(f"Silindi: {file_obj.display_name}.")
    except Exception as e:
        print(f"Dosya silinirken hata: {e}")

def delete_all_files():
    """Yüklenmiş tüm dosyaları temizler."""
    print("Tüm dosyalar siliniyor...")
    for file in genai.list_files():
        delete_file(file)
    print("Tüm dosyalar silindi.")