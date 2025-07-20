import logging
import re
from typing import Dict, Any
from graph.state import GraphState
from graph.chains.region_resolver import get_region_resolver_chain, RegionInfo

logging.basicConfig(level=logging.INFO, format='   > %(message)s')

def region_resolver_node(state: GraphState) -> Dict[str, Any]:
    """
    Kullanıcı tarafından girilen il adını standartlaştırır ve teşvik bölge numarasını bulur.
    Farklı veri tiplerine karşı dayanıklıdır.
    """
    logging.info("---NODE: Bölge Bilgileri Çözümleniyor---")
    
    # Hata durumunda döndürülecek varsayılan nesne
    # DÜZELTME: Pydantic modelindeki 'alias' tanımına uygun anahtar kelimeyi kullan
    default_response = RegionInfo(
        il="Bilinmiyor",
        teşvik_bölgesi=None,
        reasoning="Girdide il adı bulunamadığı veya okunamadığı için bölge çözümlenemedi."
    )

    try:
        chain = get_region_resolver_chain()
        
        # State'ten orijinal sorguyu al
        query = state.get("query")

        if not query:
            logging.warning("   > Orijinal sorgu bulunamadığı için bölge çözümlenemedi.")
            return {"region_info": default_response.dict()}
        
        # Zincire 'entities' yerine doğrudan 'query' ver.
        response = chain.invoke({"query": query})

        # --- SAVUNMA MEKANİZMASI: Yanıt Kontrolü ---
        # LLM'in eksik veya hatalı yanıt verme ihtimaline karşı.
        if not response or not response.corrected_name:
             logging.warning(f"   > LLM'den geçerli bir bölge adı alınamadı. Yanıt: {response}")
             return {"region_info": default_response.dict()}

        logging.info(f"   > Bölge çözümlendi: {response.corrected_name} ({response.region_number}. Bölge)")
        return {"region_info": response.dict()}

    except Exception as e:
        logging.error(f"   > HATA: Bölge çözümleme sırasında beklenmedik bir hata oluştu: {e}")
        return {"region_info": default_response.dict()} 