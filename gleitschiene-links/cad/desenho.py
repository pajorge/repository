"""Desenho A3 (escala 1:2) e vista 3D da Gleitschiene links, a partir de gleitschiene.py."""
import sys
from datetime import date
from math import radians, tan
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly, Rectangle
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gleitschiene as G  # noqa: E402

OUT = G.OUT
S = 0.5                    # escala 1:2
OX, OY = 85.6, 238.0       # posição no papel (mm) do ponto X=0 (F1) na aresta A
INK, THIN, RED, BLUE = "#111111", "#555555", "#c0392b", "#1f5fbf"


def P(x, y):
    """Coordenadas da peça (X, Y para dentro) -> papel."""
    return OX + x * S, OY - y * S


def edges_xy(face):
    out = []
    for e in face.edges():
        n = 40 if e.geom_type.name == "CIRCLE" else 2
        pts = np.array([tuple(e @ t)[:2] for t in np.linspace(0, 1, n)])
        out.append(np.column_stack([OX + pts[:, 0] * S, OY + pts[:, 1] * S]))
    return out


def arrow(ax, a, b, lw=0.35):
    ax.annotate("", xy=a, xytext=b, arrowprops=dict(arrowstyle="<|-|>", lw=lw, color=INK, mutation_scale=5,
                                                   shrinkA=0, shrinkB=0))


def hdim(ax, x1, x2, y, txt, ya=None, yb=None, star=False, fs=6.5):
    for x, yf in ((x1, ya), (x2, yb)):
        if yf is not None:
            ax.plot([x, x], [yf + (1 if y > yf else -1), y + (1.2 if y > yf else -1.2)], color=THIN, lw=0.25)
    arrow(ax, (x1, y), (x2, y))
    ax.text((x1 + x2) / 2, y + 0.6, txt + ("*" if star else ""), ha="center", va="bottom", fontsize=fs,
            color=RED if star else INK)


def vdim(ax, y1, y2, x, txt, xa=None, xb=None, star=False, fs=6.5):
    for yy, xf in ((y1, xa), (y2, xb)):
        if xf is not None:
            ax.plot([xf + (1 if x > xf else -1), x + (1.2 if x > xf else -1.2)], [yy, yy], color=THIN, lw=0.25)
    arrow(ax, (x, y1), (x, y2))
    ax.text(x - 0.6, (y1 + y2) / 2, txt + ("*" if star else ""), ha="right", va="center", rotation=90,
            fontsize=fs, color=RED if star else INK)


def leader(ax, pt, txt_pt, txt, color=INK, fs=6.3, ha="left"):
    ax.annotate(txt, xy=pt, xytext=txt_pt, fontsize=fs, color=color, ha=ha, va="center",
                arrowprops=dict(arrowstyle="-|>", lw=0.35, color=color, mutation_scale=5, shrinkA=1, shrinkB=0))


def bico_info(g):
    bx, by = g["B_vivo"]; vx, _ = g["V_vivo"]; r = g["R_BICO"]
    u1 = np.array([0.0, -1.0]); u2 = np.array([vx - bx, -by]); u2 /= np.linalg.norm(u2)
    half = np.arccos(np.dot(u1, u2)) / 2
    bis = (u1 + u2) / np.linalg.norm(u1 + u2)
    c = np.array([bx, by]) + bis * r / np.sin(half)
    ang_hip = np.degrees(np.arctan2(by, vx - bx))
    return c, ang_hip


