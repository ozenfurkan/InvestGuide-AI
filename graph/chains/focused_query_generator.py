from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

from graph.core.llm import get_llm_client

# LLM istemcisini burada oluşturma, import sırasında hataya neden oluyor.
# llm = get_llm_client()

class FocusedQuery(BaseModel):
    """
    Yatırım türü ve bölgeye göre, destek oranları ve süreleri gibi spesifik
    detayları bulmak için oluşturulan, hedefe yönelik arama sorgusu.
    """
    query: str = Field(description="Destek oranları, süreleri ve şartları gibi spesifik detayları bulmak için oluşturulan, hedefe yönelik Türkçe arama sorgusu.")

parser = PydanticOutputParser(pydantic_object=FocusedQuery)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """Sen, Türkiye yatırım teşvik mevzuatı konusunda uzman bir asistansın. Görevin, verilen yatırım türü ve bölgeye göre, bu yatırımın alabileceği desteklerin oranlarını, sürelerini ve özel şartlarını bulmak için en etkili ve spesifik arama sorgusunu oluşturmaktır. Sadece oluşturduğun sorguyu döndür.

Örnekler:
- Yatırım Türü: Bölgesel Teşvik, Bölge: 6. Bölge -> Sorgu: "6. bölge bölgesel teşvik destek oranları ve süreleri tablosu"
- Yatırım Türü: Öncelikli Yatırım -> Sorgu: "Öncelikli yatırımlar için KDV istisnası ve vergi indirimi oranları"
- Yatırım Türü: Stratejik Yatırım, Bölge: 2. Bölge -> Sorgu: "2. bölgedeki stratejik yatırımlar için faiz desteği ve sigorta primi desteği şartları"

Formatlama Talimatları:
{format_instructions}
""",
        ),
        (
            "human",
            "Yatırım Türü: {investment_type}\nBölge: {region}",
        ),
    ]
).partial(format_instructions=parser.get_format_instructions())

def get_focused_query_generator_chain():
    """
    Spesifik arama sorguları üreten LangChain zincirini döndürür.
    LLM istemcisini, sadece ihtiyaç duyulduğunda oluşturur.
    """
    llm = get_llm_client()
    return prompt | llm | parser 