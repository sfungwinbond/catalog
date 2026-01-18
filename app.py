import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os

# Page configuration
st.set_page_config(
    page_title="Winbond Sample Request Portal",
    page_icon="💾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Winbond branding
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .main-header h1 {
        color: white;
        margin: 0;
    }
    .main-header p {
        color: #a0c4e8;
        margin: 5px 0 0 0;
    }
    .part-card {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        transition: all 0.3s ease;
    }
    .part-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        border-color: #1e3a5f;
    }
    .category-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 8px;
    }
    .slc-nand { background: #e3f2fd; color: #1565c0; }
    .serial-nand { background: #e8f5e9; color: #2e7d32; }
    .nor-flash { background: #fff3e0; color: #ef6c00; }
    .dram { background: #f3e5f5; color: #7b1fa2; }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
    .stButton > button {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
        color: white;
        border: none;
        padding: 10px 25px;
        border-radius: 5px;
        font-weight: 600;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #2d5a87 0%, #3d6a97 100%);
    }
</style>
""", unsafe_allow_html=True)

# Winbond Part Catalog Data
WINBOND_CATALOG = {
    "SLC NAND Flash": [
        {"part_number": "W29N01GVSIAA", "density": "1Gb", "interface": "Parallel", "package": "TSOP-48", "voltage": "3.3V", "temp_range": "-40°C to 85°C", "description": "1Gb SLC NAND, x8 bus width, 100K P/E cycles"},
        {"part_number": "W29N02GVSIAA", "density": "2Gb", "interface": "Parallel", "package": "TSOP-48", "voltage": "3.3V", "temp_range": "-40°C to 85°C", "description": "2Gb SLC NAND, x8 bus width, 100K P/E cycles"},
        {"part_number": "W29N04GVSIAA", "density": "4Gb", "interface": "Parallel", "package": "TSOP-48", "voltage": "3.3V", "temp_range": "-40°C to 85°C", "description": "4Gb SLC NAND, x8 bus width, 100K P/E cycles"},
        {"part_number": "W29N08GVSIAA", "density": "8Gb", "interface": "Parallel", "package": "TSOP-48", "voltage": "3.3V", "temp_range": "-40°C to 85°C", "description": "8Gb SLC NAND, x8 bus width, 100K P/E cycles"},
        {"part_number": "W29N01GVSI4A", "density": "1Gb", "interface": "Parallel", "package": "TSOP-48", "voltage": "3.3V", "temp_range": "-40°C to 105°C", "description": "1Gb Industrial SLC NAND, extended temp"},
        {"part_number": "W29N02GVSI4A", "density": "2Gb", "interface": "Parallel", "package": "TSOP-48", "voltage": "3.3V", "temp_range": "-40°C to 105°C", "description": "2Gb Industrial SLC NAND, extended temp"},
    ],
    "Serial NAND Flash": [
        {"part_number": "W25N512GV", "density": "512Mb", "interface": "SPI", "package": "SOIC-8", "voltage": "3.3V", "temp_range": "-40°C to 85°C", "description": "512Mb Serial NAND, SPI interface, 100K P/E cycles"},
        {"part_number": "W25N01GV", "density": "1Gb", "interface": "SPI", "package": "SOIC-8", "voltage": "3.3V", "temp_range": "-40°C to 85°C", "description": "1Gb Serial NAND, SPI interface, 100K P/E cycles"},
        {"part_number": "W25N02GV", "density": "2Gb", "interface": "SPI", "package": "SOIC-8", "voltage": "3.3V", "temp_range": "-40°C to 85°C", "description": "2Gb Serial NAND, SPI interface, 100K P/E cycles"},
        {"part_number": "W25N04KV", "density": "4Gb", "interface": "SPI", "package": "SOIC-8", "voltage": "3.3V", "temp_range": "-40°C to 85°C", "description": "4Gb Serial NAND, SPI interface, 100K P/E cycles"},
        {"part_number": "W25N01GVZEIG", "density": "1Gb", "interface": "SPI", "package": "WSON-8", "voltage": "3.3V", "temp_range": "-40°C to 85°C", "description": "1Gb Serial NAND, compact WSON package"},
        {"part_number": "W25N02KVZEIR", "density": "2Gb", "interface": "SPI", "package": "WSON-8", "voltage": "3.3V", "temp_range": "-40°C to 105°C", "description": "2Gb Industrial Serial NAND, extended temp"},
    ],
    "NOR Flash": [
        {"part_number": "W25Q512JV", "density": "512Mb", "interface": "SPI/QPI", "package": "SOIC-16", "voltage": "3.3V", "temp_range": "-40°C to 85°C", "description": "512Mb Quad SPI NOR, DTR support, 100K P/E cycles"},
        {"part_number": "W25Q256JV", "density": "256Mb", "interface": "SPI/QPI", "package": "SOIC-16", "voltage": "3.3V", "temp_range": "-40°C to 85°C", "description": "256Mb Quad SPI NOR, DTR support"},
        {"part_number": "W25Q128JV", "density": "128Mb", "interface": "SPI/QPI", "package": "SOIC-8", "voltage": "3.3V", "temp_range": "-40°C to 85°C", "description": "128Mb Quad SPI NOR, popular general purpose"},
        {"part_number": "W25Q64JV", "density": "64Mb", "interface": "SPI/QPI", "package": "SOIC-8", "voltage": "3.3V", "temp_range": "-40°C to 85°C", "description": "64Mb Quad SPI NOR"},
        {"part_number": "W25Q32JV", "density": "32Mb", "interface": "SPI/QPI", "package": "SOIC-8", "voltage": "3.3V", "temp_range": "-40°C to 85°C", "description": "32Mb Quad SPI NOR"},
        {"part_number": "W25Q128JVSIQ", "density": "128Mb", "interface": "SPI/QPI", "package": "SOIC-8", "voltage": "3.3V", "temp_range": "-40°C to 105°C", "description": "128Mb Industrial NOR, extended temp"},
    ],
    "DRAM": [
        {"part_number": "W9425G6KH-5", "density": "256Mb", "interface": "DDR", "package": "FBGA-60", "voltage": "2.5V", "temp_range": "-40°C to 85°C", "description": "256Mb DDR SDRAM, 200MHz"},
        {"part_number": "W9751G6KB-25", "density": "512Mb", "interface": "DDR2", "package": "FBGA-84", "voltage": "1.8V", "temp_range": "-40°C to 85°C", "description": "512Mb DDR2 SDRAM, 400MHz"},
        {"part_number": "W631GG6KB-12", "density": "1Gb", "interface": "DDR3", "package": "FBGA-96", "voltage": "1.5V", "temp_range": "-40°C to 85°C", "description": "1Gb DDR3 SDRAM, 800MHz"},
        {"part_number": "W632GG6NB-12", "density": "2Gb", "interface": "DDR3", "package": "FBGA-96", "voltage": "1.35V", "temp_range": "-40°C to 85°C", "description": "2Gb DDR3L SDRAM, low power"},
    ]
}

# Application Types for targeting
APPLICATION_TYPES = [
    "Payment Terminal / POS",
    "Industrial Automation / Building Controls",
    "Networking Equipment (Router/Switch)",
    "Satellite Communication / SBD",
    "Automotive",
    "Consumer Electronics",
    "IoT / Smart Home",
    "Medical Devices",
    "Military / Aerospace",
    "Other"
]

# Initialize session state
if 'selected_parts' not in st.session_state:
    st.session_state.selected_parts = []
if 'submitted_requests' not in st.session_state:
    st.session_state.submitted_requests = []

# Header
st.markdown("""
<div class="main-header">
    <h1>Winbond Sample Request Portal</h1>
    <p>Internal Tool for Sales & FAE Teams - Select Parts and Submit Sample Requests</p>
</div>
""", unsafe_allow_html=True)

# Sidebar - Part Selector
st.sidebar.header("Part Selector")
st.sidebar.markdown("---")

# Category filter
selected_category = st.sidebar.selectbox(
    "Product Category",
    ["All Categories"] + list(WINBOND_CATALOG.keys())
)

# Density filter
all_densities = set()
for category, parts in WINBOND_CATALOG.items():
    for part in parts:
        all_densities.add(part["density"])
all_densities = sorted(list(all_densities), key=lambda x: float(x.replace("Gb", "000").replace("Mb", "")))

selected_density = st.sidebar.selectbox(
    "Density",
    ["All Densities"] + all_densities
)

# Interface filter
all_interfaces = set()
for category, parts in WINBOND_CATALOG.items():
    for part in parts:
        all_interfaces.add(part["interface"])

selected_interface = st.sidebar.selectbox(
    "Interface",
    ["All Interfaces"] + sorted(list(all_interfaces))
)

# Temperature filter
temp_filter = st.sidebar.selectbox(
    "Temperature Range",
    ["All Ranges", "Commercial (-40°C to 85°C)", "Industrial (-40°C to 105°C)"]
)

# Part search
search_term = st.sidebar.text_input("Search Part Number", placeholder="e.g., W25N01")

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Selected Parts:** {len(st.session_state.selected_parts)}")

# Main content - Two columns
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Available Parts")

    # Filter and display parts
    for category, parts in WINBOND_CATALOG.items():
        # Apply category filter
        if selected_category != "All Categories" and category != selected_category:
            continue

        # Get badge class
        badge_class = category.lower().replace(" ", "-").replace("/", "-")
        if "slc" in badge_class:
            badge_class = "slc-nand"
        elif "serial" in badge_class:
            badge_class = "serial-nand"
        elif "nor" in badge_class:
            badge_class = "nor-flash"
        elif "dram" in badge_class:
            badge_class = "dram"

        filtered_parts = []
        for part in parts:
            # Apply filters
            if selected_density != "All Densities" and part["density"] != selected_density:
                continue
            if selected_interface != "All Interfaces" and part["interface"] != selected_interface:
                continue
            if temp_filter == "Commercial (-40°C to 85°C)" and "105°C" in part["temp_range"]:
                continue
            if temp_filter == "Industrial (-40°C to 105°C)" and "105°C" not in part["temp_range"]:
                continue
            if search_term and search_term.upper() not in part["part_number"].upper():
                continue
            filtered_parts.append(part)

        if filtered_parts:
            st.subheader(category)

            for part in filtered_parts:
                with st.container():
                    pcol1, pcol2, pcol3 = st.columns([3, 2, 1])

                    with pcol1:
                        st.markdown(f"**{part['part_number']}**")
                        st.caption(part["description"])

                    with pcol2:
                        st.markdown(f"""
                        | Spec | Value |
                        |------|-------|
                        | Density | {part['density']} |
                        | Interface | {part['interface']} |
                        | Package | {part['package']} |
                        | Temp | {part['temp_range']} |
                        """)

                    with pcol3:
                        is_selected = part["part_number"] in [p["part_number"] for p in st.session_state.selected_parts]
                        if st.button(
                            "Remove" if is_selected else "Add",
                            key=f"btn_{part['part_number']}",
                            type="secondary" if is_selected else "primary"
                        ):
                            if is_selected:
                                st.session_state.selected_parts = [
                                    p for p in st.session_state.selected_parts
                                    if p["part_number"] != part["part_number"]
                                ]
                            else:
                                st.session_state.selected_parts.append({
                                    **part,
                                    "category": category
                                })
                            st.rerun()

                    st.divider()

with col2:
    st.header("Sample Request Form")

    # Display selected parts
    if st.session_state.selected_parts:
        st.subheader("Selected Parts")
        for idx, part in enumerate(st.session_state.selected_parts):
            st.markdown(f"**{idx + 1}. {part['part_number']}** ({part['density']} {part['category']})")
        st.divider()
    else:
        st.info("Select parts from the catalog to add to your sample request.")

    # Request form
    with st.form("sample_request_form"):
        st.subheader("Request Details")

        # Requester info
        requester_name = st.text_input("Your Name *", placeholder="John Smith")
        requester_email = st.text_input("Email *", placeholder="john.smith@company.com")
        requester_phone = st.text_input("Phone", placeholder="+1-555-123-4567")

        st.divider()

        # Customer info
        st.subheader("Customer Information")
        customer_name = st.text_input("Customer/Company Name *", placeholder="Acme Corporation")
        customer_contact = st.text_input("Customer Contact", placeholder="Jane Doe")
        customer_location = st.selectbox(
            "Region",
            ["North America", "Europe", "Asia Pacific", "Greater China", "Japan", "Korea", "Other"]
        )

        st.divider()

        # Application info
        st.subheader("Application Details")
        application_type = st.selectbox("Target Application *", APPLICATION_TYPES)

        current_solution = st.text_area(
            "Current Solution (if displacing competitor)",
            placeholder="e.g., Currently using MXIC MX29LV640 parallel NOR flash",
            height=80
        )

        annual_volume = st.selectbox(
            "Estimated Annual Volume",
            ["< 10K units", "10K - 50K units", "50K - 100K units", "100K - 500K units", "500K - 1M units", "> 1M units"]
        )

        sample_qty = st.number_input("Sample Quantity Requested", min_value=1, max_value=100, value=10)

        urgency = st.selectbox(
            "Urgency Level",
            ["Standard (2-3 weeks)", "Expedited (1 week)", "Critical (ASAP)"]
        )

        notes = st.text_area(
            "Additional Notes",
            placeholder="Any special requirements, technical questions, or context...",
            height=100
        )

        st.divider()

        # Submit button
        submitted = st.form_submit_button("Submit Sample Request", type="primary", use_container_width=True)

        if submitted:
            # Validation
            if not requester_name or not requester_email or not customer_name:
                st.error("Please fill in all required fields (marked with *)")
            elif not st.session_state.selected_parts:
                st.error("Please select at least one part for the sample request.")
            else:
                # Create request record
                request = {
                    "request_id": f"SR-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "timestamp": datetime.now().isoformat(),
                    "requester": {
                        "name": requester_name,
                        "email": requester_email,
                        "phone": requester_phone
                    },
                    "customer": {
                        "name": customer_name,
                        "contact": customer_contact,
                        "location": customer_location
                    },
                    "application": {
                        "type": application_type,
                        "current_solution": current_solution,
                        "annual_volume": annual_volume
                    },
                    "parts": st.session_state.selected_parts,
                    "sample_qty": sample_qty,
                    "urgency": urgency,
                    "notes": notes
                }

                # Save to session state
                st.session_state.submitted_requests.append(request)

                # Save to JSON file
                requests_file = "sample_requests.json"
                existing_requests = []
                if os.path.exists(requests_file):
                    with open(requests_file, "r") as f:
                        existing_requests = json.load(f)
                existing_requests.append(request)
                with open(requests_file, "w") as f:
                    json.dump(existing_requests, f, indent=2)

                st.success(f"Sample request submitted successfully! Request ID: **{request['request_id']}**")

                # Clear selected parts
                st.session_state.selected_parts = []
                st.rerun()

# Footer with recent requests
st.markdown("---")
if st.session_state.submitted_requests:
    with st.expander("Recent Submissions (This Session)"):
        for req in reversed(st.session_state.submitted_requests[-5:]):
            st.markdown(f"""
            **{req['request_id']}** - {req['customer']['name']}
            Parts: {', '.join([p['part_number'] for p in req['parts']])}
            Application: {req['application']['type']} | Volume: {req['application']['annual_volume']}
            """)
            st.divider()
