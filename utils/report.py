"""
report.py — Report generation utilities.
"""

import json
from datetime import datetime


def generate_pdf_report(report_data: dict) -> bytes:
    """
    Generate a structured assessment report.
    Returns JSON bytes as placeholder for PDF generation.
    In production, use reportlab or weasyprint for full PDF output.
    """
    return json.dumps(report_data, indent=2).encode("utf-8")


def format_report_text(report_data: dict) -> str:
    """Generate plain text version of the report."""
    lines = [
        "=" * 60,
        "BVLOS FLIGHT RISK ASSESSMENT REPORT",
        "=" * 60,
        f"Operation:    {report_data.get('operation_name')}",
        f"Operator:     {report_data.get('operator')}",
        f"Date:         {report_data.get('date')}",
        f"Drone Type:   {report_data.get('drone_type')}",
        "",
        "FLIGHT PARAMETERS",
        "-" * 40,
        f"Altitude:     {report_data.get('altitude')}m AGL",
        f"Speed:        {report_data.get('speed')} m/s",
        f"Range:        {report_data.get('range_km')} km",
        f"Duration:     {report_data.get('flight_time')} mins",
        f"Area Type:    {report_data.get('population')}",
        f"Weather:      {report_data.get('weather')}",
        "",
        "RISK SUMMARY",
        "-" * 40,
        f"Overall Risk: {report_data['summary'].get('overall_risk')}",
        f"Risk Score:   {report_data['summary'].get('score')}/100",
        f"SAIL Level:   {report_data['summary'].get('sail_level')}",
        "",
        "MITIGATIONS",
        "-" * 40,
    ]
    for m in report_data["summary"].get("mitigations", []):
        lines.append(f"• {m}")

    lines += [
        "",
        "REGULATORY FRAMEWORKS",
        "-" * 40,
    ]
    for fw in report_data.get("frameworks", []):
        lines.append(f"• {fw}")

    lines += ["", "=" * 60, "END OF REPORT", "=" * 60]
    return "\n".join(lines)
