import json
from pathlib import Path
from typing import List, Dict, Any, Iterator
import shutil

from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import os

# Sabitler
DATA_PATH = Path("data")
DB_PATH = "mevzuat_veritabani" # FAISS klasör olarak kaydeder
MEVZUAT_DOSYASI = "karar_2012_3305_son_versiyon.json"

def _serialize_recursive(data: Any) -> Iterator[str]:
    """
    Karmaşık ve iç içe geçmiş JSON yapılarından (sözlükler, listeler)
    anlamlı metin parçaları üreten yardımcı bir generator fonksiyonu.
    """
    if isinstance(data, dict):
        for key, value in data.items():
            # Anahtarları başlık gibi kullanarak okunabilirliği artır
            processed_key = key.replace("_", " ").replace("-", " ").title()
            # Değeri de özyineli olarak işle
            for sub_value in _serialize_recursive(value):
                # Sadece metin içeren anahtarları değil, tüm yapıyı metne dök
                # Örn: "İl Adı: Adana", "Sektör Numaraları: 1 2 3"
                if sub_value and not sub_value.isspace():
                     # Basit anahtar-değer çiftleri için daha temiz format
                    if not any(isinstance(v, (dict, list)) for v in data.values()):
                         yield f"{processed_key}: {sub_value}"
                         break # Aynı seviyedeki diğer anahtarlara geç
                    else:
                         yield sub_value

    elif isinstance(data, list):
        for item in data:
            yield from _serialize_recursive(item)
    elif data is not None:
        yield str(data).strip()

def load_documents_from_decision(file_path: Path) -> List[Document]:
    """
    Belirtilen Karar JSON dosyasını yükler. Hem 'maddeler'i hem de 'ekler'i
    kendi yapılarına uygun, bütüncül ve ayrı Document nesneleri olarak işler.
    """
    all_documents = []
    print(f"-> Nihai İşleme: {file_path.name}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 1. Maddeleri İşle
        maddeler_listesi = data.get("maddeler", [])
        if maddeler_listesi:
            for madde in maddeler_listesi:
                baslik = madde.get("başlık", "Başlıksız Madde")
                madde_no = madde.get("maddeNo", "")
                
                # Fıkra ve bentlerden tam metni birleştir
                content_parts = list(_serialize_recursive(madde.get("fıkralar", [])))
                if not content_parts:
                    continue
                
                page_content = f"Madde No: {madde_no} - Başlık: {baslik}\n\n" + "\n".join(content_parts)
                doc = Document(page_content=page_content, metadata={"source": file_path.name, "kategori": "Madde", "detay": f"Madde {madde_no}"})
                all_documents.append(doc)
            print(f"  + {len(maddeler_listesi)} madde başarıyla ayrıştırıldı.")

        # 2. Ekleri İşle
        ekler_listesi = data.get("ekler", [])
        if ekler_listesi:
            for ek in ekler_listesi:
                baslik = ek.get("baslik", "Başlıksız Ek")
                ek_no = ek.get("ekNo", "")

                # Karmaşık ek içeriğini okunabilir bir metne dönüştür
                content_parts = list(_serialize_recursive(ek.get("icerik", ek)))
                if not content_parts:
                    continue

                page_content = f"Ek No: {ek_no} - Başlık: {baslik}\n\n" + "\n".join(content_parts)
                doc = Document(page_content=page_content, metadata={"source": file_path.name, "kategori": "Ek", "detay": f"Ek {ek_no}"})
                all_documents.append(doc)
            print(f"  + {len(ekler_listesi)} ek başarıyla ayrıştırıldı.")

    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"  - HATA: Dosya okunamadı veya JSON formatı bozuk. {e}")
            
    return all_documents

def build_vector_db():
    """
    Mevzuat metinlerini işleyerek bir FAISS vektör veritabanı oluşturur ve kaydeder.
    """
    print("\n--- Vektör Veritabanı Oluşturma (FAISS Standardı) ---")
    db_path_obj = Path(DB_PATH)
    if db_path_obj.exists():
        print(f"\n🧹 Mevcut veritabanı '{DB_PATH}' temizleniyor...")
        shutil.rmtree(db_path_obj)

    documents = load_documents_from_decision(DATA_PATH / MEVZUAT_DOSYASI)
    
    if not documents:
        print("\n❌ İşlenecek doküman bulunamadı. Lütfen JSON yapısını kontrol edin.")
        return

    print(f"\nToplam {len(documents)} adet bütüncül doküman (madde/ek) yüklendi.")
    
    print("\n🧠 Metinler vektörlere dönüştürülüyor ve FAISS indexi oluşturuluyor...")
    embeddings = OpenAIEmbeddings()
    vector_db = FAISS.from_documents(documents, embeddings)
    
    vector_db.save_local(DB_PATH)
    print(f"\n✨ FAISS veritabanı başarıyla oluşturuldu: '{DB_PATH}'")

if __name__ == "__main__":
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("Lütfen projenin kök dizininde OPENAI_API_KEY'i içeren bir .env dosyası oluşturun.")
    build_vector_db()