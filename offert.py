import streamlit as st
import pandas as pd
import re
from itertools import groupby
from streamlit_pills import pills  # Importera streamlit_pills

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
LOGO_URL_LARGE = "https://www.avoki.com/media/s3ffirjs/avoki_logotype_white_rgb.png"
LOGO_URL_SMALL = "https://www.avoki.com/media/s3ffirjs/avoki_logotype_white_rgb.png"

st.logo(
    image=LOGO_URL_LARGE,
    link="https://avoki.com",
    icon_image=LOGO_URL_SMALL
)

# --- Toggle för att visa/dölja rabattfält ---
toggle_discount = st.checkbox(
    "Visa rabattfält",
    value=st.session_state['show_discount'],
    key='toggle_discount'
)
st.session_state['show_discount'] = toggle_discount

# --- Kategorier som är engångskostnader ---
engangskostnad_kategorier = [
    'Kablage Engångskostnad',
    'Årlig drift',
    'X-One 365 Cloud Security - Engångskostnad',
    'X-One 365 Endpoint Security - Engångskostnad',
    'Anpassade offertdelar - Engångskostnad',
    'Tidsuppskattning installation nätverk'
]

# --- Fördefinierade offertdelar grupperade per kategori ---
offertdelar = {
    'Nätverk som tjänst': {
        'Lokal Brandvägg - Månadskostnad': [
            {'Beskrivning': 'Lokal brandvägg 1000 Mbit/s med UTP', 'Pris': 1295},
            {'Beskrivning': 'Unified Threat Protection', 'Pris': 200},
            {'Beskrivning': 'SSL VPN', 'Pris': 150}
        ],
        'WiFi som tjänst - Månadskostnad': [
            {'Beskrivning': 'Basic Wi-Fi', 'Pris': 100},
            {'Beskrivning': 'Premium Wi-Fi 802.11ax', 'Pris': 175},
            {'Beskrivning': 'Outdoor Wi-Fi', 'Pris': 250}
        ],
        'Switchar som tjänst - Månadskostnad': [
            {'Beskrivning': 'Access switch 24-portar PoE+', 'Pris': 295},
            {'Beskrivning': 'Access switch 24-portar', 'Pris': 250},
            {'Beskrivning': 'Access switch 48-portar PoE+', 'Pris': 500}
        ],
        'UPS som tjänst - Månadskostnad': [
            {'Beskrivning': 'UPS 1kVa', 'Pris': 175},
            {'Beskrivning': 'UPS 3kVa', 'Pris': 300}
        ],
        'Kablage Engångskostnad': [
            {'Beskrivning': 'CAT6 patch', 'Pris': 35}
        ],
        'Övervakning Nätverk - Månadskostnad': [
            {'Beskrivning': 'Övervakning switchar & backup av konfiguration', 'Pris': 35},
            {'Beskrivning': 'Övervakning accesspunkter (per enhet)', 'Pris': 35},
            {'Beskrivning': 'Övervakning brandvägg & backup av konfiguration', 'Pris': 250},
            {'Beskrivning': 'Övervakning UPS (per enhet)', 'Pris': 35},
            {'Beskrivning': 'CloudIQ', 'Pris': 54}
        ],
        'Årlig drift': [
            {'Beskrivning': 'Genomgång av säkerhet', 'Pris': 1250},
            {'Beskrivning': 'Mjukvaruuppgradering av accesspunkter', 'Pris': 1250},
            {'Beskrivning': 'Mjukvaruuppgradering av switchar', 'Pris': 1250},
            {'Beskrivning': 'Uppdatering av dokumentation', 'Pris': 1250},
            {'Beskrivning': 'WiFi mätning på plats', 'Pris': 1250}
        ],
        'Tidsuppskattning installation nätverk': [
            {'Beskrivning': 'Uppgradering & grundkonfiguration av brandvägg', 'Pris': 1250, 'Antal per enhet': 1.5},
            {'Beskrivning': 'Uppgradering & grundkonfiguration av accesspunkter', 'Pris': 1250, 'Antal per enhet': 0.5},
            {'Beskrivning': 'Uppgradering & grundkonfiguration av switchar', 'Pris': 1250, 'Antal per enhet': 1.0},
            {'Beskrivning': 'Uppackning av UPS, konfiguration och montering', 'Pris': 1250, 'Antal per enhet': 1.5},
            {'Beskrivning': 'Driftsättning på plats samt tester på plats', 'Pris': 1250, 'Antal': 4},
            {'Beskrivning': 'Wi-Fi mätning på plats', 'Pris': 1250, 'Antal': 4},
            {'Beskrivning': 'Dokumentation av lösningen', 'Pris': 1250, 'Antal': 1}
        ]
    },
    'X-One': {
        'X-One 365 Cloud Security - Månadskostnad': [],
        'X-One 365 Cloud Security - Engångskostnad': [
            {'Beskrivning': 'Driftsättning X-One Tier 1-4', 'Pris': 2995},
            {'Beskrivning': 'Driftsättning X-One Tier 5-7', 'Pris': 4995}
        ],
        'X-One 365 Endpoint Security - Månadskostnad': [],
        'X-One 365 Endpoint Security - Engångskostnad': [
            {'Beskrivning': 'Driftsättning X-One Tier 1-4', 'Pris': 2995},
            {'Beskrivning': 'Driftsättning X-One Tier 5-7', 'Pris': 4995}
        ]
    },
    'Microsoft 365 CSP': {
      'Licenser': [
            {'Beskrivning': 'Microsoft 365 Business Basic', 'Pris': 50},
            {'Beskrivning': 'Microsoft 365 Business Standard', 'Pris': 100},
            {'Beskrivning': 'Microsoft 365 Business Premium', 'Pris': 243.1},
        ]
    }

}

