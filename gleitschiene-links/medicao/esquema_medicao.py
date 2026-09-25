"""Folha de medição da Gleitschiene links (Backhus A50), gerada a partir do modelo CAD.

Esquema por PONTOS: cada parede (rasgos, degrau E, topo esquerda) mede-se em 2 pontos, cada
um com X (fita ao longo da aresta A, centro do F1 no 100) e Y (régua do esquadro, a partir de A).
Assim não interessa se as paredes estão ou não a 90°: com 2 pontos tira-se o ângulo.
Os valores "esperados" saem de ../cad/gleitschiene.py.
"""
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Circle, Rectangle

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "cad"))
import gleitschiene as G  # noqa: E402

ZERO = 100.0  # leitura da fita no centro do F1
RED, BLUE, GREEN, ORANGE, GREY, INK = "#c0392b", "#1f5fbf", "#1e8449", "#b9770e", "#8a8a8a", "#222222"


def pontos(g):
    rs = g["rasgos"]
    dE, _ = G.direcao(G.DEGRAU_INCL)
    dT, _ = G.direcao(G.TOPO_INCL)
    # --- pontos nas paredes: (descrição, (X, Y))
    ps = [("topo esquerda, em cima (3 mm abaixo do chanfro)", np.array(g["C2"]) + 3 * dT),
          ("topo esquerda, em baixo (10 mm acima do fundo do dedo)",
           np.array([G.topo_x(G.DEDO_Y - 10), G.DEDO_Y - 10]))]
    for nome in ("N1", "N2", "N3", "N4"):
        r = rs[nome]
        for lado, txt in (("E", "esquerda"), ("D", "direita")):
            folga = G.R_DEDO + 1 if (nome == "N1" and lado == "E") else G.R_PEQUENO + 1
            ps.append((f"{nome} parede {txt}, em cima (logo abaixo do arco)", r[lado + "_topo"] + 2 * r["d"]))
            ps.append((f"{nome} parede {txt}, em baixo (4 mm acima do canto)", r[lado + "_boca"] - folga * r["d"]))
    c_b, _ = G.bico_centro(g)
    ps.append(("degrau E, em cima (5 mm abaixo do patamar)", np.array(g["E"]) + 5 * dE))
    e0 = np.array(g["E"])
    t_tan = float(np.dot(c_b - e0, dE))             # tangente do arredondamento do bico no degrau
    ps.append(("degrau E, em baixo (logo acima do arredondamento do bico)", e0 + (t_tan - 3) * dE))
    ps = sorted(ps, key=lambda p: p[1][0])
    ps = [(f"P{i+1}", d, p) for i, (d, p) in enumerate(ps)]
    # --- só X (fita)
    bb = g["peca"].bounding_box()
    xs = [("X1", "fim do chanfro na aresta A", g["C1"][0], 0.0),
          ("X2", "F1 bordo esquerdo", -G.FURO_D / 2, G.FURO_Y),
          ("X3", "F1 bordo direito", G.FURO_D / 2, G.FURO_Y),
          ("X4", "bico B (ponto mais baixo)", c_b[0], G.BICO_Y),
          ("X5", "fim da peça (vértice V)", bb.max.X, 4.0)]
    # --- alturas com o paquímetro (Y modelo)
    c3 = 3.0
    bo = {k: rs[k] for k in rs}
    d1l, d1r = bo["N1"]["D_boca"], bo["N2"]["E_boca"]
    d2l, d2r = bo["N2"]["D_boca"], bo["N3"]["E_boca"]
    d3l, d3r = bo["N3"]["D_boca"], bo["N4"]["E_boca"]
    ys = [
        ("chanfro: quanto desce na topo", g["C2"][0] + 2, g["C2"][1]),
        ("altura total no dedo P", G.topo_x(G.DEDO_Y) + G.DEDO_LARG / 2, G.DEDO_Y),
        ("N1: da aresta A ao fundo do rasgo", rs["N1"]["c"][0], rs["N1"]["c"][1] - rs["N1"]["w"] / 2),
        ("D1 canto esquerdo (a 3 mm)", d1l[0] + c3, G.dentes_y(d1l[0] + c3)),
        ("F1: da aresta A ao bordo do furo", 0, G.FURO_Y - G.FURO_D / 2),
        ("D1 canto direito (a 3 mm)", d1r[0] - c3, G.dentes_y(d1r[0] - c3)),
        ("N2: da aresta A ao fundo do rasgo", rs["N2"]["c"][0], rs["N2"]["c"][1] - rs["N2"]["w"] / 2),
        ("D2 canto esquerdo (a 3 mm)", d2l[0] + c3, G.dentes_y(d2l[0] + c3)),
        ("D2 canto direito (a 3 mm)", d2r[0] - c3, G.dentes_y(d2r[0] - c3)),
        ("N3: da aresta A ao fundo do rasgo", rs["N3"]["c"][0], rs["N3"]["c"][1] - rs["N3"]["w"] / 2),
        ("D3 canto esquerdo (a 3 mm)", d3l[0] + c3, G.dentes_y(d3l[0] + c3)),
        ("D3 canto direito (a 3 mm)", d3r[0] - c3, G.dentes_y(d3r[0] - c3)),
        ("N4: da aresta A ao fundo do rasgo", rs["N4"]["c"][0], rs["N4"]["c"][1] - rs["N4"]["w"] / 2),
        ("patamar antes do degrau E", G.DEGRAU_X - 10, G.dentes_y(G.DEGRAU_X - 10)),
        ("F4: da aresta A ao bordo do furo", 3 * G.PASSO_FUROS, G.FURO_Y - G.FURO_D / 2),
    ]
    ys = [(f"Y{i+1}",) + p for i, p in enumerate(ys)]
    ws = []
    for i, nome in enumerate(("N1", "N2", "N3", "N4")):
        r = rs[nome]
        m = (r["E_topo"] + r["D_topo"]) / 2 + 4 * r["d"]
        ws.append((f"W{i+1}", f"{nome}: largura (bicos de dentro do paquímetro)", m, r["w"]))
    return ps, xs, ys, ws


