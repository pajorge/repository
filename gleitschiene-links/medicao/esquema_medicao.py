"""Folha de medição da Gleitschiene links (Backhus A50), gerada a partir do modelo CAD.

Os valores "esperados" saem de ../cad/gleitschiene.py, por isso esta folha está sempre
de acordo com o modelo. Mede-se na peça, compara-se e escreve-se o valor lido.

X: posição ao longo da aresta A, lida numa fita presa ao longo de A com o centro do F1 no 100.
Y: altura a partir da aresta A, lida com o paquímetro (a tinta soma ~1 mm à leitura).
"""
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Circle, Polygon, Rectangle

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "cad"))
import gleitschiene as G  # noqa: E402
from desenho import bico_info  # noqa: E402

ZERO = 100.0  # leitura da fita no centro do F1
RED, BLUE, GREEN, GREY, INK = "#c0392b", "#1f5fbf", "#1e8449", "#8a8a8a", "#222222"


def pontos(g):
    """Pontos de medição com o valor esperado (modelo)."""
    rs = {n: (cx, w, yf) for n, cx, w, yf in G.RASGOS}
    wall = lambda n, s: rs[n][0] + s * rs[n][1] / 2
    bico_x = bico_info(g)[0][0]
    bb = g["peca"].bounding_box()
    # --- X: (descrição, X modelo, Y do ponto)
    xs = [
        ("topo esquerda, em cima (logo abaixo do chanfro)", g["C2"][0], g["C2"][1] + 2),
        ("topo esquerda, em baixo (dedo, a 10 mm do fundo)", G.topo_x(G.DEDO_Y - 10), G.DEDO_Y - 10),
        ("N1 parede esquerda", wall("N1", -1), 100),
        ("fim do chanfro na aresta A", g["C1"][0], 0),
        ("N1 parede direita", wall("N1", 1), 100),
        ("F1 bordo esquerdo", -G.FURO_D / 2, G.FURO_Y),
        ("F1 bordo direito", G.FURO_D / 2, G.FURO_Y),
        ("N2 parede esquerda", wall("N2", -1), 88),
        ("N2 parede direita", wall("N2", 1), 88),
        ("N3 parede esquerda", wall("N3", -1), 76),
        ("N3 parede direita", wall("N3", 1), 76),
        ("N4 parede esquerda", wall("N4", -1), 62),
        ("N4 parede direita", wall("N4", 1), 58),
        ("degrau E", G.DEGRAU_X, 110),
        ("bico B (ponto mais baixo)", bico_x, G.BICO_Y),
        ("fim da peça (vértice V)", bb.max.X, 4),
    ]
    xs = [(f"X{i+1}",) + p for i, p in enumerate(sorted(xs, key=lambda p: p[1]))]
    # --- Y: (descrição, X da seta, Y modelo)
    c3 = 3.0  # medir a 3 mm do canto
    d1l, d1r = wall("N1", 1), wall("N2", -1)
    d2l, d2r = wall("N2", 1), wall("N3", -1)
    d3l, d3r = wall("N3", 1), wall("N4", -1)
    ys = [
        ("chanfro: quanto desce na topo", g["C2"][0] + 2, g["C2"][1]),
        ("altura total no dedo P", G.topo_x(G.DEDO_Y) + G.DEDO_LARG / 2, G.DEDO_Y),
        ("N1: da aresta A ao fundo do rasgo", rs["N1"][0], rs["N1"][2]),
        ("D1 canto esquerdo (a 3 mm)", d1l + c3, G.dentes_y(d1l + c3)),
        ("F1: da aresta A ao bordo do furo", 0, G.FURO_Y - G.FURO_D / 2),
        ("D1 canto direito (a 3 mm)", d1r - c3, G.dentes_y(d1r - c3)),
        ("N2: da aresta A ao fundo do rasgo", rs["N2"][0], rs["N2"][2]),
        ("D2 canto esquerdo (a 3 mm)", d2l + c3, G.dentes_y(d2l + c3)),
        ("D2 canto direito (a 3 mm)", d2r - c3, G.dentes_y(d2r - c3)),
        ("N3: da aresta A ao fundo do rasgo", rs["N3"][0], rs["N3"][2]),
        ("D3 canto esquerdo (a 3 mm)", d3l + c3, G.dentes_y(d3l + c3)),
        ("D3 canto direito (a 3 mm)", d3r - c3, G.dentes_y(d3r - c3)),
        ("N4: da aresta A ao fundo do rasgo", rs["N4"][0], rs["N4"][2]),
        ("patamar antes do degrau E", G.DEGRAU_X - 10, G.dentes_y(G.DEGRAU_X - 10)),
        ("F4: da aresta A ao bordo do furo", 3 * G.PASSO_FUROS, G.FURO_Y - G.FURO_D / 2),
    ]
    ys = [(f"Y{i+1}",) + p for i, p in enumerate(ys)]
    return xs, ys


