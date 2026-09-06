import streamlit as st
import gspread
import pandas as pd
from datetime import date

st.set_page_config(page_title="Input Pengeluaran", page_icon="💸", layout="centered")

# --- 1. PASSWORD AUTHENTICATION GATE ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Restricted Access")
    st.markdown("Please enter your password to access the expense tracker.")

    with st.form("login_form"):
        entered_password = st.text_input("Password", type="password")
        login_submitted = st.form_submit_button("Login", use_container_width=True)

        if login_submitted:
            correct_password = st.secrets["auth"]["app_password"]
            if entered_password == correct_password:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ Incorrect password!")

    st.stop()

# --- 2. MAIN APP (Runs only after successful login) ---

with st.sidebar:
    if st.button("🔒 Logout"):
        st.session_state.authenticated = False
        st.rerun()

# Trim default Streamlit top padding, and force columns to stay side-by-side
# on mobile instead of Streamlit's default auto-stacking below ~640px width.
st.markdown(
    """
    <style>
        .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
        div[data-testid="stVerticalBlock"] > div { gap: 0.5rem; }

        /* Force horizontal blocks (st.columns) to stay in a row on any
           screen width, overriding Streamlit's mobile auto-stack. */
        div[data-testid="stHorizontalBlock"] {
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            gap: 0.5rem;
        }
        div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
            flex: 1 1 0 !important;
            width: 0 !important;
            min-width: 0 !important;
        }

        /* Shrink label/input text a bit so 3-up columns don't overflow */
        div[data-testid="stColumn"] label p { font-size: 0.8rem; }
        div[data-testid="stColumn"] div[data-baseweb="select"] { font-size: 0.85rem; }
        div[data-testid="stColumn"] input { font-size: 0.85rem; }

        /* Make metric values slightly smaller for a tighter dashboard layout */
        div[data-testid="stMetricValue"] { font-size: 1.1rem !important; }
    </style>
    """,
    unsafe_allow_html=True,
)
st.write("")
st.write("💸 Input Pengeluaran")

