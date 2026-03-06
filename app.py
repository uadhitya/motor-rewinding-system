import streamlit as st
import math

st.set_page_config(page_title="Operator System v7.1", layout="centered")

def calculate_system(di, do, l_c, s, v, pt):
    # Luas Slot Estimasi (45% dari luas annular)
    area_slot_total = ((math.pi * (do**2 - di**2) / 4) * 0.45) / s
    
    if "1-Phase" in pt:
        # --- LOGIKA JUJUR POMPA AIR (Standard Bengkel) ---
        # Baseline lilitan agar induktansi cukup menahan 220V tanpa panas
        tr = 55 if di < 60 else 42
        ts = int(tr * 1.2)
        
        # Fill Factor 22% (Kawat longgar, mudah masuk)
        dr = math.sqrt((4 * (area_slot_total * 0.22) / tr) / math.pi)
        ds = dr * 0.8
        
        # Estimasi Watt Realistis
        pw = (di * l_c * 0.08) * 220 * 0.01 # Rumus empiris kapasitas besi
        pitch = "1-6, 1-8, 1-10, 1-12 (Konsentris)"
        return tr, round(dr, 2), ts, round(ds, 2), round(pw, 1), pitch
    
    else:
        # --- LOGIKA INDUSTRI 3-PHASE (Standard Efisiensi) ---
        phi = (1.45 * (di * math.pi * l_c / 4)) / 1000000 # 4-Pole Default
        n_ph = v / (4.44 * 50 * phi * 0.95)
        tr_3p = int((n_ph * 3) / s)
        
        # Fill Factor 32% (Motor industri lebih padat)
        dr_3p = math.sqrt((4 * (area_slot_total * 0.32) / tr_3p) / math.pi)
        
        # Watt 3-Phase
        pw_3p = math.sqrt(3) * v * (dr_3p**2 * 4) * 0.8
        return tr_3p, round(dr_3p, 2), 0, 0, round(pw_3p, 1), "1-10, 1-12 (Tumpuk/Lap)"

# --- ANTARMUKA MOBILE ---
st.title("🛡️ Operator System v7.1")
st.caption("Sistem Rekonstruksi Final: Logika Lapangan & Industri")

with st.form("main_form"):
    pt = st.selectbox("Mode Motor", ["1-Phase (Pompa Air)", "3-Phase (Industrial)"])
    c1, c2 = st.columns(2)
    d_in = c1.number_input("D-Dalam (mm)", value=50.0)
    d_out = c2.number_input("D-Luar (mm)", value=90.0)
    l_core = c1.number_input("Panjang (mm)", value=40.0)
    slots = c2.number_input("Slot", value=24)
    volt = st.number_input("Volt (V)", value=220)
    submit = st.form_submit_button("EKSEKUSI REKONSTRUKSI")

if submit:
    tr, dr, ts, ds, pw, pitch = calculate_system(d_in, d_out, l_core, slots, volt, pt)
    
    st.subheader(f"📊 Hasil Analisis: {pt}")
    res1, res2 = st.columns(2)
    
    with res1:
        st.info(f"**UTAMA / RUN**\n\n# {tr} Lilit\n\n**{dr} mm**")
    
    if "1-Phase" in pt:
        with res2:
            st.warning(f"**BANTU / START**\n\n# {ts} Lilit\n\n**{ds} mm**")
    
    st.success(f"**Daya Kapasitas Besi:** {pw} Watt")
    st.code(f"Pola Winding: {pitch}", language="text")
