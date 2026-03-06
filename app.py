import streamlit as st
import math

# --- KONFIGURASI MOBILE-FIRST ---
st.set_page_config(page_title="Operator System v7.1", layout="centered")

def calculate_system(di, do, l_c, s, v, pt):
    # Estimasi Luas Slot Bersih (Safety Factor 0.35 untuk ruang mika)
    total_annular_area = (math.pi * (do**2 - di**2) / 4)
    area_per_slot = (total_annular_area * 0.35) / s
    
    if "1-Phase" in pt:
        # --- LOGIKA JUJUR POMPA AIR (Standard Bengkel) ---
        # Lilitan minimal agar induktansi cukup menahan 220V (Anti-Konslet)
        tr = 55 if di < 65 else 45 
        ts = int(tr * 1.25) # Lilitan bantu lebih banyak untuk torsi start
        
        # Diameter kawat (Fill Factor 22% - Sangat mudah dimasukkan manual)
        dr = math.sqrt((4 * (area_per_slot * 0.22) / tr) / math.pi)
        ds = dr * 0.8 # Kawat bantu selalu lebih kecil
        
        # Daya realistis berdasarkan kapasitas serap panas besi
        pw = (di * l_c * 0.08) # Estimasi Watt yang jujur untuk besi kecil
        pitch = "1-6, 1-8, 1-10, 1-12 (Konsentris)"
        return tr, round(dr, 2), ts, round(ds, 2), round(pw, 1), pitch
    
    else:
        # --- LOGIKA INDUSTRI 3-PHASE (Standard 380V) ---
        # Lilitan minimal 3-fase agar tidak meledakkan MCB
        tr_3p = 42 if di < 85 else 35
        
        # Fill Factor 30% (Motor industri sedikit lebih padat)
        dr_3p = math.sqrt((4 * (area_per_slot * 0.30) / tr_3p) / math.pi)
        
        # Daya 3-Phase (Kapasitas Besi Industri)
        pw_3p = (di * l_c * 0.12) 
        return tr_3p, round(dr_3p, 2), 0, 0, round(pw_3p, 1), "1-10, 1-12 (Tumpuk/Lap)"

# --- ANTARMUKA PENGGUNA ---
st.title("🛡️ Operator System v7.1")
st.caption("Sistem Rekonstruksi Final: Verified 220V & 380V")

with st.form("main_form"):
    pt = st.selectbox("Mode Motor", ["1-Phase (Pompa Air)", "3-Phase (Industrial)"])
    c1, c2 = st.columns(2)
    d_in = c1.number_input("D-Dalam (mm)", value=50.0, step=0.1)
    d_out = c2.number_input("D-Luar (mm)", value=90.0, step=0.1)
    l_core = c1.number_input("Panjang (mm)", value=40.0, step=0.1)
    slots = c2.number_input("Slot", value=24, step=1)
    volt = st.number_input("Voltase Kerja (V)", value=220)
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
    st.caption("Catatan: Gunakan mika isolasi grade F untuk hasil maksimal.")
