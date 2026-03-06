import streamlit as st
import math

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Operator Motor System v2.0", layout="wide")

# --- KONSTANTA EQUILIBRIUM ---
def get_equilibrium(di):
    if di < 100: # Motor Pompa / Kecil
        return {"B": 1.4, "J": 5.0, "eff": 0.70, "cos_phi": 0.75}
    elif di <= 300: # Motor Medium
        return {"B": 1.6, "J": 4.5, "eff": 0.85, "cos_phi": 0.82}
    else: # Motor Besar
        return {"B": 1.7, "J": 3.5, "eff": 0.92, "cos_phi": 0.88}

st.title("⚡ Operator System: Universal Motor Reconstruction")
st.markdown("Sistem pembenah rekonstruksi inti stator berbasis data statis.")
st.markdown("---")

# --- INPUT DATA (SIDEBAR) ---
st.sidebar.header("📥 Data Statis Stator")
phase_type = st.sidebar.selectbox("Tipe Fase", ["3-Phase (Industrial)", "1-Phase (Pump/Home)"])
di = st.sidebar.number_input("Diameter Dalam (mm)", min_value=0.1, value=50.0, step=0.1)
do = st.sidebar.number_input("Diameter Luar (mm)", min_value=0.1, value=90.0, step=0.1)
l_core = st.sidebar.number_input("Panjang Inti (mm)", min_value=0.1, value=40.0, step=0.1)
slots = st.sidebar.number_input("Jumlah Slot (S)", min_value=1, value=24, step=1)

st.sidebar.header("⚙️ Pilihan Modifikasi")
poles = st.sidebar.selectbox("Jumlah Pole (P)", [2, 4, 6], index=0)
v_target = st.sidebar.number_input("Voltase Kerja (V)", value=220)

# --- LOGIKA PERHITUNGAN ---
eq = get_equilibrium(di)
wt_est = (math.pi * di) / (2 * slots)
area_iron = (wt_est * l_core * (slots / poles)) / 1000000 

# Menghitung Fluks & Lilitan
phi = eq["B"] * area_iron
kw = 0.95 
f = 50

if "3-Phase" in phase_type:
    # Rumus 3-Fase
    n_ph = v_target / (4.44 * f * phi * kw)
    turns_per_slot = (n_ph * 3) / slots
    multiplier = math.sqrt(3)
else:
    # Rumus 1-Fase (Pompa)
    # n_ph untuk 1 fase lebih padat
    n_ph = v_target / (4.44 * f * phi * kw)
    turns_per_slot = n_ph / (slots * 0.6) # Asumsi 60% slot untuk Running
    multiplier = 1.0

# Menghitung Watt & Kawat
area_slot = ((math.pi * (do**2 - di**2) / 4) * 0.5) / slots 
fill_factor = 0.40
area_wire = (area_slot * fill_factor) / turns_per_slot
diameter_wire = math.sqrt((4 * area_wire) / math.pi)

current = area_wire * eq["J"]
watt = v_target * current * eq["cos_phi"] * eq["eff"] * multiplier

# --- DISPLAY HASIL ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Hasil Rekonstruksi Utuh")
    st.metric("Lilitan Utama / Slot", f"{int(turns_per_slot)} Lilit")
    st.metric("Diameter Kawat Utama", f"{round(diameter_wire, 2)} mm")
    st.metric("Estimasi Daya (Watt)", f"{round(watt, 1)} W")

with col2:
    st.subheader("🔍 Parameter Equilibrium")
    st.write(f"**Arus Kerja:** {round(current, 2)} A")
    st.write(f"**Target Flux:** {eq['B']} Tesla")
    st.write(f"**Power Factor:** {eq['cos_phi']}")
    
    if "1-Phase" in phase_type:
        st.warning("💡 Tips Pompa: Gunakan kawat bantu (Starting) 1-2 step lebih kecil dari kawat utama.")

# --- VALIDASI KEAMANAN ---
st.divider()
if turns_per_slot > 500:
    st.error("❌ Kawat terlalu halus! Lilitan terlalu banyak untuk ruang slot ini.")
elif diameter_wire > 1.5 and "1-Phase" in phase_type:
    st.info("🛠️ Saran Operator: Gunakan kawat paralel agar lebih mudah digulung di slot kecil.")
else:
    st.success("✅ Sistem Equilibrium: Desain efisien dan aman untuk dieksekusi.")
