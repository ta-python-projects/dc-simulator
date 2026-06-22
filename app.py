import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import streamlit as st
import io
import pandas as pd

# ★ Cloud で確実に動く日本語フォント
plt.rcParams["font.family"] = "Noto Sans CJK JP"


#-----------------------------------------
# DCシミュレーション関数
#-----------------------------------------
def simulate_dc(monthly, rate, years, initial=0, fee=0):
    if monthly < 0 or rate < 0 or years <= 0 or initial < 0 or fee < 0:
        raise ValueError("入力値が不正です")
    
    balance = float(initial)
    results = []

    monthly_rate = rate / 12

    # 年0（初期状態）
    results.append({"year": 0, "balance": int(balance)})

    for year in range(1, years + 1):
        for _ in range(12):
            balance += monthly
            balance -= fee
            balance *= (1 + monthly_rate)
        results.append({"year": year, "balance": int(balance)})
    
    return results


#-----------------------------------------
# Webアプリ UI
#-----------------------------------------
st.title("DCシミュレーション（Streamlit版）")
st.sidebar.header("入力パラメータ")

monthly = st.sidebar.number_input("毎月の積立額", value=20000, step=1000)

# 利率を％表示
rate_percent = st.sidebar.slider("利率（年利 %）", 0.0, 10.0, 3.0, 0.1)
rate = rate_percent / 100

years = st.sidebar.number_input("積立年数", value=20, step=1)
initial = st.sidebar.number_input("初期金額", value=0, step=10000)
fee = st.sidebar.number_input("毎月の手数料", value=170, step=10)

# テーマ切り替え
theme = st.sidebar.selectbox("テーマ", ["ダーク", "ライト"])

# タブ
tab1, tab2 = st.tabs(["📈 通常シミュレーション", "📊 利率比較（3%・4%・5%）"])


#-----------------------------------------
# 計算（通常モード用）
#-----------------------------------------
results = simulate_dc(monthly, rate, years, initial, fee)

years_list = [item["year"] for item in results]
balances = [item["balance"] for item in results]

# 初期金額を累計掛金に含める
cumulative = [initial + monthly * 12 * year for year in years_list]

years_np = np.array(years_list)
balances_np = np.array(balances)
cumulative_np = np.array(cumulative)

final_balance = balances_np[-1]
final_cumulative = cumulative_np[-1]
profit = final_balance - final_cumulative
profit_rate = profit / final_cumulative * 100


#-----------------------------------------
# 📊 タブ2：利率比較モード
#-----------------------------------------
with tab2:
    st.subheader("利率比較モード（3%・4%・5%）")

    base_principal = initial + monthly * 12 * years

    r_list = [0.03, 0.04, 0.05]
    labels = ["3%", "4%", "5%"]

    results_list = []
    for r in r_list:
        r_res = simulate_dc(monthly, r, years, initial, fee)
        fb = r_res[-1]["balance"]
        pf = fb - base_principal
        pr = pf / base_principal * 100
        results_list.append((fb, pf, pr))

    col1, col2, col3 = st.columns(3)
    (fb1, pf1, pr1), (fb2, pf2, pr2), (fb3, pf3, pr3) = results_list

    col1.metric("3% 最終残高", f"{fb1 // 10000:,} 万円", f"{pr1:.1f}%")
    col2.metric("4% 最終残高", f"{fb2 // 10000:,} 万円", f"{pr2:.1f}%")
    col3.metric("5% 最終残高", f"{fb3 // 10000:,} 万円", f"{pr3:.1f}%")

    if theme == "ダーク":
        plt.style.use("dark_background")
    else:
        plt.style.use("default")

    fig, ax = plt.subplots(figsize=(10, 5))

    cumulative_compare = [initial + monthly * 12 * year for year in range(years + 1)]
    ax.plot(range(years + 1), cumulative_compare, color="#FFB74D", linewidth=2, label="累計掛金")

    colors = ["#4FC3F7", "#66BB6A", "#EF5350"]

    for (r, label, color) in zip(r_list, labels, colors):
        res_r = simulate_dc(monthly, r, years, initial, fee)
        balances_r = [item["balance"] for item in res_r]
        ax.plot(range(years + 1), balances_r, marker="o", linewidth=2, color=color, label=f"運用残高（{label}）")

    ax.set_xlabel("年", fontsize=12)
    ax.set_ylabel("残高 (円)", fontsize=12)
    ax.set_title("利率比較シミュレーション", fontsize=14, fontweight="bold")
    ax.grid(True)
    ax.set_xlim(left=0)
    ax.set_xticks(range(0, years + 1, 1))
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"{int(x):,}"))
    ax.legend()
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=300, bbox_inches="tight")
    buf.seek(0)

    st.download_button(
        label="📥 比較グラフをPNGでダウンロード",
        data=buf,
        file_name="dc_compare.png",
        mime="image/png"
    )

    st.pyplot(fig)


