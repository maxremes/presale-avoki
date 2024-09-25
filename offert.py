import streamlit as st
import pandas as pd
import re
from itertools import groupby

# --- Initiera session state variabler ---
if 'show_discount' not in st.session_state:
    st.session_state['show_discount'] = False

if 'cloudiq_antal' not in st.session_state:
    st.session_state['cloudiq_antal'] = 0

if 'custom_items' not in st.session_state:
    st.session_state['custom_items'] = []

if 'edit_index' not in st.session_state:
    st.session_state['edit_index'] = None

# --- Lägg till logotyp med st.logo ---
# Byt ut 'LOGO_URL_LARGE' och 'LOGO_URL_SMALL' till dina egna logotyper
LOGO_URL_LARGE = "https://www.avoki.com/media/s3ffirjs/avoki_logotype_white_rgb.png?width=2499&height=424&format=webp&quality=90&v=1dac2f25eb9f3d0"
LOGO_URL_SMALL = "https://www.avoki.com/media/s3ffirjs/avoki_logotype_white_rgb.png?width=2499&height=424&format=webp&quality=90&v=1dac2f25eb9f3d0"

st.logo(
    image=LOGO_URL_LARGE,
    link="https://avoki.com",
    icon_image=LOGO_URL_SMALL
)

# --- Toggle för att visa/dölja rabattfält ---
toggle_discount = st.checkbox("Visa rabattfält", value=st.session_state['show_discount'], key='toggle_discount')
st.session_state['show_discount'] = toggle_discount

# --- Kategorier som är engångskostnader ---
engangskostnad_kategorier = [
    'Kablage Engångskostnad',
    'Tidsuppskattning installation nätverk',
    'Årlig drift',
    'One-Time Setup Fees',
    'X-One 365 Cloud Security - Engångskostnad',
    'X-One 365 Endpoint Security - Engångskostnad',
    'Anpassade offertdelar - Engångskostnad'  # För anpassade engångskostnader
]

