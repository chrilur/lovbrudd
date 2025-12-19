import streamlit as st
import pandas as pd
from io import BytesIO
from st_aggrid import AgGrid, JsCode # La til JsCode her
import altair as alt
from pathlib import Path
from sidebar_utils import setup_page_header, add_sidebar_footer

#Passordsjekk
def sjekk_passord():
    """Returnerer True hvis brukeren har tastet inn riktig passord."""
    def passord_er_riktig():
        # Sjekker mot passordet vi lagrer i Streamlit Secrets
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Sletter passordet fra minnet etter bruk
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # Første gang: Vis inntastingsfelt
        st.text_input("Vennligst oppgi passord for å se statistikken", 
                      type="password", on_change=passord_er_riktig, key="password")
        return False
    elif not st.session_state["password_correct"]:
        # Feil passord tastet inn
        st.text_input("Feil passord. Prøv igjen", 
                      type="password", on_change=passord_er_riktig, key="password")
        st.error("😕 Passordet er feil")
        return False
    else:
        # Passordet er korrekt
        return True

# --- Kjør sjekken ---
if not sjekk_passord():
    st.stop()  # Stopper resten av appen fra å kjøre

# Konfigurasjon
st.set_page_config(page_title="Anmeldte lovbrudd i Norge", layout="wide")

setup_page_header()

@st.cache_data
def load_data():
    df = pd.read_csv("anmeldt_20-24.csv")
    
    # Finn det nyeste navnet for hvert kommunenummer
    latest_names = df.sort_values("år", ascending=False).drop_duplicates("komnr")
    name_map = dict(zip(latest_names["komnr"], latest_names["navn"]))
    df["visningsnavn"] = df["komnr"].map(name_map)
    
    # Gjør tall-kolonner numeriske, men VI BEHOLDER 'NaN' (ikke fyll med 0 ennå)
    crime_cols = ["eiendomstyveri", "vold_mishandling", "rusmidler", "orden_integritet", "trafikk", "annet", "alt"]
    for col in crime_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
    return df, crime_cols

df, kategorier = load_data()

# --- Sidebar ---

st.sidebar.header("Velg kommune")

kommuner_liste = sorted(df["visningsnavn"].unique().tolist())

if "Norge" in kommuner_liste:
    kommuner_liste.remove("Norge")
    kommuner_liste = ["Norge"] + kommuner_liste

valgt_kommune = st.sidebar.selectbox("", kommuner_liste)

display_map = {k: ("Totalt" if k == "alt" else k) for k in kategorier}
reverse_display_map = {v: k for k, v in display_map.items()}

valgte_visningsnavn = st.sidebar.multiselect(
    "Velg kategorier for grafen:",
    options=list(display_map.values()),
    default=["Totalt"]
)

valgte_kolonner = [reverse_display_map[v] for v in valgte_visningsnavn]
kommune_data = df[df["visningsnavn"] == valgt_kommune].sort_values("år")

# --- Diagram ---
st.title(f"Anmeldte lovbrudd i {valgt_kommune}")
# Undertittel med markdown for å styre stil
st.markdown(
    f"""
    <div style='font-size: 18px; color: #555; margin-top: -15px; margin-bottom: 20px;'>
        Toårige gjennomsnitt for lovbrudd begått i norske kommuner 2020–2024
    </div>
    """, 
    unsafe_allow_html=True
)
if valgte_kolonner:
    plot_data = kommune_data.set_index("år")[valgte_kolonner].rename(columns=display_map).fillna(0)
    plot_data = plot_data.reset_index().melt('år', var_name='Kategori', value_name='Antall')

    #Mellomrom som tusenseparator
    plot_data['Antall_str'] = plot_data['Antall'].apply(lambda x: f"{int(x):,}".replace(",", " "))

    base = alt.Chart(plot_data).encode(
        x=alt.X('år:N', title='Tidsperiode'),
        y=alt.Y('Antall:Q', title = 'Antall anmeldelser'),
        color='Kategori:N'
    )
    
    #Lag linjer
    lines = base.mark_line(
        strokeDash=[5, 5],
        interpolate='monotone'
    )

    #Punkter med tooltips
    points = base.mark_point(
        size=60,
        filled=True
    ).encode(
        tooltip=['år','Kategori', alt.Tooltip('Antall_str:N', title='Antall')]
    )

    #Legg lagene oppå hverandre
    chart = (lines + points).properties(width='container', height=400).interactive() 

    st.altair_chart(chart, use_container_width=True)

# --- Tabell med "Mangler data" og Integer-visning ---
st.subheader(f"Alle tall for {valgt_kommune}")

# JS-funksjon som sjekker om verdien er tom (null/NaN). 
# Hvis tom: Vis "Mangler data". Hvis tall: Vis som heltall (Math.floor).
valFormatter = JsCode("""
function(params) {
    if (params.value == null || isNaN(params.value)) {
        return 'Mangler data';
    }
    // Formaterer tallet med mellomrom (f.eks 10 000)
    return Math.floor(params.value).toString().replace(/\\B(?=(\\d{3})+(?!\\d))/g, " ");
}
""")

# Klargjør tabellen
visnings_df = kommune_data[["år", "alt"] + [k for k in kategorier if k != 'alt']].rename(columns={"alt": "Totalt"})

gridOptions = {
    "columnDefs": [
        {"field": "år", "headerName": "Tidsperiode", "pinned": "left", "sortable": True},
        {"field": "Totalt", "sortable": True, "valueFormatter": valFormatter, "cellStyle": {'font-weight': 'bold'}},
        {"field": "eiendomstyveri", "sortable": True, "valueFormatter": valFormatter},
        {"field": "vold_mishandling", "sortable": True, "valueFormatter": valFormatter},
        {"field": "rusmidler", "sortable": True, "valueFormatter": valFormatter},
        {"field": "orden_integritet", "sortable": True, "valueFormatter": valFormatter},
        {"field": "trafikk", "sortable": True, "valueFormatter": valFormatter},
        {"field": "annet", "sortable": True, "valueFormatter": valFormatter},
    ],
    "defaultColDef": {
        "flex": 1,
        "minWidth": 120,
        "resizable": True,
    },
    "domLayout": "autoHeight",
}

# --- Eksport ---
def to_excel(df_to_export):
    output = BytesIO()
    gyldige_kolonner = ["år", "Totalt", "eiendomstyveri", "vold_mishandling", "rusmidler", "orden_integritet", "trafikk", "annet"]
                       
    df_excel = df_to_export.copy() 
    df_excel = df_excel[[c for c in gyldige_kolonner if c in df_excel.columns]]

    for col in df_excel.columns:
        if col != "år":
            df_excel[col] = df_excel[col].apply(
                lambda x: int(x) if pd.notnull(x) and not isinstance(x, str) else "Mangler data")
            
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_excel.to_excel(writer, index=False)
    return output.getvalue()

with st.container():
    AgGrid(
        visnings_df,
        gridOptions=gridOptions,
        theme="streamlit",
        allow_unsafe_jscode=True, # Påkrevd for at valFormatter skal virke
        update_on=["modelUpdated", "filterChanged", "sortChanged"],
        fit_columns_on_grid_load=True,
    )
    st.download_button(
        f"📥 Last ned data for {valgt_kommune} (Excel)",
        to_excel(visnings_df),
        f"krimstat_{valgt_kommune}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

add_sidebar_footer()