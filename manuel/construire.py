"""Construit le manuel PDF : figures, Markdown -> HTML (pandoc), HTML -> PDF (Chromium).

  python manuel/construire.py [sortie.pdf]

Demande pandoc, playwright (avec Chromium) et pypdf.

Deux rendus : le premier repère la page de chaque titre, le second écrit ces numéros
dans la table des matières.
"""
from __future__ import annotations

import html
import re
import subprocess
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright
from pypdf import PdfReader, PdfWriter

ICI = Path(__file__).resolve().parent
BUILD = ICI / "build"
TITRE = "Manuel de trading · Tresor Kamdem"


def markdown_vers_html() -> str:
    sources = sorted((ICI / "chapitres").glob("*.md"))
    texte = "\n\n".join(s.read_text(encoding="utf-8") for s in sources)
    corps = subprocess.run(
        ["pandoc", "-f", "markdown+fenced_divs+pipe_tables+raw_html-implicit_figures+implicit_figures",
         "-t", "html5", "--no-highlight", "--wrap=none"],
        input=texte, capture_output=True, text=True, check=True).stdout
    # Numéro de chapitre au-dessus du titre
    corps = re.sub(r'<h1 data-num="([^"]+)" id="([^"]+)">',
                   lambda m: f'<h1 id="{m[2]}"><span class="num">{m[1]}</span>', corps)
    # Une division « partie » qui commence par un titre devient <section id=...> : on remet l'id sur le titre
    corps = re.sub(r'<section id="([^"]+)" class="partie" data-pnum="([^"]+)">\s*<h1>',
                   lambda m: f'<section class="partie"><div class="pnum">{m[2]}</div><h1 id="{m[1]}">', corps)
    return corps


def titres(corps: str) -> list[tuple[int, str, str]]:
    """(niveau, id, texte) : 0 = partie, 1 = chapitre, 2 = section."""
    out = []
    dans_partie = False
    for m in re.finditer(r'<section class="partie">|<h([12]) id="([^"]+)"[^>]*>(.*?)</h\1>', corps, re.S):
        if m[0].startswith("<section"):
            dans_partie = True
            continue
        n, ident, txt = int(m[1]), m[2], re.sub(r"<[^>]+>", "", re.sub(r'<span class="num">.*?</span>', "", m[3]))
        if n == 1 and dans_partie:
            out.append((0, ident, txt.strip()))
            dans_partie = False
        else:
            out.append((n, ident, txt.strip()))
    return out


def avec_marqueurs(corps: str, liste) -> str:
    for i, (_, ident, _) in enumerate(liste):
        corps = re.sub(rf'(<h[12] id="{re.escape(ident)}"[^>]*>)', rf'\1<span class="marq">qxq{i}qxq</span>', corps, count=1)
    return corps


def tdm(liste, pages: dict[int, int] | None) -> str:
    lignes = []
    for i, (n, ident, txt) in enumerate(liste):
        p = str(pages.get(i, "")) if pages else "000"
        lignes.append(f'<li class="n{n}"><a href="#{ident}">{html.escape(txt)}</a>'
                      f'<span class="points"></span><span class="page">{p}</span></li>')
    return '<nav class="tdm"><h1 id="tdm">Table des matières</h1><ol>' + "".join(lignes) + "</ol></nav>"


def page_html(corps: str, table: str) -> str:
    style = (ICI / "style.css").read_text(encoding="utf-8")
    return (f'<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>{TITRE}</title>'
            f"<style>{style}</style></head><body>{table}{corps}</body></html>")