# --- Fördefinierade offertdelar grupperade per kategori ---
offertdelar = {
    'Nätverk som tjänst': {
        'Lokal Brandvägg - Månadskostnad': [
            {'Beskrivning': 'Lokal brandvägg 1000 Mbit/s med UTP', 'Pris': 1295, 'Antal': 0},
            {'Beskrivning': 'Unified Threat Protection', 'Pris': 200, 'Antal': 0},
            {'Beskrivning': 'SSL VPN', 'Pris': 150, 'Antal': 0}
        ],
        'WiFi som tjänst - Månadskostnad': [
            {'Beskrivning': 'Basic Wi-Fi', 'Pris': 100, 'Antal': 0},
            {'Beskrivning': 'Premium Wi-Fi 802.11ax', 'Pris': 175, 'Antal': 0},
            {'Beskrivning': 'Outdoor Wi-Fi', 'Pris': 250, 'Antal': 0}
        ],
        'Switchar som tjänst - Månadskostnad': [
            {'Beskrivning': 'Access switch 24-portar PoE+', 'Pris': 295, 'Antal': 0},
            {'Beskrivning': 'Access switch 24-portar', 'Pris': 250, 'Antal': 0},
            {'Beskrivning': 'Access switch 48-portar PoE+', 'Pris': 500, 'Antal': 0}
        ],
        'UPS som tjänst - Månadskostnad': [
            {'Beskrivning': 'UPS 1kVa', 'Pris': 175, 'Antal': 0},
            {'Beskrivning': 'UPS 3kVa', 'Pris': 300, 'Antal': 0}
        ],
        'Kablage Engångskostnad': [
            {'Beskrivning': 'CAT6 patch', 'Pris': 35, 'Antal': 0}
        ],
        'Övervakning Nätverk - Månadskostnad': [
            {'Beskrivning': 'Övervakning switchar & backup av konfiguration', 'Pris': 35, 'Antal': 0},
            {'Beskrivning': 'Övervakning accesspunkter (per enhet)', 'Pris': 35, 'Antal': 0},
            {'Beskrivning': 'Övervakning brandvägg & backup av konfiguration', 'Pris': 250, 'Antal': 0},
            {'Beskrivning': 'Övervakning UPS (per enhet)', 'Pris': 35, 'Antal': 0},
            {'Beskrivning': 'CloudIQ', 'Pris': 54, 'Antal': 0}
        ],
        'Tidsuppskattning installation nätverk': [
            {'Beskrivning': 'Uppgradering & grundkonfiguration av brandvägg', 'Pris': 1250, 'Antal': 0},
            {'Beskrivning': 'Uppgradering & grundkonfiguration av accesspunkter', 'Pris': 1250, 'Antal': 0},
            {'Beskrivning': 'Uppgradering & grundkonfiguration av switchar', 'Pris': 1250, 'Antal': 0},
            {'Beskrivning': 'Uppackning av UPS, konfiguration och montering', 'Pris': 1250, 'Antal': 0},
            {'Beskrivning': 'Driftsättning på plats samt tester på plats', 'Pris': 1250, 'Antal': 0},
            {'Beskrivning': 'Wi-Fi mätning på plats', 'Pris': 1250, 'Antal': 0},
            {'Beskrivning': 'Dokumentation av lösningen', 'Pris': 1250, 'Antal': 0}
        ],
        'Årlig drift': [
            {'Beskrivning': 'Genomgång av säkerhet', 'Pris': 1250, 'Antal': 0},
            {'Beskrivning': 'Mjukvaruuppgradering av accesspunkter', 'Pris': 1250, 'Antal': 0},
            {'Beskrivning': 'Mjukvaruuppgradering av switchar', 'Pris': 1250, 'Antal': 0},
            {'Beskrivning': 'Uppdatering av dokumentation', 'Pris': 1250, 'Antal': 0},
            {'Beskrivning': 'WiFi mätning på plats', 'Pris': 1250, 'Antal': 0}
        ]
    },
    'Hosting': {
        'Web Hosting - Månadskostnad': [
            {'Beskrivning': 'Shared Hosting', 'Pris': 50, 'Antal': 0},
            {'Beskrivning': 'VPS Hosting', 'Pris': 150, 'Antal': 0},
            {'Beskrivning': 'Dedicated Hosting', 'Pris': 300, 'Antal': 0}
        ],
        'Email Hosting - Månadskostnad': [
            {'Beskrivning': 'Basic Email Hosting', 'Pris': 20, 'Antal': 0},
            {'Beskrivning': 'Premium Email Hosting', 'Pris': 40, 'Antal': 0}
        ],
        'Managed Services - Månadskostnad': [
            {'Beskrivning': 'Managed Security', 'Pris': 100, 'Antal': 0},
            {'Beskrivning': 'Managed Backup', 'Pris': 80, 'Antal': 0}
        ],
        'One-Time Setup Fees': [
            {'Beskrivning': 'Initial Setup Fee', 'Pris': 5000, 'Antal': 0},
            {'Beskrivning': 'Migration Service', 'Pris': 2000, 'Antal': 0}
        ]
    },
    'X-One': {
        'X-One 365 Cloud Security - Månadskostnad': [
            {'Beskrivning': 'Tier 1 (1 - 4 användare)', 'Pris': 630, 'Antal': 0},
            {'Beskrivning': 'Tier 2 (5 - 9 användare)', 'Pris': 954, 'Antal': 0},
            {'Beskrivning': 'Tier 3 (10 - 19 användare)', 'Pris': 1194, 'Antal': 0},
            {'Beskrivning': 'Tier 4 (20 - 49 användare)', 'Pris': 2154, 'Antal': 0},
            {'Beskrivning': 'Tier 5 (50 - 99 användare)', 'Pris': 2994, 'Antal': 0},
            {'Beskrivning': 'Tier 6 (100 - 249 användare)', 'Pris': 4194, 'Antal': 0},
            {'Beskrivning': 'Tier 7 (250 - n användare)', 'Pris': 'Separat offert', 'Antal': 0}
        ],
        'X-One 365 Cloud Security - Engångskostnad': [
            {'Beskrivning': 'Driftsättning X-One Tier 1-4', 'Pris': 2995, 'Antal': 0},
            {'Beskrivning': 'Driftsättning X-One Tier 5-7', 'Pris': 4995, 'Antal': 0}
        ],
        'X-One 365 Endpoint Security - Månadskostnad': [
            {'Beskrivning': 'Tier 1 (1 - 4 brevlådor)', 'Pris': 630, 'Antal': 0},
            {'Beskrivning': 'Tier 2 (5 - 9 brevlådor)', 'Pris': 954, 'Antal': 0},
            {'Beskrivning': 'Tier 3 (10 - 19 brevlådor)', 'Pris': 1194, 'Antal': 0},
            {'Beskrivning': 'Tier 4 (20 - 49 brevlådor)', 'Pris': 2154, 'Antal': 0},
            {'Beskrivning': 'Tier 5 (50 - 99 brevlådor)', 'Pris': 2994, 'Antal': 0},
            {'Beskrivning': 'Tier 6 (100 - 249 brevlådor)', 'Pris': 4194, 'Antal': 0},
            {'Beskrivning': 'Tier 7 (250 - n brevlådor)', 'Pris': '-', 'Antal': 0}
        ],
        'X-One 365 Endpoint Security - Engångskostnad': [
            {'Beskrivning': 'Driftsättning X-One Tier 1-4', 'Pris': 2995, 'Antal': 0},
            {'Beskrivning': 'Driftsättning X-One Tier 5-7', 'Pris': 4995, 'Antal': 0}
        ]
    }
}

