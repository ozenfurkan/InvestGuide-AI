from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field, conlist
from typing import List, Optional, Literal
from graph.core.llm import get_llm_client

class SupportItem(BaseModel):
    """
    Bir yatırım için sağlanacak tek bir destek unsurunu ve tüm detaylarını tanımlar.
    Bir destek türü için geçerli olmayan alanlar boş bırakılmalıdır.
    """
    support_name: Literal[
        "Vergi İndirimi",
        "KDV İstisnası",
        "Gümrük Vergisi Muafiyeti",
        "Sigorta Primi İşveren Hissesi Desteği",
        "Faiz Desteği",
        "Yatırım Yeri Tahsisi",
        "Gelir Vergisi Stopajı Desteği"
    ] = Field(description="Desteğin standart adı.")

    # --- Vergi İndirimi için Özel Alanlar ---
    yatirima_katki_orani: Optional[str] = Field(
        default=None,
        description="Yatırıma Katkı Oranı (örn: '%40'). Sadece 'Vergi İndirimi' desteği için bu alanı doldur."
    )
    vergi_indirim_orani: Optional[str] = Field(
        default=None,
        description="Uygulanacak Kurumlar/Gelir Vergisi İndirim Oranı (örn: '%80'). Sadece 'Vergi İndirimi' desteği için bu alanı doldur."
    )

    # --- Faiz Desteği için Özel Alanlar ---
    tl_kredi_faiz_destegi_puani: Optional[str] = Field(
        default=None,
        description="TL cinsi krediler için faiz desteği puanı (örn: '5 Puan'). Sadece 'Faiz Desteği' için bu alanı doldur."
    )
    doviz_kredi_faiz_destegi_puani: Optional[str] = Field(
        default=None,
        description="Döviz cinsi krediler için faiz desteği puanı (örn: '2 Puan'). Sadece 'Faiz Desteği' için bu alanı doldur."
    )
    faiz_destegi_ust_limiti: Optional[str] = Field(
        default=None,
        description="Faiz desteğinin parasal üst limiti (örn: '1.8 Milyon TL'). Sadece 'Faiz Desteği' için bu alanı doldur."
    )

    # --- Sigorta Primi Desteği için Özel Alanlar ---
    sigorta_primi_destegi_suresi: Optional[str] = Field(
        default=None,
        description="Sigorta primi işveren hissesi desteğinin süresi (örn: '7 Yıl'). Sadece 'Sigorta Primi İşveren Hissesi Desteği' için bu alanı doldur."
    )

    # --- Ortak Alanlar ---
    description: str = Field(
        description="Desteğin ne işe yaradığını, kapsamını (örn: 'sadece makine-teçhizat için') ve genel şartlarını özetleyen açıklama."
    )
    legal_basis: str = Field(
        description="Bu desteğin ve oranlarının dayandığı spesifik mevzuat maddesi, tablo referansı veya kural ID'si (örn: '2012/3305 sayılı Karar, EK-2A Tablosu, 5. Bölge Sütunu')."
    )

class SupportAnalysis(BaseModel):
    """Yatırım için uygun olan tüm destek unsurlarının detaylı listesi."""
    supports: Optional[List[SupportItem]] = Field(
        description="Belirlenen yatırım türü ve koşullara göre uygun bulunan tüm destek unsurlarının, tüm detaylarıyla birlikte listesi."
    )

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
Sen, Türkiye yatırım teşvik mevzuatını harfiyen uygulayan, asla yorum yapmayan bir Mevzuat Uygulama Robotusun. Görevin, bir yatırım için geçerli olan destek unsurlarını, aşağıda belirtilen katı kurallara göre ve sağlanan belgelere dayanarak belirlemektir.

**YATIRIM TÜRÜNE GÖRE UYGULANABİLİR DESTEKLER (ANA KURAL LİSTESİ):**
Bu liste kesindir ve asla aşılamaz.
- **Genel Teşvik:** Sadece "KDV İstisnası" ve "Gümrük Vergisi Muafiyeti" uygulanabilir. BAŞKA HİÇBİR DESTEK EKLEME.
- **Bölgesel Teşvik:** "KDV İstisnası", "Gümrük Vergisi Muafiyeti", "Vergi İndirimi", "Sigorta Primi İşveren Hissesi Desteği", "Faiz Desteği" (4. Bölgeden itibaren), "Yatırım Yeri Tahsisi" uygulanabilir.
- **Öncelikli Yatırım:** 5. Bölge desteklerinin aynısı uygulanır ("KDV İstisnası", "Gümrük Vergisi Muafiyeti", "Vergi İndirimi", "Sigorta Primi İşveren Hissesi Desteği", "Faiz Desteği", "Yatırım Yeri Tahsisi"). Eğer yatırım 6. bölgede ise 6. bölge destekleri uygulanır.
- **Stratejik Yatırım:** Tüm bölgelerde "KDV İstisnası", "Gümrük Vergisi Muafiyeti", "Vergi İndirimi", "Sigorta Primi İşveren Hissesi Desteği", "Faiz Desteği", "Yatırım Yeri Tahsisi" ve ek olarak "Gelir Vergisi Stopajı Desteği" uygulanabilir.

-----
**GÖREV VERİLERİ:**
- **Analiz Edilecek Yatırım Türü:** {investment_type}
- **Özel Koşullar ve İstisnalar:** {special_conditions}
- **Referans Mevzuat Metinleri (içindeki EK-2 gibi tablolara dikkat et):**
{documents}
-----

**YAPILACAK İŞ (KESİN TALİMATLAR):**
1.  **Yetki Kontrolü:** Önce yukarıdaki **ANA KURAL LİSTESİ**'ne bak ve sana verilen `{investment_type}` için hangi desteklerin "izinli" olduğunu belirle.
2.  **Kanıt Arama:** SADECE izinli olan desteklerin detaylarını (oran, süre, limit vb.) sana verilen **Referans Mevzuat Metinleri** içinde ara.
3.  **Raporlama:** Sadece ve sadece hem "izinli" olan hem de metinlerde kanıtını bulduğun destekleri `SupportItem` olarak listele.
    - `support_name`: Desteğin standart adı.
    - `Vergi İndirimi` ise: `yatirima_katki_orani` VE `vergi_indirim_orani` alanlarını doldur.
    - `Faiz Desteği` ise: `tl_kredi_faiz_destegi_puani`, `doviz_kredi_faiz_destegi_puani` VE `faiz_destegi_ust_limiti` alanlarını doldur.
    - `Sigorta Primi İşveren Hissesi Desteği` ise: `sigorta_primi_destegi_suresi` alanını doldur.
    - `description`: Desteğin ne işe yaradığını özetle.
    - `legal_basis`: **EN ÖNEMLİ KURAL:** Bir oranın, sürenin veya limitin kaynağı bir tablo ise (örn: EK-2), referans olarak o tabloyu ve ilgili sütunu/bölgeyi göstermek zorundasın (örn: 'EK-2A Tablosu, 5. Bölge'). Eğer oranlar doğrudan bir maddede yazıyorsa o maddeyi referans göster.
4.  **YASAK:** Ana Kural Listesi'nde `{investment_type}` için izinli olmayan bir desteği, referans metinlerde görsen BİLE kesinlikle raporuna ekleme. Bilgi uydurma, yorum yapma.

**Referans için Kullanıcı Girdisi:** {entities}
""",
        )
    ]
)

def get_support_analyzer_chain():
    """
    Destek unsurları analiz zincirini oluşturur ve döndürür.
    """
    llm = get_llm_client(temperature=0)
    structured_llm = llm.with_structured_output(SupportAnalysis)
    return prompt | structured_llm 