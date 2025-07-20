import logging
from typing import Dict, List

from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

from graph.state import GraphState
from graph.chains.focused_query_generator import get_focused_query_generator_chain

# Sabitler
DB_PATH = "mevzuat_veritabani"

logging.basicConfig(level=logging.INFO, format='   > %(message)s')

def focused_retriever_node(state: GraphState) -> Dict:
    """
    Yatırım türü belirlendikten sonra, daha spesifik ve odaklanmış bir arama
    yaparak ilgili destek ve şartları netleştirecek ek dokümanlar bulur.
    Bu düğüm de standart FAISS veritabanını kullanır.
    """
    logging.info("---NODE: Odaklanmış Arama Yapılıyor---")

    investment_type_analysis = state.get("investment_type")
    if not investment_type_analysis:
        return {"documents": state.get("documents", [])}

    # Odaklanmış arama sorgusu oluştur
    chain = get_focused_query_generator_chain()
    focused_query_obj = chain.invoke({
        "investment_type": investment_type_analysis.investment_type,
        "region": state["entities"].investment_region
    })
    focused_query = focused_query_obj.query
    logging.info(f"   > Oluşturulan Odaklanmış Sorgu: '{focused_query}'")

    try:
        # Standart FAISS veritabanını yükle
        embeddings = OpenAIEmbeddings()
        vector_db = FAISS.load_local(DB_PATH, embeddings, allow_dangerous_deserialization=True)

        # Odaklanmış arama yap
        newly_found_docs = vector_db.similarity_search(focused_query, k=3)
        
        logging.info(f"   > Odaklanmış aramada {len(newly_found_docs)} adet yeni doküman bulundu.")

        # Mevcut doküman listesini al ve yeni bulunanları (tekrarsız olarak) ekle
        current_docs = state.get("documents", [])
        current_doc_contents = {doc.page_content for doc in current_docs}
        
        for doc in newly_found_docs:
            if doc.page_content not in current_doc_contents:
                current_docs.append(doc)

        logging.info(f"   > Toplam doküman sayısı {len(current_docs)}'e yükseldi.")
        return {"documents": current_docs}

    except Exception as e:
        logging.error(f"   > HATA: Odaklanmış arama sırasında veritabanı hatası: {e}")
        return {} # Hata durumunda state'i bozmamak için boş dict döndür 