# --- Spåra totalen av accesspunkter och switchar ---
total_accesspunkter = 0
total_switchar = 0

# --- Lista för att lagra alla valda delar ---
total_valda_delar = []
any_discount = False  # Variabel för att kontrollera om rabatter har satts

# --- Totalsummor för månadskostnad och engångskostnad ---
total_manadskostnad = 0
total_engangskostnad = 0

# --- Funktion för att hantera offertdelar ---
def hantera_offertdel(kategori, offertdel, huvudkategori, inkludera, prefix=''):
    global any_discount, total_manadskostnad, total_engangskostnad, total_accesspunkter, total_switchar

    # Visa antal och rabattfält
    if st.session_state['show_discount']:
        cols = st.columns([6, 1, 1])
    else:
        cols = st.columns([6, 1])

    with cols[0]:
        st.write(f"{offertdel['Beskrivning']}")

    with cols[1]:
        # Hantera dynamiskt antal
        if inkludera == 'Ja':
            if 'CloudIQ' in offertdel['Beskrivning']:
                default_antal = 0
            else:
                default_antal = 1
        else:
            default_antal = 0

        antal = st.number_input(
            "",
            min_value=0,
            value=default_antal,
            step=1,
            key=f"antal_{prefix}{kategori}_{offertdel['Beskrivning']}"
        )

        if 'accesspunkter' in offertdel['Beskrivning'].lower():
            total_accesspunkter += antal
        elif 'switchar' in offertdel['Beskrivning'].lower():
            total_switchar += antal

    if st.session_state['show_discount']:
        with cols[2]:
            rabatt_procent = st.number_input(
                "",
                min_value=0, max_value=100, value=0,
                key=f"rabatt_{prefix}{kategori}_{offertdel['Beskrivning']}"
            )
            if rabatt_procent > 0:
                any_discount = True
    else:
        rabatt_procent = 0

    # Beräkna pris med rabatt
    original_pris = offertdel['Pris']
    try:
        rabatterat_pris = float(original_pris) * (1 - rabatt_procent / 100)
        tot_pris = rabatterat_pris * antal
        original_pris_formatted = f"{original_pris:,.2f} kr".replace(',', ' ')
        rabatterat_pris_formatted = f"{rabatterat_pris:,.2f} kr".replace(',', ' ')
        tot_pris_formatted = f"{tot_pris:,.2f} kr".replace(',', ' ')
    except (ValueError, TypeError):
        original_pris_formatted = original_pris
        rabatterat_pris_formatted = original_pris
        tot_pris_formatted = original_pris
        antal = 0

    # Formatera antal som heltal
    antal_formatted = int(antal)

    # Kontrollera om antalet är 0 och rabatten inte är 100%
    if antal == 0 and rabatt_procent < 100:
        return

    # Bestäm typ baserat på kategori
    if 'Engångskostnad' in kategori or kategori in engangskostnad_kategorier:
        typ = 'Engångskostnad'
        total_engangskostnad += tot_pris
    else:
        typ = 'Månadskostnad'
        total_manadskostnad += tot_pris

    # Lägg till valda delar i sammanfattningen endast om priset är numeriskt
    if isinstance(original_pris, (int, float)):
        item = {
            'Huvudkategori': huvudkategori,
            'Kategori': kategori,
            'Typ': typ,
            'Beskrivning': offertdel['Beskrivning'],
            'Pris /st': original_pris_formatted,
            'Antal': antal_formatted,
            'Tot.pris': tot_pris_formatted
        }
        if rabatt_procent > 0:
            item['Rabatt (%)'] = rabatt_procent
            item['Pris efter rabatt'] = rabatterat_pris_formatted
            any_discount = True
        total_valda_delar.append(item)

