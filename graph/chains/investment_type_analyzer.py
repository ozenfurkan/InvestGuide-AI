# graph/chains/investment_type_analyzer.py
from typing import Optional, Literal
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from graph.core.llm import get_llm_client

class InvestmentTypeAnalysis(BaseModel):
    investment_type: Literal[
        "Genel Teşvik",
        "Bölgesel Teşvik",
        "Öncelikli Yatırım",
        "Büyük Ölçekli Yatırım",
        "Stratejik Yatırım",
        "Kapsam Dışı",
        "Belirsiz"
    ] = Field(description="Yatırımın sınıflandırıldığı ana teşvik türü.")
    reasoning: str = Field(description="Bu yatırım türü sınıflandırmasının neden yapıldığını adım adım açıklayan detaylı gerekçe.")
    legal_basis: Optional[str] = Field(description="Bu kararın dayandığı en temel kanun maddesi veya mevzuat eki (örn: Madde 17, EK-5).")

prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """Sen, Türkiye'nin yatırım teşvikleri konusunda uzman bir baş hukuk müşavirisin. Görevin, sana sunulan verileri analiz ederek bir yatırımın hangi ana teşvik kategorisine girdiğine karar vermek ve bu kararını sağlam bir gerekçeyle açıklamaktır. Cevabın SADECE istenen JSON formatında olmalıdır.

**KARAR VERME SÜRECİ (ADIM ADIM UYGULA):**

**ADIM 1: ÖNCELİKLİ YATIRIM KONTROLÜ (EN YÜKSEK ÖNCELİK)**
-   İlk ve en önemli görevin, sağlanan dokümanlar (`{documents}`) içinde "Madde 17" veya "Öncelikli yatırım konuları" ile ilgili bir bölüm olup olmadığını kontrol etmektir.
-   Kullanıcının yatırım konusunu (`{entities}`) bu listedeki maddelerle karşılaştır.
-   **Eğer bir eşleşme bulursan (örn: yatırım konusu 'seracılık', 'madencilik', 'turizm konaklama' gibi ifadeler içeriyorsa ve bu ifadeler Madde 17'de geçiyorsa), başka hiçbir şeye bakmadan kararı "Öncelikli Yatırım" olarak ver.** Gerekçeni ve yasal dayanağını doğrudan bu maddeye bağla.

**ADIM 2: KAPSAM DIŞI KONTROLÜ**
-   Eğer Adım 1'de bir sonuç bulamadıysan, `is_prohibited` denetim sonucuna bak.
-   Eğer `is_prohibited` sonucu `True` ise, kararı **"Kapsam Dışı"** olarak ver.

**ADIM 3: BÜYÜK ÖLÇEKLİ & STRATEJİK YATIRIM KONTROLÜ**
-   Eğer önceki adımlarda sonuç bulamadıysan, `is_large_scale` denetim sonucuna ve yatırım tutarına (`{entities.investment_amount}`) bak.
-   `is_large_scale` `True` ise **"Büyük Ölçekli Yatırım"** kararı ver.
-   Yatırım tutarı 500 Milyon TL'yi aşıyorsa ve mevzuattaki Stratejik Yatırım tanımına uyuyorsa, kararı **"Stratejik Yatırım"** olarak ver.

**ADIM 4: BÖLGESEL TEŞVİK KONTROLÜ**
-   Eğer hala bir sonuç yoksa, `is_regionally_eligible` denetim sonucuna bak.
-   `is_regionally_eligible` `True` ise, kararı **"Bölgesel Teşvik"** olarak ver.

**ADIM 5: GENEL TEŞVİK (VARSAYILAN)**
-   Yukarıdaki adımların hiçbiri olumlu bir sonuç vermediyse, kararı varsayılan olarak **"Genel Teşvik"** olarak belirle.

**ADIM 6: GEREKÇELENDİRME**
-   Hangi adımı izleyerek bu karara vardığını `reasoning` alanında açıkla. Örneğin: "Adım 1'de, yatırımın konusu olan 'jeotermal seracılık' Madde 17'deki 'maden işleme' tanımıyla eşleştiği için Öncelikli Yatırım olarak sınıflandırılmıştır."

---
**SANA SAĞLANAN VERİLER:**

- **Kullanıcı Sorgusu ve Varlıklar:** `{entities}`
- **Kesin Denetim Sonuçları:**
    - Bölgesel Teşvike Uygun mu? (EK-2B): `{is_regionally_eligible}`
    - Büyük Ölçekli mi? (EK-3): `{is_large_scale}`
    - Yasaklı Listede mi? (EK-4): `{is_prohibited}`
- **İlgili Mevzuat Metinleri:**
  `{documents}`
- **Önceki Adımdan Gelen Özel Direktif:** `{temporal_directive}`
""",
        )
    ]
)

def get_investment_type_analyzer_chain():
    """
    Yatırım türü analiz zincirini oluşturur ve döndürür.
    """
    llm = get_llm_client(temperature=0)
    structured_llm = llm.with_structured_output(InvestmentTypeAnalysis)
    return prompt_template | structured_llm