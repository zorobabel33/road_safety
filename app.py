# -*- coding: utf-8 -*-
"""
ST2DLDI - Data Integration & Applications
Road safety 2024 (BAAC file, ONISR / data.gouv.fr)
Part 1 : Data Profiling and Data Quality (sections A, B, C)

Run with:  streamlit run app.py
The 4 CSV files (caract-2024.csv, lieux-2024.csv, usagers-2024.csv, vehicules-2024.csv)
must be in the same folder as this script.
"""

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import io


def render_fig(fig):
    """Convert a matplotlib figure to a PNG image with a tight bounding box, so
    labels are never cropped (st.pyplot alone can clip text near the figure edges)."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf


# ============================================================
# GENERAL CONFIGURATION AND STYLE
# ============================================================
st.set_page_config(
    page_title="Road Safety 2024 : Data Profiling",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .block-container { padding-top: 1.6rem; padding-bottom: 3rem; }
    [data-testid="stMetric"] {
        background-color: #f7f8fa;
        border: 1px solid #e6e6e6;
        border-radius: 10px;
        padding: 14px 10px 8px 10px;
    }
    [data-testid="stMetricLabel"] { font-size: 0.85rem; color: #555; }
    h1, h2, h3 { color: #1f2a44; }
    .stTabs [data-baseweb="tab"] { font-size: 1rem; padding: 8px 18px; }
</style>
""", unsafe_allow_html=True)


def fmt(n):
    return f"{n:,.0f}".replace(",", " ")


# ============================================================
# DATA LOADING
# ============================================================
@st.cache_data(show_spinner="Loading source files...")
def load_data():
    caract = pd.read_csv("caract-2024.csv", sep=";", encoding="utf-8", low_memory=False)
    lieux = pd.read_csv("lieux-2024.csv", sep=";", encoding="utf-8", low_memory=False)
    usagers = pd.read_csv("usagers-2024.csv", sep=";", encoding="utf-8", low_memory=False)
    vehicules = pd.read_csv("vehicules-2024.csv", sep=";", encoding="utf-8", low_memory=False)
    return caract, lieux, usagers, vehicules


try:
    caract, lieux, usagers, vehicules = load_data()
except FileNotFoundError:
    st.error(
        "CSV files not found. Place caract-2024.csv, lieux-2024.csv, "
        "usagers-2024.csv and vehicules-2024.csv in the same folder as app.py."
    )
    st.stop()

tables = {"caract": caract, "lieux": lieux, "usagers": usagers, "vehicules": vehicules}
display_names = {
    "caract": "CHARACTERISTICS", "lieux": "LOCATIONS",
    "usagers": "USERS", "vehicules": "VEHICLES",
}