def draw_part(ax, g):
    for e in g["corte2d"].edges():
        n = 50 if e.geom_type.name == "CIRCLE" else 2
        pts = np.array([tuple(e @ t)[:2] for t in np.linspace(0, 1, n)])
        ax.plot(pts[:, 0] + ZERO, pts[:, 1], color=INK, lw=1.2, zorder=3)
    ax.fill([], [])
    for i, (x, y) in enumerate(g["furos"]):
        ax.add_patch(Circle((x + ZERO, y), G.CAIXA_D / 2, fc="none", ec=GREY, lw=0.8, ls="--", zorder=2))
        ax.text(x + ZERO, y + 19, f"F{i+1}", ha="center", fontsize=8, weight="bold", color=INK)
    for n, cx, w, yf in G.RASGOS:
        ax.text(cx + ZERO, -(yf + w / 2 + 2), n, ha="center", va="center", fontsize=8, weight="bold", color=INK)
    ax.text(160 + ZERO, -4, "aresta A (reta)", ha="center", va="top", fontsize=8, style="italic")


def bubble(ax, x, y, txt, col):
    ax.text(x, y, txt, ha="center", va="center", fontsize=7.5, color="white", weight="bold",
            bbox=dict(boxstyle="round,pad=0.25", fc=col, ec="none"), zorder=6)


def page_x(pdf, g, xs):
    fig, ax = plt.subplots(figsize=(11.69, 8.27))
    fig.subplots_adjust(left=0.01, right=0.99, top=0.92, bottom=0.01)
    ax.set_aspect("equal"); ax.axis("off")
    fig.suptitle("1) POSIÇÕES ao longo da aresta A — fita métrica + esquadro", fontsize=14, weight="bold",
                 x=0.02, ha="left", y=0.97)
    draw_part(ax, g)
    y0 = 10
    ax.add_patch(Rectangle((0, y0), 575, 9, fc="#f7dc6f", ec="#b7950b", lw=0.8, zorder=3))
    for t in range(0, 571, 10):
        h = 5 if t % 50 == 0 else 2.5
        ax.plot([t, t], [y0, y0 + h], color="#7d6608", lw=0.6, zorder=4)
        if t % 50 == 0:
            ax.text(t, y0 + 6.2, str(t), fontsize=5.5, ha="center", color="#7d6608", zorder=4)
    ax.annotate("F1 no 100", (ZERO, y0 + 9), (ZERO + 18, y0 + 17), fontsize=7, color="#7d6608", weight="bold",
                arrowprops=dict(arrowstyle="->", color="#7d6608", lw=0.8))
    lvl = [24, 40, 56, 72]
    for i, (lab, desc, x, y) in enumerate(xs):
        X = x + ZERO
        ytop = y0 + 12 + lvl[i % 4]
        ax.plot([X, X], [-y, ytop - 5], color=RED, lw=0.7, ls=(0, (3, 2)), zorder=5)
        ax.plot(X, -y, "o", color=RED, ms=3, zorder=6)
        bubble(ax, X, ytop, lab, RED)
        ax.text(X, ytop + 7, f"{X:.0f}", fontsize=6.8, ha="center", color=RED)
    txt = ("COMO\n"
           "1. Prende a fita com fita-cola ao longo da aresta A. Ajusta-a para o CENTRO do F1 ficar no 100:\n"
           "   com o esquadro, os dois bordos do F1 (pintado) devem ler ~92 e ~108 (a média tem de dar 100).\n"
           "2. Base do esquadro encostada à aresta A; alinha a régua do esquadro com o ponto; lê a fita.\n"
           "3. Escreve o que leste na tabela (página 3). Valores a vermelho = o que o modelo espera.\n"
           "   Até ±1 mm é normal (tinta). Mais de 2 mm de diferença → mede outra vez e marca.\n"
           "• X1 e X2 dizem se a topo esquerda é inclinada (modelo: 6°) ou esquadrada (X1 = X2).")
    ax.text(0, -198, txt, fontsize=7.6, va="top", ha="left", color=INK, linespacing=1.5,
            bbox=dict(boxstyle="round,pad=0.5", fc="#fdf2e9", ec=RED, lw=0.8))
    # mini desenho do esquadro
    bx, by = 455, -205
    ax.add_patch(Rectangle((bx, by - 62), 110, 62, fc="#eef1f4", ec=INK, lw=1))
    ax.add_patch(Rectangle((bx + 42, by - 63), 26, 36, fc="white", ec="none"))
    ax.plot([bx + 42, bx + 42, bx + 68, bx + 68], [by - 62, by - 27, by - 27, by - 62], color=INK, lw=1)
    ax.add_patch(Rectangle((bx, by - 9), 110, 6, fc="#f7dc6f", ec="#b7950b", lw=0.6))
    ax.add_patch(Rectangle((bx + 55, by), 40, 8, fc="#566573", ec=INK, lw=0.8))
    ax.add_patch(Rectangle((bx + 68, by - 45), 7, 45, fc="#aab7b8", ec=INK, lw=0.8, alpha=0.9))
    ax.plot([bx + 68, bx + 68], [by - 45, by + 8], color=RED, lw=1.2)
    ax.annotate("base do esquadro\nencostada à aresta A", (bx + 88, by + 8), (bx + 78, by + 22), fontsize=6,
                arrowprops=dict(arrowstyle="-", lw=0.6))
    ax.annotate("régua alinhada com\na parede do rasgo", (bx + 72, by - 38), (bx + 84, by - 52), fontsize=6,
                arrowprops=dict(arrowstyle="-", lw=0.6))
    ax.annotate("lê a fita aqui", (bx + 68, by - 6), (bx + 2, by + 18), fontsize=6.5, color=RED, weight="bold",
                arrowprops=dict(arrowstyle="->", lw=0.8, color=RED))
    ax.set_xlim(-5, 580); ax.set_ylim(-280, 105)
    pdf.savefig(fig); fig.savefig(HERE / "pagina1_posicoes_X.png", dpi=170); plt.close(fig)


