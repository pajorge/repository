"""Gleitschiene links (calha deslizante esquerda), Backhus A50: modelo paramétrico.

Gera, na pasta deste ficheiro:
  gleitschiene_links.step   modelo 3D (importa no Onshape: Import -> STEP)
  gleitschiene_links.dxf    contorno 1:1 para corte (laser/plasma/jato de água)
  desenho_gleitschiene_links.pdf / .png   desenho A3 com cotas e legenda
  preview_3d.png            vista 3D

Coordenadas: X ao longo da aresta reta A, 0 no centro do furo F1 (positivo para o triângulo).
             Y perpendicular a A, 0 na aresta A, positivo para dentro da peça.
Todas as medidas em mm, AÇO SEM TINTA (tinta medida = 0.5 mm por face).
Os valores marcados "CONFIRMAR" vieram do traçado 1:1 em papel (±2 mm) e não de medição direta.
"""
from math import radians, sqrt, tan
from pathlib import Path

import numpy as np
from build123d import (Axis, ColorIndex, Location, BuildPart, BuildSketch, Circle, ExportDXF, Locations, Mode, Plane,
                       Polygon, Rectangle, Unit, Vector, export_step, extrude, fillet, revolve)

OUT = Path(__file__).resolve().parent

# ============================ PARÂMETROS ============================
ESPESSURA = 15.0           # medido 14.7 em aço -> chapa comercial de 15

# Furos (medido: 105 / 210 / 315 a partir do F1)
PASSO_FUROS = 105.0
N_FUROS = 4
FURO_Y = 50.0              # CONFIRMAR (papel: 49.7 … 50.7)
FURO_D = 17.0              # passagem M16 (lido 16 com tinta)
CAIXA_D = 26.5             # caixa cilíndrica (lido 25.5 com tinta)
CAIXA_H = 7.0              # profundidade da caixa (medido)
ESCAREADO_ANG = 90.0       # cone entre a caixa e a passagem (as medidas fecham a 90°)

# Ponta esquerda
F1_A_TOPO = 89.5           # centro F1 -> topo esquerda, à altura do furo (lido 90 com tinta)
TOPO_INCL = 6.2            # CONFIRMAR: inclinação da topo em graus (papel ~6°; 0 = esquadrada)
CHANFRO_X, CHANFRO_Y = 43.0, 34.0   # CONFIRMAR catetos (comprimento medido 55)
DEDO_Y = 119.0             # altura total no dedo P (lido 120 com tinta)
DEDO_LARG = 13.6           # medido
R_DEDO = 6.5               # ponta do dedo (quase meia-cana)

# Linha dos dentes (faces inferiores dos dentes D1-D3 e patamar antes do degrau)
DENTES_X0, DENTES_Y0 = -26.4, 110.2   # canto do D1 junto ao N1 (110.2 medido, posição CONFIRMAR)
DENTES_INCL = 8.3                     # CONFIRMAR: graus em relação à aresta A (papel)

# Rasgos: (centro X, largura, Y do fundo) -- fundo semicircular com R = largura/2
RASGOS = [
    ("N1", -47.4, 42.0, 79.0),     # CONFIRMAR (largura e fundo do papel)
    ("N2", 55.7, 39.3, 65.2),      # CONFIRMAR posição e fundo
    ("N3", 158.8, 39.3, 51.3),     # CONFIRMAR (posição acertada para o dente D3 = 64.7 medido)
    ("N4", 262.8, 39.3, 36.0),     # largura 38.3 lida c/ tinta; fundo = canto D3 - 34.7 medido
]
# Inclinação das paredes de cada rasgo, em graus em relação à perpendicular à aresta A.
# Positivo = a boca do rasgo (junto aos dentes) foge para o lado do triângulo (+X).
# A MEDIR: com o esquadro viu-se que não estão a 90° da aresta A.
RASGOS_INCL = {"N1": 0.0, "N2": 0.0, "N3": 0.0, "N4": 0.0}

# Degrau E e triângulo
DEGRAU_X = 304.6           # CONFIRMAR (papel): X do canto de dentro patamar/degrau
DEGRAU_INCL = 3.0          # A MEDIR: não está a 90° de A (esquadro); papel ~3°, bico para +X
BICO_Y = 173.0             # medido
DEGRAU_A_VIVO = 127.0      # patamar -> canto vivo teórico do bico (lido 128 c/ tinta)
HIPOT_VIVO = 249.0         # canto vivo a canto vivo na hipotenusa (lido 250 c/ tinta)
R_VERTICE = 6.0            # CONFIRMAR (do 208 medido na parte reta da hipotenusa)
R_PEQUENO = 3.0            # CONFIRMAR: cantos dos dentes, chanfro, canto interior do degrau
# ===================================================================

