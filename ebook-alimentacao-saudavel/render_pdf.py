#!/usr/bin/env python3
"""Render the Viva Leve Markdown manuscript as a self-contained PDF.

This intentionally uses only the Python standard library, so the deliverable can
be rebuilt in minimal environments:
    python3 ebook-alimentacao-saudavel/render_pdf.py
"""
from __future__ import annotations

from pathlib import Path
import re
import textwrap

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "ebook.md"
OUTPUT = ROOT / "viva-leve-28-dias.pdf"
PAGE_W, PAGE_H = 595, 842  # A4 in PDF points
LEFT, RIGHT, TOP, BOTTOM = 58, 58, 62, 54
CONTENT_W = PAGE_W - LEFT - RIGHT


def esc(value: str) -> str:
    """Encode Portuguese text for a WinAnsi PDF literal string."""
    data = value.encode("cp1252", "replace")
    return "".join(
        "\\\\" if b == 92 else "\\(" if b == 40 else "\\)" if b == 41
        else chr(b) if 32 <= b <= 126 else f"\\{b:03o}"
        for b in data
    )


def clean(value: str) -> str:
    value = re.sub(r"\*\*(.*?)\*\*", r"\1", value)
    value = re.sub(r"\*(.*?)\*", r"\1", value)
    value = re.sub(r"`(.*?)`", r"\1", value)
    return value.replace("—", "–").replace("•", "·")


def wrap(value: str, width: int) -> list[str]:
    return textwrap.wrap(clean(value), width=width, break_long_words=False, break_on_hyphens=False) or [""]


class Pdf:
    def __init__(self) -> None:
        self.pages: list[list[str]] = []
        self.commands: list[str] = []
        self.y = PAGE_H - TOP
        self.page_no = 0

    def new_page(self, section: str = "") -> None:
        if self.commands:
            self._footer()
            self.pages.append(self.commands)
        self.commands = []
        self.page_no += 1
        self.y = PAGE_H - TOP
        if self.page_no > 1:
            self.commands.extend([
                "0.12 0.35 0.29 rg 58 798 479 2 re f",
                "BT /F2 8 Tf 0.12 0.35 0.29 rg 58 812 Td (VIVA LEVE) Tj ET",
            ])
            if section:
                self.commands.append(f"BT /F1 8 Tf 0.35 0.42 0.39 rg 537 812 Td ({esc(section.upper()[:36])}) Tj ET")

    def _footer(self) -> None:
        if self.page_no > 1:
            self.commands.extend([
                "0.85 0.89 0.86 rg 58 40 479 1 re f",
                f"BT /F1 8 Tf 0.35 0.42 0.39 rg 58 27 Td (Viva Leve  |  28 dias de refeições reais e movimento em casa) Tj ET",
                f"BT /F2 8 Tf 0.12 0.35 0.29 rg 523 27 Td ({self.page_no}) Tj ET",
            ])

    def ensure(self, height: float, section: str = "") -> None:
        if self.y - height < BOTTOM:
            self.new_page(section)

    def text(self, value: str, size: float = 10.2, leading: float = 14, font: str = "F1",
             color: str = "0.15 0.20 0.18", indent: float = 0, section: str = "") -> None:
        columns = max(28, int((CONTENT_W - indent) / (size * 0.48)))
        lines = wrap(value, columns)
        self.ensure(len(lines) * leading + 5, section)
        self.commands.append(f"BT /{font} {size} Tf {color} rg {LEFT + indent} {self.y:.1f} Td")
        for n, line in enumerate(lines):
            if n:
                self.commands.append(f"0 -{leading} Td")
            self.commands.append(f"({esc(line)}) Tj")
        self.commands.append("ET")
        self.y -= len(lines) * leading + 5

    def rule(self) -> None:
        self.ensure(18)
        self.commands.append(f"0.84 0.70 0.33 rg {LEFT} {self.y - 4:.1f} 62 2 re f")
        self.y -= 17

    def heading(self, value: str, level: int, section: str) -> None:
        if level == 1:
            self.new_page(section)
            self.y -= 22
            self.text(value, 25, 30, "F2", "0.12 0.35 0.29", section=section)
            self.rule()
        elif level == 2:
            self.ensure(38, section)
            self.y -= 9
            self.text(value, 16, 20, "F2", "0.12 0.35 0.29", section=section)
        else:
            self.ensure(31, section)
            self.y -= 6
            self.text(value, 12.2, 16, "F2", "0.54 0.32 0.10", section=section)

    def cover(self) -> None:
        self.commands = []
        self.page_no = 1
        self.y = PAGE_H - TOP
        self.commands.extend([
            "0.93 0.96 0.91 rg 0 0 595 842 re f",
            "0.12 0.35 0.29 rg 0 620 595 222 re f",
            "0.84 0.70 0.33 rg 0 597 595 23 re f",
            "0.73 0.84 0.75 rg 420 100 210 210 re f",
            "0.82 0.91 0.83 rg 395 150 135 135 re f",
        ])
        self.commands.extend([
            "BT /F2 14 Tf 1 1 1 rg 58 760 Td (VIVA LEVE) Tj ET",
            "BT /F1 11 Tf 0.9 0.95 0.9 rg 58 735 Td (28 dias de refeições reais e movimento em casa) Tj ET",
            "BT /F2 31 Tf 0.12 0.35 0.29 rg 58 535 Td (Comer melhor.) Tj ET",
            "BT /F2 31 Tf 0.12 0.35 0.29 rg 58 495 Td (Mover-se mais.) Tj ET",
            "BT /F2 31 Tf 0.12 0.35 0.29 rg 58 455 Td (Viver com leveza.) Tj ET",
            "BT /F1 13 Tf 0.15 0.20 0.18 rg 58 393 Td (Receitas práticas, planejamento sem complicação) Tj ET",
            "BT /F1 13 Tf 0.15 0.20 0.18 rg 58 374 Td (e treinos acessíveis para sua rotina.) Tj ET",
            "BT /F2 10 Tf 0.54 0.32 0.10 rg 58 115 Td (GUIA PRÁTICO · 1ª EDIÇÃO) Tj ET",
            "BT /F1 9 Tf 0.35 0.42 0.39 rg 58 88 Td (Alimentação possível. Movimento em casa. Um passo por vez.) Tj ET",
        ])
        self.pages.append(self.commands)
        self.commands = []

    def finish(self) -> None:
        if self.commands:
            self._footer()
            self.pages.append(self.commands)


