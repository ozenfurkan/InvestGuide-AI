# graph/chains/entity_extractor.py
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field, conint, confloat
from typing import Optional
from graph.core.llm import get_llm_client

class ExtractedEntities(BaseModel):
    """Kullanıcı sorgusundan çıkarılan varlıklar."""
    investment_topic: Optional[str] = Field(
        description="Yatırımın ana konusu veya sektörü (örn: 'tekstil fabrikası', 'büyükbaş hayvancılık', 'otel')."
    )
    investment_sector_code: Optional[str] = Field(
        description="Yatırım konusuna karşılık gelen ve mevzuatta kullanılan sektör kodu/numarası. Örnek: 'Otel yatırımı' -> '50', 'Makine imalatı' -> '27', 'Gıda ürünleri imalatı' -> '10'."
    )
    investment_region: Optional[str] = Field(
        description="Yatırımın yapılacağı il (şehir) veya özel bölge (örn: 'Bursa', 'Trakya Serbest Bölgesi')."
    )
    investment_amount: Optional[confloat(ge=0)] = Field(
        description="Yatırımın sayısal tutarı. Eğer belirtilmemişse boş bırak."
    )

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
Sen, metinlerden yapılandırılmış bilgi çıkaran bir uzmansın. Görevin, kullanıcının yatırım teşvikleri hakkındaki sorgusunu analiz ederek, aşağıdaki dört temel bilgiyi (varlığı) çıkarmaktır:
1.  **Yatırım Konusu:** Sorguda bahsedilen ana yatırım faaliyeti nedir? (örn: 'tekstil', 'hayvancılık', 'otel', 'enerji santrali')
2.  **Sektör Kodu:** Bu yatırım konusuna karşılık gelen mevzuat sektör kodunu belirle. (örn: Otelcilik için '50', Gıda imalatı için '10' gibi).
3.  **Yatırım Bölgesi:** Yatırımın yapılacağı il (şehir) neresidir?
4.  **Yatırım Tutarı:** Sorguda sayısal bir yatırım tutarı belirtilmiş mi? Belirtilmişse bu sayıyı al.

Bu bilgileri sağlanan JSON şemasına göre çıkar. Eğer bir bilgi mevcut değilse, o alanı boş bırak.
""",
        ),
        ("human", "{query}"),
    ]
)

def get_entity_extractor_chain():
    """
    Varlık çıkarma zincirini oluşturur ve döndürür.
    LLM istemcisini sadece bu fonksiyon çağrıldığında başlatır.
    """
    llm = get_llm_client(temperature=0)
    structured_llm = llm.with_structured_output(ExtractedEntities)
    return prompt | structured_llm     