import os
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

# Veritabanının bulunduğu yolu sabit olarak belirliyoruz.
DB_PATH = "mevzuat_veritabani"

def get_vector_store():
    """
    Daha önceden oluşturulmuş ve 'mevzuat_veritabani' klasöründe bulunan
    FAISS vektör veritabanını yükler ve kullanıma hazır bir nesne olarak döndürür.
    """
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(
            f"Vektör veritabanı '{DB_PATH}' adresinde bulunamadı. "
            "Lütfen bu isimde bir veritabanı olduğundan emin olun."
        )
        
    # OpenAI'nin embedding modelini kullanarak metinleri vektöre çevireceğiz.
    embeddings = OpenAIEmbeddings()
                
    # FAISS veritabanını yerel diskten yükle.
    # allow_dangerous_deserialization=True bayrağı, eski pickle formatındaki
    # dosyaları güvenle okuyabilmemiz için gereklidir.
    vector_store = FAISS.load_local(
        DB_PATH, 
        embeddings, 
        allow_dangerous_deserialization=True
    )
    return vector_store

if __name__ == '__main__':
    # Bu dosya doğrudan çalıştırılırsa, veritabanını yüklemeyi dener ve bilgi verir.
    print("Vektör veritabanı yükleniyor...")
    try:
        db = get_vector_store()
        print(f"Veritabanı başarıyla yüklendi. Toplam {db.index.ntotal} doküman parçası içeriyor.")
    except Exception as e:
        print(f"Hata: Veritabanı yüklenemedi. - {e}") 