def build() -> None:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    # Remove YAML front matter.
    if lines and lines[0] == "---":
        lines = lines[lines[1:].index("---") + 2:]

    pdf = Pdf()
    pdf.cover()
    pdf.new_page("Comece aqui")
    section = "Comece aqui"
    in_table = False
    table_rows: list[str] = []

    def flush_table() -> None:
        nonlocal table_rows
        for row in table_rows:
            cells = [clean(cell.strip()) for cell in row.strip().strip("|").split("|")]
            if all(re.fullmatch(r"[-: ]+", cell) for cell in cells):
                continue
            pdf.text("  ·  ".join(cells), 8.4, 11.4, "F1", "0.20 0.27 0.24", 5, section)
        table_rows = []

    for raw in lines:
        if raw.startswith("|"):
            table_rows.append(raw)
            in_table = True
            continue
        if in_table:
            flush_table()
            in_table = False
        if not raw.strip():
            pdf.y -= 4
            continue
        if raw == "---":
            pdf.rule()
            continue
        if raw.startswith("# "):
            title = clean(raw[2:])
            if title != "Viva Leve":
                section = title.replace("Parte ", "")
                pdf.heading(title, 1, section)
            continue
        if raw.startswith("## "):
            title = clean(raw[3:])
            pdf.heading(title, 2, section)
            continue
        if raw.startswith("### "):
            pdf.heading(clean(raw[4:]), 3, section)
            continue
        if raw.startswith("> "):
            pdf.text(clean(raw[2:]), 9.4, 13.2, "F3", "0.20 0.31 0.27", 10, section)
            continue
        ordered = re.match(r"^(\d+)\.\s+(.*)", raw)
        if ordered:
            pdf.text(f"{ordered.group(1)}. {clean(ordered.group(2))}", 10.0, 13.8, "F1", indent=8, section=section)
            continue
        if raw.startswith("- "):
            pdf.text(f"·  {clean(raw[2:])}", 10.0, 13.8, "F1", indent=8, section=section)
            continue
        pdf.text(clean(raw), 10.2, 14, "F1", section=section)
    if in_table:
        flush_table()
    pdf.finish()

    objects: list[bytes] = []
    def add(data: str | bytes) -> int:
        objects.append(data.encode("latin-1") if isinstance(data, str) else data)
        return len(objects)

    font_regular = add("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>")
    font_bold = add("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>")
    font_italic = add("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Oblique /Encoding /WinAnsiEncoding >>")
    page_refs = []
    for commands in pdf.pages:
        stream = "\n".join(commands).encode("latin-1")
        content = add(b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream")
        page_refs.append(add(
            f"<< /Type /Page /Parent PAGES_REF /MediaBox [0 0 {PAGE_W} {PAGE_H}] "
            f"/Resources << /Font << /F1 {font_regular} 0 R /F2 {font_bold} 0 R /F3 {font_italic} 0 R >> >> "
            f"/Contents {content} 0 R >>"
        ))
    pages = add("<< /Type /Pages /Kids [" + " ".join(f"{p} 0 R" for p in page_refs) + f"] /Count {len(page_refs)} >>")
    for index in page_refs:
        objects[index - 1] = objects[index - 1].replace(b"PAGES_REF", f"{pages} 0 R".encode())
    catalog = add(f"<< /Type /Catalog /Pages {pages} 0 R /PageLayout /OneColumn >>")
    info = add("<< /Title (Viva Leve - 28 dias) /Author (Viva Leve) /Subject (Receitas e movimento em casa) >>")

    out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for i, obj in enumerate(objects, 1):
        offsets.append(len(out))
        out.extend(f"{i} 0 obj\n".encode())
        out.extend(obj)
        out.extend(b"\nendobj\n")
    xref = len(out)
    # The xref entries remain valid without terminal padding, which also keeps
    # source-control whitespace checks meaningful for the generated PDF.
    out.extend(f"xref\n0 {len(objects)+1}\n0000000000 65535 f\n".encode())
    out.extend(b"".join(f"{offset:010d} 00000 n\n".encode() for offset in offsets[1:]))
    out.extend(f"trailer\n<< /Size {len(objects)+1} /Root {catalog} 0 R /Info {info} 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
    OUTPUT.write_bytes(out)
    print(f"Created {OUTPUT.relative_to(ROOT.parent)} with {len(pdf.pages)} pages.")


if __name__ == "__main__":
    build()
