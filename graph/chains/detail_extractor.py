from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from graph.core.llm import get_llm_client

class ExtractedDetails(BaseModel):
    """
    Kullanıcı sorgusundan, özellikle 'ÖZEL NOT' direktiflerinin gerektirdiği
    kritik tarihsel veya durumsal detayları çıkarmak için kullanılan veri modeli.
    """
    reference_date: Optional[date] = Field(
        description="Kullanıcı sorgusunda belirtilen herhangi bir genel referans tarihi (YYYY-MM-DD formatında). Bu tarih, bir başvuru, belge alımı, yatırım başlangıcı veya sadece bir zaman çerçevesi olabilir. Örn: 'Mayıs 2023' -> 2023-05-01"
    )
    reasoning: str = Field(
        description="Bu tarihin sorgudan nasıl ve neden çıkarıldığını açıklayan kısa gerekçe."
    )


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
Sen, çok dikkatli bir hukuki metin analiz asistanısın. Görevin, sana verilen bir kullanıcı sorgusunu analiz ederek, içinde geçen ve yatırımın zaman çerçevesini belirten herhangi bir tarih ifadesini tespit etmek ve bunu yapılandırılmış `YYYY-MM-DD` formatına dönüştürmektir.

YAPILACAK İŞ:
1.  **Sorguyu Tara:** Kullanıcı sorgusunu dikkatle oku ve yatırımın ne zaman planlandığına, ne zaman başladığına veya ne zaman belge alındığına dair herhangi bir tarihsel ipucu ara.
    - Örnekler: "15 mayıs 2017'de başvurdum", "gelecek ayın 10'unda belge alacağız", "2023 mayısında tesis kurmak istiyorum", "2016 sonlarında".
2.  **Tarihi Dönüştür:** Bulduğun tarihi, kesin `YYYY-MM-DD` formatına dönüştür. Eğer gün belirtilmemişse, ayın 1'ini kullan. Eğer ay belirtilmemişse, yılın Ocak ayını kullan. Sadece tek bir genel tarih çıkar.
3.  **Alanı Doldur:** Dönüştürdüğün tarihi `reference_date` alanına yerleştir.
4.  **Gerekçelendir:** Çıkarımı nasıl yaptığını kısaca `reasoning` alanında açıkla.
5.  **Bulamazsan Boş Bırak:** Eğer sorguda hiçbir tarih ifadesi yoksa, tüm tarih alanlarını boş (`null`) bırak. Asla tarih uydurma.

Kullanıcı Sorgusu: {query}
""",
        )
    ]
)

def get_detail_extractor_chain():
    """
    Detay çıkarıcı zincirini oluşturur ve döndürür.
    """
    llm = get_llm_client(temperature=0)
    structured_llm = llm.with_structured_output(ExtractedDetails)
    return prompt | structured_llm 