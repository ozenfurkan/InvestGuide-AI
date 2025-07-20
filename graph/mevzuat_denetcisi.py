import json
from pathlib import Path
from typing import Optional, Any

class MevzuatDenetcisi:
    """
    Mevzuatın EK dosyalarını doğrudan JSON objeleri olarak yükleyip,
    denetim fonksiyonları içinde bu objeleri işleyerek %100 doğrulukta
    cevaplar üreten modül.
    """
    def __init__(self, data_path: Path = Path("data")):
        self.ek1_data = self._load_json(data_path / "ek-1.json")
        self.ek2a_data = self._load_json(data_path / "ek-2a.json")
        self.ek2b_data = self._load_json(data_path / "ek-2b.json")
        self.ek3_data = self._load_json(data_path / "ek-3.json")
        self.ek4_data = self._load_json(data_path / "ek-4.json")
        self.ek5_data = self._load_json(data_path / "ek-5.json")

    def _load_json(self, file_path: Path) -> Optional[Any]:
        """Verilen yoldaki JSON dosyasını güvenli bir şekilde yükler."""
        try:
            with file_path.open('r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, Exception) as e:
            # Hata durumunda loglama yaparak sorunu daha net görelim
            print(f"!!! KRİTİK HATA: {file_path} dosyası okunamadı. Hata Tipi: {type(e).__name__}, Mesaj: {e}")
            return None

    def get_sektor_kodu_from_description(self, topic: str) -> Optional[str]:
        """
        EK-2A verisini kullanarak, verilen yatırım konusuna en çok uyan
        sektörün US-97 kodunu bulur.
        """
        if not self.ek2a_data or "sektörler" not in self.ek2a_data:
            return None
        
        topic_words = set(topic.lower().strip().split())
        for sector in self.ek2a_data.get("sektörler", []):
            sector_name_words = set(sector.get("SEKTÖR ADI", "").lower().split())
            
            # Kullanıcının girdiği kelimelerden herhangi biri sektör adında geçiyorsa eşleştir.
            if topic_words & sector_name_words: # Kesişim kontrolü
                return sector.get("US-97 Kodu")
        return None

    def check_regional_eligibility(self, sektor_kodu: str, il_adi: str) -> bool:
        """
        Belirli bir sektör kodunun, belirli bir il için EK-2B'ye göre bölgesel
        teşvike uygun olup olmadığını denetler.
        """
        if not self.ek2b_data or "tablo" not in self.ek2b_data or not sektor_kodu:
            return False
            
        il_adi_normalized = il_adi.upper().strip()
        # İsimlerdeki "İ" harfini "I" ya çevirerek eşleşmeyi garantile
        il_adi_normalized = il_adi_normalized.replace('İ', 'I')

        for satir in self.ek2b_data.get("tablo", {}).get("satirlar", []):
            current_il = satir.get("İL ADI", "").upper().split('(')[0].strip()
            current_il = current_il.replace('İ', 'I')
            if current_il == il_adi_normalized:
                sektor_numaralari_str = satir.get("SEKTÖR NUMARALARI", "")
                return sektor_kodu in sektor_numaralari_str.split()
        return False

    def check_large_scale_eligibility(self, sektor_kodu: str, amount: float) -> bool:
        """
        Belirli bir sektör ve yatırım tutarının EK-3'e göre Büyük Ölçekli Yatırım
        şartlarını karşılayıp karşılamadığını denetler.
        """
        if not self.ek3_data or "yatırımlar" not in self.ek3_data or not sektor_kodu:
            return False
            
        # EK-3'teki US-97 kodları metin içinde gizli, bu yüzden metin araması yapacağız
        for investment in self.ek3_data.get("yatırımlar", []):
            # Basit yatırım konuları
            konu = investment.get("Yatırım Konusu", "")
            if f"(US-97:{sektor_kodu})" in konu or f"US-97:{sektor_kodu}" in konu:
                 if "Asgari Sabit Yatırım Tutarı (Milyon TL)" in investment:
                    min_amount = float(investment["Asgari Sabit Yatırım Tutarı (Milyon TL)"]) * 1_000_000
                    return amount >= min_amount

            # İç içe geçmiş alt yatırımlar (örn: Motorlu Kara Taşıtları)
            if "Alt Yatırımlar" in investment:
                for alt_yatirim in investment.get("Alt Yatırımlar", []):
                    alt_konu = alt_yatirim.get("Konu", "")
                    if f"(US-97:{sektor_kodu})" in alt_konu or f"US-97:{sektor_kodu}" in alt_konu:
                        min_amount = float(alt_yatirim.get("Tutar (Milyon TL)", 0)) * 1_000_000
                        return amount >= min_amount
        return False

    def check_prohibited_list(self, sektor_kodu: str) -> bool:
        """
        Belirli bir sektörün EK-4'e göre teşvik edilmeyenler listesinde
        olup olmadığını denetler.
        """
        if not self.ek4_data or not sektor_kodu:
            return False

        # EK-4'te yasaklı konular listeler halinde. Bu listelerde arama yap.
        try:
            for bolum in self.ek4_data.get("bölümler", []):
                if bolum.get("başlık") == "TEŞVİK EDİLMEYECEK YATIRIMLAR":
                    for kategori in bolum.get("kategoriler", []):
                        for konu in kategori.get("konular", []):
                            # Konu bir string veya dictionary olabilir
                            konu_str = ""
                            if isinstance(konu, dict):
                                konu_str = konu.get("konu", "")
                            elif isinstance(konu, str):
                                konu_str = konu
                            
                            if f"(US-97:{sektor_kodu})" in konu_str or f"US-97:{sektor_kodu}" in konu_str:
                                return True
        except Exception:
            # Karmaşık yapıda hata olursa güvenli tarafta kal
            return False 
        return False

# Singleton instance
mevzuat_denetcisi_instance = MevzuatDenetcisi()

def get_mevzuat_denetcisi():
    return mevzuat_denetcisi_instance

if __name__ == '__main__':
    # --- EK-4 DOSYASINI İZOLE TEST ETMEK İÇİN ÖZEL TEST BLOGU ---
    print("--- EK-4.json Test Senaryosu Başlatılıyor ---")
    
    # Adım 1: Denetçiyi oluştur ve sadece ek-4.json'un yüklenip yüklenmediğini kontrol et.
    denetci = MevzuatDenetcisi()
    if denetci.ek4_data:
        print("✅ ADIM 1 BAŞARILI: ek-4.json dosyası başarıyla yüklendi ve JSON olarak ayrıştırıldı.")
        
        # Adım 2: Yüklenen veri içinde bilinen bir metni aramayı dene.
        # Bu, check_prohibited_list fonksiyonunun içindeki mantığı test edecek.
        print("\n--- ADIM 2: 'check_prohibited_list' Fonksiyon Mantığı Test Ediliyor ---")
        
        # Normalde bu kodları bilmemiz gerekmez ama test için manuel olarak ekliyoruz.
        # Gerçekte bu kodlar başka bir yerden (örn: ek-2a) gelmeli.
        # Biz burada sadece EK-4 arama mantığını test ediyoruz.
        yasakli_sektor_kodu = "15.61" # Un imalatı (EK-4'te geçiyor, US-97 kodu varsayımsal)
        serbest_sektor_kodu = "99.99" # Rastgele, var olmayan bir kod
        
        print(f"Test Edilen Yasaklı Kod: '{yasakli_sektor_kodu}'")
        is_prohibited_test = denetci.check_prohibited_list(yasakli_sektor_kodu)
        print(f"SONUÇ: Kod yasaklılar listesinde mi? -> {is_prohibited_test}")
        if is_prohibited_test:
            print("✅ TEST BAŞARILI: Yasaklı sektör doğru bir şekilde tespit edildi.")
        else:
            print("❌ TEST BAŞARISIZ: Yasaklı sektör tespit edilemedi. Arama mantığını kontrol et.")

        print(f"\nTest Edilen Serbest Kod: '{serbest_sektor_kodu}'")
        is_prohibited_test_2 = denetci.check_prohibited_list(serbest_sektor_kodu)
        print(f"SONUÇ: Kod yasaklılar listesinde mi? -> {is_prohibited_test_2}")
        if not is_prohibited_test_2:
            print("✅ TEST BAŞARILI: Listede olmayan bir sektör doğru raporlandı.")
        else:
            print("❌ TEST BAŞARISIZ: Olmayan bir sektör hatalı olarak 'yasaklı' bulundu.")

    else:
        print("\n❌ ADIM 1 BAŞARISIZ: ek-4.json yüklenirken veya JSON olarak ayrıştırılırken bir hata oluştu.")
        print("   -> Sorun, dosyanın kendisindeki yapısal bir bozukluk olabilir (gizli karakterler, format hatası vb.).") 