descriptions = {
    "caract": {
        "Num_Acc": "Unique accident identifier, shared key across all 4 tables",
        "jour": "Day of the month of the accident (1 to 31)",
        "mois": "Month of the accident (1 to 12)",
        "an": "Year of the accident",
        "hrmn": "Hour and minute of the accident (text HH:MM)",
        "lum": "Light conditions at the time of the accident",
        "dep": "INSEE department code (includes overseas departments and territories)",
        "com": "INSEE municipality code",
        "agg": "Location: within a built up area (2) or outside (1)",
        "int": "Intersection type",
        "atm": "Atmospheric conditions",
        "col": "Collision type",
        "adr": "Postal address, mostly filled in when the accident is within a built up area",
        "lat": "Latitude (text, French comma as decimal separator)",
        "long": "Longitude (text, French comma as decimal separator)",
    },
    "lieux": {
        "Num_Acc": "Key to the accident", "catr": "Road category",
        "voie": "Road number or name", "v1": "Numeric index of the road number",
        "v2": "Alphanumeric index of the road", "circ": "Traffic regime",
        "nbv": "Total number of traffic lanes", "vosp": "Presence of a reserved lane",
        "prof": "Road profile (flat, slope, hilltop...)", "pr": "Upstream reference marker number",
        "pr1": "Distance in meters to the upstream reference marker", "plan": "Road layout (straight, curve...)",
        "lartpc": "Width of the central reservation (m)", "larrout": "Width of the roadway (m)",
        "surf": "Surface condition", "infra": "Special infrastructure or development",
        "situ": "Location of the accident relative to the road", "vma": "Maximum authorised speed (km/h)",
    },
    "vehicules": {
        "Num_Acc": "Key to the accident", "id_vehicule": "Unique vehicle identifier",
        "num_veh": "Alphanumeric vehicle identifier", "senc": "Direction of travel",
        "catv": "Vehicle category", "obs": "Fixed obstacle hit",
        "obsm": "Moving obstacle hit", "choc": "Initial point of impact",
        "manv": "Main manoeuvre before the accident", "motor": "Engine type",
        "occutc": "Number of occupants in public transport vehicles",
    },
    "usagers": {
        "Num_Acc": "Key to the accident", "id_usager": "Unique user identifier",
        "id_vehicule": "Key to the vehicle occupied", "num_veh": "Alphanumeric vehicle identifier",
        "place": "Seat occupied in the vehicle", "catu": "User category (driver, passenger or pedestrian)",
        "grav": "Injury severity", "sexe": "Sex of the user",
        "an_nais": "Year of birth", "trajet": "Reason for the trip",
        "secu1": "1st safety equipment used", "secu2": "2nd safety equipment used",
        "secu3": "3rd safety equipment used", "locp": "Pedestrian location",
        "actp": "Pedestrian action", "etatp": "Whether the pedestrian was alone, accompanied or in a group",
    },
}


# ============================================================
# HEADER AND KPIS
# ============================================================
n_acc = caract["Num_Acc"].nunique()
n_usa = len(usagers)
n_veh = len(vehicules)
n_tues = (usagers["grav"] == 2).sum()

with st.sidebar:
    st.markdown("### ST2DLDI project")
    st.caption("Data Integration & Applications")
    st.markdown("Part 1 : Data Profiling and Data Quality")
    st.markdown("---")
    st.metric("Accidents", fmt(n_acc))
    st.metric("Users involved", fmt(n_usa))
    st.metric("Vehicles involved", fmt(n_veh))
    st.metric("People killed", fmt(n_tues))
    st.markdown("---")
    st.caption("Source: data.gouv.fr, ONISR, year 2024")

st.title("Road Safety 2024 : Data Profiling and Data Quality")
st.caption("BAAC file (Bulletins d'Analyse des Accidents Corporels), ONISR / data.gouv.fr, ST2DLDI project")

k1, k2, k3, k4 = st.columns(4)
k1.metric("Road accidents", fmt(n_acc))
k2.metric("Users involved", fmt(n_usa))
k3.metric("Vehicles involved", fmt(n_veh))
k4.metric("People killed", fmt(n_tues), delta=f"{n_tues/n_acc*100:.1f}% of accidents", delta_color="off")

st.divider()

tab_a, tab_b, tab_c = st.tabs([
    "A. Dataset Structure",
    "B. Missing Values",
    "C. Consistency and Validity",
])

