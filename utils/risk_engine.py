"""
risk_engine.py — BVLOS flight risk scoring engine.
Based on EASA SORA methodology and UK CAA OSC framework.
"""

from typing import Dict, List, Any


def assess_flight_risk(params: Dict) -> List[Dict]:
    """
    Score individual risk factors based on flight parameters.
    Returns list of risk factor dicts for display.
    """
    risks = []

    # 1. Ground Risk Class (GRC) — population density
    grc_map = {"Rural": ("Low", 2), "Suburban": ("Medium", 5), "Urban": ("High", 8), "Controlled Airspace": ("Critical", 10)}
    grc_label, grc_score = grc_map.get(params["population"], ("Medium", 5))
    risks.append({
        "Risk Factor": "Ground Risk (Population Density)",
        "Value": params["population"],
        "Risk Level": grc_label,
        "Score": grc_score,
        "Basis": "EASA SORA GRC Table"
    })

    # 2. Altitude risk
    alt = params["altitude"]
    if alt <= 50:
        alt_label, alt_score = "Low", 1
    elif alt <= 120:
        alt_label, alt_score = "Low", 2
    elif alt <= 300:
        alt_label, alt_score = "Medium", 5
    else:
        alt_label, alt_score = "High", 8
    risks.append({
        "Risk Factor": "Altitude Risk",
        "Value": f"{alt}m AGL",
        "Risk Level": alt_label,
        "Score": alt_score,
        "Basis": "UK CAA CAP 722 / EASA ARC"
    })

    # 3. Weather risk
    wx_map = {
        "VMC (Clear)": ("Low", 1),
        "IMC (Cloud/Rain)": ("High", 8),
        "High Wind (>10m/s)": ("High", 7),
        "Night": ("Medium", 5)
    }
    wx_label, wx_score = wx_map.get(params["weather"], ("Medium", 5))
    risks.append({
        "Risk Factor": "Meteorological Conditions",
        "Value": params["weather"],
        "Risk Level": wx_label,
        "Score": wx_score,
        "Basis": "EASA AMC RPAS.1309"
    })

    # 4. Range risk
    rng = params["range_km"]
    if rng <= 5:
        rng_label, rng_score = "Low", 2
    elif rng <= 20:
        rng_label, rng_score = "Medium", 5
    elif rng <= 50:
        rng_label, rng_score = "High", 7
    else:
        rng_label, rng_score = "Critical", 9
    risks.append({
        "Risk Factor": "Operational Range",
        "Value": f"{rng} km",
        "Risk Level": rng_label,
        "Score": rng_score,
        "Basis": "UK CAA BVLOS Policy"
    })

    # 5. Contingency risk
    cont_map = {
        "Full RTH": ("Low", 1),
        "Partial RTH": ("Medium", 4),
        "Parachute": ("Medium", 5),
        "None": ("Critical", 10)
    }
    cont_label, cont_score = cont_map.get(params["contingency"], ("Medium", 5))
    risks.append({
        "Risk Factor": "Contingency / Emergency Plan",
        "Value": params["contingency"],
        "Risk Level": cont_label,
        "Score": cont_score,
        "Basis": "EASA SORA OSO #09"
    })

    # 6. UAS category risk
    cat_map = {"Open": ("Low", 1), "Specific": ("Medium", 5), "Certified": ("Low", 2)}
    cat_label, cat_score = cat_map.get(params["category"], ("Medium", 5))
    risks.append({
        "Risk Factor": "UAS Regulatory Category",
        "Value": params["category"],
        "Risk Level": cat_label,
        "Score": cat_score,
        "Basis": "EASA 2019/947"
    })

    # 7. Speed risk
    spd = params["speed"]
    if spd <= 10:
        spd_label, spd_score = "Low", 1
    elif spd <= 25:
        spd_label, spd_score = "Medium", 4
    else:
        spd_label, spd_score = "High", 7
    risks.append({
        "Risk Factor": "Kinetic Energy / Speed",
        "Value": f"{spd} m/s",
        "Risk Level": spd_label,
        "Score": spd_score,
        "Basis": "EASA SORA Annex B"
    })

    return risks


def generate_risk_summary(risks: List[Dict]) -> Dict[str, Any]:
    """Generate overall risk summary from individual risk factors."""
    scores    = [r["Score"] for r in risks]
    avg_score = sum(scores) / len(scores)
    max_score = max(scores)
    total     = int((avg_score * 0.6 + max_score * 0.4) * 10)
    total     = min(total, 100)

    if total >= 70:
        overall = "High"
    elif total >= 40:
        overall = "Medium"
    else:
        overall = "Low"

    # Estimate SAIL level
    if total >= 80:
        sail = "SAIL V-VI"
    elif total >= 60:
        sail = "SAIL IV"
    elif total >= 40:
        sail = "SAIL III"
    elif total >= 20:
        sail = "SAIL II"
    else:
        sail = "SAIL I"

    # Generate mitigations
    mitigations = []
    for r in risks:
        if r["Risk Level"] in ["High", "Critical"]:
            factor = r["Risk Factor"]
            if "Population" in factor:
                mitigations.append("Re-route to minimise overflight of populated areas where possible")
            if "Weather" in factor:
                mitigations.append("Implement weather minima: cancel ops below VMC or above wind limits")
            if "Range" in factor:
                mitigations.append("Deploy ground control stations at intermediate waypoints")
            if "Contingency" in factor:
                mitigations.append("Develop and test full Return-to-Home (RTH) emergency procedure")
            if "Altitude" in factor:
                mitigations.append("File airspace notification with NATS/CAA for high-altitude operations")

    if not mitigations:
        mitigations = ["Risk profile acceptable — maintain standard BVLOS operational protocols"]

    return {
        "overall_risk": overall,
        "score": total,
        "sail_level": sail,
        "mitigations": list(set(mitigations))
    }
