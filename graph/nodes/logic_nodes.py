import logging
from typing import Dict, Optional
from graph.state import GraphState
from ..chains.region_resolver import CITY_TO_REGION

logging.basicConfig(level=logging.INFO, format='   > %(message)s')

def resolve_physical_region_node(state: GraphState) -> dict:
    """
    Çıkarılan şehir adını kullanarak, yatırımın fiziksel olarak hangi teşvik bölgesinde
    olduğunu belirler (1'den 6'ya kadar).
    """
    logging.info("---NODE: Fiziksel Bölge Belirleniyor---")
    entities = state.get("entities")
    if not entities or not entities.investment_region:
        logging.warning("   > Varlıklarda bölge bilgisi bulunamadı, atlanıyor.")
        return {}

    # Gelen şehir adını standart bir formata (baş harfi büyük) çevirerek
    # büyük/küçük harf sorununu ortadan kaldır.
    city_name = entities.investment_region.strip().title()

    region = CITY_TO_REGION.get(city_name)
    
    if region is None:
        logging.error(f"   > '{city_name}' şehri için bölge bulunamadı.")
        return {"physical_region": None}
        
    logging.info(f"   > '{city_name}' şehri, fiziki olarak {region}. Bölge'de.")
    return {"physical_region": region}

def calculate_effective_region_node(state: GraphState) -> dict:
    """
    Yatırımın türüne (Öncelikli, OSB vb.) göre, desteklerden yararlanacağı
    "efektif" bölgeyi hesaplar.
    """
    logging.info("---NODE: Efektif Bölge Hesaplanıyor---")
    
    physical_region = state.get("physical_region")
    investment_type_obj = state.get("investment_type") # Nesneyi al
    entities = state.get("entities")

    # Gerekli veriler yoksa devam etme
    if physical_region is None or not investment_type_obj:
        logging.warning("   > Fiziksel bölge veya yatırım türü belli olmadığı için efektif bölge hesaplanamıyor.")
        # Eğer fiziksel bölge yoksa, efektif bölge de olamaz.
        return {"effective_region": physical_region}

    investment_type = investment_type_obj.investment_type
    is_osb = "osb" in state.get("query", "").lower() or "organize sanayi" in state.get("query", "").lower()

    # Başlangıçta efektif bölgeyi fiziksel bölgeye eşitle
    effective_region = physical_region
    
    # 1. Öncelikli Yatırım Avantajını Değerlendir
    if investment_type == "Öncelikli":
        # Öncelikli yatırımlar 5. bölge desteği alır.
        # Ancak kendi bölgesi (6. bölge gibi) daha avantajlıysa, kendi bölgesi geçerli olur.
        effective_region = max(physical_region, 5)
        logging.info(f"   > Yatırım 'Öncelikli'. Efektif bölge en az 5 olarak ayarlandı (Mevcut: {effective_region}).")

    # 2. OSB Avantajını Değerlendir (Öncelikli'den gelen sonuca ek olarak)
    # Eğer OSB'deyse ve mevcut efektif bölge 6'dan küçükse, bir alt bölge desteği eklenir.
    if is_osb and effective_region < 6:
        effective_region += 1
        logging.info(f"   > Yatırım OSB'de. Efektif bölge +1 artırılarak {effective_region} yapıldı.")

    # 3. Sonuçları logla
    if effective_region == physical_region:
        logging.info("   > Özel bir durum (Öncelikli, OSB) avantaj sağlamadı. Efektif bölge fiziksel bölgeye eşit.")
    
    return {"effective_region": effective_region}


def select_final_region_node(state: GraphState) -> dict:
    """
    Fiziksel bölge ile efektif bölgeyi karşılaştırır ve yatırımcı
    için en avantajlı (en yüksek) olanını nihai destek bölgesi olarak seçer.
    Bu düğüm AI kullanmaz, sadece bir max() fonksiyonu çalıştırır.
    """
    logging.info("---NODE: Nihai Destek Bölgesi Seçiliyor---")
    physical_region = state.get("physical_region")
    effective_region = state.get("effective_region")

    # Eğer bölgelerden biri hesaplanamamışsa, devam etme
    if physical_region is None or effective_region is None:
        logging.error("   > Gerekli bölgeler hesaplanamadığı için nihai bölge seçilemiyor.")
        return {"final_region": None}

    # Yatırımcı lehine olan, yani sayısı daha BÜYÜK olan bölgeyi seç
    final_region = max(physical_region, effective_region)
    
    logging.info(f"   > Fiziksel ({physical_region}) ve Efektif ({effective_region}) bölgeler karşılaştırıldı.")
    logging.info(f"   > Yatırımcı lehine olan en avantajlı bölge: {final_region}. Bölge")
    
    return {"final_region": final_region} 