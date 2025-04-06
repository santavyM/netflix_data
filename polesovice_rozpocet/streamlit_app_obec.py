import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go

st.set_page_config(page_title="Obecní rozpočet - Příjmy", layout="wide")
st.title("📈 Analýza příjmů obce")

uploaded_file = st.file_uploader("Nahraj soubor 'prijmy_2024.xlsx'", type="xlsx")

if uploaded_file:
    df_raw = pd.read_excel(uploaded_file, sheet_name=0, header=None)
    df = pd.read_excel(uploaded_file, sheet_name=0, skiprows=10)

    df = df.rename(columns={
        df.columns[0]: "Obec",
        df.columns[1]: "Třída",
        df.columns[2]: "Seskupení položek",
        df.columns[3]: "Podseskupení položek",
        df.columns[4]: "Položka",
        df.columns[5]: "Schválený 2024",
        df.columns[6]: "Po změnách 11.2024",
        df.columns[7]: "Skutečnost 11.2024"
    })

    df = df[df["Skutečnost 11.2024"].notna()]
    df["Skutečnost 11.2024"] = pd.to_numeric(df["Skutečnost 11.2024"], errors="coerce")

    # Celkové příjmy
    total_income = df["Skutečnost 11.2024"].sum()
    st.markdown(f"### 💵 Celkové příjmy: **{total_income:,.0f} Kč**")

    st.subheader("💰 Top 10 příjmových položek")
    top_income = df.sort_values("Skutečnost 11.2024", ascending=False).head(10)
    st.dataframe(top_income, use_container_width=True)

    st.subheader("🍪 Rozložení největších příjmů")
    fig1, ax1 = plt.subplots()
    wedges, texts, autotexts = ax1.pie(
        top_income["Skutečnost 11.2024"],
        labels=top_income["Položka"].fillna("Neznámá"),
        autopct=lambda pct: f"{pct:.1f} %",
        startangle=90,
        textprops={"fontsize": 10}
    )
    for i, a in enumerate(autotexts):
        value = top_income.iloc[i]["Skutečnost 11.2024"]
        a.set_text(f"{value:,.0f} Kč")
    ax1.axis("equal")
    st.pyplot(fig1)

    st.subheader("📊 Příjmy podle třídy")
    tclass = df.groupby("Třída")[["Skutečnost 11.2024"]].sum().sort_values("Skutečnost 11.2024", ascending=False)
    st.bar_chart(tclass)

    st.subheader("📋 Podle seskupení položek")
    sgroup = df.groupby("Seskupení položek")[["Skutečnost 11.2024"]].sum().sort_values("Skutečnost 11.2024", ascending=False).head(10)
    st.bar_chart(sgroup)

    st.subheader("🔀 Sankey diagram – Tok příjmů")
    df_sankey = df[df["Skutečnost 11.2024"].notna()].copy()
    df_sankey["Třída"] = df_sankey["Třída"].fillna("Neznámá")
    df_sankey["Seskupení položek"] = df_sankey["Seskupení položek"].fillna("Neznámé")

    sankey_data = df_sankey.groupby(["Třída", "Seskupení položek"])["Skutečnost 11.2024"].sum().reset_index()
    sankey_data["Skutečnost 11.2024"] = sankey_data["Skutečnost 11.2024"].round(2)

    all_nodes = list(set(sankey_data["Třída"].tolist() + sankey_data["Seskupení položek"].tolist()))
    node_map = {name: i for i, name in enumerate(all_nodes)}

    source = sankey_data["Třída"].map(node_map)
    target = sankey_data["Seskupení položek"].map(node_map)
    values = sankey_data["Skutečnost 11.2024"]
    labels = [f"{row['Třída']} → {row['Seskupení položek']}: {row['Skutečnost 11.2024']:.0f} Kč" for _, row in sankey_data.iterrows()]

    fig_sankey = go.Figure(data=[go.Sankey(
        arrangement="snap",
        node=dict(
            pad=20,
            thickness=25,
            line=dict(color="black", width=0.5),
            label=all_nodes,
            color="#3A86FF"
        ),
        link=dict(
            source=source,
            target=target,
            value=values,
            color="rgba(58,134,255,0.4)",
            label=labels,
            hovertemplate="%{label}<extra></extra>",
        )
    )])

    fig_sankey.update_layout(
        title_text="💶 Tok příjmů obce (Sankey)",
        font=dict(size=16, color="black"),
        height=900
    )
    st.plotly_chart(fig_sankey, use_container_width=True)

else:
    st.info("Prosím nahraj Excelový soubor s příjmy obce. Měl by obsahovat list s tabulkou příjmů od 10. řádku.")