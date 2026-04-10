import streamlit as st
import json
import os

st.set_page_config(page_title="Dragon Tiger Tool", layout="wide")

DATA_FILE = "history.json"

# ================= LOAD DATA =================
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

# ================= SETTINGS =================
st.sidebar.header("⚙️ Cài đặt")
max_history = st.sidebar.number_input("Số ván lưu tối đa", 100, 5000, 600, step=100)
min_diff = st.sidebar.number_input("Độ lệch tối thiểu để đánh", 1, 10, 3)
min_sample = st.sidebar.number_input("Số mẫu tối thiểu", 1, 20, 3)

# ================= UI =================
st.title("🐉🐯 Dragon Tiger Tool")

cards_top = ['A','2','3','4','5','6','7']
cards_bottom = ['8','9','10','J','Q','K']

# ---------- STYLE ----------
st.markdown("""
<style>
input {
    text-align: center;
    font-size: 1.4rem !important;
    font-weight: 700 !important;
    width: 3rem !important;
    height: 2.5rem !important;
    margin: 0.2rem !important;
}
</style>
""", unsafe_allow_html=True)

# ---------- Hàm render bảng nhập ----------
def render_inputs(cards, prefix):
    cols = st.columns(len(cards))
    values = []
    for i, c in enumerate(cards):
        val = cols[i].text_input(c, key=f"{prefix}_{c}")
        values.append(val)
    return values

# ---------- RỒNG ----------
st.subheader("🐉 Rồng")
r_top = render_inputs(cards_top, "r_top")
r_bottom = render_inputs(cards_bottom, "r_bottom")
selected_r = "".join(r_top + r_bottom).strip()

# ---------- HỔ ----------
st.subheader("🐯 Hổ")
h_top = render_inputs(cards_top, "h_top")
h_bottom = render_inputs(cards_bottom, "h_bottom")
selected_h = "".join(h_top + h_bottom).strip()

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
            st.success(f"👉 DỰ BÁO: {suggestion}")
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