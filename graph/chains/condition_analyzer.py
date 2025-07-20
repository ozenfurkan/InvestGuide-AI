from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field, conlist
from typing import List, Optional
from graph.core.llm import get_llm_client

class ConditionItem(BaseModel):
    """Bir koşulu veya istisnayı ve onun yasal dayanağını tanımlar."""
    description: str = Field(description="Yatırımın sağlaması gereken özel şartın veya tabi olduğu istisnanın açıklaması.")
    legal_basis: Optional[str] = Field(description="Bu koşulun veya istisnanın dayandığı spesifik mevzuat maddesi, karar numarası veya kural ID'si.")

class SpecialConditions(BaseModel):
    """Yatırımın sağlaması gereken özel koşullar veya tabi olduğu istisnalar."""
    conditions: Optional[List[ConditionItem]] = Field(
        description="Yatırımın teşvikten yararlanabilmesi için sağlaması gereken özel şartların (asgari kapasite vb.) veya 'kazanılmış hak' gibi tabi olduğu önemli istisnaların, yasal dayanaklarıyla birlikte listesi."
    )
    reasoning: str = Field(
        description="Bu koşulların veya istisnaların neden geçerli olduğunu açıklayan detaylı gerekçe. Gerekçende kullandığın direktif, özel not veya mevzuat maddelerine atıf yap."
    )

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
Sen, Türkiye yatırım teşvikleri konusunda uzman bir hukuk danışmanısın. Görevin, belirlenmiş yatırım türü ve diğer tüm girdileri kullanarak, yatırımın tabi olduğu özel koşulları veya 'kazanılmış hak' gibi istisnaları belirlemektir.

-----
ZAMANA BAĞLI ANALİZ DİREKTİFLERİ:
{temporal_directives}
-----
SORGUDAN ÇIKARILAN KRİTİK DETAYLAR:
{extracted_details}
-----

YAPILACAK İŞ:
1.  **'ÖZEL NOT' ve 'KRİTİK DETAYLAR'a Odaklan:** Aynen yatırım türü analizindeki gibi, bu iki bölüm senin için en önemli yol göstericidir.
2.  **Akıl Yürüt ve Karşılaştır:** '**ÖZEL NOT**'un talimatını al (örn: lisans tarihini kontrol et) ve `extracted_details`'daki somut veriyle (örn: `license_date_year: 2011`) karşılaştır.
3.  **Koşul/İstisna Belirle ve Kanıtla:** Bu akıl yürütmenin sonucunda ulaştığın nihai durumu (örn: "Kullanıcının lisans tarihi 19/06/2012'den önce olduğu için kazanılmış haktan yararlanır.") ve bu durumun dayandığı mevzuat maddesini bularak `ConditionItem` olarak listeye ekle. Diğer genel mevzuat koşullarını da (asgari kapasite vb.) yasal dayanaklarıyla birlikte bu listeye eklemeye devam et.
4.  **Gerekçelendir:** Bulduğun her koşul veya istisnanın nedenini, özellikle 2. adımda yaptığın akıl yürütme sürecini adım adım açıklayarak `reasoning` alanına yaz.

Eğer herhangi bir "**ÖZEL NOT**" yoksa, o zaman sadece genel direktiflere ve mevzuat metinlerindeki standart şartlara göre koşulları belirle.

Belirlenmiş Yatırım Türü Analizi:
{investment_type}

Kullanıcı Sorgusu ve Çıkarılan Varlıklar: {entities}

İlgili Mevzuat Metinleri:
{documents}
""",
        )
    ]
)

def get_condition_analyzer_chain():
    """
    Özel koşul analiz zincirini oluşturur ve döndürür.
    LLM istemcisini sadece bu fonksiyon çağrıldığında başlatır.
    """
    llm = get_llm_client(temperature=0)
    structured_llm = llm.with_structured_output(SpecialConditions)
    return prompt | structured_llm 