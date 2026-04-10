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

cards_top = ['A','2','3','4','5','6','7']   # 7 nút hàng trên
cards_bottom = ['8','9','10','J','Q','K']  # 6 nút hàng dưới

# ---------- STYLE ----------
st.markdown("""
<style>
div[data-testid="stHorizontalBlock"] {
    flex-wrap: nowrap !important;   /* ép không cho xuống dòng */
    justify-content: center !important; /* căn giữa */
}
div[data-testid="stButton"] button {
    font-size: 32px !important;      /* chữ to hơn */
    font-weight: 900 !important;     /* đậm tối đa */
    color: #111 !important;
    height: 40px !important;         /* nút cao hơn */
    width: 48px !important;          /* nút rộng hơn */
    margin: 3px !important;
    text-shadow: 0px 0px 1px rgba(0,0,0,0.5); /* làm chữ nét hơn */
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

# ---------- Hàm render hàng ----------
def render_row(cards, prefix):
    cols = st.columns(len(cards))
    selected = None
    for i, c in enumerate(cards):
        if cols[i].button(c, key=f"{prefix}_{c}_{i}"):
            selected = c
    return selected

# ---------- RỒNG ----------
st.subheader("🐉 Rồng")
selected_r_top = render_row(cards_top, "r_top")
selected_r_bottom = render_row(cards_bottom, "r_bottom")
selected_r = selected_r_top or selected_r_bottom

# ---------- HỔ ----------
st.subheader("🐯 Hổ")
selected_h_top = render_row(cards_top, "h_top")
selected_h_bottom = render_row(cards_bottom, "h_bottom")
selected_h = selected_h_top or selected_h_bottom

# ================= INPUT =================
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