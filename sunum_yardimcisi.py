import random
from datetime import date, timedelta

# --- Veri Kaynakları ---

# 1. Türkiye'nin 81 İli
iller = [
    "Adana", "Adıyaman", "Afyonkarahisar", "Ağrı", "Aksaray", "Amasya", "Ankara", "Antalya", "Ardahan", "Artvin",
    "Aydın", "Balıkesir", "Bartın", "Batman", "Bayburt", "Bilecik", "Bingöl", "Bitlis", "Bolu", "Burdur",
    "Bursa", "Çanakkale", "Çankırı", "Çorum", "Denizli", "Diyarbakır", "Düzce", "Edirne", "Elazığ", "Erzincan",
    "Erzurum", "Eskişehir", "Gaziantep", "Giresun", "Gümüşhane", "Hakkari", "Hatay", "Iğdır", "Isparta",
    "İstanbul", "İzmir", "Kahramanmaraş", "Karabük", "Karaman", "Kars", "Kastamonu", "Kayseri", "Kırıkkale",
    "Kırklareli", "Kırşehir", "Kilis", "Kocaeli", "Konya", "Kütahya", "Malatya", "Manisa", "Mardin", "Mersin",
    "Muğla", "Muş", "Nevşehir", "Niğde", "Ordu", "Osmaniye", "Rize", "Sakarya", "Samsun", "Siirt", "Sinop",
    "Sivas", "Şanlıurfa", "Şırnak", "Tekirdağ", "Tokat", "Trabzon", "Tunceli", "Uşak", "Van", "Yalova",
    "Yozgat", "Zonguldak"
]

# 2. Mevzuatlarda geçen temsili sektörler
sektorler = [
    "gıda işleme ve paketleme tesisi", "iplik ve dokuma fabrikası", "4 yıldızlı bir otel", "mermer ocağı işletmesi",
    "otomotiv yan sanayi parça üretimi", "plastik hammadde üretim tesisi", "güneş enerjisi santrali (GES)",
    "özel hastane", "özel lise kampüsü", "veri merkezi ve yazılım geliştirme ofisi",
    "mobilya imalat fabrikası", "organik tarım ve sera işletmesi", "çağrı merkezi (call center)",
    "soğuk hava deposu ve lojistik merkezi", "ilaç üretim tesisi"
]

# --- Fonksiyonlar ---

def rastgele_tarih_uret(baslangic=date(2012, 6, 15), bitis=date(2017, 12, 31)):
    gun_farki = (bitis - baslangic).days
    rastgele_gun = random.randint(0, gun_farki)
    return baslangic + timedelta(days=rastgele_gun)

def senaryo_olustur():
    """Sunum için rastgele bir yatırım senaryosu oluşturur."""
    
    secilen_tarih = rastgele_tarih_uret()
    secilen_il = random.choice(iller)
    secilen_sektor = random.choice(sektorler)
    rastgele_tutar = random.randrange(5_000_000, 500_000_000, 1_000_000)

    # 2. Verileri ekrana yazdır
    print("--- SUNUM İÇİN RASTGELE SENARYO ---")
    print(f"Tarih    : {secilen_tarih.strftime('%d.%m.%Y')}")
    print(f"İl       : {secilen_il}")
    print(f"Sektör   : {secilen_sektor}")
    print(f"Tutar    : {rastgele_tutar:,} TL")
    print("-" * 35)

    # 3. Streamlit için hazır soru metni oluştur
    soru = (
        f"{secilen_il}'de, yaklaşık {rastgele_tutar:,} TL yatırım bedeli olan bir "
        f"{secilen_sektor} kurmak istiyorum. teşvik belgemi {secilen_tarih.strftime('%Y yılının %B ayında')} "
        f"tarihinde aldım. Bu şartlar altında devletten ne gibi teşvikler alabilirim?"
    )
    
    print("📋 Kopyalanmaya Hazır Soru Metni:\n")
    print(soru)
    print("\n" + "="*50 + "\n")


if __name__ == "__main__":
    senaryo_olustur() 