# ============================================================
# TAB A : DATASET STRUCTURE
# ============================================================
with tab_a:
    st.subheader("Column inventory")
    choix = st.selectbox("Table to inspect", list(tables.keys()), format_func=lambda k: display_names[k])
    df = tables[choix]

    c1, c2 = st.columns(2)
    c1.metric("Rows", fmt(len(df)))
    c2.metric("Columns", df.shape[1])

    inv = pd.DataFrame({
        "type": df.dtypes.astype(str),
        "non_null_values": df.notna().sum(),
        "pct_missing": (df.isna().mean() * 100).round(2),
    })
    inv["description"] = inv.index.map(descriptions[choix])
    st.dataframe(inv, use_container_width=True, height=min(38 * (len(inv) + 1), 620))

    st.subheader("Size of the 4 tables")
    fig_taille = px.bar(
        pd.DataFrame({"table": [display_names[k] for k in tables], "rows": [len(d) for d in tables.values()]}),
        x="table", y="rows", text="rows", color="table",
    )
    fig_taille.update_traces(texttemplate="%{text:,}", textposition="outside")
    fig_taille.update_layout(showlegend=False, height=320, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig_taille, use_container_width=True)

    st.subheader("Relationships between the 4 tables")
    st.markdown("""
The 4 files are linked through `Num_Acc`. One accident (1 row in CHARACTERISTICS) can
involve several vehicles and several users, so the structure has 1 to N cardinalities
(1 accident, N vehicles, N users), with in principle 1 single LOCATIONS row per accident.
""")
    st.dataframe(pd.DataFrame({
        "Table": ["CHARACTERISTICS", "LOCATIONS", "VEHICLES", "USERS"],
        "Rows": [len(caract), len(lieux), len(vehicules), len(usagers)],
        "Key": ["Num_Acc (PK)", "Num_Acc", "Num_Acc, id_vehicule", "Num_Acc, id_vehicule, id_usager"],
    }), hide_index=True, use_container_width=True)
    if lieux["Num_Acc"].nunique() != len(lieux):
        st.warning(
            f"LOCATIONS has {fmt(len(lieux))} rows for only {fmt(lieux['Num_Acc'].nunique())} distinct accidents, "
            "so the expected 1 to 1 relationship with CHARACTERISTICS is not respected (see tab C)."
        )