# --- Hantera Nätverk som tjänst ---
with st.expander("Nätverk som tjänst", expanded=True):
    huvudkategori = 'Nätverk som tjänst'
    for kategori, delar in offertdelar['Nätverk som tjänst'].items():
        st.subheader(kategori)

        if kategori == 'Lokal Brandvägg - Månadskostnad':
            # Hantera denna kategori separat
            brandvagg_included = False
            for offertdel in delar:
                if offertdel['Beskrivning'] == 'Lokal brandvägg 1000 Mbit/s med UTP':
                    inkludera = st.radio(f"Inkludera {offertdel['Beskrivning']}?",
                                         ('Nej', 'Ja'),
                                         index=0,
                                         key=f"{kategori}_{offertdel['Beskrivning']}")
                    if inkludera == 'Ja':
                        brandvagg_included = True
                        hantera_offertdel(kategori, offertdel, huvudkategori, inkludera)
                    else:
                        brandvagg_included = False
                    break  # Avbryt loopen efter att ha hanterat denna offertdel

            if brandvagg_included:
                # Hantera de två extra optionerna
                for offertdel in delar:
                    if offertdel['Beskrivning'] in ['Unified Threat Protection', 'SSL VPN']:
                        inkludera = st.radio(f"Inkludera {offertdel['Beskrivning']}?",
                                             ('Nej', 'Ja'),
                                             index=0,
                                             key=f"{kategori}_{offertdel['Beskrivning']}")
                        if inkludera == 'Ja':
                            hantera_offertdel(kategori, offertdel, huvudkategori, inkludera)
            else:
                pass  # Gör inget

        elif kategori == 'UPS som tjänst - Månadskostnad':
            # Hantera UPS-valet
            ups_included = st.radio("Vill du inkludera UPS?", ('Nej', 'Ja'), index=0, key='include_ups')
            if ups_included == 'Ja':
                # Välj mellan 1kVa och 3kVa
                ups_variant = st.selectbox("Välj UPS-variant", ('UPS 1kVa', 'UPS 3kVa'), key='ups_variant')
                # Hämta offertdelen för vald variant
                for offertdel in delar:
                    if offertdel['Beskrivning'] == ups_variant:
                        hantera_offertdel(kategori, offertdel, huvudkategori, 'Ja', prefix='UPS_')
            else:
                pass  # Gör inget

        elif kategori == 'WiFi som tjänst - Månadskostnad':
            # Hantera WiFi-valet
            wifi_included = st.radio("Vill du inkludera WiFi som tjänst?", ('Nej', 'Ja'), index=0, key='include_wifi')
            if wifi_included == 'Ja':
                # Välj mellan Basic, Premium och Outdoor WiFi
                wifi_variant = st.selectbox("Välj WiFi-variant",
                                           ('Basic Wi-Fi', 'Premium Wi-Fi 802.11ax', 'Outdoor Wi-Fi'),
                                           key='wifi_variant')
                # Hämta offertdelen för vald variant
                for offertdel in delar:
                    if offertdel['Beskrivning'] == wifi_variant:
                        hantera_offertdel(kategori, offertdel, huvudkategori, 'Ja', prefix='WiFi_')
            else:
                pass  # Gör inget

        elif kategori == 'Switchar som tjänst - Månadskostnad':
            # Hantera Switchar-valet
            switch_included = st.radio("Vill du inkludera Switchar som tjänst?", ('Nej', 'Ja'), index=0, key='include_switch')
            if switch_included == 'Ja':
                # Välj mellan de olika switchar-varianterna
                switch_variant = st.selectbox("Välj Switch-variant",
                                             ('Access switch 24-portar PoE+', 'Access switch 24-portar', 'Access switch 48-portar PoE+'),
                                             key='switch_variant')
                # Hämta offertdelen för vald variant
                for offertdel in delar:
                    if offertdel['Beskrivning'] == switch_variant:
                        hantera_offertdel(kategori, offertdel, huvudkategori, 'Ja', prefix='Switch_')
            else:
                pass  # Gör inget

        else:
            # Hantera övriga kategorier
            for offertdel in delar:
                inkludera = st.radio(f"Inkludera {offertdel['Beskrivning']}?",
                                     ('Nej', 'Ja'),
                                     index=0,
                                     key=f"{kategori}_{offertdel['Beskrivning']}")
                if inkludera == 'Ja':
                    hantera_offertdel(kategori, offertdel, huvudkategori, inkludera)