def desenho(g):
    fig = plt.figure(figsize=(420 / 25.4, 297 / 25.4))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 420); ax.set_ylim(0, 297); ax.axis("off")
    ax.add_patch(Rectangle((10, 10), 400, 277, fill=False, lw=0.8, ec=INK))

    # --- vista principal
    for xy in edges_xy(g["corte2d"]):
        ax.plot(xy[:, 0], xy[:, 1], color=INK, lw=0.7)
    for x, y in g["furos"]:
        cx, cy = OX + x * S, OY + y * S
        t = np.linspace(0, 2 * np.pi, 80)
        ax.plot(cx + G.CAIXA_D / 2 * S * np.cos(t), cy + G.CAIXA_D / 2 * S * np.sin(t), color=INK, lw=0.5)
        ax.plot([cx - 9, cx + 9], [cy, cy], color=THIN, lw=0.25, ls=(0, (6, 2, 1, 2)))
        ax.plot([cx, cx], [cy - 9, cy + 9], color=THIN, lw=0.25, ls=(0, (6, 2, 1, 2)))
    for nome, cx, w, yf in G.RASGOS:
        px, py = P(cx, yf + w / 2 + 3)
        ax.text(px, py, nome, ha="center", va="center", fontsize=6, color=THIN)

    ya = OY
    fx = [OX + x * S for x, _ in g["furos"]]
    fy = OY - G.FURO_Y * S
    # passo dos furos
    for a, b in zip(fx[:-1], fx[1:]):
        hdim(ax, a, b, ya + 10, f"{G.PASSO_FUROS:g}", ya=fy, yb=fy)
    # F1 -> topo esquerda (à altura do furo)
    xt, _ = P(-G.F1_A_TOPO, 0)
    hdim(ax, xt, fx[0], ya + 18, f"{G.F1_A_TOPO:g}", ya=fy, yb=fy)
    # comprimento total
    bb = g["peca"].bounding_box()
    hdim(ax, OX + bb.min.X * S, OX + bb.max.X * S, 140, f"{bb.max.X - bb.min.X:.1f}", ya=ya - 17, yb=ya,
         star=True)
    ax.texts[-1].set_va("top"); ax.texts[-1].set_y(139)
    # chanfro
    c1x, _ = P(*g["C1"]); c2x, c2y = P(*g["C2"])
    hdim(ax, c2x, c1x, ya + 4, f"{G.CHANFRO_X:g}", ya=c2y, yb=ya, star=True, fs=5.8)
    vdim(ax, ya, c2y, 30, f"{G.CHANFRO_Y:g}", xa=c1x, xb=c2x, star=True, fs=5.8)
    # altura no dedo
    dx, dy = P(g["x_dedo_ext"], G.DEDO_Y)
    vdim(ax, ya, dy, 22, f"{G.DEDO_Y:g}", xa=c1x, xb=dx)
    # furos a 50 de A
    vdim(ax, ya, fy, fx[0] + 12, f"{G.FURO_Y:g}", xa=None, xb=fx[0], star=True)
    # altura total no bico
    c, ang_hip = bico_info(g)
    bxp, byp = P(c[0], G.BICO_Y)
    vdim(ax, ya, byp, OX + bb.max.X * S + 10, f"{G.BICO_Y:g}", xa=OX + bb.max.X * S - 4, xb=bxp)
    # cotas do degrau
    ex, ey = P(*g["E"])
    hdim(ax, fx[0], ex, byp - 8, f"{G.DEGRAU_X:g}", ya=fy, yb=ey, star=True)

    # chamadas
    leader(ax, (fx[1] + 4, fy + 4), (fx[1] + 30, ya + 27),
           f"4× Ø{G.FURO_D:g} passante (M16)\ncaixa Ø{G.CAIXA_D:g} × {G.CAIXA_H:g} prof. + escareado {G.ESCAREADO_ANG:g}°\n(ver corte A-A; lado da etiqueta)")
    rb = g["R_BICO"]
    leader(ax, (bxp + 3, byp + 2), (bxp + 22, byp + 6), f"R{rb:.1f}*", RED)
    vx = OX + bb.max.X * S
    leader(ax, (vx - 1.5, ya - 1.5), (vx - 22, ya + 7), f"R{G.R_VERTICE:g}*", RED)
    hx, hy = P(g["V_vivo"][0] - 60, 60 * tan(radians(ang_hip)))
    ax.text(hx + 6, hy - 2, f"{ang_hip:.1f}°* com A", fontsize=6.3, color=RED)
    d3a = G.RASGOS[2][1] + G.RASGOS[2][2] / 2; d3b = G.RASGOS[3][1] - G.RASGOS[3][2] / 2
    x1, y1 = P(d3a, G.dentes_y(d3a)); x2, y2 = P(d3b, G.dentes_y(d3b))
    hdim(ax, x1, x2, y2 - 16, f"{d3b - d3a:.1f}", ya=y1, yb=y2, fs=5.8)
    n4 = G.RASGOS[3]
    nx1, ny = P(n4[1] - n4[2] / 2, n4[3] + n4[2] / 2); nx2, _ = P(n4[1] + n4[2] / 2, 0)
    leader(ax, (nx1 + 2, ny - 3), (nx1 - 26, ny - 30), f"4× rasgo, fundo R = largura/2\nN2–N4 largura {n4[2]:g}   N1 {G.RASGOS[0][2]:g}*", fs=6)
    leader(ax, P(G.DENTES_X0 + 40, G.dentes_y(G.DENTES_X0 + 40)), (28, 160),
           f"face dos dentes a {G.DENTES_INCL:g}°* da aresta A\npassa em X{G.DENTES_X0:g} / Y{G.DENTES_Y0:g}", RED, fs=6)
    ax.text(P(150, 0)[0], ya + 1.2, "A (aresta de referência)", fontsize=6, style="italic", ha="center", va="bottom")
    # linha de corte A-A por F1
    ax.plot([fx[0], fx[0]], [ya + 3, fy - 14], color=THIN, lw=0.35, ls=(0, (8, 2, 1, 2)))
    for yy in (ya + 3, fy - 14):
        ax.text(fx[0] + 1.5, yy, "A", fontsize=7, weight="bold", va="center")

    # --- corte A-A (2:1)
    cxp, cyp = 372, 226
    k = 2.0; t = G.ESPESSURA; hc = g["cone_h"]; hw = 16
    for sg in (-1, 1):
        prof = [(sg * hw, 0), (sg * G.CAIXA_D / 2, 0), (sg * G.CAIXA_D / 2, -G.CAIXA_H),
                (sg * G.FURO_D / 2, -G.CAIXA_H - hc), (sg * G.FURO_D / 2, -t), (sg * hw, -t)]
        ax.add_patch(MPoly([(cxp + x * k, cyp + y * k) for x, y in prof], closed=True, fc="#e5e7e9", ec=INK,
                           lw=0.6, hatch="////"))
    ax.plot([cxp, cxp], [cyp + 4, cyp - t * k - 4], color=THIN, lw=0.3, ls=(0, (8, 2, 1, 2)))
    hdim(ax, cxp - G.CAIXA_D, cxp + G.CAIXA_D, cyp + 4, f"Ø{G.CAIXA_D:g}", ya=cyp, yb=cyp, fs=6)
    hdim(ax, cxp - G.FURO_D, cxp + G.FURO_D, cyp - t * k - 5, f"Ø{G.FURO_D:g}", ya=cyp - t * k, yb=cyp - t * k, fs=6)
    ax.texts[-1].set_va("top"); ax.texts[-1].set_y(cyp - t * k - 6)
    vdim(ax, cyp, cyp - G.CAIXA_H * k, cxp + 18, f"{G.CAIXA_H:g}", fs=6)
    vdim(ax, cyp, cyp - t * k, cxp - 7, f"{t:g}", fs=6)
    ax.text(cxp + G.FURO_D + 1, cyp - (G.CAIXA_H + hc / 2) * k - 1, f"{G.ESCAREADO_ANG:g}°", ha="left",
            va="center", fontsize=6.5)
    ax.text(cxp, cyp + 14, "CORTE A-A (2:1)", ha="center", fontsize=8, weight="bold")
    ax.text(cxp, cyp - t * k - 14, f"cabeça do parafuso {G.CAIXA_H:g} mm\nabaixo da face", ha="center",
            fontsize=5.8, style="italic", va="top")

    # --- tabela de coordenadas
    rows = [("Elemento", "X (de F1)", "Y (de A)", "Notas")]
    rows.append(("Furos F1–F4", "0 / 105 / 210 / 315", f"{G.FURO_Y:g}*", "Ø17 + caixa Ø26.5×7 + 90°"))
    rows.append(("Topo esquerda", f"−{G.F1_A_TOPO:g} (à altura dos furos)", "", f"inclinada {G.TOPO_INCL:g}°*"))
    rows.append(("Chanfro C", f"{g['C2'][0]:.1f} → {g['C1'][0]:.1f}", f"{G.CHANFRO_Y:g} → 0", f"catetos {G.CHANFRO_X:g} × {G.CHANFRO_Y:g}*  (≈55)"))
    rows.append(("Dedo P", f"{g['x_dedo_ext']:.1f} … {g['x_dedo_ext'] + G.DEDO_LARG:.1f}", f"{G.DEDO_Y:g}", f"largura {G.DEDO_LARG:g}, R{G.R_DEDO:g}"))
    for nome, cx, w, yf in G.RASGOS:
        st = "" if nome == "N4" else "*"
        rows.append((f"Rasgo {nome}", f"{cx:g}{'*' if nome != 'N4' else '*'}", f"fundo {yf:g}{st}", f"largura {w:g}{'*' if nome == 'N1' else ''}, R{w/2:g}"))
    rows.append(("Linha dos dentes", f"passa em {G.DENTES_X0:g}", f"{G.DENTES_Y0:g}", f"{G.DENTES_INCL:g}° com A*"))
    rows.append(("Degrau E", f"{G.DEGRAU_X:g}*", f"{g['E'][1]:.1f} → bico", f"canto interior R{G.R_PEQUENO:g}*"))
    rows.append(("Bico B (ponto + baixo)", f"{c[0]:.1f}", f"{G.BICO_Y:g}", f"R{g['R_BICO']:.1f}*  (de 173, 128, 250)"))
    rows.append(("Vértice V (ponta)", f"{bb.max.X:.1f}", "0", f"R{G.R_VERTICE:g}*;  hipotenusa {ang_hip:.1f}°"))
    rows.append(("Cantos dos dentes/chanfro", "", "", f"R{G.R_PEQUENO:g}*"))
    x0, y0, wcol = 15, 124, [42, 50, 28, 78]
    ax.text(x0, y0 + 4, "COORDENADAS (mm, aço sem tinta)   * = do traçado em papel, CONFIRMAR", fontsize=7,
            weight="bold")
    for i, r in enumerate(rows):
        yy = y0 - i * 6.2
        xx = x0
        for j, cell in enumerate(r):
            ax.add_patch(Rectangle((xx, yy - 5.2), wcol[j], 6.2, fill=i == 0, fc="#eaecee", ec=THIN, lw=0.3))
            ax.text(xx + 1.2, yy - 2.1, cell, fontsize=5.9, va="center",
                    color=RED if "*" in cell else INK, weight="bold" if i == 0 else "normal")
            xx += wcol[j]

    # --- notas
    notas = ("NOTAS\n"
             "1. PRELIMINAR – não fabricar sem confirmar as cotas com *.\n"
             "2. Cotas em aço sem tinta. Tolerâncias gerais ISO 2768-m. Quebrar arestas vivas.\n"
             "3. Corte pelo DXF gleitschiene_links.dxf (camada CORTE, 1:1). Caixas e escareados maquinados.\n"
             "4. Caixas na face da etiqueta (vista representada). Peça direita (rechts) = simétrica.\n"
             f"5. Parafuso M16: confirmar que a cabeça cabe na caixa Ø{G.CAIXA_D:g} (DIN 7991 M16 tem Ø30).\n"
             "6. Ref. Backhus 25.12.17P-1545-7040 'Gleitschiene links'.")
    ax.text(230, 128, notas, fontsize=6.2, va="top", linespacing=1.55)

    # --- legenda (formato do desenho do veio)
    X0, Y0 = 230, 12
    def box(x, y, w, h, fill=False):
        ax.add_patch(Rectangle((X0 + x, Y0 + y), w, h, fill=fill, fc="#f4f6f7", ec=INK, lw=0.4))
    def txt(x, y, s, fs=5.5, **kw):
        ax.text(X0 + x, Y0 + y, s, fontsize=fs, **kw)
    box(0, 0, 178, 58)
    box(0, 0, 44, 58)
    txt(1.5, 55, "SALVO INDICAÇÃO EM CONTRÁRIO,\nCOTAS EM MILÍMETROS", 4.6, va="top")
    txt(1.5, 45, "TOLERÂNCIAS: ISO 2768-m", 4.6)
    txt(1.5, 38, "ACABAMENTO SUPERFICIAL", 4.6)
    box(0, 20, 44, 7); txt(3, 22.5, "NÃO MEDIR NO DESENHO", 5)
    box(0, 12, 44, 8); txt(2, 15.5, "QUEBRAR ARESTAS VIVAS\nE REMOVER REBARBAS", 4.4, va="center")
    box(0, 0, 44, 12); txt(2, 9, "1.º DIEDRO (EUROPEU)", 4.6)
    ax.add_patch(Rectangle((X0 + 8, Y0 + 2), 7, 4.5, fill=False, lw=0.4))
    ax.add_patch(plt.Circle((X0 + 25, Y0 + 4.2), 2.4, fill=False, lw=0.4))
    ax.add_patch(plt.Circle((X0 + 25, Y0 + 4.2), 1.1, fill=False, lw=0.4))
    # nomes
    for i, (lab, val) in enumerate([("", ""), ("DESENHADO", ""), ("VERIFICADO", ""), ("APROVADO", "")]):
        yy = 51 - i * 6
        box(44, yy, 16, 6); box(60, yy, 18, 6); box(78, yy, 14, 6); box(92, yy, 14, 6)
        txt(45, yy + 2, lab, 4.3)
    txt(62, 53, "NOME", 4.5); txt(79, 53, "ASSIN.", 4.5); txt(94, 53, "DATA", 4.5)
    txt(93, 47, date.today().isoformat(), 4.2)
    box(44, 0, 30, 33); box(74, 0, 32, 33)
    txt(45, 29, "MATERIAL", 4.5); txt(75, 29, "ACABAMENTO", 4.5)
    txt(59, 20, "Chapa aço S355J2\n15 mm\n(confirmar:\nHardox?)", 5.2, ha="center", va="center")
    txt(90, 20, "Pintado\n(tinta 0.5 mm)", 5.5, ha="center", va="center")
    box(106, 45, 72, 13); txt(142, 51.5, "Valorsul - ETVO", 10, ha="center", va="center")
    box(106, 20, 72, 25); txt(107, 42, "TÍTULO", 4.5)
    txt(142, 30, "Calha deslizante esquerda\n(Gleitschiene links)\nCharrua Backhus A50", 7.2,
        ha="center", va="center")
    box(106, 7, 14, 13); txt(107, 17, "FORMATO", 4); txt(113, 11, "A3", 9, ha="center", va="center")
    box(120, 7, 44, 13); txt(121, 17, "DES. N.º", 4); txt(142, 11, "2", 9, ha="center", va="center")
    box(164, 7, 14, 13); txt(165, 17, "REV", 4); txt(171, 11, "A", 9, ha="center", va="center")
    box(106, 0, 20, 7); txt(107, 2.2, "ESCALA 1:2", 4.6)
    box(126, 0, 28, 7); txt(127, 2.2, f"PESO {g['peca'].volume * 7.85e-6:.2f} kg", 4.6)
    box(154, 0, 24, 7); txt(155, 2.2, "FOLHA 1 de 1", 4.6)

    ax.text(210, 283, "PRELIMINAR — cotas com * a confirmar", fontsize=13, color=RED, alpha=0.8,
            ha="center", va="top", weight="bold")
    fig.savefig(OUT / "desenho_gleitschiene_links.pdf")
    fig.savefig(OUT / "desenho_gleitschiene_links.png", dpi=160)
    plt.close(fig)


