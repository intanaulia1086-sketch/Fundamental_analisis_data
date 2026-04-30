import pandas as pd
import streamlit as st
import plotly.express as px
import datetime

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="E-Commerce Full Report 2017", layout="wide")

# Custom CSS untuk Insight (Tetap sama)
st.markdown("""
    <style>
    .insight-container {
        background-color: #e3f2fd;
        padding: 30px;
        border-radius: 15px;
        border: 2px solid #1976d2;
        margin-top: 40px;
        margin-bottom: 40px;
    }
    .insight-title {
        color: #0d47a1;
        font-weight: bold;
        font-size: 24px;
        margin-bottom: 15px;
    }
    .main { background-color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

# --- LOAD DATA ---
@st.cache_data
def load_data():
    df_q1 = pd.read_csv("main_df_q1.csv")
    df_q2 = pd.read_csv("main_df_q2.csv")
    rfm_df = pd.read_csv("rfm_data.csv")
    df_q1['order_purchase_timestamp'] = pd.to_datetime(df_q1['order_purchase_timestamp'])
    df_q2['order_purchase_timestamp'] = pd.to_datetime(df_q2['order_purchase_timestamp'])
    return df_q1, df_q2, rfm_df

df_q1, df_q2, rfm_df = load_data()

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Filter Data")
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=datetime.date(2017, 1, 1),
        max_value=df_q1["order_purchase_timestamp"].max().date(),
        value=[datetime.date(2017, 1, 1), datetime.date(2017, 12, 31)]
    )

# Filter Logic
f_df_q1 = df_q1[(df_q1["order_purchase_timestamp"].dt.date >= start_date) & (df_q1["order_purchase_timestamp"].dt.date <= end_date)]
f_df_q2 = df_q2[(df_q2["order_purchase_timestamp"].dt.date >= start_date) & (df_q2["order_purchase_timestamp"].dt.date <= end_date)]

# --- HEADER ---
st.title("📊 E-Commerce Public Analysis Dashboard 2017")
st.write(f"Menampilkan analisis data dari periode **{start_date}** hingga **{end_date}**")
st.divider()

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["🛒 Analisis Produk & Kategori", "💳 Analisis Pembayaran", "👥 Analisis RFM"])

with tab1:
    st.header("Analisis Produk & Kategori (Q1)")
    
    # 1. Boxplot
    st.subheader("1. Distribusi Harga Produk")
    fig1 = px.box(f_df_q1, x="price", log_x=True, points=False)
    st.plotly_chart(fig1, use_container_width=True)

    # 2. Kategori Terlaris
    st.subheader("2. 10 Kategori Produk Terlaris")
    # Mengambil kategori, menghitung jumlah, dan mereset index
    top_cat = f_df_q1['product_category_name_english'].value_counts().head(10).reset_index()
    top_cat.columns = ['category_name', 'order_count']
    
    fig2 = px.bar(top_cat, x='order_count', y='category_name', orientation='h', color='order_count', color_continuous_scale='plasma',
                  title="Top 10 Kategori Berdasarkan Jumlah Pesanan")
    fig2.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig2, use_container_width=True)

    # 3. Top Kategori Revenue
    st.subheader("3. Top 10 Kategori Produk Berdasarkan Pendapatan")
    cat_rev = f_df_q1.groupby("product_category_name_english")["price"].sum().sort_values(ascending=False).head(10).reset_index()
    fig3 = px.bar(cat_rev, x="price", y="product_category_name_english", orientation='h', color='price', color_continuous_scale='plasma',
                  title="10 Kategori Penyumbang Pendapatan Terbesar")
    fig3.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig3, use_container_width=True)

    # 4. Tren Bulanan
    st.subheader("4. Tren Pendapatan Bulanan Top 5 Kategori")
    top_5_cat = cat_rev.head(5)["product_category_name_english"].tolist()
    df_multi_q1 = f_df_q1[f_df_q1["product_category_name_english"].isin(top_5_cat)]
    df_multi_q1 = df_multi_q1.groupby(["month", "product_category_name_english"])["price"].sum().reset_index()
    st.plotly_chart(px.line(df_multi_q1, x="month", y="price", color="product_category_name_english", markers=True), use_container_width=True)

with tab2:
    st.header("Analisis Metode Pembayaran (Q2)")
    
    # 1. Boxplot Payment Value
    fig5 = px.box(f_df_q2, x="payment_value", log_x=True, color_discrete_sequence=['#508C9B'])
    st.plotly_chart(fig5, use_container_width=True)

    # 2. Pie Chart
    st.subheader("2. Persentase Metode Pembayaran")
    pay_count = f_df_q2["payment_type"].value_counts().reset_index()
    fig_pie = px.pie(pay_count, values="count", names="payment_type", hole=0.4, 
                     color_discrete_sequence=px.colors.sequential.Plasma_r)
    st.plotly_chart(fig_pie, use_container_width=True)

    # 3. Tren Payment Bulanan
    st.subheader("3. Tren Nilai Pembayaran Bulanan")
    pay_trend = f_df_q2.groupby(["month", "payment_type"])["payment_value"].sum().reset_index()
    st.plotly_chart(px.line(pay_trend, x="month", y="payment_value", color="payment_type", markers=True), use_container_width=True)

with tab3:
    st.header("Analisis Pelanggan (RFM)")
    # Visualisasi RFM disusun kebawah
    for param, title, color_p in zip(["recency", "frequency", "monetary"], 
                                    ["Recency (Days)", "Frequency", "Monetary"], 
                                    ["Bluered", "Magma", "Turbo"]):
        st.subheader(f"Top 5 Pelanggan Berdasarkan {title}")
        top_rfm = rfm_df.sort_values(by=param, ascending=(True if param=="recency" else False)).head(5)
        fig_rfm = px.bar(top_rfm, x="customer_id", y=param, color=param, color_continuous_scale=color_p)
        st.plotly_chart(fig_rfm, use_container_width=True)

# --- BAGIAN INSIGHT (PALING BAWAH & MENCOLOK) ---
st.markdown('<div class="insight-container">', unsafe_allow_html=True)
st.markdown('<p class="insight-title">💡 Kesimpulan & Insight Strategis</p>', unsafe_allow_html=True)

st.markdown("### 🛍️ Kategori & Produk (Q1)")
st.write("""
- **Kategori Unggulan:** Kategori `bed_bath_table` adalah penyumbang revenue tertinggi. Fokus stok harus diarahkan pada kategori ini.
- **Produk Terlaris:** Identifikasi Top 10 Product ID menunjukkan bahwa promosi terpusat pada beberapa item kunci sangat efektif meningkatkan volume order.
- **Harga:** Mayoritas transaksi berada di harga rendah hingga menengah, namun produk premium (outliers) memberikan margin keuntungan yang besar secara sporadis.
""")

st.markdown("### 💳 Metode Pembayaran (Q2)")
st.write("""
- **Dominasi Kartu Kredit:** Kartu Kredit mencakup mayoritas transaksi (>70%). Fasilitas cicilan menjadi daya tarik utama bagi pelanggan.
- **Potensi Revenue:** Nilai transaksi rata-rata tertinggi berasal dari kartu kredit, membuktikan metode ini digunakan untuk belanja barang dengan harga lebih mahal.
- **Tren:** Tren penggunaan tetap stabil mengikuti total penjualan tanpa adanya pergeseran preferensi metode bayar secara mendadak.
""")

st.markdown("### 👥 Segmentasi Pelanggan (RFM)")
st.write("""
- **Customer Retention:** Kita telah berhasil memetakan ID pelanggan yang paling loyal (Frequency) dan paling berharga secara finansial (Monetary).
- **Rekomendasi:** Berikan apresiasi khusus bagi Top 5 pelanggan di kategori Monetary untuk menjaga loyalitas mereka di tahun mendatang.
""")
st.markdown('</div>', unsafe_allow_html=True)

st.caption('Copyright © Intan Aulia Agustina 2026')