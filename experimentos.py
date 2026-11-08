# -*- coding: utf-8 -*-
"""
Roda todos os testes do relatorio e salva em resultados/resultados.json.
Demora cerca de 15 minutos (o A* com 8 rainhas sozinho leva uns 5).
Uso:  python experimentos.py
"""
import json

try:
    import resource          # so existe no Linux e no macOS
except ImportError:
    resource = None
from rainhas import buscar

def memoria_mb():
    if resource is None:     # Windows: nao mede a memoria
        return None
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024

def limpar(r):
    r.pop("rainhas", None)
    return r

saida = {"astar_crescimento": [], "astar": [], "gulosa_linha": [], "gulosa_sementes": []}
try:   # se o programa foi interrompido, continua de onde parou
    saida.update(json.load(open("resultados/resultados.json")))
except FileNotFoundError:
    pass

print("A* para n = 4 ... 8", flush=True)
for n in range(4, 9):
    if any(x["n"] == n for x in saida["astar_crescimento"]):
        continue
    r = limpar(buscar(n, "astar", usar_mrv=False, limite_nos=4_000_000))
    r["memoria_mb"] = memoria_mb()
    saida["astar_crescimento"].append(r)
    print(" ", n, r["sucesso"], r["expandidos"], round(r["tempo"], 2), flush=True)
    json.dump(saida, open("resultados/resultados.json", "w"), indent=1)

print("A* para n = 80 e 800 (limite de 60 s)", flush=True)
for n in (80, 800):
    r = limpar(buscar(n, "astar", usar_mrv=False, limite_tempo=60))
    r["memoria_mb"] = memoria_mb()
    saida["astar"].append(r)
    print(" ", n, r["motivo"], r["expandidos"], flush=True)

print("Gulosa sem MRV (desempate linha a linha), limite de 30 s", flush=True)
for n in (8, 80, 800):
    r = limpar(buscar(n, "gulosa", usar_mrv=False, limite_tempo=30))
    saida["gulosa_linha"].append(r)
    print(" ", n, r["sucesso"], r["expandidos"], round(r["tempo"], 2), flush=True)
json.dump(saida, open("resultados/resultados.json", "w"), indent=1)

print("Gulosa com MRV, uma tentativa por semente", flush=True)
for n, qtd_sementes in ((8, 20), (80, 20), (800, 20)):
    limite = int(1.25 * n) + 100
    for semente in range(qtd_sementes):
        r = limpar(buscar(n, "gulosa", semente=semente, limite_nos=limite))
        r["semente"] = semente
        saida["gulosa_sementes"].append(r)
        print(" ", n, semente, r["sucesso"], r["expandidos"], round(r["tempo"], 2), flush=True)
    json.dump(saida, open("resultados/resultados.json", "w"), indent=1)
print("FIM", flush=True)