def draw_part(ax, g):
    for e in g["corte2d"].edges():
        n = 50 if e.geom_type.name == "CIRCLE" else 2
        pts = np.array([tuple(e @ t)[:2] for t in np.linspace(0, 1, n)])
        ax.plot(pts[:, 0] + ZERO, pts[:, 1], color=INK, lw=1.2, zorder=3)
    for i, (x, y) in enumerate(g["furos"]):
        ax.add_patch(Circle((x + ZERO, y), G.CAIXA_D / 2, fc="none", ec=GREY, lw=0.8, ls="--", zorder=2))
        ax.text(x + ZERO, y + 19, f"F{i+1}", ha="center", fontsize=8, weight="bold", color=INK)
    for n, r in g["rasgos"].items():
        ax.text(r["c"][0] + ZERO, -r["c"][1] + 2, n, ha="center", va="center", fontsize=8, weight="bold")
    ax.text(160 + ZERO, -4, "aresta A (reta)", ha="center", va="top", fontsize=8, style="italic")


def bubble(ax, x, y, txt, col, fs=7):
    ax.text(x, y, txt, ha="center", va="center", fontsize=fs, color="white", weight="bold",
            bbox=dict(boxstyle="round,pad=0.22", fc=col, ec="none"), zorder=6)


def fita(ax, y0=10):
    ax.add_patch(Rectangle((0, y0), 575, 9, fc="#f7dc6f", ec="#b7950b", lw=0.8, zorder=3))
    for t in range(0, 571, 10):
        h = 5 if t % 50 == 0 else 2.5
        ax.plot([t, t], [y0, y0 + h], color="#7d6608", lw=0.6, zorder=4)
        if t % 50 == 0:
            ax.text(t, y0 + 6.2, str(t), fontsize=5.5, ha="center", color="#7d6608", zorder=4)
    ax.annotate("F1 no 100", (ZERO, y0 + 9), (ZERO + 18, y0 + 17), fontsize=7, color="#7d6608", weight="bold",
                arrowprops=dict(arrowstyle="->", color="#7d6608", lw=0.8))


