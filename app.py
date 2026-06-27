import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

#-----------------------------------------
# DCシミュレーション関数
#-----------------------------------------
def simulate_dc(monthly, rate, years, initial=0, fee=0):
    balance = float(initial)
    results = []

    monthly_rate = rate / 12

    results.append({"year": 0, "balance": int(balance)})

    for year in range(1, years + 1):
        for _ in range(12):
            balance += monthly
            balance -= fee
            balance *= (1 + monthly_rate)
        results.append({"year": year, "balance": int(balance)})
    
    return results


#-----------------------------------------
# UI
#-----------------------------------------
st.title("DCシミュレーション（Plotly版）")
st.sidebar.header("入力パラメータ")

monthly = st.sidebar.number_input("毎月の積立額", value=20000, step=1000)
rate_percent = st.sidebar.slider("利率（年利 %）", 0.0, 10.0, 3.0, 0.1)
rate = rate_percent / 100
years = st.sidebar.number_input("積立年数", value=20, step=1)
initial = st.sidebar.number_input("初期金額", value=0, step=10000)
fee = st.sidebar.number_input("毎月の手数料", value=170, step=10)

tab1, tab2 = st.tabs(["📈 通常シミュレーション", "📊 利率比較（3%・4%・5%）"])


#-----------------------------------------
# 計算
#-----------------------------------------
results = simulate_dc(monthly, rate, years, initial, fee)

years_list = [item["year"] for item in results]
balances = [item["balance"] for item in results]
cumulative = [initial + monthly * 12 * year for year in years_list]

final_balance = balances[-1]
final_cumulative = cumulative[-1]
profit = final_balance - final_cumulative
profit_rate = profit / final_cumulative * 100


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

fig = go.Figure()

# ① 累計掛金（下側の線）
fig.add_trace(go.Scatter(
    x=years_list,
    y=cumulative,
    mode="lines",
    name="累計掛金",
    line=dict(color="#FFB74D", width=3)
))

# ② 運用残高（上側の線）＋ 塗りつぶし
fig.add_trace(go.Scatter(
    x=years_list,
    y=balances,
    mode="lines+markers",
    name="運用残高",
    line=dict(color="#4FC3F7", width=3) ,
    fill='tonexty',              # ← これが塗りつぶし
    fillcolor='rgba(30,136,229,0.3)'  # ← 色（青系・透明度30%）
))

fig.update_layout(
    title="DCシミュレーション結果",
    xaxis_title="年",
    yaxis_title="残高（円）",
    hovermode="x unified",
    template="plotly_white"
)


    st.plotly_chart(fig, use_container_width=True)

    df = pd.DataFrame({
        "年": years_list,
        "運用残高": balances,
        "累計掛金": cumulative,
        "利益": np.array(balances) - np.array(cumulative)
    })

    st.download_button(
        label="📄 CSVをダウンロード",
        data=df.to_csv(index=False).encode("cp932"),
        file_name="dc_simulation.csv",
        mime="text/csv"
    )


#-----------------------------------------
# 📊 タブ2：利率比較
#-----------------------------------------
with tab2:
    st.subheader("利率比較モード（3%・4%・5%）")

    r_list = [0.03, 0.04, 0.05]
    labels = ["3%", "4%", "5%"]

    fig2 = go.Figure()

    cumulative_compare = [initial + monthly * 12 * year for year in range(years + 1)]
    fig2.add_trace(go.Scatter(
        x=list(range(years + 1)),
        y=cumulative_compare,
        mode="lines",
        name="累計掛金",
        line=dict(color="#FFB74D", width=3)
    ))

    for r, label in zip(r_list, labels):
        res_r = simulate_dc(monthly, r, years, initial, fee)
        balances_r = [item["balance"] for item in res_r]

        fig2.add_trace(go.Scatter(
            x=list(range(years + 1)),
            y=balances_r,
            mode="lines+markers",
            name=f"運用残高（{label}）"
        ))

    fig2.update_layout(
        title="利率比較シミュレーション（3%・4%・5%）",
        xaxis_title="年",
        yaxis_title="残高（円）",
        hovermode="x unified",
        template="plotly_white"
    )

    st.plotly_chart(fig2, use_container_width=True)
