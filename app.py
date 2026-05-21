import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os

# Configura la pagina della Web App
st.set_page_config(page_title="Overshoot Day App", page_icon="🌍", layout="wide")

# Creiamo due colonne: la prima prende l'80% dello spazio, la seconda il 20%
col_testo, col_img = st.columns([4, 1])

with col_testo:
    st.title("🌍 Earth Overshoot Day Tracker")
    st.write("Benvenuto nella dashboard interattiva per tracciare lo spostamento dell'Overshoot Day nel tempo.")

with col_img:
    # Immagine in alto a destra (usiamo un URL web come esempio)
    st.image("https://upload.wikimedia.org/wikipedia/commons/2/22/Earth_Western_Hemisphere_transparent_background.png", width=120)

# --- Pop-up con informazioni aggiuntive ---
with st.expander("Clicca qui per maggiori informazioni sulle metriche"):
    st.markdown(
        """
        | Metrica                    | Descrizione                                                                                                                                     | Esempio pratico                                                                                                                    |
        | :------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------ | :---------------------------------------------------------------------------------------------------------------------------------- |
        | **Giorno di sovraelongazione (overshoot day)** | È il giorno in cui un Paese o il pianeta ha già utilizzato tutte le risorse naturali che dovrebbero consumare in un anno. Da lì in poi va “a debito”.  | Se l'Italia arriva all'Overshoot Day a maggio, per il resto dell'anno consuma più di quanto il suo territorio riesca a rigenerare. |
        | **Biocapacità**                | È la quantità di risorse che un territorio riesce a produrre e a rinnovare da solo.                                                                     | Boschi, campi coltivati ​​e mari produttivi aumentano la biocapacità.                                                              |
        | **Impronta Ecologica**     | È quanto “costa” alla natura il nostro stile di vita: quanta superficie serve per produrre quello che consumiamo e assorbire i rifiuti che produciamo. | Più auto, più energia, più carne, più sprechi = impronta ecologica più alta.                                                       |
        | **Gha**                        | Significa “ettaro globale”: è un'unità di misura usata per confrontare risorse naturali diverse con lo stesso criterio.                                | Serve per dire, in modo uniforme, quanta natura serve o quanta natura è disponibile.                                             |
        """
    )
    st.markdown(
        """
        **Quante Terre:** Indica quante "Terre" sarebbero necessarie se tutti vivessero con lo stesso stile di vita e consumo della nazione o entità in questione.
        Un valore superiore a 1 significa che l'entità sta consumando più risorse di quelle che il suo territorio (o il pianeta, nel caso del "Mondo") può rigenerare.
        """
    )

# Aggiungo un separatore per chiarezza
st.markdown("---")



