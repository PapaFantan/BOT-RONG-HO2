import streamlit as st
import json
import os

st.set_page_config(page_title="Dragon Tiger Tool", layout="wide")

DATA_FILE = "history.json"

def load_history():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_history(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

if "history" not in st.session_state:
    st.session_state.history = load_history()

# Sidebar settings
st.sidebar.header("⚙️ Cài đặt")
max_history = st.sidebar.number_input("Số ván lưu tối đa", 100, 5000, 600, step=100)
min_diff = st.sidebar.number_input("Độ lệch tối thiểu để đánh", 1, 10, 3)
min_sample = st.sidebar.number_input("Số mẫu tối thiểu", 1, 20, 3)

st.title("🐉🐯 Dragon Tiger Tool")

cards_top = ['A','2','3','4','5','6','7']
cards_bottom = ['8','9','10','J','Q','K']

# ---------- STYLE ----------
st.markdown("""
<style>
div[data-testid="stHorizontalBlock"] {
    flex-wrap: nowrap !important;
    justify-content: center !important;
    gap: 0.2rem !important;
}
div[data-testid="stColumn"] {
    flex: 0 0 auto !important;
}

/* Nút icon: chữ chiếm ~80% */
div[data-testid="stButton"] button {
    height: 3rem !important;        /* chiều cao nút */
    width: 3.5rem !important;       /* chiều rộng nút */
    font-size: 2.4rem !important;   /* ~80% chiều cao */
    line-height: 3rem !important;   /* căn giữa theo chiều cao */
    font-weight: 900 !important;    /* đậm tối đa */
    color: #111 !important;
    margin: 0.2rem !important;
    text-shadow: 0px 0px 1px rgba(0,0,0,0.5);
}

/* Rồng - đỏ */
div[data-testid="stButton"] button[id*="r_"] {
    background: linear-gradient(135deg, #ff4d4f, #b71c1c) !important;
}

/* Hổ - xanh */
div[data-testid="stButton"] button[id*="h_"] {
    background: linear-gradient(135deg, #42a5f5, #0d47a1) !important;
}

div[data-testid="stButton"] button:hover { filter: brightness(1.2); }
div[data-testid="stButton"] button:active { transform: scale(0.95); }

.prediction-box {
    background-color: #d4edda;
    padding: 15px;
    border-radius: 10px;
    font-size: 1.4rem;
    font-weight: bold;
    color: #155724;
}
</style>
""", unsafe_allow_html=True)

def render_row(cards, prefix):
    cols = st.columns(len(cards))
    selected = None
    for i, c in enumerate(cards):
        if cols[i].button(c, key=f"{prefix}_{c}_{i}"):
            selected = c
    return selected

# Rồng
st.subheader("🐉 Rồng")
selected_r_top = render_row(cards_top, "r_top")
selected_r_bottom = render_row(cards_bottom, "r_bottom")
selected_r = selected_r_top or selected_r_bottom

# Hổ
st.subheader("🐯 Hổ")
selected_h_top = render_row(cards_top, "h_top")
selected_h_bottom = render_row(cards_bottom, "h_bottom")
selected_h = selected_h_top or selected_h_bottom

# Input
if selected_r and selected_h:
    order = cards_top + cards_bottom
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

# Control
col1, col2 = st.columns(2)
if col1.button("Undo") and st.session_state.history:
    st.session_state.history.pop()
    save_history(st.session_state.history)
if col2.button("Reset"):
    st.session_state.history = []
    save_history(st.session_state.history)

# Analysis
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

# History
st.divider()
st.subheader("📜 Lịch sử gần nhất")
last_display = [f"{d}-{t}({r})" for d,t,r in st.session_state.history[-20:]]
st.write(" | ".join(last_display))
st.caption("Lịch sử được lưu tự động. Mỗi máy có file riêng, không ảnh hưởng nhau.")