# -*- coding: utf-8 -*-
"""
Problema das n-Rainhas com busca informada (A* e Busca Gulosa)
Disciplina de Inteligencia Artificial - IFPI Campus Picos

Como o problema foi modelado:
  - estado inicial : tabuleiro vazio
  - acao           : colocar UMA rainha em qualquer casa vazia (no maximo n rainhas)
  - custo          : 1 por estado novo (entao g = numero de rainhas no tabuleiro)
  - heuristica h   : quantidade de pares de rainhas que se atacam, direta ou
                     indiretamente (mesma linha, coluna ou diagonal, mesmo que
                     tenha outra rainha no meio)
  - meta           : n rainhas no tabuleiro e h = 0

Um estado e guardado como uma tupla ordenada com as casas das rainhas.
A casa da linha i e coluna j recebe o numero i * n + j.
"""
import heapq
import sys
import time
from bisect import insort

import numpy as np


# ----------------------------------------------------------------------
# Heuristica
# ----------------------------------------------------------------------
def contar_ataques(n, rainhas):
    """h(estado): conta os pares de rainhas que se atacam (usado para conferir a resposta)."""
    linhas, colunas, diag1, diag2 = {}, {}, {}, {}
    for casa in rainhas:
        i, j = divmod(casa, n)
        for tabela, chave in ((linhas, i), (colunas, j), (diag1, i - j), (diag2, i + j)):
            tabela[chave] = tabela.get(chave, 0) + 1
    total = 0
    for tabela in (linhas, colunas, diag1, diag2):
        for qtd in tabela.values():
            total += qtd * (qtd - 1) // 2     # pares dentro da mesma linha/coluna/diagonal
    return total


def ataques_novos(n, rainhas):
    """
    Para cada casa do tabuleiro, calcula quantos pares de ataque NOVOS aparecem
    se uma rainha for colocada ali. E a soma das rainhas que ja estao na linha,
    na coluna e nas duas diagonais daquela casa. Assim h(filho) = h(pai) + esse valor.
    """
    linhas = np.zeros(n, dtype=np.int64)
    colunas = np.zeros(n, dtype=np.int64)
    diag1 = np.zeros(2 * n - 1, dtype=np.int64)
    diag2 = np.zeros(2 * n - 1, dtype=np.int64)
    for casa in rainhas:
        i, j = divmod(casa, n)
        linhas[i] += 1
        colunas[j] += 1
        diag1[i - j + n - 1] += 1
        diag2[i + j] += 1
    i = np.arange(n)[:, None]          # indices de linha (coluna vertical)
    j = np.arange(n)[None, :]          # indices de coluna (linha horizontal)
    return linhas[:, None] + colunas[None, :] + diag1[i - j + n - 1] + diag2[i + j]