def page_y(pdf, g, ys):
    fig, ax = plt.subplots(figsize=(11.69, 8.27))
    fig.subplots_adjust(left=0.01, right=0.99, top=0.92, bottom=0.01)
    ax.set_aspect("equal"); ax.axis("off")
    fig.suptitle("2) ALTURAS a partir da aresta A — paquímetro a 90° da aresta", fontsize=14, weight="bold",
                 x=0.02, ha="left", y=0.97)
    draw_part(ax, g)
    for i, (lab, desc, x, y) in enumerate(ys):
        X = x + ZERO
        ax.annotate("", (X, -y), (X, 0), arrowprops=dict(arrowstyle="<->", color=BLUE, lw=0.9,
                                                         shrinkA=0, shrinkB=0), zorder=5)
        yl = 14 + (i % 3) * 16
        ax.plot([X, X], [0, yl - 5], color=BLUE, lw=0.6, ls=(0, (2, 2)))
        bubble(ax, X, yl, lab, BLUE)
        ax.text(X, yl + 7.5, f"{y + 1:.0f}", fontsize=6.8, ha="center", color=BLUE)
    txt = ("COMO\n"
           "• Um bico do paquímetro na aresta A e o outro no ponto, sempre a 90° da aresta A.\n"
           "• Valores a azul = leitura esperada COM tinta (modelo + 1 mm). Até ±1 mm de diferença é normal.\n"
           "• Dentes (D1–D3): mede a ~3 mm do canto, fora do arredondamento. A face é inclinada (~8°), por isso\n"
           "   os dois cantos do mesmo dente dão valores diferentes.\n"
           "• Rasgos (Y3, Y7, Y10, Y13): o bico entra no rasgo e encosta no fundo (é o 'material acima do rasgo').\n"
           "• Furos (Y5, Y15): da aresta A ao bordo mais próximo, do lado SEM caixa. Se Y5 = Y15 → paralelos a A.")
    ax.text(0, -195, txt, fontsize=7.6, va="top", ha="left", color=INK, linespacing=1.5,
            bbox=dict(boxstyle="round,pad=0.5", fc="#eaf2fb", ec=BLUE, lw=0.8))
    ax.set_xlim(-5, 580); ax.set_ylim(-280, 70)
    pdf.savefig(fig); fig.savefig(HERE / "pagina2_alturas_Y.png", dpi=170); plt.close(fig)


