from ..state import GraphState
from typing import Dict, Any
import logging
from datetime import datetime, date

logger = logging.getLogger(__name__)

def temporal_resolver_node(state: GraphState) -> Dict[str, Any]:
    """
    Kritik Detaylar Çıkarıcı'dan gelen tarih verilerini analiz eder ve 
    eğer geçmiş bir tarih saptanırsa, buna uygun bir 'Kazanılmış Hak Uyarısı' 
    ve vektör veritabanı için bir direktif oluşturur.

    Bu düğüm, özellikle geçmiş tarihli mevzuatın geçerliliği konusunda kullanıcıyı
    uyarmak ve RAG sürecini doğru belgelere yönlendirmek için kritik öneme sahiptir.
    """
    # Acil durum modu: Eğer bir şekilde bu düğüme gelinirse, hatayı logla ve pas geç.
    # Bu, normalde detail_extractor'dan sonra çalışması gereken bir düğümdür.
    # TODO: Bu acil durum modunu daha sağlam bir mantıkla değiştir.
    
    extracted_details = state.get("extracted_details")
    
    # Eğer bir önceki adımdan detaylar gelmediyse veya boşsa, atla.
    if not extracted_details or not extracted_details.get("reference_date"):
        logger.info("   > İşlenecek zamansal direktif bulunamadı. Atlanıyor.")
        return {
            "temporal_directive": None,
            "acquired_rights_warning": None
        }
        
    reference_date_str = extracted_details.get("reference_date")
    
    try:
        # Gelen tarih string'ini date objesine çevir
        reference_date = datetime.strptime(reference_date_str, "%Y-%m-%d").date()
        
        # Bugünün tarihi
        today = date.today()

        # Eğer referans tarih geçmişteyse, direktif ve uyarı oluştur
        if reference_date < today:
            logger.warning(f"   > Geçmiş tarih saptandı: {reference_date}. Kazanılmış hak uyarısı oluşturuluyor.")
            
            # Yıl ve ay bilgisini al
            year = reference_date.year
            month = reference_date.strftime("%B") # Örn: "Mayıs"
            
            temporal_directive = f"ÖZEL NOT: Bu analiz, {year} yılının {month} ayındaki duruma göre yapılmalıdır. O tarihte geçerli olan mevzuat ve bölgesel şartlar öncelikli olarak dikkate alınmalıdır."
            acquired_rights_warning = f"UYARI: Bu rapor, {year} yılı {month} ayına göre yapılmış bir analize dayanmaktadır. Yatırımlarda teşvikler açısından 'kazanılmış haklar' ilkesi geçerli olsa da, bu tarihten sonra mevzuatta meydana gelmiş olabilecek değişiklikler nihai durumu etkileyebilir. Güncel ve kesin bilgi için mutlaka resmi kurumlara danışınız."
            
            return {
                "temporal_directive": temporal_directive,
                "acquired_rights_warning": acquired_rights_warning
            }
        
    except (ValueError, TypeError) as e:
        logger.error(f"   > Tarih ayrıştırma hatası: {e}. Girdi: {reference_date_str}")
        pass # Hata durumunda sessizce devam et
        
    # Eğer tarih gelecekteyse veya ayrıştırma başarısızsa, bir şey yapma
    return {
        "temporal_directive": None,
        "acquired_rights_warning": None
    } 