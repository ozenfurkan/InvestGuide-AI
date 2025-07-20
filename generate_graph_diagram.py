import os
from dotenv import load_dotenv
from graph import create_graph

# Ortam değişkenlerini yükle. Bu, grafiğin derlenmesi sırasında
# LLM istemcilerinin düzgün başlatılması için gereklidir.
load_dotenv()

def generate_diagram():
    """
    LangGraph iş akışının bir diyagramını oluşturur ve PNG olarak kaydeder.
    """
    print("Grafik oluşturuluyor...")
    # Grafiği oluştur ve derle
    app = create_graph()
    
    output_path = "graph_diagram.png"
    
    try:
        print(f"Grafik diyagramı '{output_path}' olarak oluşturuluyor...")
        
        # get_graph() metodu, çizilebilir bir versiyonunu döndürür.
        # draw_mermaid_png() metodu bu çizimi PNG formatında byte olarak verir.
        png_bytes = app.get_graph().draw_mermaid_png()
        
        with open(output_path, "wb") as f:
            f.write(png_bytes)
        
        print(f"\n✅ Başarılı! Grafik diyagramı '{output_path}' olarak kaydedildi.")
        print("Sunumunuzda bu görseli kullanarak sistemin iş akışını anlatabilirsiniz.")

    except Exception as e:
        print(f"\n❌ Hata: Grafik diyagramı oluşturulamadı.")
        print("Bu özelliğin çalışması için sisteminizde ek bir programın (Graphviz) kurulu olması gerekebilir.")
        print("Eğer kurulu değilse, şu adresten kurabilirsiniz: https://graphviz.org/download/")
        print(f"\nDetaylı Hata: {e}")

if __name__ == "__main__":
    generate_diagram() 