def page_pontos(pdf, g, ps, xs):
    fig, ax = plt.subplots(figsize=(11.69, 8.27))
    fig.subplots_adjust(left=0.01, right=0.99, top=0.92, bottom=0.01)
    ax.set_aspect("equal"); ax.axis("off")
    fig.suptitle("1) PONTOS: X na fita + Y na régua do esquadro (2 pontos por parede)", fontsize=13.5,
                 weight="bold", x=0.02, ha="left", y=0.97)
    draw_part(ax, g)
    fita(ax)
    lvl = [24, 38, 52, 66]
    for i, (lab, desc, p) in enumerate(ps):
        X, Y = p[0] + ZERO, p[1]
        ytop = 22 + lvl[i % 4]
        ax.plot([X, X], [-Y, ytop - 4], color=RED, lw=0.5, ls=(0, (2, 2)), zorder=5)
        ax.plot(X, -Y, "o", color=RED, ms=3.2, zorder=6)
        bubble(ax, X, ytop, lab, RED)
    for lab, desc, x, y in xs:
        X = x + ZERO
        ax.plot([X, X], [-y, 20], color=ORANGE, lw=0.5, ls=(0, (1, 2)), zorder=5)
        ax.plot(X, -y, "s", color=ORANGE, ms=3, zorder=6)
        bubble(ax, X, -y - 7 if y > 100 else -y + 7 if y < 10 else -y - 7, lab, ORANGE, fs=6.3)
    txt = ("COMO\n"
           "1. Fita presa ao longo da aresta A com o centro do F1 no 100 (como antes).\n"
           "2. ANTES: encosta o esquadro à aresta A e escreve a leitura da régua do esquadro na própria aresta A  →  RA = ____\n"
           "3. Para cada ponto P: base do esquadro na aresta A; desliza até a régua do esquadro passar EXATAMENTE no ponto.\n"
           "   Escreve 2 leituras: X na fita e R na régua do esquadro. (Y = distância entre R e RA — faço eu as contas.)\n"
           "4. Cada parede tem 2 pontos: 'em cima' (logo abaixo do arco) e 'em baixo' (4 mm acima do canto do dente).\n"
           "   A régua do esquadro só toca a parede no ponto — é normal, é assim que se mede o ângulo.\n"
           "5. Quadrados laranja (X1–X5): só a leitura da fita.")
    ax.text(0, -190, txt, fontsize=7.3, va="top", ha="left", color=INK, linespacing=1.5,
            bbox=dict(boxstyle="round,pad=0.5", fc="#fdf2e9", ec=RED, lw=0.8))
    # diagnóstico: folga numa ponta vs nas duas
    bx, by = 470, -196
    ax.text(bx + 45, by + 4, "Parede inclinada ou arredondamento?", fontsize=6.8, weight="bold", ha="center")
    for k, (tit, incl) in enumerate((("folga SÓ numa ponta\n= parede inclinada", True),
                                     ("folga nas DUAS pontas\n= arredondamentos (normal)", False))):
        x0 = bx + k * 55
        ax.add_patch(Rectangle((x0 + 20, by - 50), 5, 48, fc="#aab7b8", ec=INK, lw=0.6))  # régua esquadro
        if incl:
            ax.plot([x0 + 25.3, x0 + 31], [by - 6, by - 46], color=INK, lw=1.6)
        else:
            t = np.linspace(0, 1, 30)
            ax.plot(x0 + 25.3 + 5 * (np.abs(t - 0.5) * 2) ** 3, by - 6 - 40 * t, color=INK, lw=1.6)
        ax.text(x0 + 25, by - 58, tit, fontsize=5.8, ha="center", va="top")
    ax.set_xlim(-5, 580); ax.set_ylim(-270, 95)
    pdf.savefig(fig); fig.savefig(HERE / "pagina1_pontos.png", dpi=170); plt.close(fig)