T = tan(radians(DENTES_INCL))


def dentes_y(x):
    return DENTES_Y0 - T * (x - DENTES_X0)


def topo_x(y):
    return -F1_A_TOPO + (y - FURO_Y) * tan(radians(TOPO_INCL))


def direcao(ang):
    """Direção 'para baixo' (d, +Y) inclinada 'ang' graus para +X, e a normal n (para +X)."""
    a = radians(ang)
    return np.array([np.sin(a), np.cos(a)]), np.array([np.cos(a), -np.sin(a)])


def ate_dentes(p, d):
    """Ponto onde a reta p + t*d corta a linha dos dentes."""
    t = (dentes_y(p[0]) - p[1]) / (d[1] + T * d[0])
    return p + t * d


def rasgo(nome):
    """Geometria de um rasgo em U (possivelmente inclinado)."""
    _, cx, w, yf = next(r for r in RASGOS if r[0] == nome)
    d, n = direcao(RASGOS_INCL[nome])
    c = np.array([cx, yf + w / 2])                  # centro do arco; fundo = c - (0, w/2)
    r = {"c": c, "d": d, "n": n, "w": w}
    for lado, s in (("E", -1), ("D", 1)):
        topo = c + s * (w / 2) * n                  # onde a parede reta começa (tangente ao arco)
        if nome == "N1" and lado == "E":            # parede interior do dedo acaba no fundo do dedo
            boca = topo + (DEDO_Y - topo[1]) / d[1] * d
        else:
            boca = ate_dentes(topo, d)
        r[lado + "_topo"], r[lado + "_boca"] = topo, boca
    return r


def geometria():
    """Pontos principais derivados dos parâmetros (X, Y)."""
    g = {}
    g["C2"] = (topo_x(CHANFRO_Y), CHANFRO_Y)
    g["C1"] = (g["C2"][0] + CHANFRO_X, 0.0)
    g["E"] = (DEGRAU_X, dentes_y(DEGRAU_X))
    dE, _ = direcao(DEGRAU_INCL)
    bx, by = np.array(g["E"]) + DEGRAU_A_VIVO * dE
    g["B_vivo"] = (bx, by)
    g["V_vivo"] = (bx + sqrt(HIPOT_VIVO**2 - by**2), 0.0)
    return g


def raio_bico(g):
    """Raio no bico B tal que o ponto mais baixo do arco fica a BICO_Y da aresta A."""
    bx, by = g["B_vivo"]
    vx, _ = g["V_vivo"]
    u1 = -direcao(DEGRAU_INCL)[0]                               # do bico para cima (degrau)
    u2 = np.array([vx - bx, -by]); u2 /= np.linalg.norm(u2)     # do bico para o vértice
    half = np.arccos(np.dot(u1, u2)) / 2
    bis = (u1 + u2) / np.linalg.norm(u1 + u2)
    # centro = vivo + bis * R/sin(half); ponto mais baixo = centro_y + R
    k = bis[1] / np.sin(half)
    return (BICO_Y - by) / (k + 1)


def bico_centro(g):
    """Centro do arco do bico (o ponto mais baixo tem o mesmo X) e ângulo da hipotenusa com A."""
    bx, by = g["B_vivo"]; vx, _ = g["V_vivo"]; r = g["R_BICO"]
    u1 = -direcao(DEGRAU_INCL)[0]
    u2 = np.array([vx - bx, -by]); u2 /= np.linalg.norm(u2)
    half = np.arccos(np.dot(u1, u2)) / 2
    bis = (u1 + u2) / np.linalg.norm(u1 + u2)
    c = np.array([bx, by]) + bis * r / np.sin(half)
    return c, np.degrees(np.arctan2(by, vx - bx))


