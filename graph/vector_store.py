# graph/vector_store.py
"""
Bu modül, uygulama boyunca kullanılacak olan merkezi vektör veritabanı 
retriever nesnesini başlatır ve yönetir.
"""
import os
from langchain_community.vectorstores.faiss import FAISS
from langchain_openai import OpenAIEmbeddings

# Sabitler
DB_FAISS_PATH = "mevzuat_veritabani"

def get_vector_store():
    """
    FAISS vektör veritabanını diskten yükler ve bir FAISS nesnesi olarak döndürür.
    Veritabanı mevcut değilse bir hata fırlatır.
    """
    if not os.path.exists(DB_FAISS_PATH):
        raise FileNotFoundError(
            f"'{DB_FAISS_PATH}' klasöründe vektör veritabanı bulunamadı. "
            "Lütfen önce 'vector_db_builder.py' script'ini çalıştırarak veritabanını oluşturun."
        )
    
    # Embedding modelini başlat
    embeddings = OpenAIEmbeddings()
    
    # Veritabanını diskten yükle
    db = FAISS.load_local(
        folder_path=DB_FAISS_PATH, 
        embeddings=embeddings, 
        index_name="index",
        # pydantic v2 uyumluluğu için allow_dangerous_deserialization eklenmesi gerekiyor
        allow_dangerous_deserialization=True 
    )
    return db 