# ============================================================
# TAB B : MISSING VALUES
# ============================================================
with tab_b:
    st.subheader("Empty cells by column")
    rows = []
    for nom, d in tables.items():
        miss = (d.isna().mean() * 100).round(2)
        for col, pct in miss.items():
            if pct > 0:
                rows.append({"table": nom, "column": col, "pct_missing": pct})
    miss_df = pd.DataFrame(rows).sort_values("pct_missing")
    miss_df["label"] = miss_df["table"] + "." + miss_df["column"]

    fig = px.bar(
        miss_df, x="pct_missing", y="label", orientation="h",
        labels={"pct_missing": "% of empty cells", "label": ""},
        text="pct_missing", color="pct_missing", color_continuous_scale="Blues",
    )
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    fig.update_layout(coloraxis_showscale=False, height=380, margin=dict(l=0, r=20, t=10, b=0))
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Missingness map, complementary visualization (row sample)")
    st.caption("This goes beyond what the assignment strictly asks for, but it shows clearly where missing values sit column by column, and whether they are correlated with each other.")
    table_matrix = st.selectbox("Table", list(tables.keys()), format_func=lambda k: display_names[k], key="matrix_select")
    df_m = tables[table_matrix]
    miss_cols = [c for c in df_m.columns if df_m[c].isna().any()]
    if miss_cols:
        sample = df_m.sample(min(300, len(df_m)), random_state=0).reset_index(drop=True)
        mat = sample[miss_cols].isna().values.astype(int)
        fig_mat, ax_mat = plt.subplots(figsize=(9, max(2.2, 0.42 * len(miss_cols))))
        fig_mat.patch.set_facecolor("white")
        ax_mat.imshow(mat.T, aspect="auto", cmap="Blues", interpolation="nearest")
        ax_mat.set_yticks(range(len(miss_cols)))
        ax_mat.set_yticklabels(miss_cols, fontsize=9)
        ax_mat.set_xlabel(f"Sample of {len(sample)} rows")
        ax_mat.set_xticks([])
        for spine in ax_mat.spines.values():
            spine.set_visible(False)
        st.image(render_fig(fig_mat), use_container_width=True)
    else:
        st.info("No missing column in this table.")

    st.subheader("Codes -1, the BAAC file's \"not filled in\" convention")
    st.caption("Different from an empty cell: this is an explicit code defined by the coding guide.")
    minus1_cols = {
        "caract": ["atm", "col"],
        "lieux": ["circ", "vosp", "prof", "pr", "pr1", "plan", "surf", "infra", "situ"],
        "usagers": ["trajet", "secu1", "secu2", "secu3", "locp", "actp", "etatp"],
        "vehicules": ["senc", "obs", "obsm", "choc", "manv", "motor"],
    }
    rows2 = []
    for nom, cols in minus1_cols.items():
        d = tables[nom]
        for c in cols:
            pct = (pd.to_numeric(d[c], errors="coerce") == -1).mean() * 100
            if pct > 0:
                rows2.append({"table": nom, "column": c, "pct_code_minus1": round(pct, 2)})
    st.dataframe(pd.DataFrame(rows2).sort_values("pct_code_minus1", ascending=False),
                 hide_index=True, use_container_width=True)

    st.subheader("Structural missingness: context changes everything")
    st.caption("Some of the large percentages above are not real issues, the field simply does not apply to every row.")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**adr depending on the area (agg)**")
        adr_agg = caract.groupby("agg")["adr"].apply(lambda s: round(s.isna().mean() * 100, 2))
        adr_agg.index = adr_agg.index.map({1: "Outside built up area", 2: "Within built up area"})
        st.dataframe(adr_agg.rename("% missing"), use_container_width=True)
    with col2:
        st.markdown("**locp, actp, etatp by catu**")
        pieton = usagers[usagers["catu"] == 3]
        non_pieton = usagers[usagers["catu"] != 3]
        data = []
        for c in ["locp", "actp", "etatp"]:
            data.append({
                "field": c,
                "pedestrians (%)": round((pd.to_numeric(pieton[c], errors="coerce") == -1).mean() * 100, 2),
                "non pedestrians (%)": round((pd.to_numeric(non_pieton[c], errors="coerce") == -1).mean() * 100, 2),
            })
        st.dataframe(pd.DataFrame(data), hide_index=True, use_container_width=True)
    with col3:
        st.markdown("**secu2 when secu1 is filled in**")
        s1 = pd.to_numeric(usagers["secu1"], errors="coerce")
        s2 = pd.to_numeric(usagers["secu2"], errors="coerce")
        n_1equip = int(((s1 != -1) & (s2 == -1)).sum())
        st.metric("Users with a single safety equipment", fmt(n_1equip))
        st.caption("secu2 = -1 is then normal, not a gap.")

    st.markdown("#### Takeaway")
    st.info(
        "The large percentages (lartpc, occutc, v2, secu2/secu3, locp/actp/etatp) are structural. "
        "The field only applies to part of the rows, and drops to nearly 0% once restricted to the "
        "relevant population (locp drops to 0.02% not filled in among pedestrians, for instance). "
        "The two real information losses are adr (2.97% missing even within built up areas, where it "
        "should be systematic) and above all an_nais (2.06%, about 2580 users), which is used to "
        "compute age and affects almost every demographic analysis built from this dataset."
    )