# Funzione per caricare i dati (simula un database o file CSV)
@st.cache_data
def load_data():
    # Ottieni il percorso assoluto della cartella dove si trova lo script
    # Questo risolve i problemi di FileNotFoundError su piattaforme come Netlify/Stlite
    base_path = os.path.dirname(__file__)
    file_path = os.path.join(base_path, "datiset_overshoot_fulldata.txt")
    
    # Legge i dati dal file CSV locale
    df = pd.read_csv(file_path)
    
    # Pulisce i nomi delle colonne da eventuali spazi bianchi invisibili
    df.columns = [c.strip() for c in df.columns]

    # Rinomina le colonne se presenti con i nomi alternativi (es. BiocapTotGHA, EFConsTotGHA)
    mapping_colonne = {
        "BiocapTotGHA": "Biocapacità Totale (M Gha)",
        "EFConsTotGHA": "Impronta Eco Totale (M Gha)",
        "Imponta Eco(Gha/persona)": "Impronta Eco (Gha/persona)",
        "QuanteTerre": "Quante Terre"
    }
    df = df.rename(columns=mapping_colonne)
    
    # Mappa per tradurre i mesi italiani in formato numerico
    # Aggiornata per gestire i mesi in inglese
    mesi_mapping = {
        "January": "01", "February": "02", "March": "03", "April": "04",
        "May": "05", "June": "06", "July": "07", "August": "08",
        "September": "09", "October": "10", "November": "11", "December": "12"
    } 
    
    # Funzione per convertire "01 Novembre" in formato datetime leggibile
    def parse_date(row):
        valore = str(row["Data Overshoot"]).strip()
        parti = valore.split()
        
        # Se la data è scritta male, manca o c'è una riga vuota, restituisce None per ignorarla
        if len(parti) < 2:
            return None
            
        giorno = parti[0]
        mese = parti[1].capitalize() # Rende l'iniziale maiuscola (es. 'agosto' diventa 'Agosto')
        
        if mese not in mesi_mapping or not giorno.isdigit():
            return None
            
        return f"{row['Anno']}-{mesi_mapping[mese]}-{int(giorno):02d}"
        
    df["Data Completa"] = df.apply(parse_date, axis=1)
    df["Data Completa"] = pd.to_datetime(df["Data Completa"])
    # Rimosso il dropna globale per non perdere i dati numerici del 2026 
    # se la data dell'Overshoot non è ancora disponibile.

    # Pulisci e converti le colonne numeriche per Biocapacità, Impronta Eco e Quante Terre
    numeric_cols_to_clean = [
        "Biocapacità Totale (M Gha)", 
        "Impronta Eco Totale (M Gha)", 
        "Quante Terre",
        "Biocapacità (Gha/persona)",
        "Impronta Eco (Gha/persona)"
    ]
    
    for col in numeric_cols_to_clean:
        if col not in df.columns:
            df[col] = 0
            continue
            
        def clean_numeric_value(val):
            val = str(val).strip()
            if not val or any(err in val for err in ['#VALUE!', '#REF!', '#DIV/0!', 'nan', 'Nessuno']):
                return None
            val = val.replace('"', '').replace("'", "").replace(' ', '').replace('\xa0', '')
            
            dot_idx = val.rfind('.')
            comma_idx = val.rfind(',')
            
            if dot_idx != -1 and comma_idx != -1:
                if dot_idx > comma_idx: # Inglese
                    val = val.replace(',', '')
                else: # Italiano
                    val = val.replace('.', '').replace(',', '.')
            elif comma_idx != -1:
                if val.count(',') > 1: val = val.replace(',', '')
                else: val = val.replace(',', '.')
            elif dot_idx != -1:
                if val.count('.') > 1: val = val.replace('.', '')
            return val

        df[col] = df[col].apply(clean_numeric_value)
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Gestione scala: se i valori sono Gha assoluti (miliardi) invece di M Gha (milioni), 
    # li convertiamo per coerenza con le etichette dell'interfaccia.
    for col in ["Biocapacità Totale (M Gha)", "Impronta Eco Totale (M Gha)"]:
        if col in df.columns:
            if df[col].max() > 1000000: # Se il valore massimo supera il milione, assumiamo siano Gha assoluti
                df[col] = df[col] / 1_000_000

    return df

df = load_data()

# Sidebar: Menu laterale per i comandi
st.sidebar.header("Impostazioni Dashboard")
entita_disponibili = sorted(df["Entità"].unique().tolist())
selezioni = st.sidebar.multiselect(
    "Scegli le aree geografiche da confrontare:",
    options=entita_disponibili,
    default=["Mondo", "Italia", "USA", "Cina"]
)

if not selezioni:
    st.warning("⚠️ Seleziona almeno un'area geografica dal menu a sinistra per visualizzare il grafico.")
