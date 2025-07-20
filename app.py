import streamlit as st
import asyncio
from main import get_investment_report # Sadece bu fonksiyona ihtiyacımız var

# Streamlit'in asenkron fonksiyonlarla uyumlu çalışması için olay döngüsü ayarı
# Bu, uygulamanın farklı ortamlarda sorunsuz çalışmasını sağlar.
try:
    loop = asyncio.get_running_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

st.set_page_config(
    page_title="InvestGuide AI",
    page_icon="🤖",
    layout="wide"
)

st.title("InvestGuide AI: Yatırım Teşvik Asistanı")
st.caption("Türkiye'deki yatırım teşvikleri hakkında anında, güvenilir ve mevzuata dayalı cevaplar alın.")

# Session state'i yöneterek sayfa yenilense bile raporun kaybolmamasını sağla
if 'report' not in st.session_state:
    st.session_state.report = None


# --- Arayüz Komponentleri ---
with st.form(key='investment_form'):
    user_query = st.text_area(
        "Yatırım planınızı detaylı olarak açıklayın:",
        "Örnek: Gaziantep'te 30 Milyon TL'lik bir tekstil fabrikası kurmayı planlıyorum. Devletten alabileceğim teşvikler nelerdir?",
        height=150
    )
    submit_button = st.form_submit_button(label='Analiz Et 🤖')


async def run_analysis_and_store_report(query: str):
    """Analiz sürecini çalıştırır ve sonucu session state'e kaydeder."""
    with st.spinner('Analiz yapılıyor... Bu işlem 1-2 dakika sürebilir. Lütfen bekleyin.'):
        # get_investment_report fonksiyonu bize bir sözlük (dictionary) döndürür.
        report_data = await get_investment_report(query)
        st.session_state.report = report_data


if submit_button and user_query:
    # 'Analiz Et' butonuna basıldığında asenkron analizi çalıştır
    loop.run_until_complete(run_analysis_and_store_report(user_query))
    
# --- Rapor Gösterim Alanı ---
# Analiz tamamlandıysa ve session state'de bir rapor varsa, onu ekrana yazdır.
if st.session_state.report:
    report = st.session_state.report
    st.markdown("---")
    st.header("📈 Yatırım Teşvik Analiz Raporu")
    st.markdown("---")

    st.subheader(f"Başlık: {report.get('title', 'Başlık Bulunamadı')}")
    st.info(f"**Özet:** {report.get('summary', 'Özet bulunamadı.')}")
    
    with st.expander("Detaylı Gerekçe ve Analiz Süreci"):
        st.markdown(report.get('reasoning', 'Gerekçe detayı bulunamadı.'))

    st.subheader("✅ Yararlanılabilecek Destek Unsurları")
    st.markdown(report.get('supports_section', 'Destek unsurları bulunamadı.'))

    st.subheader("📜 Özel Koşullar ve İstisnalar")
    st.markdown(report.get('conditions_section', 'Özel koşul bulunamadı.'))


# --- Yan Menü ---
with st.sidebar:
    st.header("Nasıl Çalışır?")
    st.markdown("""
    Bu asistan, sorduğunuz yatırım planını analiz etmek için gelişmiş bir yapay zeka (AI) iş akışı kullanır.
    
    Analiz süreci şu adımları içerir:
    1.  **Varlık Çıkarma:** Sorunuzdan yatırım konusu, bölge ve miktar gibi anahtar bilgileri çıkarır.
    2.  **Mevzuat Denetimi:** Yatırımınızın teşvik edilip edilemeyeceğini kontrol eder.
    3.  **Belge Arama (RAG):** İlgili güncel mevzuat metinlerini vektör veritabanından bulur.
    4.  **Analiz ve Sentez:** AI, bulduğu belgeleri ve yatırım türünüzü analiz ederek size özel bir rapor oluşturur.
    """)
    st.warning("Bu rapor ön bilgilendirme amaçlıdır ve yasal tavsiye niteliği taşımaz.") 