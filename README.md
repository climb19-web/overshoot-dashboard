# 🌍 Earth Overshoot Day Tracker

Questa dashboard interattiva, realizzata con **Python**, **Streamlit** e **Plotly**, permette di analizzare e confrontare l'**Overshoot Day** (il giorno della sovraelongazione ecologica) e le metriche di sostenibilità per l'Italia, il resto del mondo e diverse altre entità geografiche.

L'obiettivo del progetto è fornire una visualizzazione chiara e immediata del debito ecologico che l'umanità contrae ogni anno con il pianeta.

## 🚀 Funzionalità

- **Analisi Storica (2000-2026)**: Visualizzazione dei trend temporali per l'Overshoot Day, la Biocapacità e l'Impronta Ecologica.
- **Confronto Multi-Nazione**: Selezione dinamica delle aree geografiche per confrontare i modelli di consumo.
- **Metriche Chiave**: Monitoraggio del parametro "Quante Terre", che indica quanti pianeti sarebbero necessari se tutti adottassero lo stile di vita di una specifica nazione.
- **Saldo Ecologico**: Grafici ad area che evidenziano i periodi di surplus o deficit ecologico (Biocapacità vs Impronta).
- **Esportazione Dati**: Funzione integrata per scaricare i dati filtrati in formato CSV per ulteriori analisi.
- **Interfaccia Responsiva**: Design ottimizzato per l'uso sia su desktop che su dispositivi mobile grazie a Streamlit Community Cloud.

## 🛠️ Tech Stack

- **Linguaggio**: Python 3.x
- **Dashboard**: [Streamlit](https://streamlit.io/)
- **Visualizzazione Dati**: [Plotly Express & Graph Objects](https://plotly.com/python/)
- **Manipolazione Dati**: [Pandas](https://pandas.pydata.org/)

## 📂 Struttura del Progetto

- `app.py`: Il file principale contenente la logica dell'applicazione e l'interfaccia utente.
- `datiset_overshoot_fulldata.txt`: Il dataset contenente i dati storici su biocapacità e consumi.
- `requirements.txt`: Elenco delle dipendenze Python necessarie per il funzionamento sul server.
- `README.md`: Documentazione del progetto.

## 💻 Installazione Locale

Se desideri eseguire l'app localmente, segui questi passaggi:

1. Clona il repository:
   ```bash
   git clone https://github.com/tuo-username/overshoot-dashboard.git
   ```
2. Installa le dipendenze:
   ```bash
   pip install -r requirements.txt
   ```
3. Avvia l'applicazione:
   ```bash
   streamlit run app.py
   ```

## 📊 Fonti dei Dati
I dati utilizzati provengono da studi della **Footprint Data Foundation**, **York University Ecological Footprint Initiative** e **Global Footprint Network (GFN)**.

---
*Realizzato con ❤️ per sensibilizzare sulla sostenibilità ambientale.*