# --- Hantera Hosting ---
with st.expander("Hosting", expanded=True):
    huvudkategori = 'Hosting'
    for kategori, delar in offertdelar['Hosting'].items():
        st.subheader(kategori)
        for offertdel in delar:
            inkludera = st.radio(f"Inkludera {offertdel['Beskrivning']}?",
                                 ('Nej', 'Ja'),
                                 index=0,
                                 key=f"{kategori}_{offertdel['Beskrivning']}")
            if inkludera == 'Ja':
                hantera_offertdel(kategori, offertdel, huvudkategori, inkludera, prefix='Hosting_')

# --- Hantera X-One ---
with st.expander("X-One", expanded=True):
    huvudkategori = 'X-One'
    for kategori, delar in offertdelar['X-One'].items():
        st.subheader(kategori)
        for offertdel in delar:
            inkludera = st.radio(f"Inkludera {offertdel['Beskrivning']}?",
                                 ('Nej', 'Ja'),
                                 index=0,
                                 key=f"{kategori}_{offertdel['Beskrivning']}")
            if inkludera == 'Ja':
                hantera_offertdel(kategori, offertdel, huvudkategori, inkludera, prefix='X-One_')

# --- Hantera Anpassade Offertdelar ---
with st.expander("Anpassade offertdelar", expanded=True):
    with st.form("add_custom_item_form"):
        cols = st.columns([3, 1, 1, 1, 1])
        with cols[0]:
            beskrivning = st.text_input("Beskrivning", value="")
        with cols[1]:
            pris_per_st = st.number_input("Pris /st", min_value=0, value=0, step=1)
        with cols[2]:
            antal = st.number_input("Antal", min_value=0, value=1, step=1)
        with cols[3]:
            rabatt_procent = st.number_input("Rabatt (%)", min_value=0, max_value=100, value=0)
        with cols[4]:
            kategori_typ = st.selectbox("Typ", ["Månadskostnad", "Engångskostnad"])

        submitted = st.form_submit_button("Lägg till")

        if submitted and beskrivning:
            custom_item = {
                'Beskrivning': beskrivning,
                'Pris': pris_per_st,
                'Antal': antal,
                'Rabatt': rabatt_procent,
                'Typ': kategori_typ
            }
            st.session_state['custom_items'].append(custom_item)
            st.success(f"Offertdelen '{beskrivning}' har lagts till.")

            if rabatt_procent > 0:
                any_discount = True

    # Visa lista över anpassade offertdelar med möjlighet att redigera och ta bort
    if st.session_state['custom_items']:
        st.subheader("Anpassade offertdelar som har lagts till")
        for idx, item in enumerate(st.session_state['custom_items']):
            cols = st.columns([6, 1, 1])
            with cols[0]:
                st.write(f"{idx+1}. {item['Beskrivning']} - {item['Pris']} kr/st - Antal: {item['Antal']} - Rabatt: {item['Rabatt']}% - Typ: {item['Typ']}")
            with cols[1]:
                if st.button("Redigera", key=f"edit_{idx}"):
                    st.session_state['edit_index'] = idx
            with cols[2]:
                if st.button("Ta bort", key=f"delete_{idx}"):
                    st.session_state['custom_items'].pop(idx)
                    if st.session_state['edit_index'] == idx:
                        st.session_state['edit_index'] = None
                    elif st.session_state['edit_index'] is not None and st.session_state['edit_index'] > idx:
                        st.session_state['edit_index'] -= 1
                    st.experimental_set_query_params()