def couverture() -> str:
    style = (ICI / "style.css").read_text(encoding="utf-8")
    return f"""<!doctype html><html lang="fr"><head><meta charset="utf-8"><style>{style}
    .couverture h1 {{ break-before: avoid; font-size: 36pt; margin: 0 0 6mm; }}
    .bande {{ height: 6mm; background: linear-gradient(90deg, #2a78d6 0 40%, #1baf7a 40% 60%, #eda100 60% 75%, #eb6834 75%); border-radius: 2px; }}
    </style></head><body><div class="couverture">
    <div class="bande"></div>
    <div>
      <div class="pnum" style="color:#2a78d6;font-weight:650;letter-spacing:.1em;text-transform:uppercase">Trade Skills · Quant Finance</div>
      <h1>Manuel de trading<br>et d'investissement</h1>
      <p style="font-size:13pt;color:#52514e;max-width:150mm">Le cours complet en 12 modules avec exercices corrigés pas à pas,
      tes agents et tes robots, comment les calibrer, et ta vie d'investisseur au quotidien.</p>
    </div>
    <div style="font-size:10pt;color:#52514e">
      <p><strong style="color:#1b1b1a">Tresor Kamdem</strong><br>MacBook · iPhone · TradingView <em>tresor_kamdem</em> · Telegram « Tresor Trading » · SESHAT</p>
      <p>Édition du 26 octobre 2026, écrite à partir du dépôt <em>tresorkamdem/trade-skills</em>.<br>
      Contenu éducatif, pas un conseil en investissement. Tout est en argent fictif tant que les critères de la partie V ne sont pas remplis.</p>
    </div></div></body></html>"""


def imprimer(pw, page_html_txt: str, chemin: Path, pied: bool) -> None:
    chemin_html = chemin.with_suffix(".html")
    chemin_html.write_text(page_html_txt, encoding="utf-8")
    try:
        nav = pw.chromium.launch()
    except Exception:  # navigateur préinstallé d'une autre version de Playwright
        nav = pw.chromium.launch(executable_path=_chromium())
    p = nav.new_page()
    p.goto(chemin_html.as_uri(), wait_until="networkidle")
    pied_html = (f'<div style="width:100%;font-family:Inter,sans-serif;font-size:7.5pt;color:#8a8984;'
                 f'padding:0 19mm;display:flex;justify-content:space-between"><span>{TITRE}</span>'
                 f'<span class="pageNumber"></span></div>')
    p.pdf(path=str(chemin), format="A4", print_background=True, prefer_css_page_size=True,
          display_header_footer=pied, header_template="<div></div>", footer_template=pied_html if pied else "<div></div>",
          outline=True, tagged=True)
    nav.close()


def _chromium() -> str:
    for c in sorted(Path("/opt/pw-browsers").glob("chromium-*/chrome-linux*/chrome")):
        return str(c)
    return "/opt/pw-browsers/chromium"


def main(sortie: Path) -> None:
    BUILD.mkdir(exist_ok=True)
    subprocess.run([sys.executable, str(ICI / "figures.py")], check=True)
    corps = markdown_vers_html().replace('src="fig/', f'src="{(BUILD / "fig").as_uri()}/')
    liste = titres(corps)
    corps_m = avec_marqueurs(corps, liste)
    with sync_playwright() as pw:
        imprimer(pw, page_html(corps_m, tdm(liste, None)), BUILD / "passe1.pdf", True)
        pages = {}
        for num, pg in enumerate(PdfReader(BUILD / "passe1.pdf").pages, start=1):
            for i in re.findall(r"qxq(\d+)qxq", pg.extract_text() or ""):
                pages.setdefault(int(i), num)
        manquants = [liste[i][2] for i in range(len(liste)) if i not in pages]
        if manquants:
            print("Titres sans page :", manquants[:5])
        imprimer(pw, page_html(corps_m, tdm(liste, pages)), BUILD / "corps.pdf", True)
        imprimer(pw, couverture(), BUILD / "couverture.pdf", False)
    w = PdfWriter()
    for f in ("couverture.pdf", "corps.pdf"):
        w.append(str(BUILD / f))
    w.add_metadata({"/Title": "Manuel de trading et d'investissement", "/Author": "Tresor Kamdem (avec Claude)"})
    with open(sortie, "wb") as fh:
        w.write(fh)
    print(f"{sortie} : {len(PdfReader(sortie).pages)} pages")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else BUILD / "manuel-trading.pdf")
