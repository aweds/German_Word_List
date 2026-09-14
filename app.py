import streamlit as st
import json
import pandas as pd
import io

st.set_page_config(page_title="Almanca JSON Yöneticisi", page_icon="🇩🇪", layout="wide")
st.title("A1 Almanca Kelime Seti Yöneticisi 🇩🇪🇹🇷")

if 'data' not in st.session_state:
    st.session_state.data = None

if st.session_state.data is None:
    uploaded_file = st.file_uploader("Mevcut 'words.json' dosyanızı yükleyin", type=["json"])
    if uploaded_file is not None:
        st.session_state.data = json.load(uploaded_file)
        st.rerun()

if st.session_state.data is not None:
    data = st.session_state.data
    
    total_words = sum(len(cat.get("words", [])) for cat in data.get("categories", []))
    data["meta"]["total"] = total_words
    
    st.sidebar.metric("Toplam Kelime", total_words)
    if st.sidebar.button("Farklı bir JSON yükle"):
        st.session_state.data = None
        st.rerun()

    category_dict = {f"{c['emoji']} {c['name']}": c["id"] for c in data["categories"]}
    
    # 4 Sekmeli Yeni Yapı
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Tekli Ekle", "⚡ Hızlı Yapıştır (Toplu)", "📊 Excel/CSV Yükle", "📥 İndir"])

    # SEKME 1: Tekli Ekle (Eski sistemin aynısı - basitleştirilmiş)
    with tab1:
        st.write("Manuel olarak tek kelime ekleyin.")
        # ... (Önceki tekli ekleme formu buraya eklenebilir, kalabalık yapmaması için gizlendi)
        st.info("Toplu ekleme yöntemleri için diğer sekmelere geçin.")

    # SEKME 2: Hızlı Yapıştır (Yapay Zeka veya Metin formatı için)
    with tab2:
        st.markdown("**Format:** `Almanca; Türkçe; Artikel; Çoğul; Tür` (Her kelime yeni bir satırda olmalı)")
        selected_cat_paste = st.selectbox("Eklenecek Kategori:", list(category_dict.keys()), key="paste_cat")
        
        bulk_text = st.text_area("Kelimeleri Buraya Yapıştırın", height=200, 
                                 placeholder="Apfel; elma; der; Äpfel; nomen\ntrinken; içmek; null; null; verb")
        
        if st.button("Toplu İşle ve Ekle"):
            added_count = 0
            for line in bulk_text.split('\n'):
                if not line.strip(): continue
                parts = [p.strip() if p.strip() not in ["null", "Yok", "-", ""] else None for p in line.split(';')]
                
                if len(parts) >= 2:
                    new_word = {
                        "de": parts[0], "tr": parts[1],
                        "artikel": parts[2] if len(parts)>2 else None,
                        "plural": parts[3] if len(parts)>3 else None,
                        "type": parts[4] if len(parts)>4 else "nomen",
                        "type_tr": None, "level": "A1",
                        "example_tr": None, "example_de": None, "tip": None, "related": []
                    }
                    for cat in st.session_state.data["categories"]:
                        if cat["id"] == category_dict[selected_cat_paste]:
                            cat["words"].append(new_word)
                            added_count += 1
                            break
            st.success(f"✅ {added_count} kelime başarıyla eklendi!")

    # SEKME 3: Excel / CSV Yükleme
    with tab3:
        st.write("Sütun başlıkları şu şekilde olmalı: `de, tr, artikel, plural, type, type_tr, example_de, example_tr, tip`")
        selected_cat_csv = st.selectbox("Eklenecek Kategori:", list(category_dict.keys()), key="csv_cat")
        uploaded_csv = st.file_uploader("Excel veya CSV dosyanızı yükleyin", type=["csv", "xlsx"])
        
        if uploaded_csv is not None:
            if st.button("Dosyadaki Kelimeleri Ekle"):
                df = pd.read_csv(uploaded_csv) if uploaded_csv.name.endswith('.csv') else pd.read_excel(uploaded_csv)
                df = df.where(pd.notnull(df), None) # NaN değerleri None (null) yap
                
                added_csv_count = 0
                for _, row in df.iterrows():
                    if pd.notna(row.get('de')) and pd.notna(row.get('tr')):
                        new_word = {
                            "de": str(row.get('de')), "tr": str(row.get('tr')),
                            "artikel": row.get('artikel'), "plural": row.get('plural'),
                            "type": row.get('type', 'nomen'), "type_tr": row.get('type_tr'),
                            "level": "A1", "example_tr": row.get('example_tr'),
                            "example_de": row.get('example_de'), "tip": row.get('tip'), "related": []
                        }
                        for cat in st.session_state.data["categories"]:
                            if cat["id"] == category_dict[selected_cat_csv]:
                                cat["words"].append(new_word)
                                added_csv_count += 1
                                break
                st.success(f"✅ Excel'den {added_csv_count} kelime eklendi!")

    # SEKME 4: İndir
    with tab4:
        json_string = json.dumps(st.session_state.data, ensure_ascii=False, indent=2)
        st.download_button(label="📥 Güncel words.json Dosyasını İndir", data=json_string, file_name="words_v2.json", mime="application/json")