def vista_3d(g):
    verts, tris = g["peca"].tessellate(0.15, 0.3)
    V = np.array([tuple(v) for v in verts]); Tr = np.array(tris)
    tri = V[Tr]
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    light = np.array([0.35, -0.5, 0.8]); light /= np.linalg.norm(light)
    shade = 0.45 + 0.55 * np.clip(np.abs(n @ light), 0, 1)
    base = np.array([0.68, 0.72, 0.78])
    cols = np.clip(base[None, :] * shade[:, None], 0, 1)
    fig = plt.figure(figsize=(12, 6))
    ax = fig.add_subplot(111, projection="3d")
    ax.add_collection3d(Poly3DCollection(tri, facecolors=cols, edgecolors="none"))
    for e in g["peca"].edges():
        n = 48 if e.geom_type.name == "CIRCLE" else 2
        pts = np.array([tuple(e @ t) for t in np.linspace(0, 1, n)])
        ax.plot(pts[:, 0], pts[:, 1], pts[:, 2], color="#2c3e50", lw=0.5)
    ax.set_xlim(V[:, 0].min(), V[:, 0].max()); ax.set_ylim(V[:, 1].min(), V[:, 1].max())
    ax.set_zlim(-5, 20)
    ax.set_box_aspect((np.ptp(V[:, 0]), np.ptp(V[:, 1]), 25))
    ax.view_init(elev=52, azim=-95)
    ax.axis("off")
    ax.set_title("Gleitschiene links — modelo preliminar (vista 3D)", fontsize=12)
    fig.savefig(OUT / "preview_3d.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    g = G.modelo()
    G.exportar(g)
    desenho(g)
    vista_3d(g)
    print("ok")
