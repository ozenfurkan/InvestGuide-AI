import asyncio
import logging
from dotenv import load_dotenv
import os
from typing import Dict, Any

# --- 1. Adım: API Anahtarını ve Ortam Değişkenlerini Yükle ---
# Diğer her şeyden önce bu çalışmalı.
load_dotenv()

# --- 2. Adım: Sağlam Loglama Yapılandırması (Yeniden Aktif Edildi) ---
# Tüm logları 'logs/debug.log' dosyasına yaz ve konsolda sadece ana bilgileri göster.
log_directory = "logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

logging.basicConfig(
    level=logging.DEBUG, # Yakalanacak en düşük seviye
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.path.join(log_directory, 'debug.log'), # Kaydedilecek dosya
    filemode='w' # Her çalıştırmada dosyayı temizle
)
# Konsol için daha sade bir loglama formatı
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO) # Konsolda sadece INFO ve üstünü göster
formatter = logging.Formatter('%(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logging.getLogger().addHandler(console_handler)


# --- 3. Adım: Graph ve Diğer Bağımlılıkları Import Et ---
# Loglama ve dotenv ayarlandıktan sonra importları yap.
from graph.graph import create_graph
from langchain_core.runnables.graph import MermaidDrawMethod

# Uygulama grafiğini global olarak oluştur
app = create_graph()

async def get_investment_report(query: str, config: Dict = None) -> Dict[str, Any]:
    """
    Verilen bir sorgu için yatırım analizini çalıştırır ve nihai raporu döndürür.
    """
    if config is None:
        config = {"recursion_limit": 50}
        
    logging.info("Grafik akışı başlatılıyor...")
    final_state = await app.ainvoke({"query": query}, config=config)
    
    # Analiz bittiğinde, state'in son halinden raporu çekiyoruz.
    # Pydantic modelinden dict'e dönüşüm olmuş olabilir, .get() güvenlidir.
    final_response_obj = final_state.get("final_response")
    
    if not final_response_obj:
        logging.error("Analiz tamamlandı ancak nihai rapor (final_response) state'te bulunamadı. State'in son hali: %s", final_state)
        return {"error": "Nihai rapor oluşturulamadı. Detaylar için logları kontrol edin."}
        
    logging.info("Nihai Rapor başarıyla oluşturuldu.")
    
    # --- SAVUNMA MEKANİZMASI: RAPOR TİPİ KONTROLÜ ---
    # Gelen raporun Pydantic nesnesi mi yoksa sözlük mü olduğunu kontrol et.
    # Her ihtimale karşı, eğer bir nesne ise onu sözlüğe çevir.
    if hasattr(final_response_obj, 'dict'):
        return final_response_obj.dict()
    
    return final_response_obj


async def main_cli():
    """
    Komut satırı arayüzünü çalıştırır.
    """
    print("Yatırım Teşvik Asistanı'na hoş geldiniz. Çıkmak için 'exit' yazın.")
    while True:
        try:
            user_query = input("\n> Analiz için yatırım senaryonuzu girin: ")
            if user_query.lower() == 'exit':
                print("Görüşmek üzere!")
                break
            
            if not user_query.strip():
                continue

            # Raporu al
            final_report = await get_investment_report(user_query)

            # Raporu konsola yazdır
            print("\n" + "="*80)
            print(" ✨ YATIRIM TEŞVİK ANALİZ RAPORU ✨")
            print("="*80)
            
            if final_report.get("error"):
                print(f"\n❌ HATA: {final_report.get('error')}")
            else:
                print(final_report.get("report", "Rapor içeriği bulunamadı."))
                
            print("\n" + "="*80)

        except KeyboardInterrupt:
            print("\nÇıkış yapılıyor...")
            break
        except Exception as e:
            logging.error("main_cli döngüsünde beklenmedik bir hata oluştu: %s", e, exc_info=True)
            print(f"❌ Beklenmedik bir hata oluştu. Detaylar için 'logs/debug.log' dosyasına bakın.")


# --- UYGULAMA BAŞLANGIÇ NOKTASI ---
if __name__ == "__main__":
    """
    Bu ana blok, program doğrudan çalıştırıldığında devreye girer.
    Windows'a özgü asyncio olay döngüsü politikasını ayarlar ve
    ana komut satırı arayüzü (CLI) fonksiyonunu çalıştırır.
    KeyboardInterrupt (Ctrl+C) gibi istisnaları yakalayarak programın
    temiz bir şekilde sonlanmasını sağlar.
    """
    # Windows'ta "Event loop is already running" hatasını önlemek için
    if os.name == 'nt':  # Sadece Windows için geçerli
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    try:
        # Ana CLI uygulamasını çalıştır
        asyncio.run(main_cli())
    except KeyboardInterrupt:
        # Kullanıcı Ctrl+C'ye bastığında temiz bir mesajla çık
        print("\nProgram kullanıcı tarafından sonlandırıldı.")
    except Exception as e:
        # Beklenmedik bir hata olursa logla ve kullanıcıya bildir
        logging.critical(f"Program ana döngüde beklenmedik bir hata ile çöktü: {e}")
        print(f"\nProgram kritik bir hata nedeniyle durduruldu. Detaylar için 'logs/debug.log' dosyasına bakın.")

    # Grafik yapısını çizmek için (opsiyonel, debug için faydalı)
    try:
        graph_image = app.get_graph().draw_mermaid_png(draw_method=MermaidDrawMethod.PYPPETEER)
        with open("graph.png", "wb") as f:
            f.write(graph_image)
        logging.info("Grafik yapısı 'graph.png' dosyasına kaydedildi.")
    except Exception as e:
        logging.warning(f"Grafik çizimi oluşturulamadı (pyppeteer/Chromium kurulu olmayabilir): {e}")