#-----------------------------------------
# 📈 タブ1：通常シミュレーション
#-----------------------------------------
with tab1:
    st.subheader("通常シミュレーション")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("最終運用残高", f"{final_balance // 10000:,} 万円")
    col2.metric("積立総額", f"{final_cumulative // 10000:,} 万円")
    col3.metric("利益", f"{profit // 10000:,} 万円")
    col4.metric("利益率", f"{profit_rate:.1f} %")

    if theme == "ダーク":
        plt.style.use("dark_background")
    else:
        plt.style.use("default")

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(years_np, balances_np, marker="o", linewidth=2, color="#4FC3F7", label="運用残高")
    ax.plot(years_np, cumulative_np, linewidth=2, color="#FFB74D", label="累計掛金")

    ax.fill_between(
        years_np,
        balances_np,
        cumulative_np,
        where=(balances_np > cumulative_np),
        color="#1E88E5",
        alpha=1,
        label="利益エリア"
    )

    annotation_text = (
        f"最終運用残高: {final_balance:,} 円\n"
        f"積立総額: {final_cumulative:,} 円\n"
        f"利益: {profit:,} 円\n"
        f"利益率: {profit_rate:.1f}%"
    )

    ax.annotate(
        annotation_text,
        xy=(years_np[-1], balances_np[-1]),
        xytext=(years_np[-1] - years_np[-1] * 0.3, balances_np[-1] * 0.25),
        fontsize=13,
        color="black" if theme == "ライト" else "white",
        fontweight="bold",
        bbox=dict(
            boxstyle="round,pad=0.4",
            fc="white" if theme == "ライト" else "black",
            ec="black" if theme == "ライト" else "white",
            alpha=0.8
        ),
        arrowprops=dict(arrowstyle="->", color="black" if theme == "ライト" else "white")
    )

    ax.set_xlabel("年", fontsize=12)
    ax.set_ylabel("残高 (円)", fontsize=12)
    ax.set_title("DCシミュレーション結果", fontsize=14, fontweight="bold")
    ax.grid(True)
    ax.set_xlim(left=0)
    ax.set_xticks(range(min(years_list), max(years_list) + 1, 1))
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"{int(x):,}"))
    ax.legend()
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=300, bbox_inches="tight")
    buf.seek(0)

    st.download_button(
        label="📥 グラフをPNGでダウンロード",
        data=buf,
        file_name="dc_simulation.png",
        mime="image/png"
    )

    df = pd.DataFrame({
        "年": years_np,
        "運用残高": balances_np,
        "累計掛金": cumulative_np,
        "利益": balances_np - cumulative_np
    })

    csv = df.to_csv(index=False).encode("cp932")

    st.download_button(
        label="📄 CSVをダウンロード",
        data=csv,
        file_name="dc_simulation.csv",
        mime="text/csv"
    )

    st.pyplot(fig)
