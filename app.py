import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

st.set_page_config(page_title="Google Play Store Analysis", layout="wide")

# Load dan bersihkan data
@st.cache_data
def load_clean_data():
    df = pd.read_csv("googleplaystore.csv")

    # Drop baris dengan rating kosong
    df = df.dropna(subset=["Rating"])
    df = df[df["Rating"] <= 5]  # valid rating

    # Bersihkan kolom Price
    df["Price"] = df["Price"].replace("Free", "$0")
    df["Price"] = df["Price"].str.replace("$", "", regex=False)
    df["Price"] = pd.to_numeric(df["Price"], errors="coerce").fillna(0)

    # Bersihkan kolom Size
    def convert_size(x):
        if x == "Varies with device":
            return np.nan
        elif "M" in x:
            return float(x.replace("M", ""))
        elif "k" in x:
            return float(x.replace("k", "")) / 1024
        else:
            return np.nan

    df["Size_MB"] = df["Size"].apply(convert_size)

    # Bersihkan kolom Installs
    df["Installs"] = df["Installs"].str.replace("[+,]", "", regex=True)
    df["Installs"] = pd.to_numeric(df["Installs"], errors="coerce")

    df = df.dropna(subset=["Size_MB", "Installs"])

    return df

df = load_clean_data()

# Judul aplikasi
st.title("📱 Google Play Store App Analysis")
st.markdown("Analisis lanjutan terhadap dataset Google Play Store: rating, harga, ukuran, dan jumlah unduhan.")

# Sidebar filter
st.sidebar.header("🔍 Filter")
categories = ["All"] + sorted(df["Category"].unique())
selected_category = st.sidebar.selectbox("Pilih Kategori", categories)
min_rating = st.sidebar.slider("Minimum Rating", 0.0, 5.0, 3.5, 0.1)

filtered_df = df.copy()
if selected_category != "All":
    filtered_df = filtered_df[filtered_df["Category"] == selected_category]
filtered_df = filtered_df[filtered_df["Rating"] >= min_rating]

# Statistik Ringkas
st.subheader("📊 Statistik Ringkas")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Jumlah Aplikasi", len(filtered_df))
col2.metric("Rata-rata Rating", f"{filtered_df['Rating'].mean():.2f}")
col3.metric("Harga Tertinggi ($)", f"{filtered_df['Price'].max():.2f}")
col4.metric("Rata-rata Ukuran (MB)", f"{filtered_df['Size_MB'].mean():.2f}")

# Dataframe hasil filter
with st.expander("📂 Lihat Data Terfilter"):
    st.dataframe(filtered_df[['App', 'Category', 'Rating', 'Price', 'Size_MB', 'Installs']].reset_index(drop=True))

# Visualisasi Rating
st.subheader("📈 Distribusi Rating Aplikasi")
fig1, ax1 = plt.subplots()
sns.histplot(filtered_df["Rating"], bins=20, kde=True, ax=ax1)
st.pyplot(fig1)

# Visualisasi Harga
st.subheader("💵 Distribusi Harga Aplikasi (Non-Gratis)")
paid_apps = filtered_df[filtered_df["Price"] > 0]
if not paid_apps.empty:
    fig2, ax2 = plt.subplots()
    sns.histplot(paid_apps["Price"], bins=30, ax=ax2)
    ax2.set_xlim(0, paid_apps["Price"].quantile(0.95))  # Hindari outlier ekstrem
    st.pyplot(fig2)
else:
    st.info("Tidak ada aplikasi berbayar dalam filter saat ini.")

# Visualisasi Ukuran
st.subheader("📦 Distribusi Ukuran Aplikasi (MB)")
fig3, ax3 = plt.subplots()
sns.histplot(filtered_df["Size_MB"], bins=30, ax=ax3, color="green")
st.pyplot(fig3)

# Visualisasi Installs
st.subheader("⬇️ Distribusi Jumlah Unduhan")
fig4, ax4 = plt.subplots()
sns.histplot(filtered_df["Installs"], bins=30, ax=ax4, color="orange")
ax4.set_xscale("log")
ax4.set_xlabel("Installs (log scale)")
st.pyplot(fig4)

# Aplikasi paling populer
st.subheader("🏆 Aplikasi Paling Banyak Diunduh")
top_installs = filtered_df.sort_values(by="Installs", ascending=False).head(10)
st.dataframe(top_installs[['App', 'Category', 'Installs', 'Rating', 'Price']])
