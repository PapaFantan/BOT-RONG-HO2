import streamlit as st
import json
import os

st.set_page_config(page_title="Dragon Tiger Value Pattern Tool", layout="wide")

DATA_FILE = "history.json"

# ================= LOAD DATA =================
def load_history():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    else:
        try:
            with open("history.json", "r") as f:
                initial = json.load(f)
            with open(DATA_FILE, "w") as f:
                json.dump(initial, f)
            return initial
        except:
            return []

# ================= SAVE DATA =================
def save_history(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# ================= STATE =================
if "history" not in st.session_state:
    st.session_state.history = load_history()

# ================= SETTINGS =================
st.sidebar.header("⚙️ Cài đặt")
max_history = st.sidebar.number_input("Số ván lưu tối đa", min_value=100, max_value=5000, value=600, step=100)
min_diff = st.sidebar.number_input("Độ lệch tối thiểu để đánh", min_value=1, max_value=10, value=1)
min_sample = st.sidebar.number_input("Số mẫu tối thiểu", min_value=1, max_value=20, value=1)

# ================= UI =================
st.title("🐉🐯 Dragon Tiger Tool")

cards = ['A','2','3','4','5','6','7','8','9','10','J','Q','K']

# ---------- STYLE ----------
st.markdown("""
<style>
/* BUTTON BASE */
div[data-testid="stButton"] button {
    font-size: 40px !important;      /* tăng size chữ */
    font-weight: 900 !important;     /* đậm tối đa */
    color: #111 !important;          /* đen đậm, dễ nhìn */
    
    /* giữ nguyên size icon */
    padding: 0 !important;
    height: 48px !important;
    width: 40px !important;

    /* làm chữ nét hơn */
    text-shadow: 0px 0px 2px rgba(0,0,0,0.5);
}

/* RỒNG - đỏ */
div[data-testid="stButton"] button[id*="r_"] {
    background: linear-gradient(135deg, #ff4d4f, #b71c1c) !important;
}

/* HỔ - xanh */
div[data-testid="stButton"] button[id*="h_"] {
    background: linear-gradient(135deg, #42a5f5, #0d47a1) !important;
}

/* HOVER */
div[data-testid="stButton"] button:hover {
    filter: brightness(1.2);
}

/* ACTIVE */
div[data-testid="stButton"] button:active {
    transform: scale(0.95);
}

/* DỰ BÁO BOX */
.prediction-box {
    background-color: #d4edda;
    padding: 15px;
    border-radius: 10px;
    font-size: 24px;
    font-weight: bold;
    color: #155724;
}
</style>
""", unsafe_allow_html=True)

# ---------- RỒNG ----------
st.subheader("🐉 Rồng")
cols_r = st.columns(len(cards))
for i, c in enumerate(cards):
    if cols_r[i].button(c, key=f"r_{c}_{i}"):
        st.session_state.selected_r = c

# ---------- HỔ ----------
st.subheader("🐯 Hổ")
cols_h = st.columns(len(cards))
for i, c in enumerate(cards):
    if cols_h[i].button(c, key=f"h_{c}_{i}"):
        st.session_state.selected_h = c

# ================= INPUT =================
if "selected_r" in st.session_state and "selected_h" in st.session_state:
    r = st.session_state.selected_r
    h = st.session_state.selected_h

    order = cards

    if order.index(r) > order.index(h):
        result = "R"
    elif order.index(r) < order.index(h):
        result = "H"
    else:
        result = "T"

    st.session_state.history.append((r, h, result))

    del st.session_state.selected_r
    del st.session_state.selected_h

    if len(st.session_state.history) > max_history:
        st.session_state.history = st.session_state.history[-max_history:]

    save_history(st.session_state.history)

# ================= CONTROL =================
col1, col2 = st.columns(2)
if col1.button("Undo") and st.session_state.history:
    st.session_state.history.pop()
    save_history(st.session_state.history)

if col2.button("Reset"):
    st.session_state.history = []
    save_history(st.session_state.history)

# ================= ANALYSIS =================
if len(st.session_state.history) >= 2:
    last_pair = st.session_state.history[-1]
    target = (last_pair[0], last_pair[1])

    follow_results = []

    for i in range(len(st.session_state.history)-1):
        d, t, r = st.session_state.history[i]
        if (d, t) == target:
            next_result = st.session_state.history[i+1][2]
            if next_result != "T":
                follow_results.append(next_result)

    total = len(follow_results)
    r_count = follow_results.count("R")
    h_count = follow_results.count("H")

    st.markdown("## 📊 Thống kê")
    st.markdown(f"## Cặp: {target[0]}-{target[1]} | Mẫu: {total}")

    if total >= min_sample:
        diff = abs(r_count - h_count)
        st.markdown(f"## R: {r_count} | H: {h_count} | Lệch: {diff}")

        if diff >= min_diff:
            suggestion = "- RỒNG -" if r_count > h_count else "- HỔ -"
            st.markdown(f"<div class='prediction-box'>👉 DỰ BÁO: {suggestion}</div>", unsafe_allow_html=True)
        else:
            st.warning("Bỏ qua (chưa đủ lệch)")
    else:
        st.warning("Bỏ qua (chưa đủ mẫu)")

# ================= HISTORY =================
st.divider()
st.subheader("📜 Lịch sử gần nhất")
last_display = [f"{d}-{t}({r})" for d,t,r in st.session_state.history[-20:]]
st.write(" | ".join(last_display))

st.caption("Lịch sử được lưu tự động. Mỗi máy có file riêng, không ảnh hưởng nhau.")