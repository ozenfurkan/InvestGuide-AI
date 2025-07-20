# graph/nodes/support_analyzer.py
import logging
from typing import Dict, Any, List
from langchain.schema.document import Document
from graph.state import GraphState
from graph.chains.support_analyzer import get_support_analyzer_chain, SupportAnalysis

logging.basicConfig(level=logging.INFO, format='   > %(message)s')

def format_documents_for_support_analysis(docs: List[Document]) -> str:
    """Doküman listesini destek analizi için tek bir metne dönüştürür."""
    return "\n\n---\n\n".join([f"Kaynak: {doc.metadata.get('source', 'Bilinmiyor')} - Madde/Ek: {doc.metadata.get('madde_ek', 'Bilinmiyor')}\n\nİçerik:\n{doc.page_content}" for doc in docs])

def support_analyzer_node(state: GraphState) -> Dict[str, Any]:
    """
    Belirlenen yatırım türü ve özel koşullara dayanarak, yatırımın
    alabileceği destek unsurlarını (KDV istisnası, vergi indirimi vb.) analiz eder.
    """
    logging.info("---NODE: Destek Unsurları Analiz Ediliyor---")
    
    default_response = {"support_analysis": SupportAnalysis(supports=[])}

    try:
        chain = get_support_analyzer_chain()
        
        # --- DOĞRU VE GÜVENLİ STATE ERİŞİMİ ---
        main_docs = state.get("documents") or []
        focused_docs = state.get("focused_documents") or []
        investment_type = state.get("investment_type")
        special_conditions = state.get("special_conditions")
        entities = state.get("entities")
        
        # Gerekli bilgilerden herhangi biri yoksa, analiz yapmadan güvenli bir şekilde çık.
        if not investment_type or not entities:
            logging.warning("   > Yatırım türü veya temel varlıklar bulunamadığı için destek analizi atlanıyor.")
            return default_response

        all_docs = main_docs + focused_docs
        
        if not all_docs:
            logging.warning("   > Analiz için hiç doküman bulunamadı. Atlanıyor.")
            return default_response

        # Zincire gerekli tüm bilgileri, güvenli .get() metoduyla sağlayarak ver.
        response = chain.invoke({
            "investment_type": investment_type,
            "special_conditions": special_conditions,
            "entities": entities,
            "documents": format_documents_for_support_analysis(all_docs)
        })

        logging.info(f"   > Analiz Sonucu: {len(response.supports)} adet destek bulundu.")
        # DÜZELTME: Pydantic nesnesini .dict() ile sözlüğe çevirerek state'e yaz.
        return {"support_analysis": response.dict()}

    except Exception as e:
        logging.error(f"   > HATA: Destek analizi sırasında bir hata oluştu: {e}")
        # Hata durumunda bile state'i bozmuyoruz, boş bir nesne dönüyoruz.
        return default_response 