# VLOOKUP Database Mapping
SUBKATEGORI_DATA = {
    "Dana Tak Terduga Bulanan": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Dana Tak Terduga"},
    "Keperluan Rumah Habis Pakai": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Keperluan Rumah"},
    "Keperluan Rumah Tidak Habis Pakai": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Keperluan Rumah"},
    "Listrik": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Keperluan Rumah"},
    "Air": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Keperluan Rumah"},
    "Gas": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Keperluan Rumah"},
    "Internet Rumah": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Keperluan Rumah"},
    "Sewa": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Keperluan Rumah"},
    "Laundry": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Keperluan Rumah"},
    "Bahan Makanan": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Makan & Minum Primer"},
    "Buah-Buahan": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Makan & Minum Primer"},
    "Makanan Berat Reguler": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Makan & Minum Primer"},
    "Asuransi": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Kesehatan"},
    "Dokter": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Kesehatan"},
    "Vitamin & Suplemen": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Kesehatan"},
    "Obat": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Kesehatan"},
    "Olahraga": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Kesehatan"},
    "Kegiatan Kesehatan": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Kesehatan"},
    "Kosmetik": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Kesehatan"},
    "Buku": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Pendidikan"},
    "Pembelajaran": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Pendidikan"},
    "Peralatan Pendidikan": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Pendidikan"},
    "Pulsa & Internet HP": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Komunikasi"},
    "Administrasi": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Komunikasi"},
    "Transportasi Umum": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Transposrtasi"},
    "Transportasi Online": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Transposrtasi"},
    "Bensin": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Transposrtasi"},
    "Parkir": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Transposrtasi"},
    "Tol": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Transposrtasi"},
    "Pajak": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Transposrtasi"},
    "Sepeda": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Transposrtasi"},
    "Keluarga Bulanan": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Keluarga Bulanan"},
    "Ziswaf Bulanan": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Ziswaf Bulanan"},
    "Rekonsiliasi Bulanan": {"urgensi": "Bulanan", "kantong": "Bulanan Primer", "kategori": "Rekonsiliasi"},
    "Baju": {"urgensi": "Bulanan", "kantong": "Bulanan Tersier", "kategori": "Belanja Tersier"},
    "Aksesoris": {"urgensi": "Bulanan", "kantong": "Bulanan Tersier", "kategori": "Belanja Tersier"},
    "Elektronik": {"urgensi": "Bulanan", "kantong": "Bulanan Tersier", "kategori": "Belanja Tersier"},
    "Sepatu": {"urgensi": "Bulanan", "kantong": "Bulanan Tersier", "kategori": "Belanja Tersier"},
    "Belanja Lain-Lain": {"urgensi": "Bulanan", "kantong": "Bulanan Tersier", "kategori": "Belanja Tersier"},
    "Berkebun": {"urgensi": "Bulanan", "kantong": "Bulanan Tersier", "kategori": "Belanja Tersier"},
    "Olahraga Rekreatif": {"urgensi": "Bulanan", "kantong": "Bulanan Tersier", "kategori": "Rekreasi"},
    "Transportasi Rekreasi": {"urgensi": "Bulanan", "kantong": "Bulanan Tersier", "kategori": "Rekreasi"},
    "Tiket Hiburan": {"urgensi": "Bulanan", "kantong": "Bulanan Tersier", "kategori": "Rekreasi"},
    "Musik": {"urgensi": "Bulanan", "kantong": "Bulanan Tersier", "kategori": "Rekreasi"},
    "Fotografi": {"urgensi": "Bulanan", "kantong": "Bulanan Tersier", "kategori": "Rekreasi"},
    "Langganan Hiburan": {"urgensi": "Bulanan", "kantong": "Bulanan Tersier", "kategori": "Rekreasi"},
    "Rekreasi Lain": {"urgensi": "Bulanan", "kantong": "Bulanan Tersier", "kategori": "Rekreasi"},
    "Bersosialisasi": {"urgensi": "Bulanan", "kantong": "Bulanan Tersier", "kategori": "Sosial"},
    "Hadiah": {"urgensi": "Bulanan", "kantong": "Bulanan Tersier", "kategori": "Sosial"},
    "Makanan Ringan": {"urgensi": "Bulanan", "kantong": "Bulanan Tersier", "kategori": "Makan Rekreatif"},
    "Restoran": {"urgensi": "Bulanan", "kantong": "Bulanan Tersier", "kategori": "Makan Rekreatif"},
    "Kafe": {"urgensi": "Bulanan", "kantong": "Bulanan Tersier", "kategori": "Makan Rekreatif"},
    "Pesan Antar": {"urgensi": "Bulanan", "kantong": "Bulanan Tersier", "kategori": "Makan Rekreatif"},
    "Ziswaf Lain": {"urgensi": "Non-Bulanan", "kantong": "Ziswaf", "kategori": "Ziswaf"},
    "Zakat Fitrah": {"urgensi": "Non-Bulanan", "kantong": "Ziswaf", "kategori": "Zakat Fitrah"},
    "Zakat Mal": {"urgensi": "Non-Bulanan", "kantong": "Ziswaf", "kategori": "Zakat Mal"},
    "Wakaf": {"urgensi": "Non-Bulanan", "kantong": "Ziswaf", "kategori": "Wakaf"},
    "Bela Sungkawa": {"urgensi": "Non-Bulanan", "kantong": "Ziswaf", "kategori": "Bela Sungkawa"},
    "Pernikahan": {"urgensi": "Non-Bulanan", "kantong": "Keluarga", "kategori": "Pernikahan"},
    "Keluarga": {"urgensi": "Non-Bulanan", "kantong": "Keluarga", "kategori": "Keluarga"},
    "Darurat (Keluarga)": {"urgensi": "Non-Bulanan", "kantong": "Keluarga", "kategori": "Keluarga"},
    "Travelio": {"urgensi": "Non-Bulanan", "kantong": "Keluarga", "kategori": "Keluarga"},
    "Darurat": {"urgensi": "Non-Bulanan", "kantong": "Darurat", "kategori": "Darurat"},
    "Haji": {"urgensi": "Non-Bulanan", "kantong": "Haji", "kategori": "Haji"},
    "Liburan": {"urgensi": "Non-Bulanan", "kantong": "Masa Depan", "kategori": "Liburan"},
    "Pulang Kampung": {"urgensi": "Non-Bulanan", "kantong": "Masa Depan", "kategori": "Pulang Kampung"},
    "Masa Depan": {"urgensi": "Non-Bulanan", "kantong": "Masa Depan", "kategori": "Masa Depan"},
    "Kerjaan": {"urgensi": "Non-Bulanan", "kantong": "Masa Depan", "kategori": "Masa Depan"},
    "Investasi": {"urgensi": "Non-Bulanan", "kantong": "Masa Depan", "kategori": "Investasi"},
    "Langganan Lain2": {"urgensi": "Non-Bulanan", "kantong": "Masa Depan", "kategori": "Masa Depan"},
    "Konversi Uang": {"urgensi": "Non-Bulanan", "kantong": "Masa Depan", "kategori": "Konversi Uang"},
    "Pendidikan": {"urgensi": "Non-Bulanan", "kantong": "Masa Depan", "kategori": "Pendidikan"},
    "Pajak Tahunan": {"urgensi": "Non-Bulanan", "kantong": "Masa Depan", "kategori": "Pajak"},
    "Anggaran Disimpan": {"urgensi": "Non-Bulanan", "kantong": "Anggaran Disimpan", "kategori": "Anggaran Disimpan"},    
    "Emas": {"urgensi": "Investasi", "kantong": "Masa Depan", "kategori": "Investasi"},
    "Bibit": {"urgensi": "Investasi", "kantong": "Masa Depan", "kategori": "Investasi"},
    "Franchise/Bisnis": {"urgensi": "Investasi", "kantong": "Masa Depan", "kategori": "Investasi"},
    "Saham": {"urgensi": "Investasi", "kantong": "Masa Depan", "kategori": "Investasi"},
    "Investasi Lain": {"urgensi": "Investasi", "kantong": "Masa Depan", "kategori": "Investasi"},
    "Hutang": {"urgensi": "Investasi", "kantong": "Hutang", "kategori": "Hutang"},
}

