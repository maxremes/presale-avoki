# presale


# Offertgenerator med Streamlit

![Offertgenerator Logo](https://www.avoki.com/media/s3ffirjs/avoki_logotype_white_rgb.png?width=2499&height=424&format=webp&quality=90&v=1dac2f25eb9f3d0)

## 📄 Innehållsförteckning

1. [Om Offertgenerator](#om-offertgenerator)
2. [Funktioner](#funktioner)
3. [Installation](#installation)
4. [Användning](#anvandning)
5. [Teknologi](#teknologi)
6. [Alternativ](#alternativ)
7. [Bidra](#bidra)
8. [Licens](#licens)
9. [Kontakt](#kontakt)

## Om Offertgenerator

Offertgenerator är en interaktiv webbapplikation byggd med [Streamlit](https://streamlit.io/) som hjälper användare att skapa skräddarsydda offerter för nätverkstjänster, hostinglösningar och säkerhetsprodukter. 
Genom ett användarvänligt gränssnitt kan du välja olika tjänster, anpassa mängder och rabatter samt lägga till egna offertdelar. Slutligen kan du sammanfatta dina val och ladda ner en detaljerad CSV-sammanställning.

## Funktioner

- **Interaktiva Val**: Välj mellan olika tjänstekategorier och specifika produkter med hjälp av klickbara pill-knappar.
- **Rabatthantering**: Visa och ange rabatter för varje vald produkt.
- **Anpassade Offertdelar**: Lägg till egna produkter eller tjänster med specifika priser och rabatter.
- **Sammanfattning**: Se en översikt över dina valda produkter och totalkostnader i sidopanelen.
- **CSV-export**: Ladda ner en detaljerad sammanställning av offerten som en CSV-fil.
- **Responsiv Design**: Användarvänligt gränssnitt anpassat för både desktop och mobila enheter.
- **Logotyp och Footer**: Anpassade visuella element för en professionell framtoning.

## Installation

Följ stegen nedan för att komma igång med Offertgenerator:

### 1. Klona Repository

```bash
git clone https://github.com/maxremes/presale-avoki.git
cd presale-avoki/

python3 -m venv .venv
source .venv/bin/activate  # För macOS/Linux


## 1. Klona Repository

Starta Streamlit-applikationen med följande kommando:
streamlit run pills.py

Öppna din webbläsare och navigera till den lokala adress som Streamlit tillhandahåller (vanligtvis http://localhost:8501).





## Användning

1. Välj Tjänstekategori

Applikationen innehåller flera kategorier som du kan expandera för att välja specifika tjänster:

	•	Nätverk som tjänst
	•	Hosting
	•	X-One
	•	Anpassade offertdelar

2. Välj Alternativ med Pill-Knappar

För varje tjänstekategori kan du använda pill-knappar för att inkludera eller exkludera specifika produkter:

3. Ange Antal och Rabatt

När du väljer att inkludera en produkt kan du specificera antalet enheter och eventuella rabatter:

	•	Antal: Ange hur många enheter du önskar.
	•	Rabatt (%): Ange procentuell rabatt för produkten.

4. Lägg till Anpassade Offertdelar

Under sektionen “Anpassade offertdelar” kan du lägga till egna produkter eller tjänster:

	1.	Fyll i beskrivning, pris per enhet, antal, rabatt och typ (månadskostnad eller engångskostnad).
	2.	Klicka på “Lägg till” för att inkludera dem i offerten.
	3.	Du kan redigera eller ta bort befintliga anpassade offertdelar.

5. Se Sammanfattning

I sidopanelen ser du en översikt över alla valda produkter, deras priser, rabatter och totalkostnader:


6. Ladda ner CSV

När du är nöjd med din offert kan du ladda ner en detaljerad sammanställning som en CSV-fil genom att klicka på knappen “Ladda ner sammanfattning som CSV”.

Teknologi

	•	Python 3.11
	•	Streamlit: Ramverk för att bygga interaktiva webbapplikationer.
	•	Pandas: För datahantering och CSV-generering.
	•	Streamlit-Pills: För att skapa klickbara pill-knappar.



