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
min_diff = st.sidebar.number_input("Độ lệch tối thiểu để đánh", min_value=1, max_value=10, value=3)
min_sample = st.sidebar.number_input("Số mẫu tối thiểu", min_value=1, max_value=20, value=3)

# ================= UI =================
st.title("🐉🐯 Dragon Tiger Tool")

cards = ['A','2','3','4','5','6','7','8','9','10','J','Q','K']

# ---------- STYLE ----------
st.markdown("""
<style>
div[data-testid="stButton"] button {
    font-size: 28px !important;
    font-weight: 700 !important;
    color: #111 !important;
    height: 48px !important;
    width: 60px !important;
    margin: 2px !important;
}
div[data-testid="stButton"] button[id*="r_"] {
    background: linear-gradient(135deg, #ff4d4f, #b71c1c) !important;
}
div[data-testid="stButton"] button[id*="h_"] {
    background: linear-gradient(135deg, #42a5f5, #0d47a1) !important;
}
div[data-testid="stButton"] button:hover { filter: brightness(1.2); }
div[data-testid="stButton"] button:active { transform: scale(0.95); }
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

# ---------- Hàm render nút theo nhiều hàng ----------
def render_buttons(prefix):
    per_row = 5  # số nút mỗi hàng
    for i in range(0, len(cards), per_row):
        cols = st.columns(per_row)
        for j, c in enumerate(cards[i:i+per_row]):
            if cols[j].button(c, key=f"{prefix}_{c}_{i+j}"):
                return c
    return None

# ---------- RỒNG ----------
st.subheader("🐉 Rồng")
selected_r = render_buttons("r")

# ---------- HỔ ----------
st.subheader("🐯 Hổ")
selected_h = render_buttons("h")

# ================= INPUT =================
if selected_r and selected_h:
    order = cards
    if order.index(selected_r) > order.index(selected_h):
        result = "R"
    elif order.index(selected_r) < order.index(selected_h):
        result = "H"
    else:
        result = "T"

    st.session_state.history.append((selected_r, selected_h, result))

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