# ---------------------------------------------------------------
# Dashboard helpers — mirrors the "Input" sheet's summary section
# (Input!A13:F42, e.g. Input!B17 = Saldo Bulanan Primer)
# ---------------------------------------------------------------

@st.cache_data(ttl=60, show_spinner="Memuat ringkasan...")
def load_dashboard_data():
    secrets_dict = dict(st.secrets["connections"]["gsheets"])
    client = gspread.service_account_from_dict(secrets_dict)
    sh = client.open_by_url(secrets_dict["spreadsheet"])
    ws = sh.worksheet("Input")

    # One batched call for all dashboard ranges to save API quota
    ranges = ["A13:C14", "A16:F18", "A20:C22", "A24:F35", "A37:F42"]
    return ws.batch_get(ranges)


def _pad(row, n):
    row = list(row) + [""] * (n - len(row))
    return row[:n]


def _pct_style(val):
    try:
        pct = float(str(val).replace("%", "").replace(",", "."))
    except (ValueError, TypeError):
        return ""
    if val == "":
        return ""
    color = "#f5b7b1" if pct > 100 else "#a9dfbf"
    return f"background-color: {color}; color: #111;"


def render_group_table(title, subtitle, header_row, data_rows):
    st.markdown(f"**{title}**" + (f" — {subtitle}" if subtitle else ""))
    header_row = _pad(header_row, 3)
    col_a = header_row[0] or "Kategori"
    col_b = header_row[1] or "Budget"
    col_c = header_row[2] or "Pengeluaran"

    records = []
    for r in data_rows:
        nama, budget, pengeluaran, pct, hari, satuan = _pad(r, 6)
        if not nama:
            continue
        records.append({
            col_a: nama,
            col_b: budget,
            col_c: pengeluaran,
            "%": pct,
            "Sisa/hari": f"{hari} {satuan}".strip(),
        })
    if not records:
        st.caption("_(tidak ada data)_")
        return
    df = pd.DataFrame(records)
    styler = df.style
    if hasattr(styler, "map"):
        styler = styler.map(_pct_style, subset=["%"])
    else:  # older pandas fallback
        styler = styler.applymap(_pct_style, subset=["%"])
    st.dataframe(styler, hide_index=True, use_container_width=True)