# ----------------------------------------------------------------------
# Busca
# ----------------------------------------------------------------------
def buscar(n, algoritmo, semente=0, usar_mrv=True, limite_nos=None, limite_tempo=None):
    """
    Busca pela melhor escolha com lista de estados repetidos.
      algoritmo = "astar"  -> f = g + h
      algoritmo = "gulosa" -> f = h
    Na fronteira, se o f for igual, sai primeiro o estado com mais rainhas.

    Os filhos de um estado sao gerados um de cada vez, do melhor (menor h) para o
    pior. A ordem de expansao e a mesma de quem gera todos os filhos de uma vez,
    mas gasta muito menos memoria (no tabuleiro 800x800 cada estado teria 640 mil filhos).
    """
    total_casas = n * n
    comeco = time.perf_counter()
    rng = np.random.default_rng(semente)
    sorteio = rng.permutation(total_casas)      # desempate sorteado (depende da semente)

    def melhores_casas(estado, k):
        """As k melhores casas vazias (menor numero de ataques novos primeiro)."""
        novos = ataques_novos(n, estado)
        if usar_mrv:
            # Desempate "MRV": entre casas com o mesmo h, prefere a que esta numa
            # linha/coluna com POUCAS casas seguras (resolve primeiro o mais dificil).
            seguras = (novos == 0)
            seg_lin = seguras.sum(axis=1)
            seg_col = seguras.sum(axis=0)
            dificuldade = (seg_lin[:, None] * (n + 1) + seg_col[None, :]).ravel()
            chave = novos.ravel() * (total_casas * (n + 1) * (n + 1)) + dificuldade * total_casas + sorteio
        else:
            chave = novos.ravel() * total_casas + np.arange(total_casas)   # desempate: linha a linha
        if len(estado) > 0:
            chave[list(estado)] = np.iinfo(np.int64).max                   # casas ocupadas
        k = min(k, total_casas - len(estado))
        if k < total_casas - len(estado):
            candidatas = np.argpartition(chave, k - 1)[:k]
        else:
            candidatas = np.flatnonzero(chave < np.iinfo(np.int64).max)
        candidatas = candidatas[np.argsort(chave[candidatas], kind="stable")]
        return candidatas.tolist(), novos.ravel()[candidatas].tolist()

    guardados = {}                               # memoria curta para nao recalcular

    def filhos_de(estado, posicao):
        """Lista (casas, deltas) ordenada, garantindo que a 'posicao' pedida exista."""
        g = guardados.get(estado)
        livres = total_casas - len(estado)
        if g is None or (posicao >= len(g[0]) and len(g[0]) < livres):
            k = 2 * n + 64 if g is None else 4 * len(g[0])
            g = melhores_casas(estado, max(k, posicao + 1))
            if len(guardados) > 64:
                guardados.clear()
            guardados[estado] = g
        return g

    fronteira = []                               # fila de prioridade
    vistos = {()}                                # estados que ja apareceram
    contador = 0                                 # desempate por ordem de chegada
    expandidos = 0
    gerados = 0                                  # contagem "padrao": todos os filhos de cada no expandido
    maior_fronteira = 0
    ultimo_f = 0

    def colocar_na_fronteira(estado, h, posicao):
        nonlocal contador, maior_fronteira
        if posicao >= total_casas - len(estado):
            return
        casas, deltas = filhos_de(estado, posicao)
        g_filho = len(estado) + 1
        h_filho = h + deltas[posicao]
        f = g_filho + h_filho if algoritmo == "astar" else h_filho
        contador += 1
        heapq.heappush(fronteira, (f, -g_filho, contador, estado, h, posicao))
        maior_fronteira = max(maior_fronteira, len(fronteira))

    def expandir(estado, h):
        nonlocal expandidos, gerados
        expandidos += 1
        if len(estado) < n:
            gerados += total_casas - len(estado)
            colocar_na_fronteira(estado, h, 0)

    expandir((), 0)
    resultado = {"sucesso": False, "motivo": "a fronteira acabou"}
    while fronteira:
        f, _, _, pai, h_pai, posicao = heapq.heappop(fronteira)
        ultimo_f = f
        colocar_na_fronteira(pai, h_pai, posicao + 1)       # proximo filho do mesmo pai
        casas, deltas = filhos_de(pai, posicao)
        lista = list(pai)
        insort(lista, casas[posicao])
        filho = tuple(lista)
        if filho in vistos:
            continue
        vistos.add(filho)
        h_filho = h_pai + deltas[posicao]
        if len(filho) == n and h_filho == 0:                # teste de meta
            expandidos += 1
            resultado = {"sucesso": True, "rainhas": list(filho)}
            break
        expandir(filho, h_filho)
        if limite_nos and expandidos >= limite_nos:
            resultado = {"sucesso": False, "motivo": "limite de nos atingido"}
            break
        if limite_tempo and expandidos % 200 == 0 and time.perf_counter() - comeco > limite_tempo:
            resultado = {"sucesso": False, "motivo": "limite de tempo atingido"}
            break

    resultado.update(algoritmo=algoritmo, n=n, tempo=time.perf_counter() - comeco,
                     expandidos=expandidos, gerados=gerados,
                     maior_fronteira=maior_fronteira, ultimo_f=ultimo_f)
    if resultado["sucesso"]:                                # confere a resposta
        assert len(set(resultado["rainhas"])) == n
        assert contar_ataques(n, resultado["rainhas"]) == 0
    return resultado