# --- Hantera redigering av anpassade offertdelar ---
if st.session_state['edit_index'] is not None:
    idx = st.session_state['edit_index']
    item = st.session_state['custom_items'][idx]
    st.subheader("Redigera offertdel")
    with st.form("edit_custom_item_form"):
        cols = st.columns([3, 1, 1, 1, 1])
        with cols[0]:
            beskrivning = st.text_input("Beskrivning", value=item['Beskrivning'])
        with cols[1]:
            if isinstance(item['Pris'], (int, float)):
                pris_per_st = st.number_input("Pris /st", min_value=0, value=float(item['Pris']), step=1.0)
            else:
                pris_per_st = st.number_input("Pris /st", min_value=0, value=0, step=1.0)
        with cols[2]:
            antal = st.number_input("Antal", min_value=0, value=int(item['Antal']), step=1)
        with cols[3]:
            if isinstance(item['Rabatt'], (int, float)):
                rabatt_procent = st.number_input("Rabatt (%)", min_value=0, max_value=100, value=float(item['Rabatt']))
            else:
                rabatt_procent = st.number_input("Rabatt (%)", min_value=0, max_value=100, value=0)
        with cols[4]:
            if item['Typ'] in ["Månadskostnad", "Engångskostnad"]:
                kategori_typ = st.selectbox("Typ", ["Månadskostnad", "Engångskostnad"],
                                            index=["Månadskostnad", "Engångskostnad"].index(item['Typ']))
            else:
                kategori_typ = st.selectbox("Typ", ["Månadskostnad", "Engångskostnad"])

        submitted = st.form_submit_button("Spara ändringar")
        canceled = st.form_submit_button("Avbryt")
        if submitted:
            st.session_state['custom_items'][idx] = {
                'Beskrivning': beskrivning,
                'Pris': pris_per_st,
                'Antal': antal,
                'Rabatt': rabatt_procent,
                'Typ': kategori_typ
            }
            st.session_state['edit_index'] = None
            st.success("Offertdelen har uppdaterats.")
            st.experimental_set_query_params()
        elif canceled:
            st.session_state['edit_index'] = None
            st.info("Redigering avbruten.")
            st.experimental_set_query_params()