def page_y(pdf, g, ys, ws):
    fig, ax = plt.subplots(figsize=(11.69, 8.27))
    fig.subplots_adjust(left=0.01, right=0.99, top=0.92, bottom=0.01)
    ax.set_aspect("equal"); ax.axis("off")
    fig.suptitle("2) ALTURAS e LARGURAS com o paquímetro", fontsize=14, weight="bold", x=0.02, ha="left", y=0.97)
    draw_part(ax, g)
    for i, (lab, desc, x, y) in enumerate(ys):
        X = x + ZERO
        ax.annotate("", (X, -y), (X, 0), arrowprops=dict(arrowstyle="<->", color=BLUE, lw=0.9,
                                                         shrinkA=0, shrinkB=0), zorder=5)
        yl = 14 + (i % 3) * 16
        ax.plot([X, X], [0, yl - 5], color=BLUE, lw=0.6, ls=(0, (2, 2)))
        bubble(ax, X, yl, lab, BLUE, fs=7.5)
    for lab, desc, m, w in ws:
        r = [v for v in g["rasgos"].values() if abs(v["w"] - w) < 1e-6 and np.allclose((v["E_topo"] + v["D_topo"]) / 2 + 4 * v["d"], m)][0]
        a, b = m - w / 2 * r["n"], m + w / 2 * r["n"]
        ax.annotate("", (a[0] + ZERO, -a[1]), (b[0] + ZERO, -b[1]),
                    arrowprops=dict(arrowstyle="<->", color=GREEN, lw=1.0, shrinkA=0, shrinkB=0), zorder=5)
        bubble(ax, m[0] + ZERO, -m[1] - 8, lab, GREEN, fs=7)
    txt = ("COMO\n"
           "• Y (azul): um bico do paquímetro na aresta A e o outro no ponto, sempre a 90° da aresta A.\n"
           "   Dentes: a ~3 mm do canto.  Rasgos (Y3, Y7, Y10, Y13): o bico entra e encosta no fundo do arco.\n"
           "   Furos (Y5, Y15): da aresta A ao bordo mais próximo, do lado SEM caixa.\n"
           "• W (verde): largura de cada rasgo com os bicos de DENTRO, perto da boca, a 90° das paredes.\n"
           "• Escreve só o que leres (com tinta). A correção da tinta faço eu.")
    ax.text(0, -190, txt, fontsize=7.6, va="top", ha="left", color=INK, linespacing=1.5,
            bbox=dict(boxstyle="round,pad=0.5", fc="#eaf2fb", ec=BLUE, lw=0.8))
    ax.set_xlim(-5, 580); ax.set_ylim(-270, 70)
    pdf.savefig(fig); fig.savefig(HERE / "pagina2_alturas_larguras.png", dpi=170); plt.close(fig)


def tabela(pdf, titulo, sub, head, cols, rows, png):
    fig = plt.figure(figsize=(8.27, 11.69))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 210); ax.set_ylim(0, 297); ax.axis("off")
    ax.text(12, 287, titulo, fontsize=14, weight="bold", va="top")
    ax.text(12, 279.5, sub, fontsize=7, va="top", color=GREY)
    y = 272
    for (x0, w), h in zip(cols, head):
        ax.add_patch(Rectangle((x0, y - 6), w, 6, fc="#d5d8dc", ec=INK, lw=0.4))
        ax.text(x0 + 1.2, y - 3, h, fontsize=7, weight="bold", va="center")
    y -= 6
    rh = 7.0 if len(rows) < 34 else 6.0
    for r in rows:
        sec = all(c == "" for i, c in enumerate(r) if i != 1) and r[0] == ""
        for (x0, w), cell in zip(cols, r):
            ax.add_patch(Rectangle((x0, y - rh), w, rh, fc="#f2f3f4" if sec else "white", ec=GREY, lw=0.3))
        if sec:
            ax.text(cols[1][0] + 1.2, y - rh / 2, r[1], fontsize=7, weight="bold", va="center")
        else:
            col = {"P": RED, "X": ORANGE, "Y": BLUE, "W": GREEN}.get(r[0][:1], INK)
            for j, ((x0, w), cell) in enumerate(zip(cols, r)):
                ax.text(x0 + 1.2, y - rh / 2, cell, fontsize=6.6 if j == 1 else 7, va="center",
                        color=col if j != 1 else INK, weight="bold" if j == 0 else "normal")
        y -= rh
    pdf.savefig(fig); fig.savefig(HERE / png, dpi=170); plt.close(fig)