# --- Licenskrav baserat på Microsoft 365-plan ---
licenses_requirements = {
    'Microsoft 365 A3': {
        'Cloud Security': 'Microsoft 365 A5 Security for personnel, students available for free***',
        'Endpoint Security': 'Microsoft 365 A5 Security for personnel, students available for free***, servers need separate licenses',
        'Endpoint Security Premium': 'Microsoft 365 A5 Security for personnel, students available for free***, servers need separate licenses',
        'Rekommenderad licensuppsättning': 'Microsoft 365 A5 Security for personnel, students available for free***, Defender for Servers plan 1 with Azure Arc'
    },
    'Microsoft 365 A5': {
        'Cloud Security': 'Included',
        'Endpoint Security': 'Included for clients, servers need separate licenses',
        'Endpoint Security Premium': 'Included for clients, servers need separate licenses',
        'Rekommenderad licensuppsättning': 'Defender for Servers Plan 1 with Azure Arc'
    },
    'Microsoft 365 F1': {
        'Cloud Security': 'Microsoft 365 F5 Security Add-on',
        'Endpoint Security': 'Microsoft 365 F5 Security Add-on, servers need separate licenses',
        'Endpoint Security Premium': 'Microsoft 365 F5 Security Add-on, servers need separate licenses',
        'Rekommenderad licensuppsättning': 'Microsoft 365 F5 Security, Defender for Servers plan 1 with Azure Arc'
    },
    'Microsoft 365 F3': {
        'Cloud Security': 'Microsoft 365 F5 Security Add-on',
        'Endpoint Security': 'Microsoft 365 F5 Security Add-on, servers need separate licenses',
        'Endpoint Security Premium': 'Microsoft 365 F5 Security Add-on, servers need separate licenses',
        'Rekommenderad licensuppsättning': 'Microsoft 365 F5 Security, Defender for Servers plan 1 with Azure Arc onboarded'
    },
    'Microsoft 365 E3': {
        'Cloud Security': 'Defender for Office 365 Plan 1 available as addon. Included in Microsoft E5 Security',
        'Endpoint Security': 'Defender for Endpoint Plan 2 available as addon. Included in Microsoft E5 Security, servers need separate licenses',
        'Endpoint Security Premium': 'Defender for Endpoint Plan 2 available as addon. Included in Microsoft E5 Security, servers need separate licenses',
        'Rekommenderad licensuppsättning': 'Microsoft E5 Security, Defender for Servers plan 1 with Azure Arc'
    },
    'Microsoft 365 E5': {
        'Cloud Security': 'Included',
        'Endpoint Security': 'Included for clients, servers need separate licenses',
        'Endpoint Security Premium': 'Included for clients, servers need separate licenses',
        'Rekommenderad licensuppsättning': 'Defender for Servers plan 1 with Azure Arc'
    },
    'Microsoft Business Premium': {
        'Cloud Security': 'Included',
        'Endpoint Security': 'Included for clients, servers need separate licenses',
        'Endpoint Security Premium': 'Included for clients but Defender for Endpoint Plan 2 is recommended for extended coverage and features such as advanced threat hunting, servers need separate licenses',
        'Rekommenderad licensuppsättning': 'Defender for Endpoint Plan 2, Defender for Servers plan 1 with Azure Arc onboarded'
    }
}

# --- Spåra totalen av enheter ---
total_accesspunkter = 0
total_switchar = 0
total_ups = 0
total_brandvaggar = 0

# --- Variabler för att spåra val ---
wifi_selected = False
any_hardware_selected = False

# --- Lista för att lagra alla valda delar ---
total_valda_delar = []
any_discount = False  # Variabel för att kontrollera rabatter

# --- Totalsummor ---
total_manadskostnad = 0
total_engangskostnad = 0

