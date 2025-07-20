# graph/graph.py
import logging
from typing import Literal
from langgraph.graph import StateGraph, END
from .state import GraphState

# --- Tüm Düğümleri ve Mantık Fonksiyonlarını Eksiksiz İçe Aktarma ---
from .nodes.entity_extractor import entity_extractor_node
from .nodes.mevzuat_auditor import mevzuat_auditor_node
from .nodes.document_retriever import retrieve_documents_node
from .nodes.temporal_resolver_node import temporal_resolver_node
from .nodes.detail_extractor import detail_extractor_node
from .nodes.investment_type_analyzer import investment_type_analyzer_node
from .nodes.focused_retriever import focused_retriever_node
from .nodes.condition_analyzer import condition_analyzer_node
from .nodes.support_analyzer import support_analyzer_node
from .nodes.region_resolver import region_resolver_node
from .nodes.final_response_synthesizer import final_response_synthesizer_node

logging.basicConfig(level=logging.INFO, format='   > %(message)s')

def should_retrieve_documents(state: GraphState) -> Literal["continue", "end"]:
    """Varlık çıkarma işleminden sonra doküman araması yapılıp yapılmayacağına karar verir."""
    logging.info("---KARAR: Dokümanlar Aranmalı mı?---")
    entities = state.get("entities")
    if entities and entities.investment_topic and entities.investment_region:
        logging.info("   > Karar: Gerekli varlıklar mevcut. Dokümanlar aranacak.")
        return "continue"
    else:
        logging.info("   > Karar: Yetersiz varlık. Analiz sonlandırılıyor.")
        return "end"

def should_focus_search(state: GraphState) -> Literal["focus", "skip"]:
    """Yatırım türü analizinden sonra odaklanmış arama yapılıp yapılmayacağına karar verir."""
    logging.info("---KARAR: Arama Odaklanmalı mı?---")
    analysis_result = state.get("investment_type")
    
    investment_type_str = ""
    if analysis_result:
        investment_type_str = analysis_result.investment_type

    if investment_type_str in ["Genel Teşvik", "Kapsam Dışı"]:
        logging.info(f"   > Karar: Yatırım türü '{investment_type_str}'. Odaklanmış arama atlanıyor.")
        return "skip"
    
    logging.info(f"   > Karar: Yatırım türü '{investment_type_str}'. Daha spesifik bilgi için arama odaklanacak.")
    return "focus"

def create_graph():
    """Tüm modüler düğümleri ve kenarları tanımlayarak iş akışı grafiğini oluşturur."""
    workflow = StateGraph(GraphState)
    
    # --- 1. Adım: Düğümleri Tanımla (Eksiksiz Liste) ---
    workflow.add_node("entity_extractor", entity_extractor_node)
    workflow.add_node("mevzuat_auditor", mevzuat_auditor_node)
    workflow.add_node("retrieve_documents", retrieve_documents_node)
    workflow.add_node("temporal_resolver", temporal_resolver_node)
    workflow.add_node("detail_extractor", detail_extractor_node)
    workflow.add_node("investment_type_analyzer", investment_type_analyzer_node)
    workflow.add_node("focused_retriever", focused_retriever_node)
    workflow.add_node("condition_analyzer", condition_analyzer_node)
    workflow.add_node("support_analyzer", support_analyzer_node)
    workflow.add_node("region_resolver", region_resolver_node)
    workflow.add_node("final_response_synthesizer", final_response_synthesizer_node)

    # --- 2. Adım: Grafiğin Akışını Tanımla (Orijinal ve Doğru Mantık) ---
    workflow.set_entry_point("entity_extractor")
    workflow.add_edge("entity_extractor", "mevzuat_auditor")

    workflow.add_conditional_edges(
        "mevzuat_auditor",
        should_retrieve_documents,
        {"continue": "retrieve_documents", "end": "final_response_synthesizer"},
    )

    workflow.add_edge("retrieve_documents", "detail_extractor")
    workflow.add_edge("detail_extractor", "temporal_resolver")
    workflow.add_edge("temporal_resolver", "investment_type_analyzer")

    workflow.add_conditional_edges(
        "investment_type_analyzer",
        should_focus_search,
        {
            "focus": "focused_retriever",
            "skip": "condition_analyzer",
        },
    )
    
    workflow.add_edge("focused_retriever", "condition_analyzer")
    workflow.add_edge("condition_analyzer", "support_analyzer")
    workflow.add_edge("support_analyzer", "region_resolver")
    workflow.add_edge("region_resolver", "final_response_synthesizer")
    workflow.add_edge("final_response_synthesizer", END)

    # --- 3. Adım: Grafiği Derle ve Çizdir ---
    app = workflow.compile()
    
    try:
        app.get_graph().draw_mermaid_png(output_file_path="graph.png")
    except Exception as e:
        logging.warning(f"Grafik çizimi oluşturulamadı: {e}")

    return app 