@st.cache_data(ttl=30, show_spinner="Memuat transaksi terakhir...")
def load_latest_expenses(n=3):
    secrets_dict = dict(st.secrets["connections"]["gsheets"])
    client = gspread.service_account_from_dict(secrets_dict)
    sh = client.open_by_url(secrets_dict["spreadsheet"])
    ws = sh.worksheet("Pengeluaran")

    lastrow_val = ws.acell('A1').value
    if not lastrow_val:
        return []
    try:
        latest_row = int(lastrow_val) - 1  # A1 points to the next empty row
    except ValueError:
        return []
    if latest_row < 2:
        return []

    # Fetch all rows from C2..Clatest_row and iterate backwards, skipping
    # any rows whose tanggal (col C) is in the future. Keep going until
    # we collected `n` rows with tanggal <= today or we reach the top.
    values = ws.get(f"C2:L{latest_row}") or []

    from datetime import datetime, date
    today = date.today()

    def _parse_date(s):
        if not s:
            return None
        # Common formats: dd/mm/YYYY (used when writing), ISO, or others
        for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
            try:
                return datetime.strptime(s, fmt).date()
            except Exception:
                continue
        # Fallback to pandas parsing (dayfirst)
        try:
            return pd.to_datetime(s, dayfirst=True).date()
        except Exception:
            return None

    collected = []
    # iterate newest->oldest
    for row in reversed(values):
        if len(collected) >= n:
            break
        tanggal_str = row[0] if len(row) > 0 else ""
        parsed = _parse_date(tanggal_str)
        if parsed is None:
            # skip rows with invalid or missing tanggal
            continue
        if parsed <= today:
            collected.append(row)
        else:
            # tanggal > today -> skip and continue upward
            continue

    return collected  # most recent first


def render_latest_expenses(rows):
    records = []
    for r in rows:
        tanggal, _tipe, _urg, _kan, _kat, subkategori, _oleh, mata_uang, nominal, deskripsi = _pad(r, 10)
        records.append({
            "Tanggal": tanggal,
            "Subkategori": subkategori,
            "Deskripsi": deskripsi,
            "Nominal": f"{mata_uang} {nominal}".strip(),
        })
    if not records:
        st.caption("_(belum ada transaksi)_")
        return
    st.dataframe(pd.DataFrame(records), hide_index=True, use_container_width=True)


if "reset_key" not in st.session_state:
    st.session_state.reset_key = 0
k = st.session_state.reset_key

# --- Row 1: Tanggal + Nominal ---
r1c1, r1c2 = st.columns(2)
with r1c1:
    tanggal = st.date_input("Tanggal", value=date.today(), key=f"tgl_{k}")
with r1c2:
    nominal = st.number_input("Nominal", min_value=0.0, format="%.2f", key=f"nom_{k}")

# --- Row 2: Tipe + Mata Uang + Oleh (short values, fit 3-up) ---
r2c1, r2c2, r2c3 = st.columns(3)
with r2c1:
    tipe = st.selectbox("Tipe", options=["RT", "Mo"], key=f"tipe_{k}")
with r2c2:
    mata_uang = st.selectbox("Mata Uang", options=["EUR", "IDR"], key=f"mu_{k}")
