# graph/nodes/investment_type_analyzer.py
import logging
from typing import Dict, Any, List
from langchain_core.documents import Document
from graph.state import GraphState
from graph.chains.investment_type_analyzer import get_investment_type_analyzer_chain, InvestmentTypeAnalysis

logging.basicConfig(level=logging.INFO, format='   > %(message)s')

# Öncelikli yatırım olduğunu GARANTİLEYEN Kural ID'leri
PRIORITY_RULE_IDS = [
    "ONCELIKLI_YATIRIM_OTOMOTIV_GENISLEMESI",
    "ONCELIKLI_YATIRIM_YERLI_MADEN_ENERJI_GENISLEMESI",
    "ONCELIKLI_YATIRIM_TURIZM_DARALTILMASI",
    "ONCELIKLI_YATIRIM_EGITIM_GENISLETILMESI",
    "ONCELIKLI_YATIRIM_ENERJI_VERIMLILIGI_EKLENMESI",
    "ONCELIKLI_YATIRIM_ATIK_ISI_EKLENMESI",
    "ONCELIKLI_YATIRIM_LNG_DEPOLAMA_EKLENMESI",
    "EK4_SAGLIK_TESVIK_KAPSAM_DEGISIKLIGI" 
]

def format_documents_for_analysis(docs: List[Document]) -> str:
    """Doküman listesini LLM'in işleyebileceği tek bir metne dönüştürür."""
    if not docs:
        return ""
    # Mevzuat metinlerini birleştirirken daha belirgin bir ayraç kullanalım.
    return "\n\n---\n\n".join(
        [f"Kaynak: {doc.metadata.get('source', 'Bilinmiyor')} - Detay: {doc.metadata.get('detay', 'Bilinmiyor')}\n\n{doc.page_content}" for doc in docs]
    )

def investment_type_analyzer_node(state: GraphState) -> Dict[str, Any]:
    """
    Tüm toplanan bilgileri ve denetim sonuçlarını kullanarak, yatırımın nihai
    türünü (Genel, Bölgesel, Öncelikli, Stratejik vb.) belirler.
    
    Bu düğüm, hata durumlarında bile sistemin çökmemesi için ASLA None döndürmez.
    """
    logging.info("---NODE: Yatırım Türü Analiz Ediliyor---")
    
    # Hata durumunda döndürülecek varsayılan "güvenli" nesne
    default_response = InvestmentTypeAnalysis(
        investment_type="Belirsiz", 
        reasoning="Yatırım türü analizi sırasında bir hata oluştu veya yeterli veri bulunamadı.", 
        legal_basis="Yok"
    )

    try:
        # --- DOĞRU VE GÜVENLİ STATE ERİŞİMİ ---
        # GraphState bir TypedDict'tir. .get() metodu en güvenli yoldur.
        temporal_directives_text = state.get("temporal_directives") or "Uygulanacak özel bir zamansal direktif bulunamadı."
        entities = state.get("entities")
        documents = state.get("documents") or []

        # Temel veriler olmadan analiz yapılamaz.
        if not entities:
            logging.warning("   > Analiz için temel varlıklar (entities) eksik. Atlanıyor.")
            return {"investment_type": InvestmentTypeAnalysis(investment_type="Belirsiz", reasoning="Analiz için yeterli ön bilgi (varlıklar) bulunamadı.", legal_basis="Yok")}

        # --- KURAL TABANLI KONTROL ---
        if any(rule_id in temporal_directives_text for rule_id in PRIORITY_RULE_IDS):
            logging.info("   > Kural tabanlı kontrol: 'Öncelikli Yatırım' statüsü sağlayan bir Kural ID'si bulundu. LLM atlanıyor.")
            priority_response = InvestmentTypeAnalysis(
                investment_type="Öncelikli Yatırım",
                reasoning="Sistem, zamana bağlı direktifler arasında, yatırımın konusuna doğrudan 'Öncelikli Yatırım' statüsü veren bir mevzuat kuralı (Kural ID ile teyit edildi) tespit etmiştir. Bu kural, diğer analizlere göre önceliklidir.",
                legal_basis="İlgili Öncelikli Yatırım Kararı (Madde 17 veya ilgili değişiklik)"
            )
            return {"investment_type": priority_response}
            
        # --- STANDART LLM ANALİZİ ---
        logging.info("   > Standart analiz için LLM'e başvuruluyor...")
        chain = get_investment_type_analyzer_chain()

        # Zincire gönderilecek tüm girdilerin mevcut olduğundan emin ol.
        invoke_params = {
            "entities": entities,
            "documents": format_documents_for_analysis(documents),
            "temporal_directives": temporal_directives_text,
            "is_regionally_eligible": state.get("is_regionally_eligible", False),
            "is_large_scale": state.get("is_large_scale", False),
            "is_prohibited": state.get("is_prohibited", False),
        }
        
        response = chain.invoke(invoke_params)

        # --- SAĞLAMLIK KONTROLÜ ---
        if not response or not isinstance(response, InvestmentTypeAnalysis):
            logging.error("   > HATA: Yatırım türü analiz zinciri 'None' veya geçersiz bir tip döndürdü.")
            analysis_result = default_response
        else:
            analysis_result = response

        logging.info(f"   > Belirlenen Yatırım Türü: {analysis_result.investment_type}")
        
        return {"investment_type": analysis_result}

    except Exception as e:
        logging.critical(f"   > KRİTİK HATA: Yatırım türü analizi sırasında beklenmedik bir hata oluştu: {e}", exc_info=True)
        return {"investment_type": default_response} 