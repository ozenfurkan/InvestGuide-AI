from langchain_core.runnables import RunnableLambda
from pydantic import BaseModel, Field
from typing import Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from graph.core.llm import get_llm_client

# İl -> Bölge Numarası haritası
# Kaynak: 2012/3305 sayılı Karar, EK-1 ve sonraki değişiklikler
CITY_TO_REGION = {
    "Ankara": 1, "Antalya": 1, "Bursa": 1, "Eskişehir": 1, "İstanbul": 1, "İzmir": 1, "Kocaeli": 1, "Muğla": 1, "Aydın": 1, "Denizli": 1, "Tekirdağ": 1,
    "Adana": 2, "Bolu": 2, "Çanakkale": 2, "Edirne": 2, "Isparta": 2, "Kayseri": 2, "Kırklareli": 2, "Konya": 2, "Sakarya": 2, "Yalova": 2,
    "Balıkesir": 3, "Bilecik": 3, "Burdur": 3, "Gaziantep": 3, "Karabük": 3, "Karaman": 3, "Manisa": 3, "Mersin": 3, "Samsun": 3, "Trabzon": 3, "Uşak": 3, "Zonguldak": 3,
    "Afyonkarahisar": 4, "Amasya": 4, "Artvin": 4, "Bartın": 4, "Çorum": 4, "Düzce": 4, "Elazığ": 4, "Erzincan": 4, "Hatay": 4, "Kastamonu": 4, "Kırıkkale": 4, "Kırşehir": 4, "Malatya": 4, "Nevşehir": 4, "Rize": 4, "Sivas": 4,
    "Adıyaman": 5, "Aksaray": 5, "Bayburt": 5, "Çankırı": 5, "Erzurum": 5, "Giresun": 5, "Gümüşhane": 5, "Kahramanmaraş": 5, "Kilis": 5, "Niğde": 5, "Ordu": 5, "Osmaniye": 5, "Sinop": 5, "Tokat": 5, "Tunceli": 5, "Yozgat": 5,
    "Ağrı": 6, "Ardahan": 6, "Batman": 6, "Bingöl": 6, "Bitlis": 6, "Diyarbakır": 6, "Hakkari": 6, "Iğdır": 6, "Kars": 6, "Mardin": 6, "Muş": 6, "Siirt": 6, "Şanlıurfa": 6, "Şırnak": 6, "Van": 6
}

# Yaygın takma adları resmi adlara çevir
CITY_ALIASES = {
    "Antep": "Gaziantep",
    "Urfa": "Şanlıurfa",
    "Maraş": "Kahramanmaraş",
    "Afyon": "Afyonkarahisar",
    "İçel": "Mersin"
}

class RegionInfo(BaseModel):
    """Bir ilin adını ve teşvik bölge numarasını içeren yapı."""
    # alias='il' -> LLM'in 'il' anahtar kelimesini 'corrected_name' olarak tanımasını sağlar.
    corrected_name: str = Field(..., description="Yazım hataları düzeltilmiş, standart il adı.", alias='il')
    # alias='teşvik_bölgesi' -> LLM'in bu anahtar kelimeyi 'region_number' olarak tanımasını sağlar.
    region_number: Optional[int] = Field(None, description="İlin bulunduğu teşvik bölgesi (1-6 arası). Bulunamadıysa null.", alias='teşvik_bölgesi')
    reasoning: Optional[str] = Field(None, description="Bu bölge atamasının nedenini açıklayan kısa bir not.")

# --- PROMPT TEMPLATE ---
# Zincirin LLM'e göndereceği talimatlar.
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "Sen, Türkiye'deki il isimleri konusunda uzman bir coğrafya ve idari birimler uzmanısın. Görevin, sana verilen metindeki il adını bulmak, yazım hatalarını düzeltmek ve bu ilin 2012/3305 sayılı Karar'a göre hangi teşvik bölgesinde (1'den 6'ya kadar) yer aldığını belirlemektir. Cevabını sadece JSON formatında ver."),
        ("human", "Yatırım yapılacak yer: {query}")
    ]
)


def resolve_region_from_name(region_name: str) -> RegionInfo:
    """
    Verilen bir bölge adını (il) analiz eder, düzeltir ve teşvik bölge numarasını bulur.
    Bu fonksiyon API çağrısı yapmaz.
    """
    # Girdiyi standartlaştır: boşlukları temizle ve baş harfleri büyüt (örn: "  ANTEP " -> "Antep")
    # Türkçe karakterler için case-insensitive eşleştirme yapmak karmaşık olduğundan title() kullanıyoruz.
    standardized_name = region_name.strip().title()

    # Önce takma adlar sözlüğünde ara
    corrected_name = CITY_ALIASES.get(standardized_name, standardized_name)
    
    # Bölge numarasını ana haritadan al
    region_number = CITY_TO_REGION.get(corrected_name)

    if region_number:
        reasoning = f"'{region_name}' girdisi, '{corrected_name}' olarak standartlaştırıldı ve mevzuat haritasında {region_number}. bölge olarak bulundu."
        return RegionInfo(
            corrected_name=corrected_name,
            region_number=region_number,
            reasoning=reasoning
        )
    else:
        # Eşleşme bulunamazsa
        reasoning = f"'{region_name}' girdisi için teşvik bölgeleri haritasında bir eşleşme bulunamadı."
        return RegionInfo(
            corrected_name=region_name,
            region_number=None,
            reasoning=reasoning
        )

def get_region_resolver_chain():
    """Bölge çözümleyici zincirini döndürür."""
    llm = get_llm_client()
    
    structured_llm = llm.with_structured_output(RegionInfo, method="json_mode")
    
    chain = prompt | structured_llm
    
    return chain 