import operator
from typing import TypedDict, Optional, List, Dict, Any
from langchain_core.documents import Document
from pydantic import BaseModel, Field, validator

# Analiz zincirlerinden gelen yapılandırılmış Pydantic nesneleri
from .chains.investment_type_analyzer import InvestmentTypeAnalysis
from .chains.condition_analyzer import SpecialConditions
from .chains.support_analyzer import SupportAnalysis
from .chains.entity_extractor import ExtractedEntities
from .chains.detail_extractor import ExtractedDetails

class FinalReport(BaseModel):
    """Nihai yatırım teşvik analiz raporu."""
    title: str = Field(description="Raporun başlığı.")
    summary: str = Field(description="Yatırım ve sonuçlar hakkında yönetici özeti.")
    reasoning: str = Field(description="Analizin arkasındaki mantığı ve kararları açıklayan bölüm.")
    supports_section: str = Field(description="Mevcut destek unsurlarının (vergi indirimi, KDV istisnası vb.) açıklandığı bölüm.")
    conditions_section: str = Field(description="Yatırımcının bu desteklerden yararlanmak için yerine getirmesi gereken şartların listelendiği bölüm.")
    legal_references: List[str] = Field(description="Raporda atıfta bulunulan tüm yasal dayanakların, kanun maddelerinin ve eklerin listesi.")
    acquired_rights_warning: Optional[str] = Field(default=None, description="Geçmiş tarihli bir sorgulama yapıldıysa, kazanılmış haklar konusunda bir uyarı notu.")

    @validator('legal_references', pre=True)
    def split_string_to_list(cls, v):
        if isinstance(v, str):
            return [item.strip() for item in v.split(',') if item.strip()]
        return v


class GraphState(TypedDict):
    """
    Grafiğin durumu. Her bir düğüm tarafından güncellenen ve diğer
    düğümlerin kullanımına sunulan verileri içerir.

    Attributes:
        query: Kullanıcının orijinal sorgusu.
        entities: Sorgudan çıkarılan varlıklar (yatırım konusu, bölge, tutar, sektör kodu).
        is_regionally_eligible: Yatırımın, EK-2B'ye göre bölgesel teşvike uygun olup olmadığını belirten boolean bayrak.
        is_large_scale: Yatırımın, EK-3'e göre Büyük Ölçekli Yatırım şartlarını karşılayıp karşılamadığını belirten boolean bayrak.
        is_prohibited: Yatırımın, EK-4'e göre teşvik edilmeyenler listesinde olup olmadığını belirten boolean bayrak.
        documents: Vektör veritabanından alınan ilgili mevzuat metinleri.
        investment_type: Yatırımın türü ve gerekçesi.
        special_conditions: Yatırımın tabi olduğu özel koşullar ve istisnalar.
        support_analysis: Belirlenen destek unsurları ve detayları.
        temporal_directive: Zamana bağlı analiz için oluşturulan direktif metni.
        extracted_details: "ÖZEL NOT"lar için sorgudan çıkarılan kritik detaylar.
        final_response: Kullanıcıya sunulacak nihai metin.
    """
    query: str
    entities: Optional[ExtractedEntities] = None
    is_regionally_eligible: bool = False
    is_large_scale: bool = False
    is_prohibited: bool = False
    documents: Optional[List[Document]] = None
    investment_type: Optional[InvestmentTypeAnalysis] = None
    special_conditions: Optional[SpecialConditions] = None
    support_analysis: Optional[SupportAnalysis] = None
    temporal_directive: Optional[str] = None
    extracted_details: Optional[ExtractedDetails] = None
    final_response: Optional[str] = None
