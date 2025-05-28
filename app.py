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

TURNEU = True

tab_reguli, tab_submit, tab_tour = st.tabs(["Prisoner's Dilema", "Propune strategie", "Turneu"])


# ------------------------------------------------------------------ #
with tab_reguli:
    st.header("Prisoner's Dilema")
    st.markdown("Dilema prizonierului este un concept clasic din teoria jocurilor care ilustrează cum doi indivizi raționali pot alege să nu coopereze, chiar dacă colaborarea le-ar aduce un rezultat mai bun. Situația implică doi suspecți arestați separat, care pot alege să mărturisească sau să tacă. Dacă amândoi tac, primesc pedepse ușoare. Dacă unul mărturisește iar celălalt tace, cel care mărturisește scapă, iar celălalt primește o pedeapsă grea. Dacă amândoi mărturisesc, ambii primesc pedepse moderate. Paradoxul evidențiază tensiunea dintre interesul individual și binele comun.")

    st.subheader("Reguli")
    st.markdown("""
    Fiecare „jucător” are o strategie care decide dacă va coopera sau trăda în fiecare rundă. Jocul se bazează pe dilema prizonierului repetată - adică jucătorii joacă același joc de mai multe ori și își pot adapta comportamentul în funcție de rundele anterioare.
    Reguli de bază:
    Fiecare rundă, ambii jucători aleg: Cooperare (C) sau Trădare (T).
    În funcție de alegeri, se acordă puncte:""")
    
    st.image("imagini/infografic.png")

    st.markdown("""
    Explicație puncte:
    Amândoi cooperează → fiecare primește 2 puncte.
    Unul trădează, celălalt cooperează → trădătorul ia 3 puncte, celălalt -1.
    Amândoi trădează → fiecare ia 0 puncte.
    Jocul se repetă de mai multe ori, iar scorurile se adună. Scopul este să obții cât mai multe puncte
                """)

# ------------------------------------------------------------------ #
with tab_submit:
    st.header("Propune o strategie nouă")

    team = st.text_input("Numele echipei (fără diacritice)")
    strat_name = st.text_input("Numele strategiei (fără spații, fără diacritice)")
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
            "Include strategii clasice (TitForTat, Defector, Cooperator)", value=True, key=11
        )
        include_extras = st.checkbox(
            "Include strategiile (TitForTwoTats, Grudger, Random)", value=True, key=22
        )

        if st.button("▶️ Rulează turneu"):
            extra = []
            if include_classics:
                extra = [axl.TitForTat(), axl.Defector(), axl.Cooperator()]
            if include_extras:
                extra.extend([axl.TitFor2Tats(), axl.Grudger(), axl.Random()])

            try:
                players = load_players(extra_players=extra)
                
                if len(players) < 2:
                    st.warning("Ai nevoie de cel puțin două strategii pentru a porni turneul.")
                else:

                    # 1. Define your custom payoff values for R, S, T, P
                    R_custom = 2  # Reward for mutual cooperation
                    S_custom = -1 # Sucker's payoff (your score if you C, opponent D)
                    T_custom = 3  # Temptation payoff (your score if you D, opponent C)
                    P_custom = 0  # Punishment for mutual defection

                    # 2. Create your custom Game instance
                    custom_game = axl.Game(r=R_custom, s=S_custom, t=T_custom, p=P_custom)

                    # 3. SET YOUR CUSTOM GAME AS THE GLOBAL DEFAULT
                    #    This is the crucial step for run_tournament to use your game.

                    tournament = axl.Tournament(
                        players,
                        turns=int(turns),
                        repetitions=int(reps),
                        game=custom_game # <--- This is where your custom game is applied
                    )
                    results = tournament.play() # Call the play method on the instance

                    # results = run_tournament(players, turns=int(turns), repetitions=int(reps))

                    print(results.summarise())

                    meta = get_team_mapping()

                    df = pd.DataFrame(
                    data = {
                        "Rank": [row.Rank+1 for row in results.summarise()],
                        "Echipa": [meta.get(row.Name.strip().lower().replace(" ", "")) for row in results.summarise()],
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
