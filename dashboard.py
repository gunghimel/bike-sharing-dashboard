# Import libraries yang di butuhkan
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

plt.close('all')

# LOAD DATA yang disini saya menggunakan data yang sudah di bersihkan #

day_df = pd.read_csv("df_day_clean.csv")
hour_df = pd.read_csv("df_hour_clean.csv")

# HELPER FUNCTIONS

def create_weather_df(df):
    return df.groupby("weathersit")["cnt"].mean().reset_index()

def create_hourly_df(df):
    return df.groupby("hr")["cnt"].mean().reset_index()

def create_workingday_df(df):
    return df.groupby("workingday")["cnt"].sum().reset_index()

def create_user_df(df):
    return pd.DataFrame({
        "user_type": ["Casual", "Registered"],
        "count": [df["casual"].sum(), df["registered"].sum()]
    })

# SIDEBAR

with st.sidebar:
    st.title("🚴 Bike Sharing Dashboard")
    st.write("Analisis Peminjaman Sepeda")

# HEADER

st.title("🚴 Bike Sharing Dashboard")

# OVERVIEW

st.subheader("📊 Overview")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Rentals", f"{int(day_df['cnt'].sum()):,}")

with col2:
    st.metric("Rata-rata Harian", f"{int(day_df['cnt'].mean()):,}")

with col3:
    st.metric("Total Registered", f"{int(day_df['registered'].sum()):,}")

# 1. CUACA

st.subheader("🌧️ Pengaruh Cuaca")

weather_usage = hour_df.groupby('weathersit')['cnt'].mean().reset_index()

weather_usage = weather_usage.sort_values(by='cnt')

fig, ax = plt.subplots(figsize=(8,5))

sns.barplot(
    data=weather_usage,
    x='weathersit',
    y='cnt',
    ax=ax
)

ax.set_ylim(0, 250)
ax.set_title('Rata-rata Penyewaan Sepeda Berdasarkan Kondisi Cuaca')
ax.set_xlabel('Kondisi Cuaca')
ax.set_ylabel('Rata-rata Jumlah Penyewaan')

plt.xticks(rotation=30)

st.pyplot(fig)
plt.close(fig)

# 2. POLA JAM

st.subheader("⏰ Pola Peminjaman per Jam")

hourly_df = create_hourly_df(hour_df)

hourly_df = hourly_df.sort_values(by="hr")

sns.set_style("whitegrid")

fig, ax = plt.subplots(figsize=(10, 6))

sns.lineplot(
    data=hourly_df,
    x="hr",
    y="cnt",
    marker="o",
    linewidth=2,
    color="#2E7D32", 
    ax=ax
)

ax.set_ylim(0, 500)
ax.set_xticks(range(0, 24)) 
ax.set_title('Rata-rata Penyewaan Sepeda per Jam', fontsize=15)
ax.set_xlabel('Jam (00:00 - 23:00)', fontsize=12)
ax.set_ylabel('Rata-rata Jumlah Penyewaan', fontsize=12)

st.pyplot(fig)
plt.close(fig)

# 3. WORKING DAY

st.subheader("📅 Working Day vs Holiday")

grouped = day_df.groupby('workingday')['cnt'].sum().reset_index()

label_mapping = {
    'No': 'Hari Libur',
    'Yes': 'Hari Kerja'
}

grouped['workingday'] = grouped['workingday'].map(label_mapping)

total = grouped['cnt'].sum()
grouped['percentage'] = (grouped['cnt'] / total) * 100

fig, ax = plt.subplots(figsize=(8,5))

sns.barplot(
    data=grouped,
    y='workingday',
    x='cnt',
    hue='workingday',
    palette=['#ff9999', '#66b3ff'],
    legend=False,
    ax=ax
)

for i, row in grouped.iterrows():
    ax.text(
        row['cnt'],
        i,
        f" {row['percentage']:.1f}%\n({int(row['cnt']):,})",
        va='center'
    )

ax.set_title('Total Penyewaan Sepeda\nHari Kerja vs Hari Libur')
ax.set_xlabel('Total Penyewaan')
ax.set_ylabel('Tipe Hari')

ax.set_xlim(0, grouped['cnt'].max() * 1.15)

st.pyplot(fig)
plt.close(fig)

# 4. USER TYPE

st.subheader("👥 Komposisi Pengguna")

user_df = create_user_df(day_df)

colors = ['#ff9999', '#66b3ff']

explode = (0.1, 0) 

fig, ax = plt.subplots(figsize=(8, 8))

patches, texts, autotexts = ax.pie(
    user_df["count"],
    labels=user_df["user_type"],
    autopct='%1.1f%%',
    startangle=90,
    colors=colors,
    explode=explode,
    wedgeprops={'edgecolor': 'white', 'linewidth': 2}
)

plt.setp(texts, fontweight='bold', fontsize=12)
plt.setp(autotexts, fontweight='bold', fontsize=12)

ax.set_title("Proporsi Kontribusi Pengguna: Casual vs Registered", fontsize=14, pad=20)

st.pyplot(fig)
plt.close(fig)

# 5. DISTRIBUSI USAGE

st.subheader("📊 Distribusi Tingkat Penyewaan")

day_df['usage_level'] = pd.cut(
    day_df['cnt'],
    bins=[0, 2000, 4000, 7000],
    labels=['Low', 'Medium', 'High']
)

usage_dist = day_df['usage_level'].value_counts().reset_index()
usage_dist.columns = ['usage_level', 'count']

usage_dist['usage_level'] = pd.Categorical(
    usage_dist['usage_level'],
    categories=['Low', 'Medium', 'High'],
    ordered=True
)
usage_dist = usage_dist.sort_values('usage_level')

fig, ax = plt.subplots(figsize=(8,5))

sns.barplot(
    data=usage_dist,
    x='usage_level',
    y='count',
    hue='usage_level',
    palette='viridis',
    legend=False,
    ax=ax
)

ax.set_title('Distribusi Tingkat Penyewaan Sepeda')
ax.set_xlabel('Kategori Penggunaan')
ax.set_ylabel('Jumlah Hari')

st.pyplot(fig)
plt.close(fig)

# INSIGHT

st.subheader("💡 Insight")

st.write("""
- Cuaca cerah memiliki peminjaman tertinggi
- Pola jam menunjukkan aktivitas komuter
- Hari kerja memiliki total peminjaman lebih tinggi
- Pengguna registered mendominasi
- Mayoritas hari memiliki tingkat penyewaan tinggi (High)
""")