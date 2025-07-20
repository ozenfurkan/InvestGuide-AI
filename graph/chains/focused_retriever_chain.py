from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from graph.core.llm import get_llm_client

class FocusedQuery(BaseModel):
    """
    Detaylı destek tablolarını bulmak için odaklanmış bir arama sorgusu.
    """
    query: str = Field(
        description="Belirli bir yatırım türü ve bölge için oran, süre ve limit içeren tabloları (EK-2 gibi) veya listeleri bulmak üzere tasarlanmış çok spesifik ve hedefli bir arama sorgusu. Örnek: '4. bölge bölgesel teşvikleri vergi indirimi ve sigorta primi oranları tablosu'"
    )

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
Sen, bir uzman araştırmacının bir sonraki adımda ne araması gerektiğini bilen bir stratejistsin. Görevin, sana verilen yatırım analizinin mevcut durumuna bakarak, eksik olan en kritik bilgiyi (destek oranları, süreleri, limitleri) bulmak için çok spesifik bir arama sorgusu oluşturmaktır.

Mevcut Analiz Durumu:
- Yatırım Türü: {investment_type}
- Yatırımcı Bilgileri: {entities}

YAPILACAK İŞ:
1.  **Analiz Sonucunu Anla:** Yatırımın türünün (Bölgesel, Öncelikli, Stratejik vb.) ve bölgesinin ne olduğunu anla.
2.  **Hedefi Belirle:** Amacımız, bu yatırım türü ve bölge için geçerli olan desteklerin oran, süre, limit gibi sayısal detaylarını içeren tabloları (örn: EK-2, EK-3) veya listeleri bulmaktır.
3.  **Spesifik Sorgu Oluştur:** Bu hedefe ulaşmak için en uygun, kısa ve öz arama sorgusunu oluştur. Sorgun "tablo", "oranlar", "süreler", "destek listesi", "EK-2" gibi anahtar kelimeler içermelidir.

ÖRNEK SORGULAR:
- Eğer yatırım türü 'Öncelikli Yatırım' ise: "öncelikli yatırımlar için sağlanan destekler tablosu EK-2"
- Eğer yatırım türü 'Bölgesel' ve bölge 'Ankara (1. Bölge)' ise: "1. bölge bölgesel teşvikleri vergi indirimi ve sigorta primi oranları"
- Eğer yatırım türü 'Stratejik Yatırım' ise: "stratejik yatırım destek unsurları ve oranları listesi"

Oluşturduğun sorguyu `query` alanına yaz.
""",
        )
    ]
)

def get_focused_retriever_chain():
    """
    Odaklanmış arama sorgusu oluşturan zinciri döndürür.
    """
    llm = get_llm_client(temperature=0)
    structured_llm = llm.with_structured_output(FocusedQuery)
    return prompt | structured_llm 