# --- Bearbeta anpassade offertdelar ---
for item in st.session_state['custom_items']:
    beskrivning = item['Beskrivning']
    original_pris = item['Pris']
    antal = item['Antal']
    rabatt_procent = item['Rabatt']
    kategori_typ = item['Typ']

    # Beräkna pris med rabatt
    rabatterat_pris = original_pris * (1 - rabatt_procent / 100)
    tot_pris = rabatterat_pris * antal

    # Formatera antal och priser
    antal_formatted = int(antal)
    original_pris_formatted = f"{original_pris:,.2f} kr".replace(',', ' ') if isinstance(original_pris, (int, float)) else original_pris
    rabatterat_pris_formatted = f"{rabatterat_pris:,.2f} kr".replace(',', ' ') if isinstance(rabatterat_pris, (int, float)) else rabatterat_pris
    tot_pris_formatted = f"{tot_pris:,.2f} kr".replace(',', ' ') if isinstance(tot_pris, (int, float)) else tot_pris

    # Kontrollera om antalet är 0 och rabatten inte är 100%
    if antal == 0 and rabatt_procent < 100:
        continue  # Hoppa över denna offertdel

    # Lägg till i sammanfattningen endast om priset är numeriskt
    if isinstance(original_pris, (int, float)):
        # Uppdatera totalsummor baserat på typ
        if kategori_typ == "Engångskostnad":
            total_engangskostnad += tot_pris
            kategori_namn = 'Anpassade offertdelar - Engångskostnad'
        else:
            total_manadskostnad += tot_pris
            kategori_namn = 'Anpassade offertdelar - Månadskostnad'

        item_dict = {
            'Huvudkategori': 'Anpassade offertdelar',
            'Kategori': kategori_namn,
            'Typ': kategori_typ,
            'Beskrivning': beskrivning,
            'Pris /st': original_pris_formatted,
            'Antal': antal_formatted,
            'Tot.pris': tot_pris_formatted
        }
        if rabatt_procent > 0:
            item_dict['Rabatt (%)'] = rabatt_procent
            item_dict['Pris efter rabatt'] = rabatterat_pris_formatted
            any_discount = True

        total_valda_delar.append(item_dict)

