#!/usr/bin/env python3
"""Write docs/architecture.svg and render docs/architecture.png (3200x2000) with rsvg-convert."""
import subprocess
from pathlib import Path
from xml.sax.saxutils import escape

DOCS = Path(__file__).resolve().parent
SVG = DOCS / "architecture.svg"
PNG = DOCS / "architecture.png"

STYLES = {
    "input": ("#334155", "#cbd5e1"),
    "service": ("#1e3a5f", "#7dd3fc"),
    "model": ("#3b2f5c", "#c4b5fd"),
    "score": ("#4a3f14", "#fde047"),
    "output": ("#1f3d2f", "#86efac"),
    "store": ("#4a3420", "#fdba74"),
}
COLS = {1: 60, 2: 480, 3: 900}
ROWS = {1: 200, 2: 480, 3: 760}
W, H = 340, 110

BOXES = {
    "submit": (1, 1, "input", "Submitted text", ["quotes · notes · web pages · blogs"]),
    "app": (2, 1, "service", "ClipFile web app", ["Java · Spring Boot · jQuery"]),
    "nlp": (3, 1, "service", "NLP preprocessing", ["tokenize · stem · tense · plurals", "stop words · contractions · synonyms"]),
    "bags": (3, 2, "model", "Token bags", ["weight = incidence fraction"]),
    "profiles": (2, 2, "model", "User profiles", ["aggregated item token bags"]),
    "score": (1, 2, "score", "Similarity scoring", ["Σ shared weights / Σ all weights"]),
    "cf": (1, 3, "output", "Collaborative filtering", ["rank items and users by score"]),
    "recs": (2, 3, "input", "Recommendations", ["similar content · similar users"]),
}


def box(x, y, w, h, kind, name, subs):
    fill, stroke = STYLES[kind]
    cx = x + w / 2
    top = y + h / 2 - 6 - 15 * (len(subs) - 1)
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{fill}" stroke="{stroke}" stroke-width="2.5"/>',
           f'<text x="{cx:g}" y="{top:g}" class="name">{escape(name)}</text>']
    for i, sub in enumerate(subs):
        out.append(f'<text x="{cx:g}" y="{top + 30 + 26 * i:g}" class="sub">{escape(sub)}</text>')
    return out


def edge(points, label=None, at=None, dashed=False):
    pts = " ".join(f"{x:g},{y:g}" for x, y in points)
    dash = ' stroke-dasharray="10 8"' if dashed else ""
    out = [f'<polyline points="{pts}" fill="none" stroke="#cbd5e1" stroke-width="2.5"{dash} marker-end="url(#arrow)"/>']
    if label:
        lx, ly = at
        lw = len(label) * 9.6 + 16
        out += [f'<rect x="{lx - lw / 2:g}" y="{ly - 15:g}" width="{lw:g}" height="28" rx="6" fill="#0f172a" opacity="0.92"/>',
                f'<text x="{lx:g}" y="{ly + 6:g}" class="edge">{escape(label)}</text>']
    return out


def main():
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 1000">', "<defs>",
             '<marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#cbd5e1"/></marker>',
             "<style>",
             'text { font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; }',
             ".title { font-size: 40px; font-weight: 700; fill: #f8fafc; }",
             ".subtitle { font-size: 22px; fill: #94a3b8; }",
             ".name { font-size: 25px; font-weight: 700; fill: #f8fafc; text-anchor: middle; }",
             ".sub { font-size: 18px; fill: #cbd5e1; text-anchor: middle; }",
             ".edge { font-size: 16px; fill: #e2e8f0; text-anchor: middle; }",
             ".note { font-size: 18px; fill: #94a3b8; }",
             "</style>", "</defs>",
             '<rect width="1600" height="1000" fill="#0f172a"/>',
             '<text x="60" y="78" class="title">nlp-patents</text>',
             '<text x="60" y="114" class="subtitle">ClipFile token-weighted content matching and collaborative filtering on AWS DynamoDB</text>']
    for col, row, kind, name, subs in BOXES.values():
        parts += box(COLS[col], ROWS[row], W, H, kind, name, subs)
    parts += box(1310, 200, 230, 390, "store", "AWS DynamoDB", ["items · token bags", "user profiles"])

    mid = H / 2
    parts += edge([(400, 200 + mid), (480, 200 + mid)], "text", (440, 255))
    parts += edge([(820, 200 + mid), (900, 200 + mid)], "item", (860, 255))
    parts += edge([(1070, 310), (1070, 480)], "tokens", (1070, 395))
    parts += edge([(900, 480 + mid), (820, 480 + mid)], "aggregate", (860, 535))
    parts += edge([(480, 480 + mid), (400, 480 + mid)], "profiles", (440, 535))
    parts += edge([(230, 590), (230, 760)], "scores", (230, 675))
    parts += edge([(400, 760 + mid), (480, 760 + mid)], "matches", (440, 815))
    parts += edge([(1240, 255), (1310, 255)], dashed=True)
    parts += edge([(1240, 535), (1310, 535)], dashed=True)
    parts += edge([(1425, 590), (1425, 900), (230, 900), (230, 870)], "serial batch reads (not interactive)", (827, 900), dashed=True)

    parts += ['<text x="60" y="950" class="note">Co-invented with Rolly Rouse: Using Content (US 2013/0325870 A1) · Tagging and Ranking Content (US 2019/0362384 A1) — ClipFile Corporation</text>',
              '<text x="60" y="978" class="note">Attribute tagging and matching system and method for database management (US 2001/0042060 A1) — HomePortfolio Inc.</text>',
              "</svg>"]
    SVG.write_text("\n".join(parts) + "\n")
    subprocess.run(["rsvg-convert", "-w", "3200", "-h", "2000", "-o", str(PNG), str(SVG)], check=True)
    print(f"wrote {SVG.name} and {PNG.name}")


if __name__ == "__main__":
    main()
