# graph/temporal_resolver.py
import json
from datetime import date, datetime
from typing import List, Dict, Optional

# ExtractedDetails Pydantic modelini import et
from .chains.detail_extractor import ExtractedDetails

ANNOTATIONS_FILE = "annotations.json"

def _get_primary_analysis_date(extracted_details: Optional[ExtractedDetails]) -> date:
    """
    Öncelik sırasına göre analiz için kullanılacak ana tarihi belirler.
    Eğer kullanıcı bir tarih belirtmişse onu, belirtmemişse bugünü kullanır.
    Bu fonksiyon, 'None' değerlerine karşı dayanıklıdır.
    """
    if extracted_details:
        # Öncelik sırası: başvuru > belge > yatırım başlangıcı
        if extracted_details.application_date:
            return extracted_details.application_date
        if extracted_details.certificate_date:
            return extracted_details.certificate_date
        if extracted_details.investment_start_date:
            return extracted_details.investment_start_date
            
    # Eğer hiçbir tarih belirtilmemişse veya 'extracted_details' None ise, bugünü varsay
    return date.today()

def resolve_temporal_directives(extracted_details: Optional[ExtractedDetails]) -> str:
    """
    Kullanıcının sorgusundan çıkarılan hassas tarih bilgisini ve annotations.json dosyasını
    kullanarak, analiz için bir direktif seti oluşturur.
    """
    analysis_date = _get_primary_analysis_date(extracted_details)
    
    try:
        with open(ANNOTATIONS_FILE, 'r', encoding='utf-8') as f:
            annotations: List[Dict] = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return "UYARI: Annotations dosyası bulunamadı veya bozuk. Analiz sadece güncel mevzuata göre yapılacaktır."

    applicable_directives: List[str] = []
    
    for change in annotations:
        try:
            # effective_date'i datetime.date nesnesine çevir
            effective_date = datetime.strptime(change["effective_date"], "%Y-%m-%d").date()
        except (ValueError, TypeError, KeyError):
            # Hatalı veya eksik tarihli kuralları atla
            continue 

        # Kuralın analiz tarihinde geçerli olup olmadığını kontrol et
        if analysis_date >= effective_date:
            directive_to_add = change.get("directive")
            if directive_to_add:
                applicable_directives.append(f"- {directive_to_add} (Kaynak: {change.get('legal_source', 'N/A')}, Kural ID: {change.get('change_id', 'N/A')})")

    if not applicable_directives:
        return "Tarihsel analize göre uygulanacak özel bir direktif bulunamadı. Mevcut mevzuat kurallarını standart olarak uygula."

    header = f"DİKKAT: Analiz, {analysis_date.strftime('%d.%m.%Y')} tarihi mevzuatına göre yapılıyor. Aşağıdaki direktiflere kesinlikle uyulmalıdır:\n"
    return header + "\n".join(applicable_directives)