import streamlit as st
import math

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Operator Motor System v1.0", layout="wide")

# --- KONSTANTA EQUILIBRIUM (Nilai Penyeimbang Imajiner) ---
def get_equilibrium(di):
    if di < 150: # Motor Kecil
        return {"B": 1.4, "J": 5.5, "eff": 0.75, "cos_phi": 0.75}
    elif di <= 300: # Motor Medium
        return {"B": 1.6, "J": 4.5, "eff": 0.85, "cos_phi": 0.82}
    else: # Motor Besar
        return {"B": 1.7, "J": 3.5, "eff": 0.92, "cos_phi": 0.88}

# --- HEADER APLIKASI ---
st.title("⚡ Operator System: Motor Rewinding Reconstruction")
st.markdown("---")

# --- INPUT DATA (SIDEBAR) ---
st.sidebar.header("📥 Input Data Statis Stator")
di = st.sidebar.number_input("Diameter Dalam (mm)", min_value=0.0, value=100.0, step=0.1)
do = st.sidebar.number_input("Diameter Luar (mm)", min_value=0.0, value=160.0, step=0.1)
l_core = st.sidebar.number_input("Panjang Inti (mm)", min_value=0.0, value=120.0, step=0.1)
slots = st.sidebar.number_input("Jumlah Slot (S)", min_value=1, value=36, step=1)

st.sidebar.header("⚙️ Pilihan Modifikasi")
poles = st.sidebar.selectbox("Jumlah Pole (P)", [2, 4, 6, 8], index=1)
v_target = st.sidebar.number_input("Voltase Kerja (V)", value=380)

# --- LOGIKA PENYEIMBANG (EQUILIBRIUM) ---
eq = get_equilibrium(di)

# --- PERHITUNGAN TEKNIS ---
# 1. Menghitung Luas Area Gigi (Estimasi jika kosong)
wt_est = (math.pi * di) / (2 * slots) # Equilibrium tooth width
area_iron = (wt_est * l_core * (slots / poles)) / 1000000 # Area efektif per kutub (m^2)

# 2. Menghitung Fluks dan Lilitan
phi = eq["B"] * area_iron
# Rumus: N_ph = V / (4.44 * f * Phi * kw)
kw = 0.95 # Winding factor standar
f = 50
n_ph = v_target / (4.44 * f * phi * kw)
turns_per_slot = (n_ph * 3) / slots # Estimasi lilitan per slot (3 fase)

# 3. Menghitung Watt dan Arus
# Luas Slot (Estimasi)
area_slot = ((math.pi * (do**2 - di**2) / 4) * 0.5) / slots 
area_wire = (area_slot * 0.4) / turns_per_slot # Fill factor 40%
diameter_wire = math.sqrt((4 * area_wire) / math.pi)

current = area_wire * eq["J"]
watt = math.sqrt(3) * v_target * current * eq["cos_phi"] * eq["eff"]

# --- DISPLAY HASIL ---
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Jumlah Lilitan/Slot", f"{int(turns_per_slot)} Lilit")
    st.metric("Diameter Kawat", f"{round(diameter_wire, 2)} mm")

with col2:
    st.metric("Estimasi Daya (Watt)", f"{round(watt, 0)} W")
    st.metric("Arus Efektif (A)", f"{round(current, 2)} A")

with col3:
    st.metric("Target Flux (B)", f"{eq['B']} Tesla")
    st.metric("Power Factor (Cos φ)", eq["cos_phi"])

# --- SAFETY GUARD (VALIDASI) ---
st.markdown("---")
st.subheader("🛡️ Validasi Keamanan Sistem")

if turns_per_slot < 1:
    st.error("❌ ERROR: Geometri tidak memungkinkan untuk lilitan ini. Periksa kembali diameter!")
elif diameter_wire < 0.1:
    st.warning("⚠️ PERINGATAN: Kawat terlalu tipis, risiko putus tinggi.")
else:
    st.success("✅ Equilibrium Tercapai: Desain berjalan sesuai kapasitas fisik inti.")

# Informasi Panas
heat_loss = 3 * (current**2) * 0.5 # Estimasi rugi tembaga sederhana
st.info(f"📊 Estimasi Panas: {round(heat_loss, 2)} Watt (Losses). Pastikan pendinginan berfungsi!")