if __name__ == "__main__":
    g = G.modelo()
    ps, xs, ys, ws = pontos(g)
    bb = g["peca"].bounding_box()
    rows1 = [("", "RA = leitura da régua do esquadro na aresta A", "", "", "", "")]
    rows1 += [("", "PONTOS NAS PAREDES", "", "", "", "")]
    rows1 += [(lab, desc, f"{p[0] + ZERO:.0f}", f"{p[1]:.0f}", "", "") for lab, desc, p in ps]
    rows1 += [("", "SÓ FITA", "", "", "", "")]
    rows1 += [(lab, desc, f"{x + ZERO:.0f}", "", "", "") for lab, desc, x, _ in xs]
    rows2 = [("", "ALTURAS (paquímetro, com tinta)", "", "")]
    rows2 += [(lab, desc, f"{y + 1:.0f}", "") for lab, desc, _, y in ys]
    rows2 += [("", "LARGURAS DOS RASGOS (bicos de dentro, com tinta)", "", "")]
    rows2 += [(lab, desc, f"{w - 1:.1f}", "") for lab, desc, _, w in ws]
    rows2 += [("", "RAIOS (moeda que encaixa no canto)", "", "")]
    rows2 += [("R1", "vértice V", f"R{G.R_VERTICE:g}", ""), ("R2", "bico B", f"R{g['R_BICO']:.0f}", ""),
              ("R3", "cantos de fora dos dentes / patamar", f"R{G.R_PEQUENO:g}", ""),
              ("R4", "cantos de dentro (degrau E, patamar)", f"R{G.R_PEQUENO:g}", ""),
              ("R5", "cantos do chanfro C", f"R{G.R_PEQUENO:g}", ""), ("R6", "ponta do dedo P", f"R{G.R_DEDO:g}", "")]
    rows2 += [("", "OUTROS", "", "")]
    rows2 += [("L", "comprimento total (de ponta a ponta)", f"{bb.max.X - bb.min.X + 1:.0f}", ""),
              ("Q2", "parafuso: rosca / Ø cabeça / altura / norma", "M16 / ≤26 / ? / ?", ""),
              ("Q3", "a cabeça entra toda na caixa Ø26.5?", "sim", ""),
              ("Q4", "lima: escorrega (Hardox) ou morde (S355)?", "?", ""),
              ("Q5", "peso na balança", f"≈{g['peca'].volume * 7.85e-6 + 0.15:.1f} kg", "")]
    with PdfPages(HERE / "esquema_medicao.pdf") as pdf:
        page_pontos(pdf, g, ps, xs)
        page_y(pdf, g, ys, ws)
        tabela(pdf, "3) TABELA — pontos (fita + esquadro)",
               "Esperado = modelo atual, com as paredes ainda a 90°. Nas paredes, diferenças de alguns mm no X são o que queremos medir.",
               ["#", "O quê", "X esp.", "Y esp.", "X lido (fita)", "R lido (esquadro)"],
               [(12, 11), (23, 85), (108, 14), (122, 14), (136, 31), (167, 31)], rows1, "pagina3_tabela_pontos.png")
        tabela(pdf, "4) TABELA — paquímetro, raios e outros",
               "Esperado = modelo atual, já com a tinta (Y +1 mm; larguras −1 mm). Diferença > 2 mm → mede de novo.",
               ["#", "O quê", "Esperado", "Lido"], [(12, 12), (24, 98), (122, 30), (152, 46)], rows2,
               "pagina4_tabela_paquimetro.png")
    for old in ("pagina1_posicoes_X.png", "pagina2_alturas_Y.png", "pagina3_tabela.png"):
        (HERE / old).unlink(missing_ok=True)
    print("ok")
