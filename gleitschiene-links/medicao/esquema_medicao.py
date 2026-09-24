"""Esquema de medição da Gleitschiene links (Backhus A50).

Geometria aproximada, digitalizada da folha traçada a 1:1 (escala calibrada
pelo passo de 105 mm entre furos). Serve só para orientar as medições.
Coordenadas: X ao longo da aresta A, 0 na topo esquerda; Y perpendicular a A,
0 na aresta A, positivo para dentro da peça.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle, Polygon

OX = 90.0  # centro do F1 a 90 mm da topo esquerda (medido)

def arc(cx, cy, r, a0, a1, n=24):
    a = np.radians(np.linspace(a0, a1, n))
    return list(zip(cx + r*np.cos(a), cy + r*np.sin(a)))

def outline():
    """Contorno em coordenadas de desenho (x = X, y = -Y)."""
    P = [(-52.6, 0), (441, 0)]
    P += arc(441, -11, 11, 90, -39.8)                 # vértice V
    P += arc(314.6, -163.3, 10, -39.7, -180)          # bico B
    P += [(304.6, -63.6), (281.3, -65)]               # degrau E + patamar
    def notch(xr, xl, ybot, yr, yl):
        r = (xr - xl)/2; cx = (xr + xl)/2; cy = -(ybot + r)
        return [(xr, -yr), (xr, cy)] + arc(cx, cy, r, 0, 180) + [(xl, cy), (xl, -yl)]
    P += notch(281.3, 244.2, 36.5, 65, 70.7)          # N4
    P += notch(178.6, 140.8, 51.3, 81.6, 89.5)        # N3
    P += notch(75.3, 36.0, 65.2, 96.5, 100.7)         # N2
    P += notch(-27.4, -68.1, 79.0, 109.7, 109.3)      # N1
    P += arc(-76.4, -109.3, 8.3, 0, -180)             # dedo P
    P += [(-84.7, -108.9), (-92.9, -33.7), (-52.6, 0)]
    return np.array([(x + OX, y) for x, y in P])

HOLES = [(0, 50), (105, 50), (210, 50), (315, 50)]
RED, BLUE, GREEN, GREY, INK = "#c0392b", "#1f5fbf", "#1e8449", "#8a8a8a", "#222222"

def draw_part(ax, alpha=1.0):
    o = outline()
    ax.add_patch(Polygon(o, closed=True, fc="#eef1f4", ec=INK, lw=1.4, alpha=alpha, zorder=1))
    for i, (hx, hy) in enumerate(HOLES):
        ax.add_patch(Circle((hx + OX, -hy), 8.5, fc="white", ec=INK, lw=1.1, zorder=2))
        ax.add_patch(Circle((hx + OX, -hy), 14, fc="none", ec=GREY, lw=0.8, ls="--", zorder=2))
        ax.text(hx + OX, -hy + 19, f"F{i+1}", ha="center", va="center", fontsize=8, color=INK, weight="bold")
    for name, x, y in [("N1", -47.8, 90), ("N2", 55.7, 76), ("N3", 159.7, 62), ("N4", 262.8, 48)]:
        ax.text(x + OX, -y, name, ha="center", va="center", fontsize=8, color=INK, weight="bold")
    for name, x, y in [("D1", 5, 117), ("D2", 108, 104), ("D3", 211, 89)]:
        ax.text(x + OX, -y, name, ha="center", va="center", fontsize=8, color=GREY, weight="bold")
    ax.text(150 + OX, -4, "aresta A (reta)", ha="center", va="top", fontsize=8, color=INK, style="italic")
    ax.text(-76 + OX, -128, "P", ha="center", fontsize=8, weight="bold")
    ax.text(292 + OX, -120, "E", ha="center", fontsize=8, weight="bold")
    ax.text(318 + OX, -184, "B", ha="center", fontsize=8, weight="bold")
    ax.text(463 + OX, -8, "V", ha="center", fontsize=8, weight="bold")
    ax.text(-82 + OX, -12, "C", ha="center", fontsize=8, weight="bold")

def bubble(ax, x, y, txt, col, fs=7.5):
    ax.text(x, y, txt, ha="center", va="center", fontsize=fs, color="white", weight="bold",
            bbox=dict(boxstyle="round,pad=0.25", fc=col, ec="none"), zorder=6)

def page_x(pdf):
    fig, ax = plt.subplots(figsize=(11.69, 8.27))
    fig.subplots_adjust(left=0.01, right=0.99, top=0.92, bottom=0.01)
    ax.set_aspect("equal"); ax.axis("off")
    fig.suptitle("1) POSIÇÕES ao longo da aresta A  (fita métrica + esquadro)", fontsize=14, weight="bold", x=0.02, ha="left", y=0.97)
    draw_part(ax)
    # fita métrica ao longo de A
    y0 = 10
    ax.add_patch(Rectangle((-8, y0), 570, 9, fc="#f7dc6f", ec="#b7950b", lw=0.8, zorder=3))
    for t in range(0, 561, 10):
        h = 5 if t % 50 == 0 else 2.5
        ax.plot([t, t], [y0, y0 + h], color="#7d6608", lw=0.6, zorder=4)
        if t % 50 == 0:
            ax.text(t, y0 + 6.2, str(t), fontsize=5, ha="center", color="#7d6608", zorder=4)
    ax.text(-10, y0 + 4.5, "0", fontsize=7, ha="right", va="center", color="#7d6608", weight="bold")
    # leituras X
    pts = [  # (X desde a topo, Y do ponto, valor aprox.) -> numerados por ordem
        (0, 60, "0"), (5.3, 108, "≈ 5"), (21.9, 100, "≈ 22"), (37.4, 0, "≈ 37"),
        (62.6, 100, "≈ 63"), (90 - 8.5, 50, "bordo"), (90 + 8.5, 50, "bordo"),
        (126.0, 90, "≈ 126"), (165.3, 90, "≈ 165"), (230.8, 76, "≈ 231"), (268.6, 76, "≈ 269"),
        (334.2, 60, "≈ 334"), (371.3, 60, "≈ 371"), (394.6, 110, "≈ 395"), (408.2, 173, "≈ 408"),
        (542, 10, "≈ 542"),
    ]
    pts = [(f"X{i+1}",) + p for i, p in enumerate(pts)]
    lvl = [22, 38, 54, 70]
    for i, (lab, x, y, v) in enumerate(pts):
        ytop = y0 + 12 + lvl[i % 4]
        ax.plot([x, x], [-y, ytop - 5], color=RED, lw=0.7, ls=(0, (3, 2)), zorder=5)
        ax.plot(x, -y, "o", color=RED, ms=3, zorder=6)
        bubble(ax, x, ytop, lab, RED)
        ax.text(x, ytop + 7, v, fontsize=6.5, ha="center", color=RED)
    # caixa de instruções
    txt = ("COMO:  1. Prende a fita com fita-cola ao longo da aresta A, com o 0 na topo esquerda (X1).\n"
           "2. Encosta a base do esquadro à aresta A e alinha a régua do esquadro com o ponto.  3. Lê a fita junto à régua.\n"
           "• Furo F1: lê os dois bordos (X6 e X7); o centro é a média.  Os outros furos já tens (105 / 210 / 315).\n"
           "• Rasgos N1…N4: lê as duas paredes de cada um (X3/X5, X8/X9, X10/X11, X12/X13).\n"
           "• X2 é para ver se a topo esquerda é esquadrada: no papel o dedo está ~5 mm para dentro (inclinada ~6°).\n"
           "• Valores '≈' tirados do teu papel (±2–3 mm). Se a tua medição fugir mais de 3 mm, diz-me.")
    ax.text(-5, -200, txt, fontsize=7.6, va="top", ha="left", color=INK, linespacing=1.55,
            bbox=dict(boxstyle="round,pad=0.5", fc="#fdf2e9", ec=RED, lw=0.8))
    # mini desenho do esquadro (vista de cima)
    bx, by = 450, -205
    ax.add_patch(Rectangle((bx, by - 62), 110, 62, fc="#eef1f4", ec=INK, lw=1))
    ax.add_patch(Rectangle((bx + 42, by - 63), 26, 36, fc="white", ec="none"))
    ax.plot([bx + 42, bx + 42, bx + 68, bx + 68], [by - 62, by - 27, by - 27, by - 62], color=INK, lw=1)
    ax.add_patch(Rectangle((bx, by - 9), 110, 6, fc="#f7dc6f", ec="#b7950b", lw=0.6))
    ax.add_patch(Rectangle((bx + 55, by), 40, 8, fc="#566573", ec=INK, lw=0.8))
    ax.add_patch(Rectangle((bx + 68, by - 45), 7, 45, fc="#aab7b8", ec=INK, lw=0.8, alpha=0.9))
    ax.plot([bx + 68, bx + 68], [by - 45, by + 8], color=RED, lw=1.2)
    ax.annotate("base do esquadro\nencostada à aresta A", (bx + 88, by + 8), (bx + 80, by + 22), fontsize=6, arrowprops=dict(arrowstyle="-", lw=0.6))
    ax.annotate("régua alinhada com\na parede do rasgo", (bx + 72, by - 38), (bx + 85, by - 50), fontsize=6, arrowprops=dict(arrowstyle="-", lw=0.6))
    ax.annotate("lê a fita aqui", (bx + 68, by - 6), (bx + 2, by + 18), fontsize=6.5, color=RED, weight="bold", arrowprops=dict(arrowstyle="->", lw=0.8, color=RED))
    ax.text(bx + 55, by - 70, "vista de cima (exemplo)", fontsize=6, ha="center", style="italic")
    ax.set_xlim(-20, 575); ax.set_ylim(-285, 105)
    pdf.savefig(fig); fig.savefig("pagina1_posicoes_X.png", dpi=170); plt.close(fig)

def page_y(pdf):
    fig, ax = plt.subplots(figsize=(11.69, 8.27))
    fig.subplots_adjust(left=0.01, right=0.99, top=0.92, bottom=0.01)
    ax.set_aspect("equal"); ax.axis("off")
    fig.suptitle("2) ALTURAS a partir da aresta A  (paquímetro, perpendicular a A)", fontsize=14, weight="bold", x=0.02, ha="left", y=0.97)
    draw_part(ax)
    pts = [  # (X, Y, valor aprox.) -> numerados por ordem
        (1, 33.7, "≈ 34"), (14, 117.6, "(120)?"), (42.2, 79, "≈ 79"), (66, 109, "110.2?"),
        (90, 41.5, "≈ 41.5*"), (124, 100.5, "≈ 101"), (145.7, 65.2, "≈ 65"), (169, 96, "≈ 96"),
        (229, 89.5, "≈ 89"), (249.7, 51.3, "≈ 51"), (271, 81.3, "≈ 81"), (332, 70.9, "≈ 71"),
        (352.8, 36.5, "≈ 36"), (385, 63.6, "≈ 64"), (408.2, 173.3, "173 ✓"),
    ]
    pts = [(f"Y{i+1}",) + p for i, p in enumerate(pts)]
    for i, (lab, x, y, v) in enumerate(pts):
        ax.annotate("", (x, -y), (x, 0), arrowprops=dict(arrowstyle="<->", color=BLUE, lw=0.9, shrinkA=0, shrinkB=0), zorder=5)
        yl = 14 + (i % 3) * 16
        ax.plot([x, x], [0, yl - 5], color=BLUE, lw=0.6, ls=(0, (2, 2)))
        bubble(ax, x, yl, lab, BLUE)
        ax.text(x, yl + 7.5, v, fontsize=6.5, ha="center", color=BLUE)
    ax.plot([-20, 575], [0, 0], color=BLUE, lw=0.5, alpha=0.4)
    txt = ("COMO:  um bico do paquímetro na aresta A e o outro no ponto, sempre a 90° da aresta A.\n"
           "• Y5 (furos): da aresta A ao bordo MAIS PRÓXIMO do furo, do lado SEM escareado; eu somo metade do Ø.\n"
           "   Mede no F1 e no F4: se der igual, os furos estão paralelos à aresta A (no papel dá ~50 ao centro).\n"
           "• Y4, Y6, Y8, Y9, Y11, Y12 (cantos dos dentes): mede a 3–4 mm do canto (fora do arredondamento).\n"
           "   A face dos dentes é inclinada ~8°, por isso os dois cantos de cada dente dão valores diferentes.\n"
           "• Y3, Y7, Y10, Y13 (fundo dos rasgos): o bico entra no rasgo e encosta no fundo = 'material acima do rasgo'.\n"
           "• Y1: quanto o chanfro desce na topo.   Y2: altura total no dedo P.   Y4: é este o teu 110.2?")
    ax.text(-5, -195, txt, fontsize=7.6, va="top", ha="left", color=INK, linespacing=1.55,
            bbox=dict(boxstyle="round,pad=0.5", fc="#eaf2fb", ec=BLUE, lw=0.8))
    ax.text(470, -195, "* se medires ao centro\n   do furo: ≈ 50", fontsize=7, color=BLUE, va="top")
    ax.set_xlim(-20, 575); ax.set_ylim(-285, 70)
    pdf.savefig(fig); fig.savefig("pagina2_alturas_Y.png", dpi=170); plt.close(fig)

def page_extra(pdf):
    fig = plt.figure(figsize=(11.69, 8.27))
    fig.suptitle("3) ESCAREADO, RAIOS e o que já está resolvido", fontsize=14, weight="bold", x=0.02, ha="left", y=0.97)
    # escareado: caixa cilíndrica + cone 90° + furo (medido na 3.ª folha)
    ax = fig.add_axes([0.01, 0.40, 0.50, 0.53]); ax.set_aspect("equal"); ax.axis("off")
    t, dcb, hcb, dh, hcyl = 14.7, 25.5, 7.0, 16.0, 3.0
    hcone = t - hcb - hcyl
    ang = 2*np.degrees(np.arctan((dcb - dh)/2/hcone))
    W = 22
    for sgn in (-1, 1):
        prof = [(sgn*W, 0), (sgn*dcb/2, 0), (sgn*dcb/2, -hcb), (sgn*dh/2, -hcb - hcone), (sgn*dh/2, -t), (sgn*W, -t)]
        ax.add_patch(Polygon(prof, fc="#d5d8dc", ec=INK, lw=1.2, hatch="///"))
    ax.plot([0, 0], [3, -t - 3], color=GREY, lw=0.6, ls="-.")
    def dimh(y, x0, x1, txt, col):
        ax.annotate("", (x0, y), (x1, y), arrowprops=dict(arrowstyle="<->", lw=0.9, color=col))
        ax.text((x0 + x1)/2, y + 1, txt, ha="center", va="bottom", fontsize=9, color=col, weight="bold")
    def dimv(x, y0, y1, txt, col, ha="left"):
        ax.annotate("", (x, y0), (x, y1), arrowprops=dict(arrowstyle="<->", lw=0.9, color=col))
        ax.text(x + (1 if ha == "left" else -1), (y0 + y1)/2, txt, ha=ha, va="center", fontsize=9, color=col, weight="bold")
    dimh(2.5, -dcb/2, dcb/2, "Ø25.5 caixa", GREEN)
    dimh(-t - 3.5, -dh/2, dh/2, "", GREEN); ax.text(0, -t - 6.5, "Ø16 passagem", ha="center", fontsize=9, color=GREEN, weight="bold")
    dimv(W + 2, 0, -hcb, "7", GREEN); dimv(W + 2, -hcb, -hcb - hcone, f"{hcone:.1f}", RED); dimv(W + 2, -hcb - hcone, -t, "3", GREEN)
    dimv(-W - 2, 0, -t, "14.7", GREY, ha="right")
    ax.text(-dh/2 + 1.0, -hcb - hcone/2 - 0.3, f"{ang:.0f}° ≈ 90°", ha="left", va="center", fontsize=10, color=RED, weight="bold")
    ax.text(0, 8, "ESCAREADO: agora bate certo  ✓", ha="center", fontsize=11, weight="bold", color=GREEN)
    ax.text(-W - 8, -t - 10,
            f"Caixa Ø25.5 com 7 de fundo + cone + Ø16 com 3 no fundo.  Sobram 14.7 − 7 − 3 = {hcone:.1f} mm para o cone,\n"
            f"e de Ø25.5 para Ø16 em {hcone:.1f} mm dá {ang:.0f}°, ou seja, escareado normal de 90°.\n"
            "A caixa de 7 mm deixa a cabeça do parafuso bem abaixo da superfície (protegida do desgaste).\n\n"
            "Falta só confirmar 2 coisas:\n"
            "  1. O que LEU o paquímetro no furo pintado? A tinta ENCOLHE os furos: Ø aço = Ø lido + 1.\n"
            "      Se leste 16 na passagem → aço 17 (passagem normal de M16). Se leste 15 → aço 16.\n"
            "      Idem na caixa: se leste 25.5 → aço 26.5.\n"
            "  2. O parafuso (M16? cabeça de embeber? norma?) — confirma que a cabeça cabe na caixa.",
            fontsize=8, va="top", linespacing=1.5)
    ax.set_xlim(-32, 32); ax.set_ylim(-52, 11)
    # raios
    ax2 = fig.add_axes([0.52, 0.40, 0.46, 0.52]); ax2.axis("off")
    ax2.text(0, 1, "RAIOS dos cantos: truque das moedas", fontsize=10, weight="bold", va="top")
    ax2.text(0, 0.92,
             "Encosta a moeda ao canto arredondado; a que 'assenta' certinho dá o raio.\n\n"
             "   1 cêntimo  Ø16.25 → R8          10 cêntimos Ø19.75 → R10\n"
             "   5 cêntimos Ø21.25 → R10.6       1 euro      Ø23.25 → R11.6\n"
             "   50 cêntimos Ø24.25 → R12        2 euros     Ø25.75 → R12.9\n\n"
             "Preciso de:\n"
             "   R1  vértice V          (no papel ≈ R9–11)\n"
             "   R2  bico B             (no papel ≈ R8–10)\n"
             "   R3  cantos de fora dos dentes D1–D3 e do patamar E\n"
             "   R4  cantos de dentro (dente → rasgo, patamar → degrau)\n"
             "   R5  ponta do dedo P (é meia-cana? então R = largura/2 = 6.8)\n"
             "   R6  cantos do chanfro C\n"
             "Para raios pequenos (<5 mm) basta 'pequeno ~3' — não é crítico.",
             fontsize=8.3, va="top", family="DejaVu Sans Mono")
    # resolvido / a confirmar
    ax3 = fig.add_axes([0.02, 0.03, 0.96, 0.36]); ax3.axis("off")
    ax3.text(0, 1, "Com as tuas novas cotas, já batem certo:", fontsize=10, weight="bold", va="top", color=GREEN)
    ax3.text(0, 0.88,
             "✓ Furos a 105 / 210 / 315 do F1 (passo 105) e, no papel, todos a ~50 da aresta A.\n"
             "✓ Escareado: caixa Ø25.5 × 7 + cone 90° + Ø16 × 3 (ver acima).\n"
             "✓ (128) e (250) são até aos cantos 'vivos' teóricos do triângulo: batem com 173, 102 e 208 se V e B tiverem raio ~R9–R10.\n"
             "✓ Os rasgos parecem estar a meio entre furos (~52 mm do furo anterior) e com fundo de ~R19–20. Confirma com X3…X13.",
             fontsize=8.5, va="top", linespacing=1.6)
    ax3.text(0, 0.50, "Ainda não batem certo — confirma:", fontsize=10, weight="bold", va="top", color=RED)
    ax3.text(0, 0.38,
             "✗ Comprimento total (567): 505 + chanfro (~43) + vértice (~3) ≈ 550, não 567. No papel dá ~545. Mede X16.\n"
             "✗ 110.2: a linha tracejada no papel está inclinada (do canto do chanfro ao canto do D1) — no papel essa diagonal dá ~116.\n"
             "     Se é a altura do canto do D1, tem de ser medida a 90° da aresta A → Y4.\n"
             "✗ Topo esquerda (81): no papel está inclinada ~6° em relação à perpendicular de A → X1 e X2 confirmam.",
             fontsize=8.5, va="top", linespacing=1.6)
    pdf.savefig(fig); fig.savefig("pagina3_escareado_raios.png", dpi=170); plt.close(fig)

if __name__ == "__main__":
    with PdfPages("esquema_medicao.pdf") as pdf:
        page_x(pdf); page_y(pdf); page_extra(pdf)
