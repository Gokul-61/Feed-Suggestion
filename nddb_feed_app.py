import streamlit as st
import pandas as pd

EXCEL_PATH = "Fodder and Nutrients.xlsx"

# Page config
st.set_page_config(
    page_title="Feed Recommendation System",
    page_icon="🌾",
    layout="wide"
)

# Professional Agri-based CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    .main { background-color: #f8f9fa; }

    .agri-header {
        background: linear-gradient(135deg, #2d5016 0%, #4a7c2c 100%);
        padding: 2.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .agri-title { color: white; font-size: 2.2rem; font-weight: 700; }
    .agri-subtitle { color: #c8e6c9; font-size: 1rem; margin-top: 0.5rem; }

    .section-header {
        color: #2d5016; font-size: 1.4rem; font-weight: 600;
        margin: 2rem 0 1rem 0; padding-bottom: 0.5rem;
        border-bottom: 3px solid #4a7c2c;
    }

    .feed-item {
        background: white; border: 1px solid #e0e0e0;
        border-radius: 8px; padding: 1.2rem; margin-bottom: 0.8rem;
        display: flex; justify-content: space-between; align-items: center;
        transition: all 0.2s;
    }
    .feed-item:hover { box-shadow: 0 2px 8px rgba(74,124,44,0.15); border-color: #4a7c2c; }

    .feed-label { color: #555; font-size: 0.85rem; font-weight: 500; letter-spacing: 0.5px; }
    .feed-name { color: #2d5016; font-size: 1.1rem; font-weight: 600; }
    .feed-quantity {
        background: #f1f8e9; color: #2d5016; padding: 0.5rem 1.2rem;
        border-radius: 6px; font-size: 1.3rem; font-weight: 700;
    }

    .nutrient-card {
        background: white; border: 2px solid #4a7c2c;
        border-radius: 10px; padding: 1.5rem; text-align: center; height: 100%;
    }
    .nutrient-label { color: #666; font-size: 0.9rem; }
    .nutrient-value { color: #2d5016; font-size: 2.0rem; font-weight: 700; }
    .nutrient-unit { color: #888; }

    .herd-summary {
        background: #f1f8e9; border-left: 4px solid #4a7c2c;
        padding: 1rem 1.5rem; margin-bottom: 0.8rem;
        border-radius: 4px;
    }
    .herd-ingredient { color: #2d5016; font-size: 1rem; font-weight: 600; }
    .herd-amount { color: #4a7c2c; font-size: 1.2rem; font-weight: 700; float: right; }

    .info-box {
        background: #11111; border-left: 4px solid #4a7c2c;
        padding: 1rem; border-radius: 4px; margin: 1rem 0;
        font-size: 0.9rem;
    }

    .custom-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #4a7c2c, transparent);
        margin: 2rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Load and clean data
@st.cache_data
def load_data():
    return pd.read_excel(EXCEL_PATH)

df = load_data()
df.columns = df.columns.str.strip().str.replace('\u200b','').str.replace('\ufeff','')

# -------------------------------
# NDDB BASE RATION VALUES (kg/day)
# -------------------------------
NDDB_COW = {
    "Dry (0 L milk)": {"dry": 7, "green": 4,  "conc": 2, "oil": 0, "bran": 0, "mineral": 50},
    "5 L milk":       {"dry": 7, "green": 4,  "conc": 4, "oil": 0, "bran": 0, "mineral": 100},
    "10 L milk":      {"dry": 7, "green": 4,  "conc": 6, "oil": 0, "bran": 0, "mineral": 150},
}

NDDB_BUFFALO = {
    "Dry (0 L milk)": {"dry": 6, "green": 2,  "conc": 0, "oil": 2, "bran": 0, "mineral": 75},
    "5 L milk":       {"dry": 7, "green": 5,  "conc": 5, "oil": 0, "bran": 0, "mineral": 125},
    "10 L milk":      {"dry": 7, "green": 10, "conc": 6, "oil": 2, "bran": 0, "mineral": 175},
}

# Pregnant animal ration from NDDB (generic cow/buffalo) – mid-points of ranges
PREGNANT_BASE = {"dry": 4.5, "green": 17.5, "conc": 2.5, "oil": 1.0, "bran": 0.0, "mineral": 50}

# Body size factors (approximate)
BODY_FACTORS = {
    "Small": 0.9,
    "Medium": 1.0,
    "Large": 1.15,
}

# -------------------------------
# HEADER
# -------------------------------
st.markdown("""
<div class="agri-header">
    <div class="agri-title">🌾 Feed Recommendation System</div>
    <div class="agri-subtitle">NDDB-Based Scientific Ration Balancing for Dairy Animals</div>
</div>
""", unsafe_allow_html=True)

# -------------------------------
# SIDEBAR CONFIG
# -------------------------------
with st.sidebar:
    st.markdown("### 📋 Animal Configuration")
    animal = st.selectbox("Animal Type", ["Cow", "Buffalo"])
    milk_level = st.selectbox("Milk Production Level", ["Dry (0 L milk)", "5 L milk", "10 L milk"])
    body_type = st.selectbox("Body Size", ["Small", "Medium", "Large"])
    stage = st.selectbox(
        "Stage of Lactation",
        ["Early lactation", "Mid lactation", "Late lactation", "Pregnant (7–9 months)", "Dry period"],
    )
    num = st.number_input("Number of Animals", 1, 500, 1)
    st.markdown("----")
    st.markdown("""
    <div class="info-box">
        Recommendations use NDDB TMR tables as base.<br>
        Body size and stage are used to make small +/- adjustments
        (early lactation ↑ concentrate, late lactation ↓ concentrate, pregnant animals use pregnant ration).
    </div>
    """, unsafe_allow_html=True)

# -------------------------------
# DETERMINE BASE RATION
# -------------------------------
def get_base_ration(animal, milk_level, stage):
    if stage == "Pregnant (7–9 months)":
        base = PREGNANT_BASE
    elif stage == "Dry period":
        # always use dry ration from NDDB
        if animal == "Cow":
            base = NDDB_COW["Dry (0 L milk)"]
        else:
            base = NDDB_BUFFALO["Dry (0 L milk)"]
    else:
        if animal == "Cow":
            base = NDDB_COW[milk_level]
        else:
            base = NDDB_BUFFALO[milk_level]
    return base.copy()

def adjust_ration(base, body_type, stage):
    ration = base.copy()
    body_factor = BODY_FACTORS.get(body_type, 1.0)

    # scale by body size
    for k in ["dry", "green", "conc", "oil", "bran"]:
        ration[k] = round(ration[k] * body_factor, 2)

    # stage-based adjustments (mild)
    if stage == "Early lactation":
        ration["conc"] = round(ration["conc"] * 1.15, 2)
        ration["green"] = round(ration["green"] * 1.05, 2)
    elif stage == "Late lactation":
        ration["conc"] = round(ration["conc"] * 0.9, 2)

    # mineral – keep NDDB base, small body-size scaling
    ration["mineral"] = round(base["mineral"] * body_factor, 0)

    return ration

base_ration = get_base_ration(animal, milk_level, stage)
ration = adjust_ration(base_ration, body_type, stage)

# -----------------------------
# MANUAL FEED SELECTION
# -----------------------------
# Dry fodder
dry_list = df[df["Category"] == "Dry fodder"]["Ingredient"].unique()
dry_choice = st.sidebar.selectbox("Select Dry Fodder", dry_list)
dry_fodder = df[df["Ingredient"] == dry_choice].iloc[0]

# Green fodder
green_list = df[df["Category"] == "Green fodder"]["Ingredient"].unique()
green_choice = st.sidebar.selectbox("Select Green Fodder", green_list)
green_fodder = df[df["Ingredient"] == green_choice].iloc[0]

# Concentrate
conc_list = df[df["Category"] == "Concentrate"]["Ingredient"].unique()
conc_choice = st.sidebar.selectbox("Select Concentrate", conc_list)
concentrate = df[df["Ingredient"] == conc_choice].iloc[0]

# Oil cake (only if required)
if ration["oil"] > 0:
    oil_list = df[df["Category"] == "Oil cake"]["Ingredient"].unique()
    oil_choice = st.sidebar.selectbox("Select Oil Cake", oil_list)
    oil_cake = df[df["Ingredient"] == oil_choice].iloc[0]
else:
    oil_cake = None

# Bran (only if required)
if ration["bran"] > 0:
    bran_list = df[df["Category"] == "Bran"]["Ingredient"].unique()
    bran_choice = st.sidebar.selectbox("Select Bran", bran_list)
    bran_feed = df[df["Ingredient"] == bran_choice].iloc[0]
else:
    bran_feed = None

# ----------------------------------------
# NUTRIENT CALCULATION (ALL NUTRIENTS)
# ----------------------------------------
NUTRIENT_COLS = ["CP", "EE", "CF", "NFE", "Ash", "NDF", "ADF", "ME"]

def nutrient_from_feed(feed_row, qty_kg):
    """
    Returns dict of nutrient amounts per day for a given feed:
    CP–ADF in kg/day, ME in MJ/day.
    """
    if feed_row is None or qty_kg <= 0:
        return {k: 0.0 for k in NUTRIENT_COLS}
    vals = {}
    # percentage-based nutrients (kg)
    for col in ["CP", "EE", "CF", "NFE", "Ash", "NDF", "ADF"]:
        vals[col] = qty_kg * feed_row[col] / 100.0
    # ME is MJ per kg
    vals["ME"] = qty_kg * feed_row["ME"]
    return vals

# initialize totals
nutrient_totals = {k: 0.0 for k in NUTRIENT_COLS}

for feed_row, qty in [
    (dry_fodder, ration["dry"]),
    (green_fodder, ration["green"]),
    (concentrate, ration["conc"]),
    (oil_cake, ration["oil"]),
    (bran_feed, ration["bran"]),
]:
    nf = nutrient_from_feed(feed_row, qty)
    for k in NUTRIENT_COLS:
        nutrient_totals[k] += nf[k]

# ----------------------------------------
# FEED RECOMMENDATION OUTPUT
# ----------------------------------------
st.markdown('<div class="section-header">Daily Feed Recommendation (Per Animal)</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

def show_feed(feed, qty, label, col):
    if feed is not None and qty > 0:
        col.markdown(f"""
        <div class="feed-item">
            <div>
                <div class="feed-label">{label}</div>
                <div class="feed-name">{feed['Ingredient']}</div>
            </div>
            <div class="feed-quantity">{qty:.2f} kg</div>
        </div>
        """, unsafe_allow_html=True)

show_feed(dry_fodder, ration["dry"], "Dry Fodder", col1)
show_feed(green_fodder, ration["green"], "Green Fodder", col1)
show_feed(concentrate, ration["conc"], "Concentrate", col2)
show_feed(oil_cake, ration["oil"], "Oil Cake", col2)
show_feed(bran_feed, ration["bran"], "Bran", col2)

# Mineral mixture
st.markdown(f"""
<div class="feed-item" style="background:#fffde7;border-color:#f9a825;">
    <div>
        <div class="feed-label">Mineral Supplement</div>
        <div class="feed-name">Mineral Mixture</div>
    </div>
    <div class="feed-quantity" style="background:#fff9c4;color:#f57f17;">{ration['mineral']:.0f} g</div>
</div>
""", unsafe_allow_html=True)

NUTRIENT_NAMES = {
    "CP": "Crude Protein (Protein)",
    "EE": "Ether Extract (Fat)",
    "CF": "Crude Fibre (Fibre)",
    "NFE": "Nitrogen Free Extract (Carbohydrates)",
    "Ash": "Ash (Minerals)",
    "NDF": "Neutral Detergent Fibre (Digestible Fibre)",
    "ADF": "Acid Detergent Fibre (Indigestible Fibre)",
    "ME": "Metabolizable Energy (Energy)"
}


# ----------------------------------------
# NUTRITIONAL ANALYSIS – ALL NUTRIENTS
# ----------------------------------------
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-header">Nutritional Analysis (Per Animal Per Day)</div>', unsafe_allow_html=True)

row1 = st.columns(4)
row2 = st.columns(4)

# row 1: CP, EE, CF, NFE  (kg/day)
for col, name in zip(row1, ["CP", "EE", "CF", "NFE"]):
    val = nutrient_totals[name]
    label = NUTRIENT_NAMES[name]
    col.markdown(f"""
    <div class="nutrient-card">
        <div class="nutrient-label">{label}</div>
        <div class="nutrient-value">{val:.2f}</div>
        <div class="nutrient-unit">kg/day</div>
    </div>
    """, unsafe_allow_html=True)

# row 2: Ash, NDF, ADF, ME
for col, name, unit in zip(
    row2,
    ["Ash", "NDF", "ADF", "ME"],
    ["kg/day", "kg/day", "kg/day", "MJ/day"]
):
    val = nutrient_totals[name]
    label = NUTRIENT_NAMES[name]
    col.markdown(f"""
    <div class="nutrient-card">
        <div class="nutrient-label">{label}</div>
        <div class="nutrient-value">{val:.2f}</div>
        <div class="nutrient-unit">{unit}</div>
    </div>
    """, unsafe_allow_html=True)

# ----------------------------------------
# HERD SUMMARY
# ----------------------------------------
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
st.markdown(f'<div class="section-header">Total Feed Requirements ({num} Animals)</div>', unsafe_allow_html=True)

def herd_line(feed, qty):
    if feed is not None and qty > 0:
        st.markdown(f"""
        <div class="herd-summary">
            <span class="herd-ingredient">{feed['Ingredient']}</span>
            <span class="herd-amount">{qty * num:.2f} kg/day</span>
        </div>
        """, unsafe_allow_html=True)

herd_line(dry_fodder, ration["dry"])
herd_line(green_fodder, ration["green"])
herd_line(concentrate, ration["conc"])
herd_line(oil_cake, ration["oil"])
herd_line(bran_feed, ration["bran"])

# Mineral mixture for herd
st.markdown(f"""
<div class="herd-summary" style="background:#fff9c4;border-left-color:#f9a825;">
    <span class="herd-ingredient">Mineral Mixture</span>
    <span class="herd-amount">{(ration['mineral'] * num)/1000:.2f} kg/day</span>
</div>
""", unsafe_allow_html=True)

# ----------------------------------------
# FOOTER
# ----------------------------------------
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center;color:#888;padding:1rem;font-size:0.85rem;">
    <strong>National Dairy Development Board (NDDB)</strong> Standards Applied<br>
    Base rations from NDDB TMR tables; body size & stage adjustments follow NDDB feeding principles.
</div>
""", unsafe_allow_html=True)

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import datetime
import io

st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)
st.markdown("## 📄 Download Feed Report")

# Button to generate report
if st.button("Export PDF Report"):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    def draw_header_box(c, y_pos):
        """Draw green header box"""
        c.setFillColorRGB(0.176, 0.314, 0.086)  # Dark green
        c.rect(40, y_pos - 35, width - 80, 50, fill=True, stroke=False)
        c.setFillColorRGB(1, 1, 1)  # White text
        c.setFont("Helvetica-Bold", 18)
        c.drawString(55, y_pos - 15, "Feed Recommendation Report")
        c.setFont("Helvetica", 10)
        c.drawString(55, y_pos - 30, "NDDB-Based Scientific Ration Balancing for Dairy Animals")
        return y_pos - 50
    
    def draw_section_box(c, y_pos, title, content_lines, bg_color=(0.941, 0.973, 0.902)):
        """Draw a styled section box with content"""
        box_height = 30 + (len(content_lines) * 18)
        
        # Check if we need a new page
        if y_pos - box_height < 50:
            c.showPage()
            y_pos = height - 80
        
        # Draw background box
        c.setFillColorRGB(*bg_color)
        c.rect(40, y_pos - box_height, width - 80, box_height, fill=True, stroke=True)
        
        # Draw title bar
        c.setFillColorRGB(0.176, 0.314, 0.086)
        c.rect(40, y_pos - 25, width - 80, 25, fill=True, stroke=False)
        c.setFillColorRGB(1, 1, 1)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y_pos - 18, title)
        
        # Draw content
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica", 10)
        y_content = y_pos - 42
        for line in content_lines:
            c.drawString(55, y_content, line)
            y_content -= 18
        
        return y_pos - box_height - 20
    
    def draw_feed_table(c, y_pos, feeds_data):
        """Draw feed recommendation table"""
        if y_pos < 200:
            c.showPage()
            y_pos = height - 80
        
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y_pos, "Daily Feed Recommendation (Per Animal)")
        y_pos -= 25
        
        # Table header
        c.setFillColorRGB(0.176, 0.314, 0.086)
        c.rect(50, y_pos - 20, width - 100, 25, fill=True, stroke=True)
        c.setFillColorRGB(1, 1, 1)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(60, y_pos - 13, "Feed Type")
        c.drawString(250, y_pos - 13, "Ingredient")
        c.drawString(450, y_pos - 13, "Quantity")
        
        y_pos -= 25
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica", 10)
        
        # Table rows
        for i, (feed_type, ingredient, quantity, unit) in enumerate(feeds_data):
            if quantity > 0:
                # Alternate row colors
                if i % 2 == 0:
                    c.setFillColorRGB(0.97, 0.97, 0.97)
                else:
                    c.setFillColorRGB(1, 1, 1)
                c.rect(50, y_pos - 18, width - 100, 20, fill=True, stroke=True)
                
                c.setFillColorRGB(0, 0, 0)
                c.drawString(60, y_pos - 12, feed_type)
                c.drawString(250, y_pos - 12, ingredient)
                c.drawString(450, y_pos - 12, f"{quantity:.2f} {unit}")
                y_pos -= 20
        
        return y_pos - 20
    
    def draw_nutrient_grid(c, y_pos, nutrients_data):
        """Draw nutrient analysis in a grid"""
        if y_pos < 300:
            c.showPage()
            y_pos = height - 80
        
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y_pos, "Nutritional Analysis (Per Animal Per Day)")
        y_pos -= 30
        
        # Draw 2 columns x 4 rows grid
        col_width = (width - 100) / 2
        row_height = 60
        x_start = 50
        
        row = 0
        col = 0
        
        for nutrient, full_name, value, unit in nutrients_data:
            x = x_start + (col * col_width)
            y = y_pos - (row * row_height)
            
            # Draw box
            c.setFillColorRGB(0.97, 0.97, 0.97)
            c.rect(x, y - row_height + 10, col_width - 10, row_height - 10, fill=True, stroke=True)
            
            # Draw content
            c.setFillColorRGB(0.4, 0.4, 0.4)
            c.setFont("Helvetica", 8)
            c.drawString(x + 10, y - 20, full_name)
            
            # Value and unit on same line
            c.setFillColorRGB(0.176, 0.314, 0.086)
            c.setFont("Helvetica-Bold", 18)
            value_text = f"{value:.2f}"
            c.drawString(x + 10, y - 43, value_text)
            
            # Calculate width of value text to position unit right after it
            value_width = c.stringWidth(value_text, "Helvetica-Bold", 18)
            
            c.setFillColorRGB(0.5, 0.5, 0.5)
            c.setFont("Helvetica", 10)
            c.drawString(x + 10 + value_width + 3, y - 43, f" {unit}")
            
            col += 1
            if col >= 2:
                col = 0
                row += 1
        
        return y_pos - (row * row_height) - 30

    # Start building PDF
    y = height - 60
    
    # Header
    y = draw_header_box(c, y)
    y -= 30
    
    # Generated date
    c.setFont("Helvetica", 9)
    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.drawString(50, y, f"Generated: {datetime.datetime.now().strftime('%B %d, %Y at %H:%M')}")
    y -= 30
    
    # Animal Configuration
    animal_info = [
        f"Animal Type: {animal}",
        f"Milk Production Level: {milk_level}",
        f"Body Size: {body_type}",
        f"Lactation Stage: {stage}",
        f"Number of Animals: {num}"
    ]
    y = draw_section_box(c, y, "■ Animal Configuration", animal_info)
    
    # Feed Recommendation Table
    feeds_data = [
        ("DRY FODDER", dry_fodder['Ingredient'] if dry_fodder is not None else "", ration["dry"], "kg"),
        ("GREEN FODDER", green_fodder['Ingredient'] if green_fodder is not None else "", ration["green"], "kg"),
        ("CONCENTRATE", concentrate['Ingredient'] if concentrate is not None else "", ration["conc"], "kg"),
        ("OIL CAKE", oil_cake['Ingredient'] if oil_cake is not None else "", ration["oil"], "kg"),
        ("BRAN", bran_feed['Ingredient'] if bran_feed is not None else "", ration["bran"], "kg"),
        ("MINERAL SUPPLEMENT", "Mineral Mixture", ration["mineral"], "g"),
    ]
    y = draw_feed_table(c, y, feeds_data)
    
    # Nutritional Analysis Grid
    nutrients_data = [
        ("CP", "Crude Protein (Protein)", nutrient_totals["CP"], "kg/day"),
        ("EE", "Ether Extract (Fat)", nutrient_totals["EE"], "kg/day"),
        ("CF", "Crude Fibre (Fibre)", nutrient_totals["CF"], "kg/day"),
        ("NFE", "NFE (Carbohydrates)", nutrient_totals["NFE"], "kg/day"),
        ("Ash", "Ash (Minerals)", nutrient_totals["Ash"], "kg/day"),
        ("NDF", "NDF (Digestible Fibre)", nutrient_totals["NDF"], "kg/day"),
        ("ADF", "ADF (Indigestible Fibre)", nutrient_totals["ADF"], "kg/day"),
        ("ME", "Metabolizable Energy", nutrient_totals["ME"], "MJ/day"),
    ]
    y = draw_nutrient_grid(c, y, nutrients_data)
    
    # Check if we need a new page for herd summary
    if y < 200:
        c.showPage()
        y = height - 80
    
    # Total Herd Requirements
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, f"Total Herd Requirements ({num} Animals)")
    y -= 25
    
    herd_feeds = [
        ("Dry Fodder", dry_fodder, ration["dry"]),
        ("Green Fodder", green_fodder, ration["green"]),
        ("Concentrate", concentrate, ration["conc"]),
        ("Oil Cake", oil_cake, ration["oil"]),
        ("Bran", bran_feed, ration["bran"]),
    ]
    
    c.setFont("Helvetica", 10)
    for label, feed, qty in herd_feeds:
        if feed is not None and qty > 0:
            c.setFillColorRGB(0.941, 0.973, 0.902)
            c.rect(50, y - 18, width - 100, 20, fill=True, stroke=True)
            c.setFillColorRGB(0, 0, 0)
            c.drawString(60, y - 12, f"{label}: {feed['Ingredient']}")
            c.setFillColorRGB(0.176, 0.314, 0.086)
            c.setFont("Helvetica-Bold", 10)
            c.drawString(450, y - 12, f"{qty * num:.2f} kg/day")
            c.setFont("Helvetica", 10)
            c.setFillColorRGB(0, 0, 0)
            y -= 22
    
    # Mineral mixture
    c.setFillColorRGB(1, 0.98, 0.8)
    c.rect(50, y - 18, width - 100, 20, fill=True, stroke=True)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(60, y - 12, "Mineral Mixture")
    c.setFillColorRGB(0.96, 0.66, 0.09)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(450, y - 12, f"{(ration['mineral'] * num)/1000:.2f} kg/day")
    
    # Footer
    c.setFillColorRGB(0.7, 0.7, 0.7)
    c.setFont("Helvetica", 8)
    footer_text = "National Dairy Development Board (NDDB) Standards Applied"
    c.drawCentredString(width/2, 40, footer_text)
    c.drawCentredString(width/2, 28, "Base rations from NDDB TMR tables; adjustments follow NDDB feeding principles")
    
    c.save()
    buffer.seek(0)

    st.download_button(
        label="📥 Download PDF Report",
        data=buffer,
        file_name="Feed_Recommendation_Report.pdf",
        mime="application/pdf"
    )