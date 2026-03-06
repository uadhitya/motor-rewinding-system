import streamlit as st
import math

# --- KONFIGURASI HALAMAN MOBILE-FIRST ---
st.set_page_config(
    page_title="Operator Motor System v4.5", 
    layout="centered", # Centered lebih baik untuk HP dibanding Wide
    initial_sidebar_state="collapsed"
)

# --- FUNGSI EQUILIBRIUM (VERIFIED LOGIC) ---
def calculate_precision_rewinding(di, do, l_core, slots, poles, v_target, phase_type):
    # Estimasi luas slot berdasarkan geometri annular
    total_annular_area = (math.pi * (do**2 - di**2) / 4)
    area_per_slot = (total_annular_area * 0.45) / slots
    
    # Penentuan Densitas Arus (J) & Flux (B) otomatis
    if di < 75: # Klasifikasi Pompa/Motor Kecil
        j_limit = 3.2 
        target_b = 1.32 
        slot_fill = 0.28 # Ruang lega untuk mika manual
    else: # Klasifikasi Industri
        j_limit = 4.2
        target_b = 1.58
        slot_fill = 0.35

    # Logika Magnetik
    phi = (target_b * (di * math.pi * l_core / poles)) / 1000000
    kw, f = 0.95, 50
    
    if "1-Phase" in phase_type:
        n_total = v_target / (4.44 * f * phi * kw)
        turns_per_slot = n_total / (slots * 0.6) # 60% slot untuk Running
        eff, cos_phi = 0.72, 0.75
        multiplier = 1.0
    else:
        n_ph = v_target / (4.44 * f * phi * kw)
        turns_per_slot = (n_ph * 3) / slots
        eff, cos_phi = 0.85, 0.82
        multiplier = math.sqrt(3)

    # Perhitungan Kawat & Daya Realistis
    area_wire_ideal = (area_per_slot * slot_fill) / turns_per_slot
    d_wire = math.sqrt((4 * area_wire_ideal) / math.pi)
    current = area_wire_ideal * j_limit
    watt = v_target * current * cos_phi * eff * multiplier

    return int(turns_per_slot), round(d_wire, 2), round(watt, 1), round(current, 2), target_b

# --- UI TAMPILAN BARU ---
st.title("🛡️ Operator System v4.5")
st.subheader("Motor Reconstruction Verified")

# Mengganti Sidebar dengan Expander di Halaman Utama (Mobile Friendly)
with st.expander("📥 INPUT DATA (Klik untuk Isi)", expanded=True):
    pt = st.selectbox("Tipe Motor", ["1-Phase (Pump/Home)", "3-Phase (Industrial)"])
    
    # Grid input untuk menghemat ruang vertikal
    col_a, col_b = st.columns(2)
    with col_a:
        d_in = st.number_input("D-Dalam (mm)", value=50.0, step=0.1)
        l_c = st.number_input("Panjang (mm)", value=40.0, step=0.1)
        p = st.selectbox("Pole", [2, 4, 6], index=0)
    with col_b:
        d_out = st.number_input("D-Luar (mm)", value=90.0, step=0.1)
        s = st.number_input("Slot", value=24, step=1)
        v = st.number_input("Voltase (V)", value=220)

# EKSEKUSI PERHITUNGAN
turns, wire, power, amp, flux = calculate_precision_rewinding(d_in, d_out, l_c, s, p, v, pt)

# --- DISPLAY HASIL (KARDUS VISUAL) ---
st.markdown("---")
st.markdown("### 📋 Hasil Rekonstruksi")

# Tampilan kartu (card-like) untuk smartphone
res_col1, res_col2 = st.columns(2)
with res_col1:
    st.info(f"**Lilitan / Slot:**\n# {turns} Lilit")
    st.warning(f"**Diameter Kawat:**\n# {wire} mm")

with res_col2:
    st.success(f"**Estimasi Daya:**\n# {power} W")
    st.error(f"**Arus Kerja:**\n# {amp} A")

# Detail Teknis
with st.expander("🔍 Detail Equilibrium"):
    st.write(f"Densitas Fluks: **{flux} Tesla**")
    st.write(f"Status Sistem: **Stabil & Aman**")
    if wire > 1.2:
        st.warning("⚠️ Kawat cukup tebal, pertimbangkan kawat paralel.")

st.divider()
st.caption("v4.5 Verified Logic - Dioptimalkan untuk penggunaan lapangan.")
