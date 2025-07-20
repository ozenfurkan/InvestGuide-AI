# graph/nodes/final_response_synthesizer.py
import logging
from typing import Dict, Any
from graph.state import GraphState
from graph.chains.final_response_synthesizer import get_final_response_synthesizer_chain
from graph.chains.investment_type_analyzer import InvestmentTypeAnalysis
from graph.chains.support_analyzer import SupportAnalysis, SupportItem

logging.basicConfig(level=logging.INFO, format='   > %(message)s')

def final_response_synthesizer_node(state: GraphState) -> Dict[str, Any]:
    """
    Tüm analiz adımlarından gelen yapılandırılmış verileri, son kullanıcıya sunulacak,
    kolay anlaşılır, profesyonel ve bütünlüklü bir metne dönüştürür.
    
    Bu düğüm, önceki adımlarda oluşabilecek hatalara karşı 'kurşun geçirmez' olacak şekilde
    tasarlanmıştır. Önceki bir adımdan gelen veri 'None' ise, bunu güvenli bir şekilde
    ele alır ve raporun ilgili bölümünü varsayılan bir metinle doldurur.
    """
    logging.info("---NODE: Nihai Rapor Oluşturuluyor---")

    # --- SAVUNMA MEKANİZMASI: None'a Karşı Koruma ---
    # Önceki adımlardan gelen Pydantic nesnelerini al. Eğer 'None' iseler,
    # raporun neden eksik olduğunu açıklayan varsayılan, güvenli bir nesne oluştur.

    investment_type_analysis = state.get("investment_type")
    if not isinstance(investment_type_analysis, InvestmentTypeAnalysis):
        investment_type_analysis = InvestmentTypeAnalysis(
            investment_type="Belirsiz",
            reasoning="Yatırım türü analizi adımı tamamlanamadı veya bir hata ile karşılaştı. Bu nedenle raporun bu bölümü oluşturulamadı.",
            legal_basis="Yok"
        )

    support_analysis = state.get("support_analysis")
    if not isinstance(support_analysis, SupportAnalysis):
        support_analysis = SupportAnalysis(
            supports=[
                SupportItem(
                    support_name="Vergi İndirimi", # Örnek bir isim
                    description="Destek unsurları analizi adımı tamamlanamadı veya bir hata ile karşılaştı. Bu nedenle hangi desteklerden yararlanılabileceği tespit edilemedi.",
                    legal_basis="Yok"
                )
            ]
        )
    
    # Raporlama için kullanılacak tam state'i oluştur.
    # Burada sadece string'e çevrilebilen temel tipler olmalı.
    final_state_for_prompt = {
        "entities": state.get("entities", {}),
        "extracted_details": state.get("extracted_details", {}),
        "is_regionally_eligible": state.get("is_regionally_eligible", "Belirsiz"),
        "is_large_scale": state.get("is_large_scale", "Belirsiz"),
        "is_prohibited": state.get("is_prohibited", "Belirsiz"),
        "temporal_directives": state.get("temporal_directives", "Zamana bağlı direktifler oluşturulamadı."),
        "investment_type": investment_type_analysis.dict(), # Pydantic nesnesini dict'e çevir
        "support_analysis": support_analysis.dict(), # Pydantic nesnesini dict'e çevir
    }

    try:
        chain = get_final_response_synthesizer_chain()
        # Zincir artık bir Pydantic nesnesi (FinalReport) döndürüyor.
        structured_response = chain.invoke({"state": final_state_for_prompt})
        
        logging.info("Nihai Rapor başarıyla oluşturuldu.")
        # Yapısal yanıtı, main.py'nin beklediği 'final_response' anahtarıyla döndür.
        return {"final_response": structured_response.dict()}
    except Exception as e:
        logging.error(f"   > HATA: Nihai rapor oluşturulurken bir zincir hatası oluştu: {e}")
        # Hata durumunda, yanıltıcı başarı mesajını önlemek için boş veya hata içeren bir durum döndür
        return {"final_response": None} 