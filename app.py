"""
Interfață Streamlit care:
1) colectează descrieri de strategie de la participanți
2) lansează turnee Axelrod și arată clasamentul
Rulează cu:   streamlit run app.py
"""

import axelrod as axl
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

from utils import gepeto_to_player, gemini_to_player, load_players, run_tournament, get_team_mapping

st.set_page_config(page_title="Game of Trust", layout="centered")
st.title("🕹️ Game of Trust")

TURNEU = False

tab_submit, tab_tour = st.tabs(["Propune strategie", "Rulează turneu"])
    

# ------------------------------------------------------------------ #
with tab_submit:
    st.header("Propune o strategie nouă")

    team = st.text_input("Numele echipei")
    strat_name = st.text_input("Numele strategiei (identificator Python)")
    desc = st.text_area(
        "Descrierea strategiei (max ~250 cuvinte)",
        height=200,
        placeholder=(
            "Exemplu: Cooperez în prima rundă, apoi copiez ultima mutare a adversarului. "
            "Dacă adversarul trădează de două ori consecutiv, trădez și eu."
        ),
    )

    if st.button("💾 Salvează strategia", type="primary"):
        if not (team and strat_name and desc.strip()):
            st.error("Te rugăm să completezi toate câmpurile.")
        else:
            try:
                file_path = gemini_to_player(strat_name, desc, team)
                # file_path = gepeto_to_player(strat_name, desc, team)
                st.success(f"✔️ Strategia a fost generată și salvată în `{file_path.name}`.")
            except Exception as exc:
                st.exception(exc)


# ------------------------------------------------------------------ #
with tab_tour:
    if TURNEU:
        st.header("Rulează turneu")
        turns = st.number_input("Runde per joc", 50, 1000, value=200, step=50)
        reps = st.number_input("Repetiții per pereche", 1, 20, value=5, step=1)
        include_classics = st.checkbox(
            "Include strategii clasice (TitForTat, Defector, Cooperator)", value=True
        )

        if st.button("▶️ Rulează turneu"):
            extra = []
            if include_classics:
                extra = [axl.TitForTat(), axl.Defector(), axl.Cooperator()]

            try:
                players = load_players(extra_players=extra)
                if len(players) < 2:
                    st.warning("Ai nevoie de cel puțin două strategii pentru a porni turneul.")
                else:
                    results = run_tournament(players, turns=int(turns), repetitions=int(reps))

                    meta = get_team_mapping()

                    df = pd.DataFrame(
                    data = {
                        "Clasament": [row.Rank+1 for row in results.summarise()],
                        "Echipa": [meta.get(row.Name.strip().lower()) for row in results.summarise()],
                        "Strategie": [row.Name for row in results.summarise()],
                        "Scor mediu": [round(row.Median_score,2) for row in results.summarise()],
                        "Wins": [row.Wins for row in results.summarise()],
                        "CC": [f"{row.CC_rate:.0%}" for row in results.summarise()],
                        "CT": [f"{row.CD_rate:.0%}" for row in results.summarise()],
                        "TC": [f"{row.DC_rate:.0%}" for row in results.summarise()],
                        "TT": [f"{row.DD_rate:.0%}" for row in results.summarise()],
                    }

                    )

                    df_mine = pd.DataFrame(
                    data = {
                        "Scor mediu": [round(row.Median_score,2) for row in results.summarise()],
                        "Strategie": [row for row in results.ranked_names],
                    }    
                    )
                    st.subheader("Clasament")
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    st.bar_chart(df_mine.set_index("Strategie"))




            except Exception as exc:
                st.exception(exc)
    else:
        st.markdown("Un pic de răbdare până când toate echipele au o strategie...")
