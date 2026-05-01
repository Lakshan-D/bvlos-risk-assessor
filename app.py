import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import json
from datetime import datetime
from utils.risk_engine import assess_flight_risk, generate_risk_summary
from utils.airspace import check_airspace_conflicts, get_notam_zones
from utils.report import generate_pdf_report

st.set_page_config(
    page_title="BVLOS Flight Risk Assessor",
    page_icon="🚁",
    layout="wide"
)

st.markdown("""
<style>
    .main-title { font-size: 2.2rem; font-weight: 700; color: #1a3a5c; }
    .sub-title  { font-size: 1rem; color: #595959; margin-bottom: 1.5rem; }
    .risk-high   { background: #e74c3c; color: white; padding: 6px 14px; border-radius: 8px; font-weight: 700; }
    .risk-medium { background: #e67e22; color: white; padding: 6px 14px; border-radius: 8px; font-weight: 700; }
    .risk-low    { background: #27ae60; color: white; padding: 6px 14px; border-radius: 8px; font-weight: 700; }
    .metric-box  { background: #f0f4ff; border-radius: 10px; padding: 1rem; border-left: 4px solid #1a3a5c; }
    .footer      { font-size: 0.75rem; color: #999; text-align: center; margin-top: 2rem; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<p class="main-title">🚁 BVLOS Flight Risk Assessment Tool</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-title">Independent evaluation framework for Beyond Visual Line of Sight drone operations — '
    'aligned with the EU EARHEART project and UK CAA / EASA regulatory frameworks.</p>',
    unsafe_allow_html=True
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Flight Parameters")

    operation_name = st.text_input("Operation Name", "BVLOS Trial Run 001")
    operator       = st.text_input("Operator", "BCU Research Team")
    drone_type     = st.selectbox("Drone Type", [
        "Fixed Wing (>25kg)", "Fixed Wing (<25kg)",
        "Multirotor (>25kg)", "Multirotor (<25kg)",
        "Hybrid VTOL"
    ])

    st.divider()
    st.subheader("Flight Envelope")

    altitude     = st.slider("Max Altitude (m AGL)", 30, 500, 120)
    speed        = st.slider("Max Speed (m/s)", 5, 50, 20)
    range_km     = st.slider("Range (km)", 1, 100, 15)
    flight_time  = st.slider("Flight Duration (mins)", 5, 180, 45)

    st.divider()
    st.subheader("Environment")

    population   = st.selectbox("Area Type", ["Rural", "Suburban", "Urban", "Controlled Airspace"])
    weather      = st.selectbox("Weather Conditions", ["VMC (Clear)", "IMC (Cloud/Rain)", "High Wind (>10m/s)", "Night"])
    contingency  = st.selectbox("Contingency Plan", ["Full RTH", "Partial RTH", "Parachute", "None"])

    st.divider()
    st.subheader("Regulatory Context")

    framework    = st.multiselect("Applicable Frameworks", [
        "UK CAA CAP 722", "EASA UAS Regulation 2019/947",
        "EASA SAIL Assessment", "UK Airspace Act 1982",
        "Network Rail ORR Requirements"
    ], default=["UK CAA CAP 722", "EASA UAS Regulation 2019/947"])

    category     = st.selectbox("UAS Category", ["Open", "Specific", "Certified"])

# ── Main tabs ─────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "Flight Planning & Map",
    "Risk Assessment",
    "Regulatory Analysis",
    "Export Report"
])

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — MAP
# ════════════════════════════════════════════════════════════════════════════
with tab1:
    st.subheader("Define Flight Path")
    st.info("Click on the map to add waypoints. The tool will assess risks along the full route.")

    col1, col2 = st.columns([2, 1])

    with col1:
        # Base map centred on UK
        m = folium.Map(location=[52.5, -1.5], zoom_start=7, tiles="CartoDB positron")

        # Add example no-fly zones (UK airports)
        nfz_data = [
            {"name": "Heathrow CTR", "lat": 51.477, "lon": -0.461, "radius": 10000, "type": "ATZ"},
            {"name": "Birmingham Airport", "lat": 52.453, "lon": -1.748, "radius": 8000, "type": "ATZ"},
            {"name": "Manchester Airport", "lat": 53.354, "lon": -2.275, "radius": 8000, "type": "ATZ"},
            {"name": "Gatwick CTR", "lat": 51.148, "lon": -0.190, "radius": 9000, "type": "ATZ"},
            {"name": "Bristol Airport", "lat": 51.382, "lon": -2.719, "radius": 7000, "type": "ATZ"},
        ]

        for nfz in nfz_data:
            folium.Circle(
                location=[nfz["lat"], nfz["lon"]],
                radius=nfz["radius"],
                color="red",
                fill=True,
                fill_opacity=0.15,
                popup=f"{nfz['name']} — {nfz['type']} No-Fly Zone",
                tooltip=nfz["name"]
            ).add_to(m)

        # Example BVLOS route
        if "waypoints" not in st.session_state:
            st.session_state.waypoints = [
                {"lat": 52.400, "lon": -1.500, "name": "WP1 — Takeoff"},
                {"lat": 52.450, "lon": -1.450, "name": "WP2"},
                {"lat": 52.500, "lon": -1.380, "name": "WP3"},
                {"lat": 52.520, "lon": -1.300, "name": "WP4 — Landing"},
            ]

        coords = [(wp["lat"], wp["lon"]) for wp in st.session_state.waypoints]

        folium.PolyLine(
            coords, color="#1a3a5c", weight=3, opacity=0.8,
            tooltip="Planned BVLOS Route"
        ).add_to(m)

        for i, wp in enumerate(st.session_state.waypoints):
            folium.Marker(
                [wp["lat"], wp["lon"]],
                popup=wp["name"],
                tooltip=wp["name"],
                icon=folium.Icon(
                    color="green" if i == 0 else ("red" if i == len(st.session_state.waypoints)-1 else "blue"),
                    icon="plane"
                )
            ).add_to(m)

        folium.LayerControl().add_to(m)
        st_folium(m, width=700, height=500)

    with col2:
        st.markdown("**Waypoints**")
        for i, wp in enumerate(st.session_state.waypoints):
            st.write(f"**{i+1}.** {wp['name']}")
            st.caption(f"Lat: {wp['lat']:.3f} | Lon: {wp['lon']:.3f}")

        st.divider()
        st.markdown("**Legend**")
        st.markdown("🔴 No-Fly Zones (ATZ/CTR)")
        st.markdown("🔵 Route Waypoints")
        st.markdown("🟢 Takeoff | 🔴 Landing")

        st.divider()
        st.markdown("**Route Summary**")
        st.metric("Waypoints", len(st.session_state.waypoints))
        st.metric("Est. Range", f"{range_km} km")
        st.metric("Max Altitude", f"{altitude} m AGL")

# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — RISK ASSESSMENT
# ════════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("BVLOS Risk Assessment Matrix")

    params = {
        "altitude": altitude,
        "speed": speed,
        "range_km": range_km,
        "flight_time": flight_time,
        "population": population,
        "weather": weather,
        "contingency": contingency,
        "drone_type": drone_type,
        "category": category,
    }

    risks = assess_flight_risk(params)
    summary = generate_risk_summary(risks)

    # Overall risk badge
    col1, col2, col3 = st.columns(3)
    risk_class = summary["overall_risk"]
    css_class  = f"risk-{risk_class.lower()}"

    col1.markdown(f'**Overall Risk:** <span class="{css_class}">{risk_class}</span>', unsafe_allow_html=True)
    col2.metric("Risk Score", f"{summary['score']}/100")
    col3.metric("SAIL Level (Est.)", summary["sail_level"])

    st.divider()

    # Risk breakdown table
    st.markdown("**Risk Factor Breakdown**")
    df = pd.DataFrame(risks)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.divider()

    # Airspace conflict check
    st.markdown("**Airspace Conflict Analysis**")
    conflicts = check_airspace_conflicts(st.session_state.waypoints, nfz_data)

    if conflicts:
        st.error(f"⚠️ {len(conflicts)} potential airspace conflict(s) detected along route:")
        for c in conflicts:
            st.write(f"- Route passes within {c['distance_km']:.1f} km of **{c['zone']}**")
    else:
        st.success("No airspace conflicts detected along planned route.")

    st.divider()

    # Mitigations
    st.markdown("**Recommended Mitigations**")
    for m_item in summary["mitigations"]:
        st.write(f"• {m_item}")

# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — REGULATORY ANALYSIS
# ════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("Regulatory Framework Analysis")

    st.markdown("**Selected Frameworks**")
    if not framework:
        st.warning("No frameworks selected. Use the sidebar to select applicable regulations.")
    else:
        reg_data = {
            "UK CAA CAP 722": {
                "full_name": "CAP 722 — UAS Flight in UK Airspace",
                "body": "UK Civil Aviation Authority",
                "key_requirements": [
                    "Operator must hold valid CAA UAS operator ID",
                    "BVLOS requires specific CAA permission (Article 16 exemption or OSC)",
                    "Risk assessment must follow CAA Operational Safety Case (OSC) methodology",
                    "Emergency response plan (ERP) must be in place",
                    "Real-time airspace monitoring required for BVLOS ops",
                ],
                "bvlos_status": "Permitted with CAA Permission only",
                "trial_pathway": "Apply via CAA SORA/OSC process — typical approval 3-6 months"
            },
            "EASA UAS Regulation 2019/947": {
                "full_name": "Commission Delegated Regulation (EU) 2019/947",
                "body": "European Union Aviation Safety Agency (EASA)",
                "key_requirements": [
                    "UAS must be registered in relevant EASA member state",
                    "BVLOS operations fall under Specific category — require SORA assessment",
                    "Specific Operations Risk Assessment (SORA) determines SAIL level",
                    "Remote ID required for all Specific category operations",
                    "ConOps (Concept of Operations) document required",
                ],
                "bvlos_status": "Specific Category — SORA required",
                "trial_pathway": "SORA submission to National Aviation Authority (NAA)"
            },
            "EASA SAIL Assessment": {
                "full_name": "Specific Assurance and Integrity Level (SAIL)",
                "body": "EASA",
                "key_requirements": [
                    "SAIL I-VI determined by Ground Risk Class (GRC) and Air Risk Class (ARC)",
                    "Higher SAIL = more stringent operational safety objectives (OSO)",
                    "BVLOS over populated areas typically SAIL IV-VI",
                    "OSO compliance must be demonstrated before flight approval",
                ],
                "bvlos_status": f"Estimated SAIL Level: {summary['sail_level']}",
                "trial_pathway": "Demonstrate OSO compliance via technical and operational evidence"
            },
            "UK Airspace Act 1982": {
                "full_name": "Civil Aviation Act 1982 (as amended)",
                "body": "UK Parliament / CAA",
                "key_requirements": [
                    "All aircraft including UAS subject to Rules of the Air Regulations",
                    "Operator liable for damage caused by UAS",
                    "Low-flying restrictions apply (min 500ft over congested areas)",
                    "UAS must not endanger any person or property",
                ],
                "bvlos_status": "Applies to all UK UAS operations",
                "trial_pathway": "Compliance demonstrated through OSC and insurance documentation"
            },
            "Network Rail ORR Requirements": {
                "full_name": "Network Rail UAS Operations Requirements",
                "body": "Office of Rail and Road (ORR) / Network Rail",
                "key_requirements": [
                    "Specific approval required for UAS ops within 50m of railway",
                    "Risk assessment must consider EMI interference with signalling",
                    "Possession or line blockage may be required for close proximity ops",
                    "Network Rail Engineering Access Statement required",
                ],
                "bvlos_status": "Railway proximity operations require specific NR approval",
                "trial_pathway": "Submit via Network Rail UAS approval process"
            }
        }

        for fw in framework:
            if fw in reg_data:
                data = reg_data[fw]
                with st.expander(f"📋 {fw}", expanded=True):
                    col1, col2 = st.columns(2)
                    col1.markdown(f"**Full Name:** {data['full_name']}")
                    col1.markdown(f"**Regulatory Body:** {data['body']}")
                    col2.markdown(f"**BVLOS Status:** {data['bvlos_status']}")
                    col2.markdown(f"**Trial Pathway:** {data['trial_pathway']}")
                    st.markdown("**Key Requirements:**")
                    for req in data["key_requirements"]:
                        st.write(f"• {req}")

    st.divider()
    st.markdown("**Regulatory Compliance Checklist**")

    checklist = [
        ("UAS Operator ID registered", True),
        ("CAA / NAA permission obtained", False),
        ("SORA / OSC completed", False),
        ("Remote ID fitted and tested", True),
        ("Emergency Response Plan documented", False),
        ("Insurance in place (min £2.5M liability)", True),
        ("ConOps document submitted", False),
        ("Airspace deconfliction confirmed", False),
        ("Ground risk assessment completed", True),
        ("Communication links tested", True),
    ]

    for item, done in checklist:
        status = "✅" if done else "⬜"
        st.write(f"{status} {item}")

# ════════════════════════════════════════════════════════════════════════════
# TAB 4 — EXPORT
# ════════════════════════════════════════════════════════════════════════════
with tab4:
    st.subheader("Export Assessment Report")
    st.info("Generate a structured PDF report suitable for submission to regulatory bodies or consortium partners.")

    col1, col2 = st.columns(2)
    col1.markdown(f"**Operation:** {operation_name}")
    col1.markdown(f"**Operator:** {operator}")
    col1.markdown(f"**Date:** {datetime.now().strftime('%d %B %Y')}")
    col2.markdown(f"**Overall Risk:** {summary['overall_risk']}")
    col2.markdown(f"**Risk Score:** {summary['score']}/100")
    col2.markdown(f"**SAIL Level:** {summary['sail_level']}")

    st.divider()

    report_data = {
        "operation_name": operation_name,
        "operator": operator,
        "date": datetime.now().strftime("%d %B %Y"),
        "drone_type": drone_type,
        "altitude": altitude,
        "speed": speed,
        "range_km": range_km,
        "flight_time": flight_time,
        "population": population,
        "weather": weather,
        "category": category,
        "frameworks": framework,
        "risks": risks,
        "summary": summary,
        "waypoints": st.session_state.waypoints,
    }

    report_json = json.dumps(report_data, indent=2)
    st.download_button(
        "Download Report (JSON)",
        data=report_json,
        file_name=f"BVLOS_Assessment_{operation_name.replace(' ', '_')}.json",
        mime="application/json"
    )

    st.caption("PDF export requires additional setup. JSON report contains all assessment data for integration with digital twin platforms.")

st.markdown(
    '<p class="footer">BVLOS Flight Risk Assessor — Lakshan Divakar — Brunel University London — '
    'Aligned with EU EARHEART Project</p>',
    unsafe_allow_html=True
)
