import logging
from graph.state import GraphState
from graph.chains.entity_extractor import get_entity_extractor_chain

logging.basicConfig(level=logging.INFO, format='   > %(message)s')

def entity_extractor_node(state: GraphState):
    """Sorgudan varlıkları (yatırım konusu, bölge, tutar) çıkarır."""
    logging.info("---NODE: Varlıklar Çıkarılıyor---")
    chain = get_entity_extractor_chain()
    response = chain.invoke({"query": state["query"]})
    logging.info(f"Çıkarılan Varlıklar: {response}")
    return {"entities": response} 