with r2c3:
    oleh = st.selectbox("Oleh", options=["Gan", "Mof"], key=f"oleh_{k}")

# --- Row 3: Penyimpanan + Subkategori ---
r3c1, r3c2 = st.columns(2)
with r3c1:
    penyimpanan_list = [
        "ABN Mo-Ga", "ABN Gan", "Permata Gan", "Jago Mo-Ga", "Mandiri Gan", "Gopay Gan",
        "Cash Gan", "Emoney Gan", "Jenius Gan", "Revolut Gan", 
        "Wise Gan", "Kas Gan", "Kas Mo", "Mandiri Mo",
    ]
    penyimpanan = st.selectbox("Penyimpanan", options=penyimpanan_list, index=0, key=f"peny_{k}")
with r3c2:
    subkategori = st.selectbox("Subkategori", options=list(SUBKATEGORI_DATA.keys()), key=f"subkat_{k}")

urgensi = SUBKATEGORI_DATA[subkategori]["urgensi"]
kantong = SUBKATEGORI_DATA[subkategori]["kantong"]
kategori = SUBKATEGORI_DATA[subkategori]["kategori"]

# Auto-derived fields shown as one compact read-only line instead of 3 disabled inputs
st.caption(f"📍 {urgensi}  ·  {kantong}  ·  {kategori}")

deskripsi = st.text_area("Deskripsi", key=f"desk_{k}", height=70)

if st.button("Submit Data", use_container_width=True, type="primary"):
    if nominal <= 0:
        st.error("⚠️ Nominal tidak boleh kosong atau nol!")
    else:
        try:
            with st.spinner("Menyimpan data..."):
                secrets_dict = dict(st.secrets["connections"]["gsheets"])
                client = gspread.service_account_from_dict(secrets_dict)

                sheet_url = secrets_dict["spreadsheet"]
                sh = client.open_by_url(sheet_url)
                pengeluaran = sh.worksheet("Pengeluaran")

                lastrow_val = pengeluaran.acell('A1').value
                if not lastrow_val:
                    st.error("Cell A1 is kosong. Tidak dapat menentukan baris terakhir.")
                    st.stop()

                lastrow = str(lastrow_val)

                updates = [
                    {'range': f'C{lastrow}', 'values': [[tanggal.strftime("%d/%m/%Y")]]},
                    {'range': f'D{lastrow}', 'values': [[tipe]]},
                    {'range': f'E{lastrow}', 'values': [[urgensi]]},
                    {'range': f'F{lastrow}', 'values': [[kantong]]},
                    {'range': f'G{lastrow}', 'values': [[kategori]]},
                    {'range': f'H{lastrow}', 'values': [[subkategori]]},
                    {'range': f'I{lastrow}', 'values': [[oleh]]},
                    {'range': f'J{lastrow}', 'values': [[mata_uang]]},
                    {'range': f'K{lastrow}', 'values': [[nominal]]},
                    {'range': f'L{lastrow}', 'values': [[deskripsi]]},
                    {'range': f'M{lastrow}', 'values': [[penyimpanan]]},
                ]

                # Write each range with USER_ENTERED so Sheets parses the
                # date string as a date instead of inserting a leading
                # apostrophe (text marker). Using the per-worksheet
                # `update` method avoids the JSON payload format mismatch.
                for upd in updates:
                    pengeluaran.update(upd['range'], upd['values'], value_input_option='USER_ENTERED')
                st.success(f"✅ Berhasil menambahkan {mata_uang} {nominal} ke baris {lastrow}!")

                load_dashboard_data.clear()  # refresh dashboard so it reflects the new entry
                load_latest_expenses.clear()  # refresh latest-expenses list too
                st.session_state.reset_key += 1
                st.rerun()

        except Exception as e:
            st.error(f"❌ Terjadi kesalahan: {e}")

