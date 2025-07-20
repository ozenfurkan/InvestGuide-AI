# graph/knowledge.py
"""
Bu dosya, Türkiye'deki yatırım teşvikleri için zaman içinde değişen kritik verileri
içeren merkezi bir bilgi bankası (knowledge base) görevi görür.
Bu veriler, "lehe olan hükümlerin" deterministik olarak kod ile hesaplanmasını
sağlayarak LLM hatalarını önler.
"""

# Önemli mevzuat değişikliklerinin yürürlüğe girdiği tarihler ve ilgili Karar Sayıları
# Bu tarihler, hangi dönemde hangi kuralların geçerli olduğunu belirlemek için kullanılır.
VERSION_DATES = {
    "2012/3305": "2012-06-19",
    "2013/4288": "2013-02-20",
    "2013/5559": "2013-10-31",
    "2014/6008": "2014-03-21",
    "2015/7492": "2015-04-08",
    "2016/9139": "2016-09-08",
    "2017/9942": "2017-03-10",
    "2018/11735": "2018-05-29",
    "2021/4707": "2021-10-29",
    "2022/6468": "2022-11-23"
}

# Her bir mevzuat versiyonu için şehirlerin hangi bölgede olduğunu tutan veri.
# Sadece değişen şehirleri eklemek yeterlidir. Sistem bir önceki versiyondan miras alır.
REGION_DEFINITIONS = {
    "2012-06-19": {
        "Adana": "2", "Adıyaman": "6", "Afyonkarahisar": "4", "Ağrı": "6", "Aksaray": "5",
        "Amasya": "4", "Ankara": "1", "Antalya": "1", "Ardahan": "6", "Artvin": "5",
        "Aydın": "2", "Balıkesir": "2", "Bartın": "4", "Batman": "6", "Bayburt": "6",
        "Bilecik": "3", "Bingöl": "6", "Bitlis": "6", "Bolu": "2", "Burdur": "3",
        "Bursa": "1", "Çanakkale": "3", "Çankırı": "5", "Çorum": "3", "Denizli": "2",
        "Diyarbakır": "6", "Düzce": "3", "Edirne": "2", "Elazığ": "4", "Erzincan": "5",
        "Erzurum": "5", "Eskişehir": "1", "Gaziantep": "3", "Giresun": "5", "Gümüşhane": "5",
        "Hakkari": "6", "Hatay": "3", "Iğdır": "6", "Isparta": "3", "İstanbul": "1",
        "İzmir": "1", "Kahramanmaraş": "4", "Karabük": "3", "Karaman": "3", "Kars": "6",
        "Kastamonu": "5", "Kayseri": "3", "Kırıkkale": "3", "Kırklareli": "2", "Kırşehir": "4",
        "Kilis": "5", "Kocaeli": "1", "Konya": "2", "Kütahya": "3", "Malatya": "4",
        "Manisa": "3", "Mardin": "6", "Mersin": "2", "Muğla": "1", "Muş": "6",
        "Nevşehir": "4", "Niğde": "5", "Ordu": "5", "Osmaniye": "5", "Rize": "4",
        "Sakarya": "2", "Samsun": "3", "Siirt": "6", "Sinop": "5", "Sivas": "4",
        "Şanlıurfa": "6", "Şırnak": "6", "Tekirdağ": "2", "Tokat": "4", "Trabzon": "3",
        "Tunceli": "6", "Uşak": "3", "Van": "6", "Yalova": "2", "Yozgat": "5", "Zonguldak": "3"
    },
    # Örnek: 2016'da bir şehrin bölgesi değişseydi buraya eklenirdi.
    # "2016-09-08": {
    #    "Ankara": "2" 
    # }
}


# Her bir mevzuat versiyonu için BÖLGESEL DESTEK unsurlarını tutan veri.
# Sadece değişen destekleri eklemek yeterlidir. Sistem bir önceki versiyondan miras alır.
# NOT: Bu yapı "Öncelikli Yatırım" ve "Stratejik Yatırım" gibi özel durumları içermez,
# onlar mantık katmanında ayrıca ele alınır. Bu sadece standart bölgesel desteklerdir.
SUPPORT_DEFINITIONS = {
    "2012-06-19": {
        "1": {
            "Vergi İndirimi": {"YKO": 15, "İndirim Oranı": 50},
            "Sigorta Primi İşveren Hissesi Desteği": {"Süre (yıl)": 2},
            "Faiz Desteği": {"TL Puan": 3, "Döviz Puan": 0, "Limit (Bin TL)": 500}
        },
        "2": {
            "Vergi İndirimi": {"YKO": 20, "İndirim Oranı": 55},
            "Sigorta Primi İşveren Hissesi Desteği": {"Süre (yıl)": 3},
            "Faiz Desteği": {"TL Puan": 4, "Döviz Puan": 0, "Limit (Bin TL)": 600}
        },
        "3": {
            "Vergi İndirimi": {"YKO": 25, "İndirim Oranı": 60},
            "Sigorta Primi İşveren Hissesi Desteği": {"Süre (yıl)": 5},
            "Faiz Desteği": {"TL Puan": 5, "Döviz Puan": 2, "Limit (Bin TL)": 700}
        },
        "4": {
            "Vergi İndirimi": {"YKO": 30, "İndirim Oranı": 70},
            "Sigorta Primi İşveren Hissesi Desteği": {"Süre (yıl)": 6},
            "Faiz Desteği": {"TL Puan": 6, "Döviz Puan": 2, "Limit (Bin TL)": 800}
        },
        "5": {
            "Vergi İndirimi": {"YKO": 40, "İndirim Oranı": 80},
            "Sigorta Primi İşveren Hissesi Desteği": {"Süre (yıl)": 7},
            "Gelir Vergisi Stopajı Desteği": {"Süre (yıl)": 10, "Not": "Bu destek sadece bu bölgede geçerlidir."},
            "Sigorta Primi Desteği (İşçi Hissesi)": {"Süre (yıl)": 7, "Not": "Bu destek sadece bu bölgede geçerlidir."},
            "Faiz Desteği": {"TL Puan": 7, "Döviz Puan": 2, "Limit (Bin TL)": 900}
        },
        "6": {
            "Vergi İndirimi": {"YKO": 50, "İndirim Oranı": 90},
            "Sigorta Primi İşveren Hissesi Desteği": {"Süre (yıl)": 10},
            "Gelir Vergisi Stopajı Desteği": {"Süre (yıl)": 10},
            "Sigorta Primi Desteği (İşçi Hissesi)": {"Süre (yıl)": 10},
            "Faiz Desteği": {"TL Puan": 7, "Döviz Puan": 2, "Limit (Bin TL)": 900}
        }
    },
    # Örnek: 2016'da 3. bölgenin vergi indirimi artsaydı, sadece o değişiklik eklenirdi.
    # "2016-09-08": {
    #    "3": {
    #        "Vergi İndirimi": {"YKO": 30, "İndirim Oranı": 65}
    #    }
    # }
}

# Genel destekler (bölgeden bağımsız ve çoğu zaman değişmeyen)
GENERAL_SUPPORTS = {
    "KDV İstisnası": "Yatırım teşvik belgesi kapsamındaki makine ve teçhizat alımları için KDV ödenmez.",
    "Gümrük Vergisi Muafiyeti": "Yatırım teşvik belgesi kapsamındaki makine ve teçhizat ithalatı için gümrük vergisi ödenmez.",
} 