def modelo():
    g = geometria()
    g["R_BICO"] = raio_bico(g)
    x_dedo_ext = topo_x(DEDO_Y)
    n1 = RASGOS[0]
    x_n1 = n1[1]
    # contorno base com cantos vivos (y do CAD = -Y)
    base = [g["C1"], g["V_vivo"], g["B_vivo"], g["E"], (x_n1, dentes_y(x_n1)), (x_n1, DEDO_Y),
            (x_dedo_ext, DEDO_Y), g["C2"]]
    base = [(x, -y) for x, y in base]

    rs = {r[0]: rasgo(r[0]) for r in RASGOS}
    with BuildSketch() as sk:
        Polygon(*base, align=None)
        for r in rs.values():
            c, d, n, w = r["c"], r["d"], r["n"], r["w"]
            cantos = [c - w / 2 * n, c + w / 2 * n, c + w / 2 * n + 200 * d, c - w / 2 * n + 200 * d]
            Polygon(*[(x, -y) for x, y in cantos], align=None, mode=Mode.SUBTRACT)
            with Locations((c[0], -c[1])):
                Circle(w / 2, mode=Mode.SUBTRACT)

        def perto(pts, tol=0.8):
            out = []
            for v in sk.vertices():
                p = Vector(v.X, v.Y, 0)
                if any((p - Vector(x, -y, 0)).length < tol for x, y in pts):
                    out.append(v)
            return out

        # cantos da boca dos rasgos (dentes) e canto interior do degrau
        bocas = [tuple(r[k]) for r in rs.values() for k in ("E_boca", "D_boca")]
        dedo_int = bocas.pop(0)                      # N1 esquerdo = canto interior do dedo
        fillet(perto(bocas + [g["E"], g["C1"], g["C2"]]), R_PEQUENO)
        fillet(perto([dedo_int, (x_dedo_ext, DEDO_Y)]), R_DEDO)
        fillet(perto([g["B_vivo"]]), g["R_BICO"])
        fillet(perto([g["V_vivo"]]), R_VERTICE)
    perfil = sk.sketch

    cone_h = (CAIXA_D - FURO_D) / 2 / tan(radians(ESCAREADO_ANG / 2))
    furos = [(i * PASSO_FUROS, -FURO_Y) for i in range(N_FUROS)]
    prof = [(0, ESPESSURA + 1), (CAIXA_D / 2, ESPESSURA + 1), (CAIXA_D / 2, ESPESSURA - CAIXA_H),
            (FURO_D / 2, ESPESSURA - CAIXA_H - cone_h), (FURO_D / 2, -1), (0, -1)]
    with BuildPart() as ferramenta:        # caixa + cone + passagem, rodado em torno de Z
        with BuildSketch(Plane.XZ):
            Polygon(*prof, align=None)
        revolve(axis=Axis.Z)
    with BuildPart() as bp:
        extrude(perfil, amount=ESPESSURA)
    peca = bp.part
    for x, y in furos:
        peca = peca - ferramenta.part.moved(Location((x, y, 0)))

    corte2d = perfil
    for x, y in furos:
        with BuildSketch() as c:
            with Locations((x, y)):
                Circle(FURO_D / 2)
        corte2d = corte2d - c.sketch

    g.update(dict(perfil=perfil, corte2d=corte2d, peca=peca, furos=furos, cone_h=cone_h,
                  x_dedo_ext=x_dedo_ext, rasgos=rs))
    return g


def exportar(g):
    export_step(g["peca"], str(OUT / "gleitschiene_links.step"))
    dxf = ExportDXF(unit=Unit.MM)
    dxf.add_layer("CORTE", color=ColorIndex.BLACK)
    dxf.add_layer("MAQUINAGEM_CAIXA", color=ColorIndex.RED)
    dxf.add_shape(g["corte2d"], layer="CORTE")
    for x, y in g["furos"]:
        with BuildSketch() as c:
            with Locations((x, y)):
                Circle(CAIXA_D / 2)
        dxf.add_shape(c.sketch, layer="MAQUINAGEM_CAIXA")
    dxf.write(str(OUT / "gleitschiene_links.dxf"))


if __name__ == "__main__":
    g = modelo()
    exportar(g)
    vol = g["peca"].volume
    print(f"volume {vol/1000:.0f} cm3, peso aço {vol*7.85e-6:.2f} kg")
    print(f"R bico = {g['R_BICO']:.1f}, vértice vivo X = {g['V_vivo'][0]:.1f}, E = {g['E']}")
    bb = g["peca"].bounding_box()
    print(f"caixa envolvente X {bb.min.X:.1f}..{bb.max.X:.1f}  Y {-bb.max.Y:.1f}..{-bb.min.Y:.1f}")
