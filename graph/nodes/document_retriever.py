import logging
from typing import List

from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

from graph.state import GraphState

# Sabitler
DB_PATH = "mevzuat_veritabani"

logging.basicConfig(level=logging.INFO, format='   > %(message)s')

def retrieve_documents_node(state: GraphState) -> dict:
    """
    Kullanıcının sorgusuna ve çıkarılan varlıklara dayanarak, önceden oluşturulmuş
    olan FAISS vektör veritabanından ilgili mevzuat dokümanlarını alır.
    """
    logging.info("---NODE: İlgili Dokümanlar Alınıyor---")
    
    entities = state["entities"]
    
    search_query = f"{entities.investment_topic} {entities.investment_region}"
    logging.info(f"   > Vektör Veritabanı Arama Sorgusu: '{search_query}'")

    try:
        # Mevcut FAISS veritabanını yükle
        embeddings = OpenAIEmbeddings()
        vector_db = FAISS.load_local(DB_PATH, embeddings, allow_dangerous_deserialization=True)

        # Benzerlik araması yap ve en ilgili dokümanları al
        documents: List[Document] = vector_db.similarity_search(search_query, k=5)
        
        logging.info(f"   > {len(documents)} adet ilgili doküman bulundu.")
        return {"documents": documents}

    except Exception as e:
        logging.error(f"   > HATA: Vektör veritabanı okunurken bir hata oluştu: {e}")
        return {"documents": []} 