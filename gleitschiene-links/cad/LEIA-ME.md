# Gleitschiene links: modelo CAD preliminar

| Ficheiro | Para quê |
|---|---|
| `gleitschiene_links.step` | Modelo 3D. No Onshape: **Create → Import** → escolher o ficheiro. |
| `gleitschiene_links.dxf` | Contorno 1:1 para o fornecedor cortar. Camada `CORTE` = contorno + furos Ø17. Camada `MAQUINAGEM_CAIXA` = caixas Ø26.5, só como referência. |
| `desenho_gleitschiene_links.pdf` | Desenho A3 a 1:2, no formato Valorsul – ETVO. Imprimir a 100 %. |
| `preview_3d.png` | Vista rápida. |
| `gleitschiene.py` | Modelo paramétrico: todas as medidas estão no bloco `PARÂMETROS`. |
| `desenho.py` | Gera o desenho e a vista 3D (`python3 desenho.py`). |

**PRELIMINAR.** Os valores marcados com * (no desenho) ou com `CONFIRMAR` (no código) vêm do traçado 1:1 em papel e ainda não foram medidos.

## Alterar no Onshape

- **Pequenos ajustes no 3D importado.** Usar *Move face* ou *Offset face*, por exemplo para mudar a largura de um rasgo ou mover uma face.
- **Refazer o contorno com cotas próprias.**
  1. Criar um Part Studio novo.
  2. Fazer um Sketch no plano Top e usar *Insert DXF/DWG* com `gleitschiene_links.dxf`, em mm.
  3. Cotar e restringir o sketch como quiseres.
  4. Fazer *Extrude* de 15.
  5. Fazer os furos com *Hole* do tipo Counterbore: Ø17 passante, caixa Ø26.5 com 7 de profundidade.
  6. Aplicar *Chamfer* de 4.75 na aresta do fundo da caixa, que dá o cone a 90°.
- **Mais rápido.** Dizer os valores novos ao Claude, que gera tudo de novo (STEP, DXF e PDF).