# --- Prislista och Tier-definitioner ---
tiers = [
    {'Beskrivning': 'Tier 1 (1 - 4 användare)', 'Pris': 630},
    {'Beskrivning': 'Tier 2 (5 - 9 användare)', 'Pris': 1045},
    {'Beskrivning': 'Tier 3 (10 - 19 användare)', 'Pris': 1385},
    {'Beskrivning': 'Tier 4 (20 - 49 användare)', 'Pris': 2495},
    {'Beskrivning': 'Tier 5 (50 - 99 användare)', 'Pris': 3495},
    {'Beskrivning': 'Tier 6 (100 - 249 användare)', 'Pris': 4995},
    {'Beskrivning': 'Tier 7 (250+ användare)', 'Pris': 'Separat offert'},
]

# --- Funktion för att hantera offertdelar ---
def hantera_offertdel(kategori, offertdel, huvudkategori,
                      inkludera, prefix='', skip_quantity_input=False):
    global any_discount, total_manadskostnad, total_engangskostnad

    # Vi visar inte längre några val för dessa delar i användargränssnittet
    # Om skip_quantity_input är True, sätt antal direkt
    if skip_quantity_input:
        antal = offertdel.get('Antal', 1)
    else:
        if inkludera == 'Ja':
            default_antal = offertdel.get('Antal', 1)
        else:
            default_antal = 0

        antal = default_antal

    rabatt_procent = 0

    # Beräkna pris med rabatt
    original_pris = offertdel['Pris']
    try:
        if isinstance(original_pris, (int, float)):
            rabatterat_pris = float(original_pris) * (1 - rabatt_procent / 100)
            tot_pris = rabatterat_pris * antal
            original_pris_formatted = f"{original_pris:,.2f} kr"
            rabatterat_pris_formatted = f"{rabatterat_pris:,.2f} kr"
            tot_pris_formatted = f"{tot_pris:,.2f} kr"
        else:
            rabatterat_pris = original_pris
            tot_pris = original_pris
            original_pris_formatted = original_pris
            rabatterat_pris_formatted = original_pris
            tot_pris_formatted = original_pris
            antal = 0
    except (ValueError, TypeError):
        original_pris_formatted = original_pris
        rabatterat_pris_formatted = original_pris
        tot_pris_formatted = original_pris
        antal = 0

    # Formatera antal
    try:
        if antal.is_integer():
            antal_formatted = int(antal)
        else:
            antal_formatted = antal
    except AttributeError:
        antal_formatted = antal

    # Kontrollera om antalet är 0
    if antal == 0:
        return

    # Bestäm typ baserat på kategori
    if 'Engångskostnad' in kategori or kategori in engangskostnad_kategorier:
        typ = 'Engångskostnad'
        total_engangskostnad += tot_pris
    else:
        typ = 'Månadskostnad'
        total_manadskostnad += tot_pris

    # Lägg till valda delar i sammanfattningen
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
        total_valda_delar.append(item)


def hantera_microsoft_licenser():
    huvudkategori = 'Microsoft 365 CSP'
    kategori = 'Licenser'
    delar = offertdelar[huvudkategori][kategori]
    
    st.subheader(huvudkategori)
    
    # Skapa en lista med licensbeskrivningar för multiväljaren
    licens_beskrivningar = [licens['Beskrivning'] for licens in delar]
    
    # Visa en sökbar multiväljare
    valda_licenser = st.multiselect(
        "Välj Microsoft 365 CSP-licenser",
        options=licens_beskrivningar,
        key='valda_microsoft_licenser'
    )
    
    # Hantera valda licenser
    for licens_namn in valda_licenser:
        # Hämta licensdetaljer
        licens = next((lic for lic in delar if lic['Beskrivning'] == licens_namn), None)
        if licens:
            # Ange antal för varje vald licens
            antal = st.number_input(
                f"Ange antal för {licens_namn}",
                min_value=1,
                value=1,
                step=1,
                key=f"antal_{licens_namn}"
            )
            licens_copy = licens.copy()
            licens_copy['Antal'] = antal
            hantera_offertdel(
                kategori=kategori,
                offertdel=licens_copy,
                huvudkategori=huvudkategori,
                inkludera='Ja',
                skip_quantity_input=True
            )


# --- Funktion för att bestämma Tier baserat på antal användare ---
def bestäm_tier_xone(antal_användare):
    for tier in tiers:
        beskrivning = tier['Beskrivning']
        pris = tier['Pris']
        match = re.search(r'(\d+)\s*-\s*(\d+)', beskrivning)
        if match:
            min_anv, max_anv = int(match.group(1)), int(match.group(2))
            if min_anv <= antal_användare <= max_anv:
                return beskrivning, pris
        elif '250+' in beskrivning and antal_användare >= 250:
            return beskrivning, pris
    return None, None

# --- Hantera Nätverk som tjänst ---