def page_tabela(pdf, g, xs, ys):
    bb = g["peca"].bounding_box()
    rows = [("", "POSIÇÕES X (fita, F1 no 100)", "", "")]
    rows += [(lab, desc, f"{x + ZERO:.1f}", "") for lab, desc, x, _ in xs]
    rows += [("", "ALTURAS Y (paquímetro, com tinta)", "", "")]
    rows += [(lab, desc, f"{y + 1:.1f}", "") for lab, desc, _, y in ys]
    rows += [("", "RAIOS (moeda que encaixa no canto)", "", "")]
    rows += [
        ("R1", "vértice V", f"R{G.R_VERTICE:g}", ""),
        ("R2", "bico B", f"R{g['R_BICO']:.1f}", ""),
        ("R3", "cantos de fora dos dentes / patamar", f"R{G.R_PEQUENO:g}", ""),
        ("R4", "cantos de dentro (degrau E, fundo do patamar)", f"R{G.R_PEQUENO:g}", ""),
        ("R5", "cantos do chanfro C", f"R{G.R_PEQUENO:g}", ""),
        ("R6", "ponta do dedo P", f"R{G.R_DEDO:g}", ""),
    ]
    rows += [("", "OUTROS", "", "")]
    rows += [
        ("L", "comprimento total (fita, de ponta a ponta)", f"{bb.max.X - bb.min.X + 1:.0f}", ""),
        ("Q1", "paredes dos rasgos a 90° da aresta A? (esquadro)", "sim", ""),
        ("Q2", "parafuso: rosca / Ø cabeça / altura cabeça / norma", "M16 / ≤26 / ? / ?", ""),
        ("Q3", "a cabeça entra toda na caixa Ø26.5?", "sim", ""),
        ("Q4", "lima na aresta: escorrega (Hardox) ou morde (S355)?", "?", ""),
        ("Q5", "peso na balança", f"≈{g['peca'].volume * 7.85e-6 + 0.15:.1f} kg", ""),
    ]
    fig = plt.figure(figsize=(8.27, 11.69))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 210); ax.set_ylim(0, 297); ax.axis("off")
    ax.text(12, 287, "3) TABELA — escreve o que leste", fontsize=14, weight="bold", va="top")
    ax.text(12, 279, "Esperado = valor do modelo CAD (X na fita; Y já com +1 mm de tinta). "
            "Diferença > 2 mm → mede de novo.", fontsize=7, va="top", color=GREY)
    cols = [(12, 12), (24, 98), (122, 30), (152, 46)]
    head = ["#", "O quê", "Esperado", "Lido"]
    y = 272
    for (x0, w), h in zip(cols, head):
        ax.add_patch(Rectangle((x0, y - 6), w, 6, fc="#d5d8dc", ec=INK, lw=0.4))
        ax.text(x0 + 1.5, y - 3, h, fontsize=7.5, weight="bold", va="center")
    y -= 6
    rh = 5.55
    for r in rows:
        sec = r[0] == "" and r[2] == ""
        for (x0, w), cell in zip(cols, r):
            ax.add_patch(Rectangle((x0, y - rh), w, rh, fc="#f2f3f4" if sec else "white", ec=GREY, lw=0.3))
        if sec:
            ax.text(cols[1][0] + 1.5, y - rh / 2, r[1], fontsize=7, weight="bold", va="center")
        else:
            col = RED if r[0].startswith("X") else BLUE if r[0].startswith("Y") else INK
            ax.text(cols[0][0] + 1.5, y - rh / 2, r[0], fontsize=7, weight="bold", va="center", color=col)
            ax.text(cols[1][0] + 1.5, y - rh / 2, r[1], fontsize=6.8, va="center")
            ax.text(cols[2][0] + 1.5, y - rh / 2, r[2], fontsize=7, va="center", color=col)
        y -= rh
    pdf.savefig(fig); fig.savefig(HERE / "pagina3_tabela.png", dpi=170); plt.close(fig)


if __name__ == "__main__":
    g = G.modelo()
    xs, ys = pontos(g)
    with PdfPages(HERE / "esquema_medicao.pdf") as pdf:
        page_x(pdf, g, xs)
        page_y(pdf, g, ys)
        page_tabela(pdf, g, xs, ys)
    print("ok")
