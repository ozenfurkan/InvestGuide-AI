"""
graph paketi, yatırım teşvik analizini yöneten iş akışı grafiğini
ve bu grafiği oluşturan tüm bileşenleri (düğümler, zincirler, durum) içerir.

Bu paketin ana çıktısı, `create_graph` fonksiyonu tarafından oluşturulan
derlenmiş LangGraph uygulamasıdır.
"""
from .graph import create_graph

# Bu, dışarıdan `from graph import create_graph` şeklinde
# kolayca erişim sağlanabilmesi için __all__ listesine eklenir.
__all__ = ['create_graph']