# --- Sammanfattning i sidopanelen ---
with st.sidebar:
    st.header("Sammanfattning")

    if total_valda_delar or st.session_state['custom_items']:
        # Kontrollera om någon rabatt har använts
        any_discount_in_items = any('Rabatt (%)' in item and item['Rabatt (%)'] > 0 for item in total_valda_delar)

        if any_discount_in_items:
            headers = ['Benämning', 'Pris /st', 'Rabatt (%)', 'Pris efter rabatt', 'Antal', 'Tot.pris']
        else:
            headers = ['Benämning', 'Pris /st', 'Antal', 'Tot.pris']

        # Sortera total_valda_delar efter 'Kategori'
        sorted_items = sorted(total_valda_delar, key=lambda x: x['Kategori'])

        # Bygg CSV-rader med kategorirubriker
        csv_rows = []
        for kategori, items in groupby(sorted_items, key=lambda x: x['Kategori']):
            items = list(items)  # Konvertera groupby-objektet till en lista
            # Lägg till kategorirubrik
            csv_rows.append({'Benämning': kategori})
            # Lägg till kolumnrubriker
            header_row = {'Benämning': 'Benämning', 'Pris /st': 'Pris /st', 'Antal': 'Antal', 'Tot.pris': 'Tot.pris'}
            if any_discount_in_items:
                header_row['Rabatt (%)'] = 'Rabatt (%)'
                header_row['Pris efter rabatt'] = 'Pris efter rabatt'
            csv_rows.append(header_row)
            kategori_summa = 0.0
            typ = None
            for item in items:
                # Lägg till item-data
                row = {
                    'Benämning': item['Beskrivning'],
                    'Pris /st': item['Pris /st'],
                    'Antal': item['Antal'],
                    'Tot.pris': item['Tot.pris']
                }
                if any_discount_in_items and 'Rabatt (%)' in item:
                    row['Rabatt (%)'] = f"{item['Rabatt (%)']:.0f}%"
                    row['Pris efter rabatt'] = item['Pris efter rabatt']
                elif any_discount_in_items:
                    row['Rabatt (%)'] = ''
                    row['Pris efter rabatt'] = ''
                csv_rows.append(row)
                # Summera totalen för kategorin
                tot_pris_str = item['Tot.pris']
                try:
                    # Ta bort icke-numeriska tecken
                    tot_pris_numeric = float(re.sub(r'[^\d.,]', '', tot_pris_str).replace(',', '.'))
                    kategori_summa += tot_pris_numeric
                except ValueError:
                    pass
                typ = item['Typ']
            # Efter items, lägg till sumrad
            if typ == 'Månadskostnad':
                sum_label = 'Summa per månad'
            else:
                sum_label = 'Summa'
            csv_rows.append({'Benämning': sum_label, 'Tot.pris': f"{kategori_summa:,.2f} kr".replace(',', ' ')})
            # Lägg till tom rad för avstånd
            csv_rows.append({key: '' for key in headers})

        # Skapa DataFrame för sammanfattning
        df_total = pd.DataFrame(csv_rows)
        df_total = df_total.fillna('')  # Fyller NaN med tomma strängar

        # Visa sammanfattning i sidopanelen
        st.table(df_total[headers])

        # Totalsummor
        st.markdown(f"**Total månadskostnad**: {int(total_manadskostnad)} kr")
        st.markdown(f"**Total engångskostnad**: {int(total_engangskostnad)} kr")

        # Villkor att inkludera i CSV-filen
        villkor = [
            "Vi förutsätter att det finns lediga nätverksuttag Cat 6 där utrustning ska placeras.",
            "Montering av accesspunkter utförs av elektriker enligt separat offert.",
            "Lösningen kan kompletteras med fler switchar eller accesspunkter vid behov.",
            "Fastighetsnät ingår ej, separat offert tillkommer.",
            "Projektledning ingår ej.",
            "Alla tjänster tecknas på 36 månaders avtal.",
            "Anpassning av Wifi-portal debiteras löpande enligt kundens önskemål.",
            "CAT6 kablage är ej inkluderat."
        ]

        # Lägg till villkor i CSV-filen
        csv_rows.append({key: '' for key in headers})
        csv_rows.append({'Benämning': 'Villkor'})
        for condition in villkor:
            csv_rows.append({'Benämning': condition})

        # Skapa DataFrame för CSV
        df_csv = pd.DataFrame(csv_rows)
        df_csv = df_csv.fillna('')  # Fyller NaN med tomma strängar

        # Ladda ner CSV-fil
        st.download_button(
            label="Ladda ner sammanfattning som CSV",
            data=df_csv.to_csv(index=False, sep='\t').encode('utf-8'),
            file_name='offert_sammanfattning.csv',
            mime='text/csv',
        )
    else:
        st.write("Inga produkter valda ännu.")

# --- Lägg till Footer ---
footer = """
<style>
.footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    background-color: transparent;
    color: inherit;
    text-align: center;
    padding: 10px 0;
    font-size: 14px;
    pointer-events: none;
    z-index: 1000; /* Se till att footern ligger ovanpå andra element */
}

/* Anpassa textfärg beroende på dark/light mode */
@media (prefers-color-scheme: dark) {
    .footer {
        color: #FFFFFF; /* Vit text för mörkt tema */
    }
}

@media (prefers-color-scheme: light) {
    .footer {
        color: #000000; /* Svart text för ljust tema */
    }
}
</style>
<div class="footer">
    © 2024 Avoki AB. Alla rättigheter förbehållna.
</div>
"""

st.markdown(footer, unsafe_allow_html=True)
