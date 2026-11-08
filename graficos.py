# -*- coding: utf-8 -*-
"""
Cria os graficos do relatorio a partir de resultados/resultados.json.
Precisa do matplotlib:  pip install matplotlib
Uso:  python graficos.py
"""
import json
import statistics
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from rainhas import resolver

dados = json.load(open("resultados/resultados.json"))
AZUL, LARANJA = "#1f5fa8", "#d9822b"
tamanhos = [8, 80, 800]

# ---- dados do A* (n = 8 vem da lista de crescimento) ----
astar = {8: [r for r in dados["astar_crescimento"] if r["n"] == 8][0],
         80: dados["astar"][0], 800: dados["astar"][1]}

# ---- dados da gulosa: simula "tentar sementes 0, 1, 2... ate dar certo" ----
gulosa = {}
for n in tamanhos:
    rodadas = [r for r in dados["gulosa_sementes"] if r["n"] == n]
    nos = tempo = 0
    for k, r in enumerate(rodadas):
        nos += r["expandidos"]
        tempo += r["tempo"]
        if r["sucesso"]:
            gulosa[n] = {"tentativas": k + 1, "expandidos": nos, "tempo": tempo,
                         "acertos": sum(x["sucesso"] for x in rodadas), "total": len(rodadas)}
            break

json.dump({"astar": {str(k): v for k, v in astar.items()}, "gulosa": {str(k): v for k, v in gulosa.items()}},
          open("resultados/resumo.json", "w"), indent=1)


def pontos(v):
    return f"{int(v):,}".replace(",", ".")


def barras(chave, titulo, rotulo_y, arquivo, formato):
    fig, ax = plt.subplots(figsize=(7, 4))
    larg = 0.38
    va = [astar[n][chave] for n in tamanhos]
    vg = [gulosa[n][chave] for n in tamanhos]
    b1 = ax.bar([i - larg / 2 for i in range(3)], va, larg, color=AZUL, label="A*")
    b2 = ax.bar([i + larg / 2 for i in range(3)], vg, larg, color=LARANJA, label="Busca Gulosa")
    for i, n in enumerate(tamanhos):
        if not astar[n]["sucesso"]:
            b1[i].set_hatch("//")
            b1[i].set_alpha(0.6)
    for barras_, valores, eh_astar in ((b1, va, True), (b2, vg, False)):
        for b, v, n in zip(barras_, valores, tamanhos):
            texto = formato(v) + ("*" if eh_astar and not astar[n]["sucesso"] else "")
            ax.annotate(texto, (b.get_x() + b.get_width() / 2, v), ha="center", va="bottom", fontsize=8)
    ax.set_yscale("log")
    ax.set_xticks(range(3))
    ax.set_xticklabels([f"{n} rainhas" for n in tamanhos])
    ax.set_ylabel(rotulo_y)
    ax.set_title(titulo)
    ax.legend(loc="upper right", fontsize=9)
    ax.set_ylim(top=max(va + vg) * 40)
    fig.text(0.01, 0.01, "* o A* não terminou: parou no limite de tempo (barra hachurada = valor atingido até parar)", fontsize=7)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(arquivo, dpi=170)
    plt.close(fig)


barras("expandidos", "Passos (nós expandidos)", "nós expandidos (escala log)", "resultados/grafico_passos.png", pontos)
barras("tempo", "Tempo de execução", "segundos (escala log)", "resultados/grafico_tempo.png", lambda v: f"{v:.3g} s")

# ---- crescimento do A* ----
fig, ax = plt.subplots(figsize=(7, 3.8))
cres = dados["astar_crescimento"]
ax.plot([r["n"] for r in cres], [r["expandidos"] for r in cres], "o-", color=AZUL)
for r in cres:
    ax.annotate(pontos(r["expandidos"]), (r["n"], r["expandidos"]), textcoords="offset points",
                xytext=(-6, 7), ha="right", fontsize=8)
ax.set_yscale("log")
ax.set_xlabel("quantidade de rainhas (n)")
ax.set_ylabel("nós expandidos (escala log)")
ax.set_title("Crescimento do esforço do A*")
ax.set_xlim(3.3, 8.4)
fig.tight_layout()
fig.savefig("resultados/grafico_crescimento_astar.png", dpi=170)
plt.close(fig)

# ---- desenho de uma solucao com 8 rainhas ----
sol = resolver(8, "gulosa")["rainhas"]
fig, ax = plt.subplots(figsize=(4, 4))
for i in range(8):
    for j in range(8):
        ax.add_patch(plt.Rectangle((j, 7 - i), 1, 1, color="#f0d9b5" if (i + j) % 2 == 0 else "#b58863"))
for casa in sol:
    ax.text(casa % 8 + 0.5, 7 - casa // 8 + 0.5, "\u265B", ha="center", va="center", fontsize=26, color="black")
ax.set_xlim(0, 8)
ax.set_ylim(0, 8)
ax.set_aspect("equal")
ax.set_xticks([k + 0.5 for k in range(8)])
ax.set_xticklabels(range(1, 9))
ax.set_yticks([k + 0.5 for k in range(8)])
ax.set_yticklabels(range(8, 0, -1))
ax.set_title("Solução encontrada para 8 rainhas")
fig.tight_layout()
fig.savefig("resultados/tabuleiro_8_rainhas.png", dpi=170)
print("Graficos salvos na pasta resultados/")