with st.expander("Nätverk som tjänst", expanded=True):
    huvudkategori = 'Nätverk som tjänst'
    for kategori, delar in offertdelar['Nätverk som tjänst'].items():
        if kategori in ['Tidsuppskattning installation nätverk', 'Övervakning Nätverk - Månadskostnad']:
            continue  # Hanteras senare
        st.subheader(kategori)

        if kategori == 'Lokal Brandvägg - Månadskostnad':
            inkludera_options = ['Nej', 'Ja']
            selected_option = pills(
                label=f"Inkludera Lokal brandvägg 1000 Mbit/s med UTP?",
                options=inkludera_options,
                key=f"{kategori}_Lokal_brandvagg",
                label_visibility='visible',
                clearable=False
            )
            inkludera = selected_option if selected_option else 'Nej'

            if inkludera == 'Ja':
                any_hardware_selected = True
                hantera_offertdel(kategori, delar[0], huvudkategori, inkludera)
                total_brandvaggar += 1  # Uppdatera totalen

                # Inkludera övervakning av brandvägg automatiskt
                overvakning_kategori = 'Övervakning Nätverk - Månadskostnad'
                overvakning_delar = offertdelar['Nätverk som tjänst'][overvakning_kategori]
                for offertdel in overvakning_delar:
                    if offertdel['Beskrivning'] == 'Övervakning brandvägg & backup av konfiguration':
                        offertdel_copy = offertdel.copy()
                        offertdel_copy['Antal'] = total_brandvaggar
                        hantera_offertdel(
                            overvakning_kategori,
                            offertdel_copy,
                            huvudkategori,
                            'Ja',
                            skip_quantity_input=True
                        )

                # Hantera extra optioner
                for offertdel in delar[1:]:
                    selected_option = pills(
                        label=f"Inkludera {offertdel['Beskrivning']}?",
                        options=['Nej', 'Ja'],
                        key=f"{kategori}_{offertdel['Beskrivning']}",
                        label_visibility='visible',
                        clearable=False
                    )
                    inkludera_extra = selected_option if selected_option else 'Nej'
                    if inkludera_extra == 'Ja':
                        hantera_offertdel(kategori, offertdel, huvudkategori, inkludera_extra)
            else:
                pass  # Gör inget

        elif kategori == 'WiFi som tjänst - Månadskostnad':
            # Hantera WiFi-valet
            inkludera_wifi = pills(
                label="Vill du inkludera WiFi som tjänst?",
                options=['Nej', 'Ja'],
                key='include_wifi',
                label_visibility='visible',
                clearable=False
            )

            if inkludera_wifi == 'Ja':
                wifi_selected = True
                any_hardware_selected = True
                # Välj WiFi-variant
                wifi_variant = pills(
                    label="Välj WiFi-variant",
                    options=[offertdel['Beskrivning'] for offertdel in delar],
                    key='wifi_variant',
                    label_visibility='visible',
                    clearable=False
                )

                # Ange antal accesspunkter
                wifi_antal = st.number_input(
                    f"Ange antal för {wifi_variant}",
                    min_value=1,
                    value=1,
                    step=1,
                    key=f"antal_{wifi_variant}"
                )

                # Hämta offertdelen för vald variant
                for offertdel in delar:
                    if offertdel['Beskrivning'] == wifi_variant:
                        offertdel_copy = offertdel.copy()
                        offertdel_copy['Antal'] = wifi_antal
                        hantera_offertdel(
                            kategori,
                            offertdel_copy,
                            huvudkategori,
                            'Ja',
                            skip_quantity_input=True
                        )
                        total_accesspunkter += wifi_antal

        elif kategori == 'Switchar som tjänst - Månadskostnad':
            # Hantera Switchar-valet
            inkludera_switch = pills(
                label="Vill du inkludera Switchar som tjänst?",
                options=['Nej', 'Ja'],
                key='include_switch',
                label_visibility='visible',
                clearable=False
            )

            if inkludera_switch == 'Ja':
                any_hardware_selected = True
                # Välj Switch-variant
                switch_variant = pills(
                    label="Välj Switch-variant",
                    options=[offertdel['Beskrivning'] for offertdel in delar],
                    key='switch_variant',
                    label_visibility='visible',
                    clearable=False
                )

                # Ange antal switchar
                switch_antal = st.number_input(
                    f"Ange antal för {switch_variant}",
                    min_value=1,
                    value=1,
                    step=1,
                    key=f"antal_{switch_variant}"
                )

                # Hämta offertdelen för vald variant
                for offertdel in delar:
                    if offertdel['Beskrivning'] == switch_variant:
                        offertdel_copy = offertdel.copy()
                        offertdel_copy['Antal'] = switch_antal
                        hantera_offertdel(
                            kategori,
                            offertdel_copy,
                            huvudkategori,
                            'Ja',
                            skip_quantity_input=True
                        )
                        total_switchar += switch_antal

        elif kategori == 'UPS som tjänst - Månadskostnad':
            # Hantera UPS-valet
            inkludera_ups = pills(
                label="Vill du inkludera UPS?",
                options=['Nej', 'Ja'],
                key='include_ups',
                label_visibility='visible',
                clearable=False
            )

            if inkludera_ups == 'Ja':
                any_hardware_selected = True
                # Välj UPS-variant
                ups_variant = pills(
                    label="Välj UPS-variant",
                    options=[offertdel['Beskrivning'] for offertdel in delar],
                    key='ups_variant',
                    label_visibility='visible',
                    clearable=False
                )

                # Ange antal UPS
                ups_antal = st.number_input(
                    f"Ange antal för {ups_variant}",
                    min_value=1,
                    value=1,
                    step=1,
                    key=f"antal_{ups_variant}"
                )

                # Hämta offertdelen för vald variant
                for offertdel in delar:
                    if offertdel['Beskrivning'] == ups_variant:
                        offertdel_copy = offertdel.copy()
                        offertdel_copy['Antal'] = ups_antal
                        hantera_offertdel(
                            kategori,
                            offertdel_copy,
                            huvudkategori,
                            'Ja',
                            skip_quantity_input=True
                        )
                        total_ups += ups_antal

        elif kategori == 'Årlig drift':
            inkludera_arlig_drift = pills(
                label="Vill du inkludera Årlig drift?",
                options=['Nej', 'Ja'],
                key='include_arlig_drift',
                label_visibility='visible',
                clearable=False
            )

            if inkludera_arlig_drift == 'Ja':
                for offertdel in delar:
                    hantera_offertdel(kategori, offertdel, huvudkategori, 'Ja')

        else:
            # Hantera övriga kategorier
            for offertdel in delar:
                inkludera = pills(
                    label=f"Inkludera {offertdel['Beskrivning']}?",
                    options=['Nej', 'Ja'],
                    key=f"{kategori}_{offertdel['Beskrivning']}",
                    label_visibility='visible',
                    clearable=False
                )
                if inkludera == 'Ja':
                    hantera_offertdel(kategori, offertdel, huvudkategori, inkludera)

    # Hantera Övervakning Nätverk - Månadskostnad (automatiskt)
    overvakning_kategori = 'Övervakning Nätverk - Månadskostnad'
    overvakning_delar = offertdelar['Nätverk som tjänst'][overvakning_kategori]

    # Inkludera övervakning av switchar
    if total_switchar > 0:
        for offertdel in overvakning_delar:
            if offertdel['Beskrivning'] == 'Övervakning switchar & backup av konfiguration':
                offertdel_copy = offertdel.copy()
                offertdel_copy['Antal'] = total_switchar
                hantera_offertdel(
                    overvakning_kategori,
                    offertdel_copy,
                    huvudkategori,
                    'Ja',
                    skip_quantity_input=True
                )

    # Inkludera övervakning av accesspunkter
    if total_accesspunkter > 0:
        for offertdel in overvakning_delar:
            if offertdel['Beskrivning'] == 'Övervakning accesspunkter (per enhet)':
                offertdel_copy = offertdel.copy()
                offertdel_copy['Antal'] = total_accesspunkter
                hantera_offertdel(
                    overvakning_kategori,
                    offertdel_copy,
                    huvudkategori,
                    'Ja',
                    skip_quantity_input=True
                )

    # Inkludera övervakning av UPS
    if total_ups > 0:
        for offertdel in overvakning_delar:
            if offertdel['Beskrivning'] == 'Övervakning UPS (per enhet)':
                offertdel_copy = offertdel.copy()
                offertdel_copy['Antal'] = total_ups
                hantera_offertdel(
                    overvakning_kategori,
                    offertdel_copy,
                    huvudkategori,
                    'Ja',
                    skip_quantity_input=True
                )

    # Inkludera CloudIQ
    if total_switchar > 0 or total_accesspunkter > 0:
        for offertdel in overvakning_delar:
            if offertdel['Beskrivning'] == 'CloudIQ':
                cloudiq_antal = total_switchar + total_accesspunkter
                offertdel_copy = offertdel.copy()
                offertdel_copy['Antal'] = cloudiq_antal
                hantera_offertdel(
                    overvakning_kategori,
                    offertdel_copy,
                    huvudkategori,
                    'Ja',
                    skip_quantity_input=True
                )

    # Hantera Tidsuppskattning installation nätverk
    tidskategori = 'Tidsuppskattning installation nätverk'
    tidsdelar = offertdelar['Nätverk som tjänst'][tidskategori]

    # Uppgradering & grundkonfiguration av brandvägg
    if total_brandvaggar > 0:
        for offertdel in tidsdelar:
            if offertdel['Beskrivning'] == 'Uppgradering & grundkonfiguration av brandvägg':
                offertdel_copy = offertdel.copy()
                offertdel_copy['Antal'] = total_brandvaggar * offertdel['Antal per enhet']
                hantera_offertdel(
                    tidskategori,
                    offertdel_copy,
                    huvudkategori,
                    'Ja',
                    skip_quantity_input=True
                )

    # Uppgradering & grundkonfiguration av accesspunkter
    if total_accesspunkter > 0:
        for offertdel in tidsdelar:
            if offertdel['Beskrivning'] == 'Uppgradering & grundkonfiguration av accesspunkter':
                offertdel_copy = offertdel.copy()
                offertdel_copy['Antal'] = total_accesspunkter * offertdel['Antal per enhet']
                hantera_offertdel(
                    tidskategori,
                    offertdel_copy,
                    huvudkategori,
                    'Ja',
                    skip_quantity_input=True
                )

    # Uppgradering & grundkonfiguration av switchar
    if total_switchar > 0:
        for offertdel in tidsdelar:
            if offertdel['Beskrivning'] == 'Uppgradering & grundkonfiguration av switchar':
                offertdel_copy = offertdel.copy()
                offertdel_copy['Antal'] = total_switchar * offertdel['Antal per enhet']
                hantera_offertdel(
                    tidskategori,
                    offertdel_copy,
                    huvudkategori,
                    'Ja',
                    skip_quantity_input=True
                )

    # Uppackning av UPS, konfiguration och montering
    if total_ups > 0:
        for offertdel in tidsdelar:
            if offertdel['Beskrivning'] == 'Uppackning av UPS, konfiguration och montering':
                offertdel_copy = offertdel.copy()
                offertdel_copy['Antal'] = total_ups * offertdel['Antal per enhet']
                hantera_offertdel(
                    tidskategori,
                    offertdel_copy,
                    huvudkategori,
                    'Ja',
                    skip_quantity_input=True
                )

    # Lägg till fasta tider baserat på villkor
    for offertdel in tidsdelar:
        if 'Antal' in offertdel and 'Antal per enhet' not in offertdel:
            include_item = False
            if offertdel['Beskrivning'] == 'Wi-Fi mätning på plats' and wifi_selected:
                include_item = True
            elif offertdel['Beskrivning'] == 'Driftsättning på plats samt tester på plats' and any_hardware_selected:
                include_item = True
            elif offertdel['Beskrivning'] == 'Dokumentation av lösningen' and any_hardware_selected:
                include_item = True
            if include_item:
                hantera_offertdel(
                    tidskategori,
                    offertdel,
                    huvudkategori,
                    'Ja',
                    skip_quantity_input=True
                )

