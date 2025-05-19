import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from io import BytesIO, StringIO

st.title("📊 Aplikasi Sosiometri Berbasis Excel + Interpretasi Otomatis")

st.markdown("### 📥 1. Unduh Format Excel")
st.download_button("📄 Unduh Format Excel", data="""Nama,Pilihan1,Pilihan2,Pilihan3
Alya,Bima,Citra,Dodi
Bima,Alya,Elsa,
Citra,Bima,Gita,
Dodi,Alya,Citra,Fajar
Elsa,Bima,Citra,
Fajar,Elsa,Gita,
Gita,Citra,Dodi,
""", file_name="format_sosiometri.csv", mime="text/csv")

st.markdown("### 📤 2. Upload Data Excel")
uploaded_file = st.file_uploader("Upload file CSV atau Excel dengan format sesuai", type=["csv", "xlsx"])

def interpretasi_skor(skor):
    if skor == 0:
        return "❗ Terisolasi – Perlu perhatian khusus"
    elif skor <= 2:
        return "⚠️ Sosial Terbatas – Perlu dorongan interaksi"
    elif skor <= 5:
        return "✅ Cukup Sosial"
    elif skor <= 9:
        return "🌟 Populer – Disukai banyak teman"
    else:
        return "🏅 Sangat Populer – Potensial jadi fasilitator"

if uploaded_file:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.markdown("### 👥 Data yang Diunggah")
        st.dataframe(df)

        names = df['Nama'].tolist()
        sosiometri_data = {row['Nama']: [row['Pilihan1'], row['Pilihan2'], row['Pilihan3']] for _, row in df.iterrows()}

        popularitas = {name: 0 for name in names}
        for pilihan in sosiometri_data.values():
            for teman in pilihan:
                if pd.notna(teman) and teman in popularitas:
                    popularitas[teman] += 1

        data_interpretasi = [(nama, skor, interpretasi_skor(skor)) for nama, skor in popularitas.items()]
        df_result = pd.DataFrame(data_interpretasi, columns=["Nama", "Skor Popularitas", "Interpretasi"])
        st.markdown("### 📊 Hasil Popularitas & Interpretasi")
        st.dataframe(df_result.sort_values(by="Skor Popularitas", ascending=False))

        G = nx.DiGraph()
        G.add_nodes_from(names)
        for anak, pilihans in sosiometri_data.items():
            for teman in pilihans:
                if pd.notna(teman) and teman in names:
                    G.add_edge(anak, teman)

        st.markdown("### 🧠 Sosiogram Visual")
        fig, ax = plt.subplots(figsize=(8, 6))
        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True, node_color='lightgreen', edge_color='gray', node_size=2000, font_size=10, arrows=True, ax=ax)
        st.pyplot(fig)

        csv_result = df_result.to_csv(index=False)
        st.download_button("⬇️ Unduh Hasil Popularitas & Interpretasi", data=csv_result, file_name="hasil_sosiometri.csv", mime="text/csv")

    except Exception as e:
        st.error(f"Gagal memproses file: {e}")
