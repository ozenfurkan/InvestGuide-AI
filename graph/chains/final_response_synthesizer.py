from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List

from graph.core.llm import get_llm_client

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
Sen, yapılandırılmış analiz verilerini, son kullanıcı için profesyonel bir rapora dönüştüren bir uzmansın.

**EN ÖNEMLİ KURAL: ZAMAN UYARISI**
Eğer `{state}` içindeki `temporal_directives` alanı "NOT:" ile başlıyorsa, raporun `summary` alanının en başına aşağıdaki **KAZANILMIŞ HAK UYARISI** metnini ekle. Bu senin birincil görevin.
---
**KAZANILMIŞ HAK UYARISI:** Bu rapor, mevcut güncel mevzuata göre hazırlanmıştır. Ancak, teşvik belgenizi geçmiş bir tarihte aldığınız için, o tarihte yürürlükte olan ve lehinize olabilecek desteklerden yararlanma hakkınız bulunmaktadır. Bu rapor bir ön bilgilendirme olup, nihai haklarınız için mutlaka belgeyi aldığınız tarihteki mevzuata hakim bir uzmana danışmanız şiddetle tavsiye edilir.
---

**GÖREVİN:**
Aşağıdaki `{state}` verilerini kullanarak, aşağıdaki anahtarlara sahip bir JSON raporu oluştur:
- `title`: Rapor için özetleyici bir başlık.
- `summary`: Tüm analizin 1-2 cümlelik özeti.
- `reasoning`: Tüm analiz adımlarını birleştiren, akıcı bir "nasıl bu sonuca ulaşıldı" metni.
- `supports_section`: Bulunan desteklerin ve yasal dayanaklarının metin formatında bir listesi.
- `conditions_section`: Bulunan özel koşulların ve yasal dayanaklarının metin formatında bir listesi.
- `legal_references`: Analizde kullanılan tüm kanun, madde ve eklerin tam listesi.

-----
ANALİZ VERİLERİ:
{state}
-----
""",
        )
    ]
)

# --- ÇIKTI MODELİ (PYDANTIC) ---
# Nihai raporun yapısını tanımlar.
class FinalReport(BaseModel):
    """Nihai yatırım teşvik analiz raporu."""
    title: str = Field(description="Rapor için özetleyici bir başlık. Örnek: 'Eskişehir Lojistik Merkezi Yatırımı için Genel Teşvik Analizi'")
    summary: str = Field(description="Tüm analizin bir veya iki cümlelik özeti. Yatırımın türü ve temel sonucu içermelidir.")
    reasoning: str = Field(description="Tüm analiz sürecinin, başlangıçtan sona kadar, her bir düğümün kararını mantıksal bir akış içinde anlatan detaylı bir açıklaması. Neden 'Genel Teşvik' seçildi, neden 'Bölgesel' veya 'Öncelikli' değil, hangi koşullar geçerli vb.")
    supports_section: str = Field(description="Yatırımcının alabileceği desteklerin (KDV İstisnası, Gümrük Vergisi Muafiyeti vb.) ve bu desteklerin yasal dayanaklarının listelendiği bölüm.")
    conditions_section: str = Field(description="Yatırımın sağlaması gereken özel koşulların (asgari kapasite, lisans gerekliliği vb.) ve yasal dayanaklarının listelendiği bölüm.")
    # DÜZELTME: Bu alan artık bir metin listesi kabul ediyor.
    legal_references: List[str] = Field(description="Analizde kullanılan tüm kanun, madde ve eklerin tam listesi.")


def get_final_response_synthesizer_chain():
    """Nihai cevap oluşturma zincirini döndürür."""
    llm = get_llm_client(temperature=0.7) # Daha yaratıcı ve akıcı bir metin için sıcaklığı biraz artır
    
    # LLM'i, Pydantic modeline uygun bir JSON çıktısı üretmesi için yapılandır.
    structured_llm = llm.with_structured_output(FinalReport, method="json_mode")
    
    chain = prompt | structured_llm
    
    return chain 