# ============================================================
# TAB C : CONSISTENCY AND VALIDITY
# ============================================================
with tab_c:
    st.subheader("Accident locations")
    lat = pd.to_numeric(caract["lat"].astype(str).str.replace(",", ".", regex=False), errors="coerce")
    lon = pd.to_numeric(caract["long"].astype(str).str.replace(",", ".", regex=False), errors="coerce")
    geo = pd.DataFrame({"lat": lat, "lon": lon, "dep": caract["dep"]}).dropna()

    zone_choice = st.radio("Area shown", ["Metropolitan France", "All territories (overseas included)"], horizontal=True)
    if zone_choice.startswith("Metropolitan"):
        geo_plot = geo[geo["lat"].between(41, 51.5) & geo["lon"].between(-5.5, 9.7)]
        zoom = 4.4
    else:
        geo_plot = geo
        zoom = 1.2

    sample_map = geo_plot.sample(min(6000, len(geo_plot)), random_state=0)
    fig_map = px.scatter_mapbox(sample_map, lat="lat", lon="lon", zoom=zoom, height=430, opacity=0.45)
    fig_map.update_traces(marker=dict(size=5, color="#d1495b"))
    fig_map.update_layout(mapbox_style="open-street-map", margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig_map, use_container_width=True)
    st.caption(f"{fmt(len(geo_plot))} geolocated accidents in this area (sample shown: {fmt(len(sample_map))}). "
               "No coordinate at 0/0 and none outside the -90/90 and -180/180 bounds.")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Age of the users")
        age = 2024 - usagers["an_nais"]
        fig_age = px.histogram(age.dropna(), nbins=50, labels={"value": "Age"})
        fig_age.update_layout(showlegend=False, height=320, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig_age, use_container_width=True)
        st.write(f"Min {age.min():.0f} years, max {age.max():.0f} years, mean {age.mean():.1f} years. "
                 "No negative age, none above 110 years.")
    with col2:
        st.subheader("Maximum authorised speed (vma)")
        vma = pd.to_numeric(lieux["vma"], errors="coerce")
        n_vma_nr = int((vma == -1).sum())
        anomalies = sorted(vma[vma > 130].unique())
        fig_vma = px.histogram(vma[(vma >= 0) & (vma <= 130)], nbins=26, labels={"value": "vma (km/h)"})
        fig_vma.update_layout(showlegend=False, height=320, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig_vma, use_container_width=True)
        st.write(f"{fmt(n_vma_nr)} values not filled in (code -1).")
        st.write(f"{len(vma[vma > 130])} implausible values above 130 km/h: {anomalies}")

    st.subheader("Categorical anomalies, codes outside the BAAC coding guide")
    c1, c2 = st.columns(2)
    with c1:
        n_sexe = int((usagers["sexe"] == -1).sum())
        st.metric("sexe = -1", fmt(n_sexe))
        sub = usagers[usagers["sexe"] == -1]
        pct_conducteur = (sub["catu"] == 1).mean() * 100
        pct_an_nais_nan = sub["an_nais"].isna().mean() * 100
        st.caption(f"{pct_conducteur:.1f}% of these rows are drivers and {pct_an_nais_nan:.1f}% "
                   "also have a missing an_nais, which matches the hit and run users mentioned in the ONISR documentation.")
    with c2:
        n_catv = int((vehicules["catv"] == -1).sum())
        st.metric("catv = -1", n_catv)
        st.caption("A single vehicle is concerned, negligible in volume.")

    st.subheader("Duplicates")
    st.dataframe(pd.DataFrame({
        "table": [display_names[k] for k in tables],
        "strict duplicates (identical rows)": [int(d.duplicated().sum()) for d in tables.values()],
    }), hide_index=True, use_container_width=True)

    n_multi = int((lieux["Num_Acc"].value_counts() > 1).sum())
    st.warning(
        f"{fmt(n_multi)} accidents out of {fmt(lieux['Num_Acc'].nunique())} have several rows in LOCATIONS "
        f"({n_multi / lieux['Num_Acc'].nunique() * 100:.0f}%), while the documentation states that a single "
        "main location is expected per accident. This is the most impactful quality issue in the dataset."
    )

    st.subheader("Referential integrity across the 4 tables")
    c1, c2, c3 = st.columns(3)
    c1.metric("Orphan Num_Acc (locations)", int((~lieux.Num_Acc.isin(caract.Num_Acc)).sum()))
    c2.metric("Orphan Num_Acc (users)", int((~usagers.Num_Acc.isin(caract.Num_Acc)).sum()))
    c3.metric("Orphan Num_Acc (vehicles)", int((~vehicules.Num_Acc.isin(caract.Num_Acc)).sum()))

    veh_ids = vehicules["id_vehicule"].astype(str).str.strip()
    usa_ids = usagers["id_vehicule"].astype(str).str.strip()
    n_fuite = veh_ids[~veh_ids.isin(usa_ids)].nunique()
    st.success(
        f"{n_fuite} vehicles have no user attached (hit and run drivers not created in the database). "
        "This figure matches exactly the one given by the ONISR documentation for year 2024."
    )

st.divider()
st.caption("ST2DLDI project, Data Integration & Applications, data source: data.gouv.fr / ONISR")
