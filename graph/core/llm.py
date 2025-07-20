import os
from langchain_openai import ChatOpenAI

def get_llm_client(temperature=0.0, model="gpt-4-turbo"):
    """
    OpenAI dil modelini başlatan ve yapılandıran merkezi fonksiyon.
    API anahtarını ortam değişkenlerinden okur ve istemciye doğrudan sağlar.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY bulunamadı. Lütfen .env dosyanızda veya ortam değişkenlerinizde ayarlandığından emin olun."
        )

    return ChatOpenAI(
        temperature=temperature,
        model=model,
        api_key=api_key, # API anahtarını doğrudan istemciye ver
        streaming=True,
        # --- RATE LIMIT HATASI İÇİN GECE 1 ÇÖZÜMÜ ---
        # Eğer API rate limit'e takılırsak (429 Hatası),
        # sistemin çökmesini engelle ve 5 kereye kadar tekrar denemesini sağla.
        max_retries=5,
        # --- TOKEN LİMİTİ HATASI İÇİN KALICI ÇÖZÜM ---
        # Detaylı raporların yarıda kesilmesini önlemek için maksimum token limitini artır.
        max_tokens=4096
    ) 