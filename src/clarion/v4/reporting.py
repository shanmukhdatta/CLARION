"""Offline case dossier export (JSON and optional ReportLab PDF).

Contains source hashes, uncertainty and evidence paths, never guilt assertions.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def case_export(run_dir: str | Path, txid: str, out_dir: str | Path) -> dict[str,Any]:
    root=Path(run_dir)
    manifest=json.loads((root/"run_manifest.json").read_text(encoding="utf-8"))
    leads=json.loads((root/"leads.json").read_text(encoding="utf-8"))
    selected=next((lead for lead in leads if lead["txid"]==txid),None)
    if selected is None:
        raise ValueError("selected transaction not in local run")
    report={
        "kind":"INVESTIGATIVE_LEAD_UNVERIFIED",
        "warning":"A candidate transaction lead is not proof of wrongdoing or wallet ownership.",
        "txid":txid,"cutoff":manifest.get("cutoff"),
        "source_hashes":manifest.get("data_source_hashes",{}),
        "lead":selected,
        "review_status":"UNREVIEWED",
        "negative_control":"change, batching, consolidation or privacy alternatives require review",
    }
    output=Path(out_dir)
    output.mkdir(parents=True,exist_ok=True)
    file=output/("case-"+txid[:16]+".json")
    file.write_text(json.dumps(report,sort_keys=True,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return {"path":str(file),"sha256":hashlib.sha256(file.read_bytes()).hexdigest(),
            "format":"JSON","status":"UNREVIEWED"}


def case_pdf_from_json(json_path: str | Path, pdf_path: str | Path) -> dict[str,str]:
    """Create text-only PDF with no remote assets; render/visually audit before release."""
    from xml.sax.saxutils import escape

    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

    source=Path(json_path)
    report=json.loads(source.read_text(encoding="utf-8"))
    output=Path(pdf_path)
    output.parent.mkdir(parents=True,exist_ok=True)
    styles=getSampleStyleSheet()
    story=[
        Paragraph("CLARION | Evidence Dossier",styles["Title"]),
        Spacer(1,12),
        Paragraph(escape(str(report.get("warning","Unverified investigative lead"))),styles["Normal"]),
    ]
    for label,value in (
        ("Transaction ID",report.get("txid")),
        ("Event cutoff",report.get("cutoff")),
        ("Review status",report.get("review_status")),
        ("Priority",report.get("lead",{}).get("priority")),
        ("Score type",report.get("lead",{}).get("score_type")),
    ):
        story.append(Spacer(1,8))
        story.append(Paragraph("<b>"+escape(label)+":</b> "+escape(str(value)),styles["Normal"]))
    for name,digest in report.get("source_hashes",{}).items():
        story.append(Spacer(1,6))
        story.append(Paragraph("<b>SHA256 "+escape(str(name))+":</b> "+escape(str(digest)),styles["Normal"]))
    SimpleDocTemplate(str(output),pagesize=A4,rightMargin=45,leftMargin=45,
                      topMargin=45,bottomMargin=45).build(story)
    return {"path":str(output),"sha256":hashlib.sha256(output.read_bytes()).hexdigest()}
