import logging
from typing import Dict
from graph.state import GraphState
from graph.mevzuat_denetcisi import get_mevzuat_denetcisi

logging.basicConfig(level=logging.INFO, format='   > %(message)s')

def mevzuat_auditor_node(state: GraphState) -> Dict:
    """
    Tüm mevzuat denetimlerini merkezi olarak yürüten düğüm.
    Bu düğüm, yatırımın ilk analizini LLM'in yorumuna bırakmadan,
    kodun kesinliğiyle yapar.
    """
    logging.info("---NODE: Mevzuat Uygunluk Denetimi (EK-2B, EK-3, EK-4)---")
    
    entities = state.get("entities")
    if not entities or not entities.investment_region or not entities.investment_topic:
        logging.warning("   > Denetim için il veya yatırım konusu bulunamadı. Atlanyor.")
        return {}

    il_adi = entities.investment_region
    konu = entities.investment_topic
    tutar = entities.investment_amount or 0.0

    denetci = get_mevzuat_denetcisi()

    # Adım 1: Konudan kesin sektör kodunu bul (Arşivci)
    sektor_kodu = denetci.get_sektor_kodu_from_description(konu)
    if not sektor_kodu:
        logging.warning(f"   > '{konu}' için bir sektör kodu bulunamadı.")
        # HATA DÜZELTME: Her zaman Pydantic objesi döndür, dict değil.
        # Mevcut entity nesnesinin bir kopyasını oluşturup sadece sektör kodunu güncelle.
        updated_entities = entities.copy(update={"investment_sector_code": None})
        return {
            "entities": updated_entities,
            "is_regionally_eligible": False,
            "is_large_scale": False,
            "is_prohibited": False,
        }
    
    logging.info(f"   > '{konu}' konusu için Sektör Kodu '{sektor_kodu}' olarak tespit edildi.")
    # State'deki entities'i yeni bulunan kesin sektör koduyla güncelle
    updated_entities = entities.copy(update={"investment_sector_code": sektor_kodu})

    # Adım 2: Tüm denetimleri yap
    is_regionally_eligible = denetci.check_regional_eligibility(sektor_kodu, il_adi)
    is_large_scale = denetci.check_large_scale_eligibility(sektor_kodu, tutar)
    is_prohibited = denetci.check_prohibited_list(sektor_kodu)
    
    logging.info(f"   > Bölgesel Uygunluk (EK-2B): {is_regionally_eligible}")
    logging.info(f"   > Büyük Ölçekli Yatırım (EK-3): {is_large_scale}")
    logging.info(f"   > Yasaklılar Listesi (EK-4): {is_prohibited}")

    return {
        "entities": updated_entities,
        "is_regionally_eligible": is_regionally_eligible,
        "is_large_scale": is_large_scale,
        "is_prohibited": is_prohibited,
    } 