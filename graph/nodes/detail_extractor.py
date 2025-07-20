import logging
from graph.state import GraphState
from graph.chains.detail_extractor import get_detail_extractor_chain

logging.basicConfig(level=logging.INFO, format='   > %(message)s')

def detail_extractor_node(state: GraphState):
    """
    Temporal Resolver'dan gelen direktifleri analiz eder ve bu direktiflerin
    gerektirdiği spesifik detayları (lisans tarihi, başvuru tarihi vb.)
    kullanıcı sorgusundan çıkarır. Hatalara karşı dayanıklıdır.
    """
    logging.info("---NODE: Kritik Detaylar Çıkarılıyor---")
    
    # Hata durumunda döndürülecek varsayılan boş nesne
    default_response = {"extracted_details": {}}

    try:
        # Girdilerin 'None' olmadığından emin ol
        query = state.get("query", "")
        # ÖNEMLİ: temporal_directives state'inden al, tekil değil çoğul
        temporal_directives = state.get("temporal_directives", "")

        # Eğer işlenecek direktif yoksa, boşuna LLM'i çağırma
        if not temporal_directives:
            logging.info("   > İşlenecek zamansal direktif bulunamadı. Atlanıyor.")
            return default_response

        chain = get_detail_extractor_chain()
        response = chain.invoke({
            "query": query,
            "temporal_directives": temporal_directives # çoğul olanı kullan
        })
        
        logging.info(f"   > Çıkarılan Detaylar: {response.dict()}")
        return {"extracted_details": response}

    except Exception as e:
        logging.error(f"   > HATA: Detay çıkarımı sırasında bir zincir hatası oluştu: {e}")
        return default_response 