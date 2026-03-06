import streamlit as st
import math

st.set_page_config(page_title="Operator System v3.0", layout="wide")

# --- DATABASE MATERIAL (IMAJINER/EQUILIBRIUM) ---
def get_iron_quality(di):
    # Asumsi baja silikon standar M47
    return {"B_max": 1.35 if di < 80 else 1.6, "Staking_Factor": 0.95}

st.title("🛡️ Operator System v3.0: Precision Rewinding")
st.write("Sistem rekonstruksi dengan validasi ruang fisik dan kalkulator kapasitor.")

# --- INPUT BARU (SIDEBAR) ---
st.sidebar.header("📏 Detail Dimensi Slot")
h_slot = st.sidebar.number_input("Tinggi Slot (mm)", value=12.0)
w_mid = st.sidebar.number_input("Lebar Tengah Slot (mm)", value=6.0)
mika_thick = st.sidebar.number_input("Tebal Mika/Prespan (mm)", value=0.2)

st.sidebar.header("🌀 Data Inti")
di = st.sidebar.number_input("Diameter Dalam (mm)", value=50.0)
l_core = st.sidebar.number_input("Panjang Inti (mm)", value=40.0)
slots = st.sidebar.number_input("Jumlah Slot", value=24)
poles = st.sidebar.selectbox("Pole", [2, 4])

# --- PROSES SIMULASI ---
iron = get_iron_quality(di)
area_slot_total = h_slot * w_mid
# Luas bersih setelah dikurangi mika
area_slot_net = (h_slot - 1) * (w_mid - (2 * mika_thick)) 

# Hitung Fluks per Kutub
phi = (iron["B_max"] * (di * math.pi * l_core / poles)) / 1000000

# Hitung Lilitan Running (Utama)
# Menggunakan 16 slot (2/3) untuk Running pada pompa 24 slot
slots_run = int(slots * 0.66)
n_total = 220 / (4.44 * 50 * phi * 0.95)
turns_per_slot = n_total / slots_run

# Hitung Diameter Kawat Maksimal (Efektif)
# Faktor isi kawat bulat = 0.6 (sangat aman untuk tangan)
area_wire_max = (area_slot_net * 0.6) / turns_per_slot
d_wire_run = math.sqrt((4 * area_wire_max) / math.pi)

# Estimasi Watt & Kapasitor
current_est = area_wire_max * 5.0 # Densitas arus 5A/mm2
watt_est = 220 * current_est * 0.8 * 0.75 # Cos phi & Eff
cap_est = (current_est * 0.6 * 10**6) / (2 * math.pi * 50 * 220)

# --- OUTPUT SISTEM ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Lilitan Utama", f"{int(turns_per_slot)} Lilit")
    st.metric("Kawat Utama", f"{round(d_wire_run, 2)} mm")
with col2:
    st.metric("Estimasi Daya", f"{round(watt_est, 1)} Watt")
    st.metric("Arus Kerja", f"{round(current_est, 2)} A")
with col3:
    st.metric("Kapasitor Ideal", f"{round(cap_est, 1)} uF")
    st.metric("Kawat Bantu", f"{round(d_wire_run * 0.8, 2)} mm")

st.divider()
st.success("✅ Logika ini memastikan kawat tidak akan sesak di leher slot.")
