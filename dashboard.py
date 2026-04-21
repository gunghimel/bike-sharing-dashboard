# Import libraries yang di butuhkan
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

plt.close('all')

# LOAD DATA yang disini saya menggunakan data yang sudah di bersihkan #
day_df = pd.read_csv("df_day_clean.csv")
hour_df = pd.read_csv("df_hour_clean.csv")

# Memastikan kolom dteday bertipe datetime agar bisa difilter
day_df["dteday"] = pd.to_datetime(day_df["dteday"])
hour_df["dteday"] = pd.to_datetime(hour_df["dteday"])

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

# SIDEBAR (FITUR INTERAKTIF: FILTER TANGGAL)
with st.sidebar:
    st.title("🚴 Bike Sharing Dashboard")
    
    # Mengambil rentang tanggal untuk filter
    min_date = day_df["dteday"].min()
    max_date = day_df["dteday"].max()
    
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# FILTER DATA UTAMA BERDASARKAN INPUT SIDEBAR
main_df_day = day_df[(day_df["dteday"] >= str(start_date)) & 
                     (day_df["dteday"] <= str(end_date))]

main_df_hour = hour_df[(hour_df["dteday"] >= str(start_date)) & 
                      (hour_df["dteday"] <= str(end_date))]

# HEADER
st.title("🚴 Bike Sharing Dashboard")

# OVERVIEW (Menggunakan data yang sudah difilter)
st.subheader("📊 Overview")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Rentals", f"{int(main_df_day['cnt'].sum()):,}")

with col2:
    st.metric("Rata-rata Harian", f"{int(main_df_day['cnt'].mean()):,}")

with col3:
    st.metric("Total Registered", f"{int(main_df_day['registered'].sum()):,}")

# 1. CUACA
st.subheader("🌧️ Pengaruh Cuaca")

weather_usage = main_df_hour.groupby('weathersit')['cnt'].mean().reset_index()
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

hourly_df = create_hourly_df(main_df_hour)
hourly_df = hourly_df.sort_values(by="hr")

sns.set_style("whitegrid")
fig, ax = plt.subplots(figsize=(10, 6))
sns.lineplot(
    data=hourly_df,
    x="hr",
    y="cnt",
    marker="o",
    linewidth=2,
    color="#2E5A88", 
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

grouped = main_df_day.groupby('workingday')['cnt'].sum().reset_index()
label_mapping = {'No': 'Hari Libur', 'Yes': 'Hari Kerja'}
grouped['workingday'] = grouped['workingday'].map(label_mapping)

total = grouped['cnt'].sum()
if total > 0:
    grouped['percentage'] = (grouped['cnt'] / total) * 100
else:
    grouped['percentage'] = 0

colors = ["#D3D3D3", "#2E5A88"]
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(
    data=grouped,
    y='workingday',
    x='cnt',
    hue='workingday',
    palette=colors,
    legend=False,
    ax=ax
)

for i, row in grouped.iterrows():
    ax.text(
        row['cnt'],
        i,
        f" {row['percentage']:.1f}% ({int(row['cnt']):,})",
        va='center',
        fontweight='bold',
        fontsize=11
    )

ax.set_title('Penyewaan Sepeda Lebih Banyak Terjadi pada Hari Kerja', loc='left', fontsize=14, fontweight='bold', pad=20)
ax.set_xlabel(None)
ax.set_ylabel(None)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.get_xaxis().set_visible(False)

st.pyplot(fig)
plt.close(fig)

# 4. USER TYPE
st.subheader("👥 Komposisi Pengguna")

user_df = create_user_df(main_df_day)
colors = ['#D3D3D3', '#2E5A88']
fig, ax = plt.subplots(figsize=(8, 8))
patches, texts, autotexts = ax.pie(
    user_df["count"],
    labels=user_df["user_type"],
    autopct='%1.1f%%',
    startangle=140,
    colors=colors,
    wedgeprops={'edgecolor': 'white', 'linewidth': 2}
)

plt.setp(texts, fontweight='bold', fontsize=12)
plt.setp(autotexts, fontweight='bold', fontsize=12, color='white')
ax.set_title("Mayoritas Kontribusi Berasal dari Pengguna Terdaftar (Registered)", fontsize=16, pad=20)

st.pyplot(fig)
plt.close(fig)

# 5. DISTRIBUSI USAGE
st.subheader("📊 Distribusi Tingkat Penyewaan")

main_df_day['usage_level'] = pd.cut(
    main_df_day['cnt'],
    bins=[0, 2000, 4000, 10000], 
    labels=['Low', 'Medium', 'High']
)

usage_dist = main_df_day['usage_level'].value_counts().reset_index()
usage_dist.columns = ['usage_level', 'count']

usage_dist['usage_level'] = pd.Categorical(
    usage_dist['usage_level'],
    categories=['Low', 'Medium', 'High'],
    ordered=True
)
usage_dist = usage_dist.sort_values('usage_level')

colors = ["#D3D3D3", "#D3D3D3", "#2E5A88"] 
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(
    data=usage_dist,
    x='usage_level',
    y='count',
    hue='usage_level',
    palette=colors, 
    legend=False,
    ax=ax
)

ax.set_title('Distribusi Tingkat penyewaan sepeda', loc='center', fontsize=16, pad=15)
ax.set_xlabel(None) 
ax.set_ylabel('Jumlah Hari', fontsize=12)
ax.tick_params(axis='x', labelsize=12)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

for p in ax.patches:
    ax.annotate(f'{int(p.get_height())}', 
                (p.get_x() + p.get_width() / 2., p.get_height()), 
                ha='center', va='center', 
                xytext=(0, 10), 
                textcoords='offset points',
                fontsize=11,
                fontweight='bold')

st.pyplot(fig)
plt.close(fig)

# INSIGHT
st.subheader("💡 Insight")
st.write(f"Data ditampilkan untuk rentang waktu: **{start_date}** sampai **{end_date}**")
st.write("""
- Penyewaan tertinggi terjadi saat cuaca cerah, dan menurun signifikan pada cuaca buruk.
- Terjadi dua puncak penyewaan: pagi (±08.00) dan sore (±17.00–18.00), menunjukkan pola komuter.
- Sebagian besar penyewaan terjadi pada hari kerja (~70%), dibanding hari libur.
- Pengguna registered mendominasi
- Mayoritas hari memiliki tingkat penyewaan tinggi (High)
""")
