import streamlit as st
import json

# Sayfa Ayarları
st.set_page_config(page_title="Almanca JSON Yöneticisi", page_icon="🇩🇪", layout="wide")

st.title("A1 Almanca Kelime Seti Yöneticisi 🇩🇪🇹🇷")
st.markdown("Bu araç ile mevcut 246 kelimelik veri setinizi kolayca 1500 kelimeye çıkarabilirsiniz. JSON dosyanızı yükleyin, form ile kelimeleri ekleyin ve indirin.")

# Session State ile veriyi hafızada tutma
if 'data' not in st.session_state:
    st.session_state.data = None

# 1. JSON Yükleme Alanı
if st.session_state.data is None:
    uploaded_file = st.file_uploader("Mevcut 'words.json' dosyanızı yükleyin", type=["json"])
    if uploaded_file is not None:
        try:
            st.session_state.data = json.load(uploaded_file)
            st.success("JSON başarıyla yüklendi!")
            st.rerun()
        except Exception as e:
            st.error(f"Dosya okuma hatası: {e}")

# Veri yüklendikten sonra gösterilecek arayüz
if st.session_state.data is not None:
    data = st.session_state.data
    
    # Sidebar - İstatistikler
    st.sidebar.header("📊 İstatistikler")
    # Toplam kelime sayısını anlık hesapla
    total_words = sum(len(cat.get("words", [])) for cat in data.get("categories", []))
    # Meta'daki total'i güncelle
    data["meta"]["total"] = total_words
    
    st.sidebar.metric("Toplam Kelime", total_words)
    st.sidebar.metric("Kategori Sayısı", len(data.get("categories", [])))
    
    if st.sidebar.button("Farklı bir JSON yükle"):
        st.session_state.data = None
        st.rerun()

    # Sekmeler
    tab1, tab2, tab3 = st.tabs(["➕ Kelime Ekle", "📂 Kategori Ekle", "📥 Veriyi İndir / Gör"])

    # --- SEKME 1: KELİME EKLE ---
    with tab1:
        st.subheader("Yeni Kelime Ekle")
        # Mevcut kategorileri listele
        category_dict = {f"{c['emoji']} {c['name']}": c["id"] for c in data["categories"]}
        selected_cat_label = st.selectbox("Eklenecek Kategoriyi Seçin:", list(category_dict.keys()))
        selected_cat_id = category_dict[selected_cat_label]

        with st.form("add_word_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                de = st.text_input("Almanca Kelime (de) *", placeholder="örn: der Apfel")
                tr = st.text_input("Türkçe Anlamı (tr) *", placeholder="örn: elma")
                artikel = st.selectbox("Artikel", ["Yok (null)", "der", "die", "das"])
                plural = st.text_input("Çoğul Hali (plural)", placeholder="örn: die Äpfel (Yoksa boş bırakın)")
                word_type = st.selectbox("Kelime Türü (type)", ["nomen", "verb", "adjektiv", "adverb", "pronomen", "praeposition", "konjunktion", "ausruf", "phrase"])
                type_tr = st.text_input("Tür Türkçe Karşılığı (type_tr)", placeholder="örn: isim, fiil, sıfat...")
            
            with col2:
                level = st.selectbox("Seviye", ["A1", "A2", "B1", "B2"])
                example_de = st.text_area("Örnek Cümle (Almanca)", placeholder="Ich esse einen Apfel.")
                example_tr = st.text_area("Örnek Cümle (Türkçe)", placeholder="Bir elma yiyorum.")
                tip = st.text_area("İpucu / Not (tip)", placeholder="Bulmaca ipucu veya kullanım notu...")
                related = st.text_input("İlgili Kelimeler (Virgülle ayırın)", placeholder="Essen, trinken, Obst")

            submit_btn = st.form_submit_button("Kelimeyi JSON'a Ekle")
            
            if submit_btn:
                if de and tr:
                    # Yeni kelime objesini senin şemana göre oluştur
                    new_word = {
                        "de": de.strip(),
                        "tr": tr.strip(),
                        "artikel": None if artikel == "Yok (null)" else artikel,
                        "plural": plural.strip() if plural else None,
                        "type": word_type,
                        "type_tr": type_tr.strip(),
                        "level": level,
                        "example_tr": example_tr.strip() if example_tr else None,
                        "example_de": example_de.strip() if example_de else None,
                        "tip": tip.strip() if tip else None,
                        "related": [r.strip() for r in related.split(",")] if related else []
                    }
                    
                    # Seçilen kategoriye ekle
                    for cat in st.session_state.data["categories"]:
                        if cat["id"] == selected_cat_id:
                            cat["words"].append(new_word)
                            break
                            
                    st.success(f"✅ '{de}' kelimesi başarıyla '{selected_cat_label}' kategorisine eklendi!")
                else:
                    st.error("⚠️ Lütfen en azından Almanca ve Türkçe kelime alanlarını doldurun.")

    # --- SEKME 2: KATEGORİ EKLE ---
    with tab2:
        st.subheader("Yeni Kategori Ekle")
        with st.form("add_cat_form", clear_on_submit=True):
            cat_id = st.text_input("Kategori ID (Boşluksuz, küçük harf)*", placeholder="örn: tiere, natur, stadt")
            cat_name = st.text_input("Kategori Adı (Görünecek ad)*", placeholder="örn: Hayvanlar")
            cat_emoji = st.text_input("Emoji", placeholder="örn: 🐾")
            
            cat_submit = st.form_submit_button("Kategoriyi Kaydet")
            if cat_submit:
                if cat_id and cat_name:
                    new_cat = {
                        "id": cat_id.strip(),
                        "name": cat_name.strip(),
                        "emoji": cat_emoji.strip(),
                        "words": []
                    }
                    st.session_state.data["categories"].append(new_cat)
                    st.success(f"✅ '{cat_name}' kategorisi oluşturuldu!")
                else:
                    st.error("⚠️ ID ve Kategori Adı zorunludur.")

    # --- SEKME 3: İNDİR VE GÖRÜNTÜLE ---
    with tab3:
        st.subheader("Güncel JSON Çıktısı")
        st.markdown("Yaptığınız eklemeler sonucunda oluşan güncel JSON dosyasını buradan indirebilirsiniz.")
        
        # JSON'u String formatına çevir (Türkçe karakterlerin bozulmaması için ensure_ascii=False)
        json_string = json.dumps(st.session_state.data, ensure_ascii=False, indent=2)
        
        st.download_button(
            label="📥 Güncel words.json Dosyasını İndir",
            data=json_string,
            file_name="words_v2.json",
            mime="application/json"
        )
        
        with st.expander("JSON Kodunu İncele", expanded=False):
            st.json(st.session_state.data)