try:
    _sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    dashboard_url = "https://datastudio.google.com/u/0/reporting/3a415aab-b183-477b-a2ef-6c199832b2b4/page/zqjpF"
    c1, c2 = st.columns(2)
    with c1:
        st.link_button("📄 Buka Spreadsheet", _sheet_url)
    with c2:
        st.link_button("📊 Buka Dashboard", dashboard_url)
except Exception:
    pass

def render_subkategori_structure():
    from collections import defaultdict

    tree = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for subkat, info in SUBKATEGORI_DATA.items():
        tree[info["urgensi"]][info["kantong"]][info["kategori"]].append(subkat)

    for urgensi in sorted(tree.keys()):
        st.markdown(f"#### {urgensi}")
        for kantong in sorted(tree[urgensi].keys()):
            st.markdown(f"**{kantong}**")
            for kategori in sorted(tree[urgensi][kantong].keys()):
                subkats = ", ".join(sorted(tree[urgensi][kantong][kategori]))
                st.markdown(f"- _{kategori}_: {subkats}")


with st.expander("📖 Daftar Urgensi / Kantong / Kategori / Subkategori", expanded=False):
    render_subkategori_structure()

# ---------------------------------------------------------------
# 3 latest expenses — from the "Pengeluaran" sheet using lastrow
# ---------------------------------------------------------------

# st.divider()
if st.button("🔄 Muat ulang", use_container_width=True):
    load_dashboard_data.clear()
    
st.write("🧾 3 Transaksi Terakhir")

try:
    render_latest_expenses(load_latest_expenses(3))
except Exception as e:
    st.warning(f"Tidak bisa memuat transaksi terakhir: {e}")

# ---------------------------------------------------------------
# Dashboard — replicates the "Input" sheet summary below the form
# ---------------------------------------------------------------

# st.divider()

st.write("📊 Ringkasan")

try:
    info, ringkasan, aset, primer, tersier = load_dashboard_data()

    # Bulan Ini / Rekon / Mata Uang
    info = [_pad(r, 3) for r in info]
    bulan_ini = info[0][1] if len(info) > 0 else "-"
    rekon = info[1][1] if len(info) > 1 else "-"
    mata_uang_dash = info[1][2] if len(info) > 1 else "-"

    m1, m2, m3 = st.columns(3)
    m1.metric("Bulan Ini", bulan_ini)
    m2.metric("Rekon", rekon)
    m3.metric("Mata Uang", mata_uang_dash)

    # Ringkasan Kantong (Saldo / Pengeluaran Bulanan)
    if ringkasan:
        render_group_table("Ringkasan Kantong", "", ringkasan[0], ringkasan[1:])

    # Aset
    if aset:
        aset = [_pad(r, 3) for r in aset]
        headers_a = aset[0] if len(aset) > 0 else ["Aset Lancar", "Aset Tidak Lancar", "Aset Tak Berwujud"]
        values_a = aset[1] if len(aset) > 1 else ["-", "-", "-"]
        total_kekayaan = aset[2][2] if len(aset) > 2 else "-"

        st.markdown("**Aset**")
        a1, a2, a3, a4 = st.columns(4)
        a1.metric(headers_a[0] or "Aset Lancar", values_a[0] or "-")
        a2.metric(headers_a[1] or "Aset Tidak Lancar", values_a[1] or "-")
        a3.metric(headers_a[2] or "Aset Tak Berwujud", values_a[2] or "-")
        a4.metric("Total Kekayaan", total_kekayaan or "-")

    # Bulanan Primer categories
    if primer:
        total_row = _pad(primer[0] if len(primer) > 0 else [], 2)
        header_row = primer[1] if len(primer) > 1 else []
        render_group_table("Bulanan Primer", total_row[1], header_row, primer[2:])

    # Bulanan Tersier categories
    if tersier:
        total_row = _pad(tersier[0] if len(tersier) > 0 else [], 2)
        header_row = tersier[1] if len(tersier) > 1 else []
        render_group_table("Bulanan Tersier", total_row[1], header_row, tersier[2:])

except Exception as e:
    st.warning(f"Tidak bisa memuat ringkasan: {e}")