# --- Resten av din kod för X-One, Anpassade offertdelar, Sammanfattning osv. ---

# --- Hantera X-One ---
with st.expander("X-One", expanded=True):
    huvudkategori = 'X-One'

with st.expander("Microsoft 365 CSP", expanded=True):
    hantera_microsoft_licenser()


    # --- Licensval baserat på Microsoft 365-plan ---
    st.subheader("Nuvarande licens")
    selected_m365_plan = st.selectbox(
        "Välj din nuvarande Microsoft 365 plan",
        options=list(licenses_requirements.keys()),
        key='selected_m365_plan'
    )

    # Hantera X-One 365 Cloud Security - Månadskostnad
    st.subheader('X-One 365 Cloud Security - Månadskostnad')
    antal_cloud_security = st.number_input(
        "Antal användare för X-One 365 Cloud Security",
        min_value=0,
        step=1,
        key='xone_cloud_security_users'
    )
    if antal_cloud_security > 0:
        beskrivning, pris = bestäm_tier_xone(antal_cloud_security)
        if beskrivning and pris:
            if isinstance(pris, (int, float)):
                offertdel = {'Beskrivning': beskrivning, 'Pris': pris}
                offertdel['Antal'] = 1
                hantera_offertdel(
                    kategori='X-One 365 Cloud Security - Månadskostnad',
                    offertdel=offertdel,
                    huvudkategori=huvudkategori,
                    inkludera='Ja'
                )
            else:
                st.warning("För mer än 249 användare, vänligen kontakta oss för en separat offert.")

    # Hantera X-One 365 Endpoint Security - Månadskostnad
    st.subheader('X-One 365 Endpoint Security - Månadskostnad')
    antal_endpoint_security = st.number_input(
        "Antal användare för X-One 365 Endpoint Security",
        min_value=0,
        step=1,
        key='xone_endpoint_security_users'
    )
    if antal_endpoint_security > 0:
        beskrivning, pris = bestäm_tier_xone(antal_endpoint_security)
        if beskrivning and pris:
            if isinstance(pris, (int, float)):
                offertdel = {'Beskrivning': beskrivning, 'Pris': pris}
                offertdel['Antal'] = 1
                hantera_offertdel(
                    kategori='X-One 365 Endpoint Security - Månadskostnad',
                    offertdel=offertdel,
                    huvudkategori=huvudkategori,
                    inkludera='Ja'
                )
            else:
                st.warning("För mer än 249 användare, vänligen kontakta oss för en separat offert.")

    # Hantera X-One 365 Cloud Security - Engångskostnad baserat på antal användare
    st.subheader('X-One 365 Cloud Security - Engångskostnad')
    if antal_cloud_security > 0:
        if 1 <= antal_cloud_security <= 49:
            deployment_option = 'Driftsättning X-One Tier 1-4'
        elif antal_cloud_security >= 50:
            deployment_option = 'Driftsättning X-One Tier 5-7'
        else:
            deployment_option = None

        if deployment_option:
            for offertdel in offertdelar['X-One']['X-One 365 Cloud Security - Engångskostnad']:
                if offertdel['Beskrivning'] == deployment_option:
                    offertdel_copy = offertdel.copy()
                    offertdel_copy['Antal'] = 1
                    hantera_offertdel(
                        kategori='X-One 365 Cloud Security - Engångskostnad',
                        offertdel=offertdel_copy,
                        huvudkategori=huvudkategori,
                        inkludera='Ja'
                    )

    # Hantera X-One 365 Endpoint Security - Engångskostnad baserat på antal användare
    st.subheader('X-One 365 Endpoint Security - Engångskostnad')
    if antal_endpoint_security > 0:
        if 1 <= antal_endpoint_security <= 49:
            deployment_option = 'Driftsättning X-One Tier 1-4'
        elif antal_endpoint_security >= 50:
            deployment_option = 'Driftsättning X-One Tier 5-7'
        else:
            deployment_option = None

        if deployment_option:
            for offertdel in offertdelar['X-One']['X-One 365 Endpoint Security - Engångskostnad']:
                if offertdel['Beskrivning'] == deployment_option:
                    offertdel_copy = offertdel.copy()
                    offertdel_copy['Antal'] = 1
                    hantera_offertdel(
                        kategori='X-One 365 Endpoint Security - Engångskostnad',
                        offertdel=offertdel_copy,
                        huvudkategori=huvudkategori,
                        inkludera='Ja'
                    )

    # --- Lägg till Licenskrav baserat på valda X-One-tjänster och Microsoft 365-plan ---
    def lägg_till_licenser(selected_plan, selected_services):
        if not selected_plan:
            return

        licenser = licenses_requirements.get(selected_plan, {})
        for service in selected_services:
            if service == 'X-One 365 Cloud Security - Månadskostnad':
                licens = licenser.get('Cloud Security')
                if licens and licens != 'Included':
                    item = {
                        'Huvudkategori': 'X-One',
                        'Kategori': 'X-One 365 Cloud Security - Licenskrav',
                        'Typ': 'Engångskostnad',
                        'Beskrivning': licens,
                        'Pris /st': 'N/A',
                        'Antal': 1,
                        'Tot.pris': 'N/A'
                    }
                    total_valda_delar.append(item)
            elif service == 'X-One 365 Endpoint Security - Månadskostnad':
                licens = licenser.get('Endpoint Security')
                if licens and licens != 'Included':
                    item = {
                        'Huvudkategori': 'X-One',
                        'Kategori': 'X-One 365 Endpoint Security - Licenskrav',
                        'Typ': 'Engångskostnad',
                        'Beskrivning': licens,
                        'Pris /st': 'N/A',
                        'Antal': 1,
                        'Tot.pris': 'N/A'
                    }
                    total_valda_delar.append(item)
            elif service == 'Rekommenderad licensuppsättning':
                licens = licenser.get('Rekommenderad licensuppsättning')
                if licens:
                    item = {
                        'Huvudkategori': 'X-One',
                        'Kategori': 'X-One - Rekommenderad Licensuppsättning',
                        'Typ': 'Engångskostnad',
                        'Beskrivning': licens,
                        'Pris /st': 'N/A',
                        'Antal': 1,
                        'Tot.pris': 'N/A'
                    }
                    total_valda_delar.append(item)

    # --- Efter alla tjänster är hanterade, sammanfoga licenser ---
    def hämta_valda_xone_tjänster():
        valda_tjänster = []
        if antal_cloud_security > 0:
            valda_tjänster.append('X-One 365 Cloud Security - Månadskostnad')
        if antal_endpoint_security > 0:
            valda_tjänster.append('X-One 365 Endpoint Security - Månadskostnad')
        return valda_tjänster

    selected_services = hämta_valda_xone_tjänster()
    lägg_till_licenser(selected_m365_plan, selected_services)



