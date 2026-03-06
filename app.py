import streamlit as st
import math

st.set_page_config(page_title="Operator System v6.0", layout="centered")

def calculate_honest_rewinding(di, do, l_c, s, p, v, pt):
    # Konstanta Kejujuran Fisik
    f, kw = 50, 0.95
    # Pembatasan Tesla berdasarkan ukuran (Semakin kecil semakin rendah)
    b_limit = 1.25 if di < 60 else 1.45
    
    # 1. Hitung Fluks
    phi = (b_limit * (di * math.pi * l_c / p)) / 1000000
    
    if "1-Phase" in pt:
        # --- LOGIKA KHUSUS POMPA AIR ---
        # Lilitan Utama (Running) - Menggunakan 2/3 total slot
        n_run_total = v / (4.44 * f * phi * kw)
        s_run = int(s * 0.66)
        turns_per_slot_run = int(n_run_total / s_run)
        
        # Lilitan Bantu (Starting) - Biasanya 1.3x lebih banyak lilitan
        turns_per_slot_start = int(turns_per_slot_run * 1.3)
        
        # Kapasitas Ruang Slot (Fill Factor Realistis 25%)
        area_annular = (math.pi * (do**2 - di**2) / 4) * 0.4 # 40% adalah estimasi luas slot total
        area_per_slot = area_annular / s
        
        # Diameter Kawat Utama (Harus muat!)
        area_wire_run = (area_per_slot * 0.25) / turns_per_slot_run
        d_wire_run = math.sqrt((4 * area_wire_run) / math.pi)
        
        # Diameter Kawat Bantu (Biasanya 1-2 step di bawah Utama)
        d_wire_start = d_wire_run * 0.75
        
        # Pitch/Langkah (Contoh 24 slot, 2 pole)
        pitch = "1-6, 1-8, 1-10, 1-12 (Konsentris)"
        
        return turns_per_slot_run, round(d_wire_run, 2), turns_per_slot_start, round(d_wire_start, 2), pitch
    
    else:
        # Logika 3-Phase tetap standar namun dengan J-limit
        n_ph = v / (4.44 * f * phi * kw)
        turns_3p = int((n_ph * 3) / s)
        area_wire_3p = ((area_annular / s) * 0.35) / turns_3p
        d_wire_3p = math.sqrt((4 * area_wire_3p) / math.pi)
        return turns_3p, round(d_wire_3p, 2), 0, 0, "1-10 (Lap Winding)"

# --- TAMPILAN SMARTPHONE OPTIMIZED ---
st.title("🛡️ Operator System v6.0")
st.caption("Sistem Rekonstruksi Tanpa Dusta - Verified by Internal Logic")

with st.form("motor_data"):
    pt = st.selectbox("Tipe Fase", ["1-Phase (Pump)", "3-Phase (Industrial)"])
    c1, c2 = st.columns(2)
    d_in = c1.number_input("D-Dalam (mm)", value=50.0)
    d_out = c2.number_input("D-Luar (mm)", value=90.0)
    l_core = c1.number_input("Panjang (mm)", value=40.0)
    slots = c2.number_input("Slot", value=24)
    p = st.selectbox("Pole", [2, 4], index=0)
    v = st.number_input("Voltase (V)", value=220)
    submit = st.form_submit_button("REKONSTRUKSI SISTEM")

if submit:
    tr, dr, ts, ds, pitch = calculate_honest_rewinding(d_in, d_out, l_core, slots, p, v, pt)
    
    st.subheader(f"📊 Hasil Eksekusi: {pt}")
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.info(f"**UTAMA (RUN)**\n\n{tr} Lilit\n\n**{dr} mm**")
    
    if "1-Phase" in pt:
        with col_b:
            st.warning(f"**BANTU (START)**\n\n{ts} Lilit\n\n**{ds} mm**")
        st.success(f"**Pola Winding:** {pitch}")
        
    else:
        st.success(f"**Pola Winding:** {pitch}")