else:
    # Selector for the metric to display in the line chart
    line_metric_options = {
        "Data Overshoot": "Data Overshoot",
        "Impronta Eco Totale (M Gha)": "Impronta Eco Totale (M Gha)",
        "Biocapacità Totale (M Gha)": "Biocapacità Totale (M Gha)",
        "Biocapacità (Gha/persona)": "Biocapacità (Gha/persona)",
        "Impronta Eco (Gha/persona)": "Impronta Eco (Gha/persona)"
    }
    selected_line_metric = st.selectbox(
        "Scegli la metrica da visualizzare nel grafico a linee:",
        options=list(line_metric_options.keys()),
        index=0 # Default to "Data Overshoot"
    )
    # Creazione del Grafico
    fig = go.Figure()
    
    # Tavolozza di colori Plotly per differenziare le nazioni
    # Usiamo una tavolozza più grande (26 colori) per supportare più nazioni senza ripetizioni
    colori = px.colors.qualitative.Alphabet
    
    # Nome della nuova colonna nel file CSV (modificalo se nel CSV l'hai chiamata diversamente)
    colonna_tipo = "Stato DOS"

    for i, entita in enumerate(selezioni):
        df_entita = df[df["Entità"] == entita].copy()
        
        # Determine which column to plot on the Y-axis
        y_plot_column = ""
        if selected_line_metric == "Data Overshoot":
            # Escludiamo i dati senza data valida solo per questo specifico grafico a linee
            df_entita = df_entita[df_entita["Data Completa"].notna()].copy()
            if df_entita.empty: continue
            df_entita["overshoot_day_y"] = df_entita["Data Completa"].apply(lambda d: d.replace(year=2004))
            y_plot_column = "overshoot_day_y"
        else:
            y_plot_column = selected_line_metric
            # Filter out NaN or 0 values for numeric metrics for this specific trace
            df_entita = df_entita[(df_entita[y_plot_column].notna()) & (df_entita[y_plot_column] > 0)]

        df_entita["hover_text_overshoot"] = df_entita["Data Completa"].dt.strftime("%d %b %Y")
        colore = colori[i % len(colori)]
        
        # Prepare customdata for hovertemplate to include all relevant metrics
        # Ensure colonna_tipo is handled even if not present in original df
        if colonna_tipo not in df_entita.columns:
            df_entita[colonna_tipo] = "Non specificato"
        df_entita[colonna_tipo] = df_entita[colonna_tipo].fillna("Non specificato")

        custom_data_cols = [
            "hover_text_overshoot",
            colonna_tipo,
            "Biocapacità Totale (M Gha)",
            "Impronta Eco Totale (M Gha)",
            "Quante Terre",
            "Biocapacità (Gha/persona)",
            "Impronta Eco (Gha/persona)"
        ]
        custom_dati = df_entita[custom_data_cols]

        # Dynamic hovertemplate
        hovertemplate_base = f"<b>{entita}</b><br>Anno: %{{x}}<br>"
        if selected_line_metric == "Data Overshoot":
            hovertemplate = hovertemplate_base + \
                            f"Overshoot Day: %{{customdata[0]}}<br>" + \
                            f"Tipologia: %{{customdata[1]}}<br>" + \
                            f"Biocapacità Totale (M Gha): %{{customdata[2]:.1f}}<br>" + \
                            f"Impronta Eco Totale (M Gha): %{{customdata[3]:.1f}}<br>" + \
                            f"Biocapacità (Gha/persona): %{{customdata[5]:.2f}}<br>" + \
                            f"Impronta Eco (Gha/persona): %{{customdata[6]:.2f}}<br>" + \
                            f"Quante Terre: %{{customdata[4]:.2f}}<extra></extra>"
            # Symbols based on 'Stato DOS' only if 'Data Overshoot' is selected
            simboli = df_entita[colonna_tipo].apply(lambda x: "circle-open" if "estrapolato" in str(x).lower() else "circle").tolist()
        else:
            hovertemplate = hovertemplate_base + \
                            f"{selected_line_metric}: %{{y:.2f}}<br>" + \
                            f"Overshoot Day: %{{customdata[0]}}<br>" + \
                            f"Tipologia: %{{customdata[1]}}<br>" + \
                            f"Biocapacità Totale (M Gha): %{{customdata[2]:.1f}}<br>" + \
                            f"Impronta Eco Totale (M Gha): %{{customdata[3]:.1f}}<br>" + \
                            f"Biocapacità (Gha/persona): %{{customdata[5]:.2f}}<br>" + \
                            f"Impronta Eco (Gha/persona): %{{customdata[6]:.2f}}<br>" + \
                            f"Quante Terre: %{{customdata[4]:.2f}}<extra></extra>"
            simboli = "circle" # Default symbol for numeric metrics

        fig.add_trace(go.Scatter(
            x=df_entita["Anno"],
            y=df_entita[y_plot_column],
            customdata=custom_dati,
            mode="lines+markers",
            name=entita,
            marker=dict(size=10, color=colore, symbol=simboli),
            line=dict(width=2, color=colore),
            hovertemplate=hovertemplate
        ))

    # Update layout dynamically based on selected metric
    yaxis_title_text = ""
    if selected_line_metric == "Data Overshoot":
        yaxis_title_text = "Data dell’Overshoot Day"
        fig.update_yaxes(autorange="reversed", tickformat="%d %b")
    else:
        yaxis_title_text = selected_line_metric
        fig.update_yaxes(autorange=True, tickformat=".2f") # Reset y-axis for numeric values

    fig.update_layout(
        title=f"{selected_line_metric} per: " + ", ".join(selezioni),
        xaxis_title="Anno",
        yaxis_title=yaxis_title_text,
        template="plotly_white",
        hovermode="x unified",
        legend_title="Aree Selezionate"
    )
    fig.update_xaxes(rangeslider_visible=True)

    # Renderizza il grafico interattivo all'interno della Web App
    st.plotly_chart(fig, use_container_width=True)
    st.info("💡 Usa il menu a sinistra per selezionare e confrontare più nazioni contemporaneamente. Usa lo slider in fondo al grafico per stringere il range di anni.")

    # --- NUOVA SEZIONE: TABELLA DATI ---
    st.markdown("---")
    st.subheader("Tabella Dati Dettagliata per le Nazioni Selezionate")

    # Filtriamo i dati per le nazioni selezionate
    df_table_data = df[df["Entità"].isin(selezioni)].copy()

    # Se la metrica selezionata per il grafico a linee è numerica,
    # potremmo voler filtrare i dati non validi anche per la tabella,
    # o almeno evidenziarli. Per ora, mostriamo tutti i dati disponibili.

    # Selezioniamo le colonne da visualizzare nella tabella
    columns_to_display = [
        "Anno",
        "Entità",
        "Data Overshoot",
        "Stato DOS",
        "Biocapacità Totale (M Gha)",
        "Biocapacità (Gha/persona)",
        "Impronta Eco Totale (M Gha)",
        "Impronta Eco (Gha/persona)",
        "Quante Terre"
    ]

    st.dataframe(df_table_data[columns_to_display].sort_values(by=["Entità", "Anno"]), use_container_width=True, hide_index=True)
    st.caption("Questa tabella mostra i dati grezzi per le nazioni e gli anni selezionati, inclusi i valori di Overshoot Day, Biocapacità, Impronta Ecologica e Quante Terre.")


    # --- NUOVA SEZIONE: GRAFICO A TORTA ---
    st.markdown("---")
    
    # Selezione dell'anno tramite menu a tendina
    anni_disponibili = sorted(df["Anno"].unique(), reverse=True)
    anno_selezionato = st.selectbox("Seleziona l'anno da esplorare per i grafici a torta:", anni_disponibili)
    
    # Selector for the metric to display in the first pie chart
    metric_options = {
        "Giorni dall'inizio dell'anno": "Giorni dall'inizio dell'anno",
        "Impronta Eco Totale (M Gha)": "Impronta Eco Totale (M Gha)",
        "Biocapacità Totale (M Gha)": "Biocapacità Totale (M Gha)"
    }
    selected_pie_metric = st.selectbox(
        "Scegli la metrica da visualizzare nel primo grafico a torta:",
        options=list(metric_options.keys()),
        index=0 # Default to "Giorni dall'inizio dell'anno"
    )

    # Filtriamo i dati per l'anno e le nazioni correntemente selezionate
    df_anno_first_pie = df[(df["Anno"] == anno_selezionato) & (df["Entità"].isin(selezioni))].copy()

    # Calculate "Giorni dall'inizio dell'anno" if it's a potential metric
    if "Giorni dall'inizio dell'anno" in metric_options.keys():
        df_anno_first_pie["Giorni dall'inizio dell'anno"] = df_anno_first_pie["Data Completa"].dt.dayofyear

    # Filter based on the selected metric for validity
    df_first_pie_valid_data = df_anno_first_pie[
        (df_anno_first_pie[selected_pie_metric].notna()) &
        (df_anno_first_pie[selected_pie_metric] > 0)
    ]

    nations_with_valid_first_pie_data = df_first_pie_valid_data["Entità"].unique().tolist()
    nations_excluded_from_first_pie_chart = [n for n in selezioni if n not in nations_with_valid_first_pie_data]

    if not df_first_pie_valid_data.empty:
        # Dynamic title based on selected metric, but keeping the original title if "Giorni dall'inizio dell'anno"
        if selected_pie_metric == "Giorni dall'inizio dell'anno":
            st.subheader(f"📊 Numero di giorni per consumare le risorse disponibili ({anno_selezionato})")
            pie_caption = "Nota: Lo spicchio rappresenta il numero di giorni necessari per esaurire le risorse in quell'anno - Più è piccolo, prima viene raggiunto l'overshoot day."
        else:
            st.subheader(f"📊 {selected_pie_metric} per Nazione ({anno_selezionato})")
            pie_caption = f"Nota: Lo spicchio rappresenta proporzionalmente la {selected_pie_metric} di ciascuna nazione nell'anno {anno_selezionato}."

        # Calcoliamo quanti giorni sono passati dal 1 gennaio per usare il numero negli spicchi
        # Questa riga è stata spostata e integrata nel filtro sopra
        
        # Creiamo una mappa dei colori per mantenere coerenza con il grafico a linee
        mappa_colori_first_pie = {entita: colori[i % len(colori)] for i, entita in enumerate(selezioni)}
        
        fig_pie = px.pie(
            df_first_pie_valid_data,
            values=selected_pie_metric,
            names="Entità",
            color="Entità",
            color_discrete_map=mappa_colori_first_pie,
            hover_data=["Data Overshoot", "Biocapacità Totale (M Gha)", "Impronta Eco Totale (M Gha)", "Quante Terre"]
        )
        fig_pie.update_traces(
            textposition='inside', 
            textinfo='value+label',
            texttemplate='%{value:.1f}',
            hovertemplate=f"<b>%{{label}}</b><br>" +
                          f"{selected_pie_metric}: %{{value:.1f}}<br>" +
                          "Overshoot Day: %{customdata[0]}<br>" +
                          "Biocapacità Totale (M Gha): %{customdata[1]:.1f}<br>" +
                          "Impronta Eco Totale (M Gha): %{customdata[2]:.1f}<br>" +
                          "Quante Terre: %{customdata[3]:.2f}<extra></extra>"
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        st.caption(pie_caption)
        
        if nations_excluded_from_first_pie_chart:
            st.warning(f"⚠️ I seguenti paesi selezionati non sono visualizzati nel grafico a torta '{selected_pie_metric}' per l'anno {anno_selezionato} a causa di dati mancanti o non validi ({selected_pie_metric} non positivo): {', '.join(nations_excluded_from_first_pie_chart)}.")
    else:
        if not selezioni:
            st.info(f"Seleziona almeno un'area geografica dal menu a sinistra per visualizzare il grafico a torta '{selected_pie_metric}'.")
        elif nations_excluded_from_first_pie_chart:
            st.info(f"Nessun dato valido per '{selected_pie_metric}' per l'anno {anno_selezionato} per le nazioni selezionate. I seguenti paesi non sono visualizzati a causa di dati mancanti o non validi: {', '.join(nations_excluded_from_first_pie_chart)}.")
        else:
            st.info(f"Nessun dato valido per '{selected_pie_metric}' per l'anno {anno_selezionato} e le nazioni selezionate.")

    # --- NUOVA SEZIONE: GRAFICO A TORTA (Quante Terre) ---
    st.markdown("---")
    st.subheader(f"🌍 Quante Terre Necessarie ... se vivessimo tutti come la nazione ... ({anno_selezionato})")

    # Filtriamo per includere solo record con valori numerici > 0 per "Quante Terre"
    df_anno_quante_terre_valid_data = df_anno_first_pie[ # Use df_anno_first_pie which is already filtered by year and entity
        (df_anno_first_pie["Quante Terre"].notna()) &
        (df_anno_first_pie["Quante Terre"] > 0)
    ]

    # Identifichiamo le nazioni selezionate ma escluse a causa di dati non validi
    nations_with_valid_quante_terre_pie_data = df_anno_quante_terre_valid_data["Entità"].unique().tolist()
    nations_excluded_from_quante_terre_pie_chart = [n for n in selezioni if n not in nations_with_valid_quante_terre_pie_data]

    if not df_anno_quante_terre_valid_data.empty:
        mappa_colori_quante_terre = {entita: colori[i % len(colori)] for i, entita in enumerate(selezioni)}
        
        fig_pie_quante_terre = px.pie(
            df_anno_quante_terre_valid_data,
            values="Quante Terre",
            names="Entità",
            color="Entità",
            color_discrete_map=mappa_colori_quante_terre,
            hover_data=["Data Overshoot", "Biocapacità Totale (M Gha)", "Impronta Eco Totale (M Gha)"]
        )
        fig_pie_quante_terre.update_traces(
            textposition='inside', 
            textinfo='value+label',
            texttemplate='%{value:.2f}',
            hovertemplate="<b>%{label}</b><br>" +
                          "Quante Terre: %{value:.2f}<br>" +
                          "Overshoot Day: %{customdata[0]}<br>" + # customdata[0] è Data Overshoot
                          "Biocapacità Totale (M Gha): %{customdata[1]:.1f}<br>" +
                          "Impronta Eco Totale (M Gha): %{customdata[2]:.1f}<extra></extra>"
        )
        st.plotly_chart(fig_pie_quante_terre, use_container_width=True)
        st.caption(f"Nota: Lo spicchio rappresenta proporzionalmente il numero di 'Terre' necessarie per sostenere il consumo di ciascuna nazione nell'anno {anno_selezionato}.")
        
        if nations_excluded_from_quante_terre_pie_chart:
            st.warning(f"⚠️ I seguenti paesi selezionati non sono visualizzati nel grafico a torta 'Quante Terre' per l'anno {anno_selezionato} a causa di dati mancanti o non validi (Quante Terre non positivo): {', '.join(nations_excluded_from_quante_terre_pie_chart)}.")
    else:
        if not selezioni:
            st.info("Seleziona almeno un'area geografica dal menu a sinistra per visualizzare il grafico a torta 'Quante Terre'.")
        elif nations_excluded_from_quante_terre_pie_chart:
            st.info(f"Nessun dato valido per 'Quante Terre' per l'anno {anno_selezionato} per le nazioni selezionate. I seguenti paesi non sono visualizzati a causa di dati mancanti o non validi: {', '.join(nations_excluded_from_quante_terre_pie_chart)}.")
        else:
            st.info(f"Nessun dato valido per 'Quante Terre' per l'anno {anno_selezionato} e le nazioni selezionate.")

    # --- NUOVA SEZIONE: GRAFICO A BARRE IMPILATE ---
    st.markdown("---")
    st.subheader(f"📈 Biocapacità e Impronta Ecologica ({anno_selezionato})")

    # Selettore per la metrica delle barre
    tipo_barre = st.radio(
        "Seleziona la metrica per il confronto:",
        options=["Totale (M Gha)", "Pro-capite (Gha/persona)"],
        horizontal=True,
        index=0,
        key="bar_metric_selector"
    )

    if tipo_barre == "Totale (M Gha)":
        col_bio_bar = "Biocapacità Totale (M Gha)"
        col_imp_bar = "Impronta Eco Totale (M Gha)"
        unit_bar = "(M Gha)"
        prec_bar = "1f"
    else:
        col_bio_bar = "Biocapacità (Gha/persona)"
        col_imp_bar = "Impronta Eco (Gha/persona)"
        unit_bar = "(Gha/persona)"
        prec_bar = "2f"

    # Filtriamo i dati per l'anno e le nazioni correntemente selezionate
    df_filtered_by_selection = df[(df["Anno"] == anno_selezionato) & (df["Entità"].isin(selezioni))].copy()

    # Filtriamo per includere solo record con valori numerici > 0 in entrambi i campi
    df_bar_valid_data = df_filtered_by_selection[
        (df_filtered_by_selection[col_bio_bar].notna()) &
        (df_filtered_by_selection[col_imp_bar].notna()) &
        (df_filtered_by_selection[col_bio_bar] > 0) &
        (df_filtered_by_selection[col_imp_bar] > 0)
    ]

    # Identifichiamo le nazioni selezionate ma escluse a causa di dati non validi
    nations_with_valid_bar_data = df_bar_valid_data["Entità"].unique().tolist()
    nations_excluded_from_bar_chart = [n for n in selezioni if n not in nations_with_valid_bar_data]

    # Calcola l'altezza dinamica per il grafico a barre per migliorare la leggibilità su schermi piccoli
    # Altezza base + altezza extra per ogni entità per prevenire la compressione
    bar_chart_height = max(400, 50 * len(df_bar_valid_data["Entità"].unique()))

    if not df_bar_valid_data.empty:
        # Prepariamo il DataFrame per il grafico a barre impilate, mantenendo 'Quante Terre'
        df_melted = df_bar_valid_data.melt(
            id_vars=["Entità", "Quante Terre"], # Manteniamo 'Quante Terre' come variabile identificativa
            value_vars=[col_bio_bar, col_imp_bar],
            var_name="Tipo Dato",
            value_name=f"Valore {unit_bar}"
        )
        
        # Creiamo una colonna per il tooltip di 'Quante Terre' che sia visibile solo per l'Impronta Ecologica
        df_melted['Quante Terre Hover'] = df_melted.apply(
            lambda row: f"Quante Terre: {row['Quante Terre']:.2f}" if row['Tipo Dato'] == col_imp_bar and pd.notna(row['Quante Terre']) else "",
            axis=1
        )
        
        fig_bar = px.bar(
            df_melted,
            x="Entità",
            y=f"Valore {unit_bar}",
            color="Tipo Dato",
            title=f"Biocapacità e Impronta Ecologica ({tipo_barre}) per le Nazioni Selezionate ({anno_selezionato})",
            labels={f"Valore {unit_bar}": f"Valore {unit_bar}", "Entità": "Nazione"},
            barmode="group", # Questo crea un grafico a barre raggruppate
            text_auto=f".{prec_bar}", # Mostra automaticamente i valori sopra le barre
            # Usiamo custom_data per un controllo più fine sul tooltip
            custom_data=["Tipo Dato", f"Valore {unit_bar}", "Quante Terre Hover"]
        )
        
        fig_bar.update_layout(height=bar_chart_height) # Applica l'altezza dinamica
        # Aggiorniamo il hovertemplate per includere 'Quante Terre' condizionalmente
        fig_bar.update_traces(
            textposition='outside', # Posiziona il testo sopra le barre
            hovertemplate="<b>%{x}</b><br>" + \
                          "Tipo Dato: %{customdata[0]}<br>" + \
                          f"Valore {unit_bar}: %{{customdata[1]:.{prec_bar}}}<br>" + \
                          "%{customdata[2]}<extra></extra>" # customdata[2] è 'Quante Terre Hover'
        )
        fig_bar.update_layout(hovermode="x unified") # Manteniamo hovermode unificato
        st.plotly_chart(fig_bar, use_container_width=True)
        
        if nations_excluded_from_bar_chart:
            st.warning(f"⚠️ I seguenti paesi selezionati non sono visualizzati nel grafico a barre per l'anno {anno_selezionato} a causa di dati mancanti o non validi ({col_bio_bar} o {col_imp_bar} non positivi): {', '.join(nations_excluded_from_bar_chart)}.")
    else:
        # Se df_bar_valid_data è vuoto, forniamo un messaggio più specifico
        if not selezioni:
            st.info("Seleziona almeno un'area geografica dal menu a sinistra per visualizzare il grafico a barre.")
        elif nations_excluded_from_bar_chart:
            st.info(f"Nessun dato valido per {col_bio_bar} e {col_imp_bar} per l'anno {anno_selezionato} per le nazioni selezionate. I seguenti paesi non sono visualizzati a causa di dati mancanti o non validi: {', '.join(nations_excluded_from_bar_chart)}.")
        else:
            st.info(f"Nessun dato valido per {col_bio_bar} e {col_imp_bar} per l'anno {anno_selezionato} e le nazioni selezionate.")

# --- NUOVA SEZIONE: GRAFICO AD AREA SALDO ECOLOGICO ---
st.markdown("---")
st.subheader("📈 Saldo Ecologico (Biocapacità - Impronta Ecologica) per Anno")

# Selettore per la metrica del saldo
tipo_saldo = st.radio(
    "Seleziona la metrica per il saldo ecologico:",
    options=["Totale (M Gha)", "Pro-capite (Gha/persona)"],
    horizontal=True,
    index=0
)

if tipo_saldo == "Totale (M Gha)":
    col_bio = "Biocapacità Totale (M Gha)"
    col_imp = "Impronta Eco Totale (M Gha)"
    label_saldo = "Saldo (M Gha)"
    prec_saldo = "1f"
else:
    col_bio = "Biocapacità (Gha/persona)"
    col_imp = "Impronta Eco (Gha/persona)"
    label_saldo = "Saldo (Gha/persona)"
    prec_saldo = "2f"

# Filtriamo i dati per le nazioni correntemente selezionate
df_area_all = df[df["Entità"].isin(selezioni)].copy()

# Calcoliamo il saldo ecologico
df_area_all[label_saldo] = df_area_all[col_bio] - df_area_all[col_imp]

# Filtriamo i dati non validi per il saldo
df_area_all = df_area_all[df_area_all[label_saldo].notna()]

if not df_area_all.empty:
    # Logica di paginazione per visualizzare 4 territori alla volta per migliorare la leggibilità
    nazioni_valide = sorted(df_area_all["Entità"].unique().tolist())
    num_nazioni = len(nazioni_valide)
    page_size = 4
    num_pages = (num_nazioni + page_size - 1) // page_size
    
    if num_pages > 1:
        col_pag1, col_pag2 = st.columns([1, 5])
        with col_pag1:
            pagina_attuale = st.number_input(f"Pagina (1-{num_pages})", min_value=1, max_value=num_pages, value=1, key="saldo_page_input")
        
        start_idx = (pagina_attuale - 1) * page_size
        end_idx = start_idx + page_size
        nazioni_visibili = nazioni_valide[start_idx:end_idx]
        df_area_chart_data = df_area_all[df_area_all["Entità"].isin(nazioni_visibili)].copy()
        st.info(f"Visualizzazione nazioni da {start_idx + 1} a {min(end_idx, num_nazioni)} di {num_nazioni}")
    else:
        df_area_chart_data = df_area_all.copy()
        nazioni_visibili = nazioni_valide

    # Determiniamo lo stato del saldo per la colorazione
    df_area_chart_data['Stato Saldo'] = df_area_chart_data[label_saldo].apply( # Se il saldo è positivo, è un surplus; se negativo, è un deficit
        lambda x: 'Surplus Ecologico' if x > 0 else 'Deficit Ecologico'
    )

    # Definiamo la mappa dei colori
    color_map_saldo = {
        'Deficit Ecologico': 'red',
        'Surplus Ecologico': 'green'
    }

    fig_area = px.area(
        df_area_chart_data,
        x="Anno",
        y=label_saldo,
        color="Stato Saldo",
        line_group="Entità", # Assicura che le linee siano raggruppate per entità
        facet_col="Entità",
        facet_col_wrap=2, # Mostra 2 colonne di grafici per una migliore visualizzazione
        title="Saldo Ecologico (Biocapacità - Impronta Ecologica) per Nazione e Anno",
        height=800, # Aumentiamo l'altezza complessiva per dare più spazio verticale ai grafici
        labels={
            label_saldo: label_saldo,
            "Anno": "Anno",
            "Stato Saldo": "Stato Saldo"
        },
        color_discrete_map=color_map_saldo,
        hover_data={
            col_bio: f":.{prec_saldo}",
            col_imp: f":.{prec_saldo}",
            label_saldo: f":.{prec_saldo}",
            "Stato Saldo": True,
            "Anno": True,
            "Entità": False # Nascondi Entità dal hover in quanto già nel titolo del facet
        }
    )

    fig_area.update_layout(hovermode="x unified")
    # Rimuoviamo matches='y' per evitare che nazioni con scale diverse (es. Mondo vs Italia) 
    # rendano i grafici illeggibili e compressi.
    # Forza la centratura dello zero per ogni subplot calcolando il limite locale
    fig_area.update_yaxes(
        matches=None, 
        zeroline=True, 
        zerolinewidth=2, 
        zerolinecolor='black', 
    )

    # Applichiamo i limiti individuali per ogni facet per massimizzare la visibilità (effetto "ampio")
    # mantenendo lo zero al centro di ogni box per un confronto visivo immediato
    for i, entita in enumerate(nazioni_visibili):
        local_max = df_area_chart_data[df_area_chart_data["Entità"] == entita][label_saldo].abs().max()
        local_limit = local_max * 1.3 if local_max > 0 else 1.0
        fig_area.update_yaxes(range=[-local_limit, local_limit], row=(i // 2) + 1, col=(i % 2) + 1)

    fig_area.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1])) # Pulisce il titolo del facet

    # Rimuoviamo i valori numerici dai punti per migliorare la pulizia visiva e la leggibilità
    fig_area.update_traces(mode="lines+markers")

    st.plotly_chart(fig_area, use_container_width=True)
    st.caption("Questo grafico mostra il saldo ecologico (Biocapacità - Impronta Ecologica) per le nazioni selezionate. Un valore positivo indica un surplus ecologico (area verde), mentre un valore negativo indica un deficit ecologico (area rossa).")

else:
    st.info("Nessun dato valido per il calcolo del Saldo Ecologico per le nazioni selezionate.")

st.caption("Fonte dei dati: Footprint Data Foundation, York University Ecological Footprint Initiative, e Global Footprint Network (GFN).")