# --- Hantera Microsoft 365 CSP ---
def hantera_microsoft_licenser():
    huvudkategori = 'Microsoft 365 CSP'
    kategori = 'Licenser'
    delar = offertdelar[huvudkategori][kategori]
    
    st.subheader(huvudkategori)
    
    # Skapa en lista med licensbeskrivningar för multiväljaren
    licens_beskrivningar = [licens['Beskrivning'] for licens in delar]
    
    # Visa en sökbar multiväljare
    valda_licenser = st.multiselect(
        "Välj Microsoft 365 CSP-licenser",
        options=licens_beskrivningar,
        key='valda_microsoft_licenser'
    )
    
    # Hantera valda licenser
    for licens_namn in valda_licenser:
        # Hämta licensdetaljer
        licens = next((lic for lic in delar if lic['Beskrivning'] == licens_namn), None)
        if licens:
            cols = st.columns([2, 1])
            with cols[0]:
                # Ange antal för varje vald licens
                antal = st.number_input(
                    f"Ange antal för {licens_namn}",
                    min_value=1,
                    value=1,
                    step=1,
                    key=f"antal_{licens_namn}"
                )
            with cols[1]:
                if st.session_state['show_discount']:
                    rabatt_procent = st.number_input(
                        "Rabatt (%)",
                        min_value=0,
                        max_value=100,
                        value=0,
                        key=f"rabatt_{licens_namn}"
                    )
                else:
                    rabatt_procent = 0
            licens_copy = licens.copy()
            licens_copy['Antal'] = antal
            hantera_offertdel(
                kategori=kategori,
                offertdel=licens_copy,
                huvudkategori=huvudkategori,
                inkludera='Ja',
                prefix='Microsoft_',
                skip_quantity_input=True
            )



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
            antal = st.number_input("Antal", min_value=0, value=float(item['Antal']), step=1)
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
    if isinstance(original_pris, (int, float)):
        rabatterat_pris = original_pris * (1 - rabatt_procent / 100)
        tot_pris = rabatterat_pris * antal
        original_pris_formatted = f"{original_pris:,.2f} kr"
        rabatterat_pris_formatted = f"{rabatterat_pris:,.2f} kr"
        tot_pris_formatted = f"{tot_pris:,.2f} kr"
    else:
        # Hantera fall där priset är en sträng
        rabatterat_pris = original_pris
        tot_pris = original_pris
        original_pris_formatted = original_pris
        rabatterat_pris_formatted = original_pris
        tot_pris_formatted = original_pris
        antal = 0  # Sätt antal till 0 eftersom priset inte är numeriskt

    # Formatera antal som heltal
    antal_formatted = int(antal)

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

        # Sortera total_valda_delar efter 'Huvudkategori'
        sorted_items = sorted(total_valda_delar, key=lambda x: x['Huvudkategori'])

        # Bygg CSV-rader med kategorirubriker
        csv_rows_for_table = []  # För tabellen i sidopanelen
        csv_rows_for_csv = []    # För CSV-filen

        for huvudkategori, items_in_huvudkategori in groupby(sorted_items, key=lambda x: x['Huvudkategori']):
            items_in_huvudkategori = list(items_in_huvudkategori)
            for kategori, items in groupby(items_in_huvudkategori, key=lambda x: x['Kategori']):
                items = list(items)  # Konvertera groupby-objektet till en lista
                # Lägg till kategorirubrik
                kategori_rubrik = {'Benämning': kategori}
                csv_rows_for_table.append(kategori_rubrik)
                csv_rows_for_csv.append(kategori_rubrik)
                # Lägg till kolumnrubriker
                header_row = {'Benämning': 'Benämning', 'Pris /st': 'Pris /st', 'Antal': 'Antal', 'Tot.pris': 'Tot.pris'}
                if any_discount_in_items:
                    header_row['Rabatt (%)'] = 'Rabatt (%)'
                    header_row['Pris efter rabatt'] = 'Pris efter rabatt'
                csv_rows_for_table.append(header_row)
                csv_rows_for_csv.append(header_row)
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
                    csv_rows_for_table.append(row)
                    csv_rows_for_csv.append(row)
                    # Summera totalen för kategorin
                    tot_pris_str = item['Tot.pris']
                    try:
                        # Ta bort icke-numeriska tecken
                        tot_pris_numeric = float(re.sub(r'[^\d.,]', '', tot_pris_str).replace(',', '.'))
                        kategori_summa += tot_pris_numeric
                    except ValueError:
                        pass
                    typ = item['Typ']
                # Efter items, lägg till summa
                if typ == 'Månadskostnad':
                    sum_label = 'Summa per månad'
                else:
                    sum_label = 'Summa'
                summa_row = {'Benämning': sum_label, 'Tot.pris': f"{kategori_summa:,.2f} kr"}
                csv_rows_for_table.append(summa_row)
                csv_rows_for_csv.append(summa_row)
                # Lägg till tom rad för avstånd
                empty_row = {key: '' for key in headers}
                csv_rows_for_table.append(empty_row)
                csv_rows_for_csv.append(empty_row)

        # Skapa DataFrame för sammanfattning
        df_total = pd.DataFrame(csv_rows_for_table)
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

        # Lägg till villkor endast i CSV-filen
        csv_rows_for_csv.append({key: '' for key in headers})
        csv_rows_for_csv.append({'Benämning': 'Villkor'})
        for condition in villkor:
            csv_rows_for_csv.append({'Benämning': condition})

        # Skapa DataFrame för CSV
        df_csv = pd.DataFrame(csv_rows_for_csv)
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
    z-index: 1000;
}
@media (prefers-color-scheme: dark) {
    .footer {
        color: #FFFFFF;
    }
}
@media (prefers-color-scheme: light) {
    .footer {
        color: #000000;
    }
}
</style>
<div class="footer">
    © 2024 Max Remes. Alla rättigheter förbehållna.
</div>
"""

st.markdown(footer, unsafe_allow_html=True)
