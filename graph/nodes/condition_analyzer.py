# graph/nodes/condition_analyzer.py
import logging
from typing import Dict, Any, List
from langchain.schema.document import Document
from graph.state import GraphState
from graph.chains.condition_analyzer import get_condition_analyzer_chain, SpecialConditions

logging.basicConfig(level=logging.INFO, format='   > %(message)s')

def format_documents(docs: List[Document]) -> str:
    """Doküman listesini LLM'in işleyebileceği tek bir metne dönüştürür."""
    if not docs:
        return "İlgili doküman bulunamadı."
    return "\\n\\n---\\n\\n".join([f"Kaynak: {doc.metadata.get('source', 'Bilinmiyor')} - Madde/Ek: {doc.metadata.get('madde_ek', 'Bilinmiyor')}\\n\\n{doc.page_content}" for doc in docs])

def condition_analyzer_node(state: GraphState) -> Dict[str, Any]:
    """
    Yatırımın karşılaması gereken özel koşulları veya 'kazanılmış hak' gibi
    tabi olduğu istisnaları, tüm girdileri kullanarak analiz eder.
    """
    logging.info("---NODE: Özel Koşullar Analiz Ediliyor---")
    
    try:
        chain = get_condition_analyzer_chain()
        
        # --- DOĞRU VE GÜVENLİ STATE ERİŞİMİ ---
        investment_type = state.get("investment_type")
        entities = state.get("entities")
        documents = state.get("documents", [])
        # KANITLANDIĞI ÜZERE DOĞRU ANAHTAR: "temporal_directives" (çoğul)
        temporal_directives = state.get("temporal_directives", "Uygulanacak özel bir zamansal direktif bulunamadı.")
        extracted_details = state.get("extracted_details")

        # Gerekli bilgilerden herhangi biri yoksa, analiz yapmadan güvenli bir şekilde çık.
        if not investment_type or not entities:
            logging.warning("   > Yatırım türü veya varlıklar bulunamadığı için özel koşul analizi atlanıyor.")
            return {"special_conditions": SpecialConditions(conditions=[], reasoning="Ön koşullar (yatırım türü, varlıklar) sağlanamadığı için analiz yapılamadı.")}

        # Tüm ilgili bilgileri zincire girdi olarak ver
        response = chain.invoke({
            "investment_type": investment_type, 
            "entities": entities,
            "documents": format_documents(documents), 
            "temporal_directives": temporal_directives,
            "extracted_details": extracted_details
        })
        
        logging.info(f"Analiz Sonucu: Koşullar: {response.conditions} - Gerekçe: {response.reasoning}")
        return {"special_conditions": response}

    except Exception as e:
        logging.error(f"   > Özel koşul analizi sırasında beklenmedik bir hata oluştu: {e}", exc_info=True)
        # Hata durumunda bile sistemin çökmemesi için güvenli bir varsayılan değer döndür
        return {
            "special_conditions": SpecialConditions(
                conditions=[],
                reasoning=f"Özel koşul analizi sırasında kritik bir hata oluştu: {e}"
            )
        } 