def resolver(n, algoritmo):
    """
    A*: uma unica busca (com limite de nos para nao estourar a memoria).
    Gulosa: como o resultado depende do desempate sorteado, se uma tentativa nao
    der certo dentro do limite, tentamos de novo com outra semente.
    """
    if algoritmo == "astar":
        # Ate 8 rainhas o A* termina (alguns minutos). Acima disso ele nao termina,
        # entao o programa desiste depois de 2 minutos.
        limite = 900 if n <= 8 else 120
        return buscar(n, "astar", usar_mrv=False, limite_nos=4_000_000, limite_tempo=limite)
    limite = int(1.25 * n) + 100
    tentativas, total_nos, total_tempo = 0, 0, 0.0
    while True:
        r = buscar(n, "gulosa", semente=tentativas, limite_nos=limite)
        tentativas += 1
        total_nos += r["expandidos"]
        total_tempo += r["tempo"]
        if r["sucesso"] or tentativas >= 200:
            r.update(tentativas=tentativas, expandidos_total=total_nos, tempo_total=total_tempo)
            return r


# ----------------------------------------------------------------------
# Programa principal
# ----------------------------------------------------------------------
def desenhar(n, rainhas):
    ocupadas = set(rainhas)
    for i in range(n):
        print(" ".join("Q" if i * n + j in ocupadas else "." for j in range(n)))


def ler_entrada():
    """Le a quantidade de rainhas e o algoritmo (pela linha de comando ou perguntando)."""
    try:
        if len(sys.argv) >= 3:                  # uso: python rainhas.py 8 2
            n, opcao = int(sys.argv[1]), sys.argv[2].strip()
        else:
            n = int(input("Quantidade de rainhas: "))
            opcao = input("Algoritmo (1 = A*, 2 = Busca Gulosa): ").strip()
    except ValueError:
        sys.exit("Entrada invalida: a quantidade de rainhas deve ser um numero inteiro.")
    if n < 1:
        sys.exit("A quantidade de rainhas deve ser pelo menos 1.")
    if opcao not in ("1", "2"):
        sys.exit("Algoritmo invalido: digite 1 para A* ou 2 para Busca Gulosa.")
    return n, opcao


def main():
    n, opcao = ler_entrada()
    if n in (2, 3):
        sys.exit(f"O problema das n-rainhas nao tem solucao para n = {n}.")
    algoritmo = "astar" if opcao == "1" else "gulosa"
    nome = "A*" if algoritmo == "astar" else "Busca Gulosa"
    print(f"\nResolvendo {n} rainhas com {nome}... (pode demorar)")
    if algoritmo == "astar" and n > 8:
        print("Aviso: o A* nao consegue resolver tabuleiros grandes. Ele vai parar em 2 minutos.")
    r = resolver(n, algoritmo)

    if not r["sucesso"]:
        print(f"\nNao encontrou solucao: {r['motivo']}.")
        print(f"Nos expandidos: {r['expandidos']}   Tempo: {r['tempo']:.2f} s")
        return
    print("\nSolucao encontrada!")
    if algoritmo == "gulosa":
        print(f"Tentativas (sementes): {r['tentativas']}")
        print(f"Passos (nos expandidos), somando as tentativas: {r['expandidos_total']}")
        print(f"Tempo total: {r['tempo_total']:.2f} s")
    else:
        print(f"Passos (nos expandidos): {r['expandidos']}")
        print(f"Tempo: {r['tempo']:.2f} s")
    print(f"Pares de rainhas se atacando: {contar_ataques(n, r['rainhas'])}\n")
    if n <= 20:
        desenhar(n, r["rainhas"])
    else:
        arquivo = f"solucao_{n}_rainhas.txt"
        with open(arquivo, "w") as f:
            for casa in r["rainhas"]:
                f.write(f"linha {casa // n + 1}, coluna {casa % n + 1}\n")
        print(f"O tabuleiro e grande, entao as posicoes foram salvas em {arquivo}")


if __name__ == "__main__":
    main()
