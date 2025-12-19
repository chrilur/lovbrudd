import streamlit as st

def setup_page_header(title=""):
    # CSS og Logo (kalles øverst på siden)
    st.markdown(
        """
        <style>
            .block-container { padding-top: 5rem !important; }
            [data-testid="stSidebarNavItems"] span {
                font-family: 'Helvetica', sans-serif !important;
                font-size: 16px !important;
                font-weight: 500 !important;
            }
            [data-testid="stImage"] img { border-radius: 0px !important; }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.image("logo.png", width=250)
    if title:
        st.title(title)
    #st.markdown("---")

def add_sidebar_footer():
    # Bunntekst (kalles nederst i skriptet)
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
        <div style='font-size: 14px; color: gray;'>
            <strong>Deskfolk:</strong><br>
            Christian Lura<br>
            Prosjektleder<br>
            christian.lura@nrk.no<br>
            416 77 177<br>
            <br>
            Laila Borge<br>
            Journalist<br>
            laila@lla.no<br>
            994 62 687<br>
            <br>
            Maja Aarbakke<br>
            Journalist<br>
            maja@lla.no<br>
            481 81 997<br>
            <br>
            Øivind Skjervheim<br>
            Journalist<br>
            oivind@lla.no<br>
            924 31 955<br>
            <br>
            Ida Harr Overland<br>
            Journalist<br>
            ida.harr.overland@nrk.no<br>
            932 29 611<br>
            <br>
            Per Christian Magnus<br>
            Reportasjeleder<br>
            per.magnus@uib.no<br>
            414 23 330<br>
            <br>
            Kristine Holmelid<br>
            Reportasjeleder<br>
            kristine.holmelid@uib.no<br>
            909 50 320<br>
        </div>
        """, 
        unsafe_allow_html=True
    )
    #st.sidebar.caption("Samarbeidsdesken / Christian Skaar Lura")