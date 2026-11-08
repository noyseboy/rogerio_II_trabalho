# Problema das n-Rainhas com A* e Busca Gulosa

Trabalho da disciplina de **Inteligência Artificial** 
(Módulo III)

Tecnólogo em Análise e Desenvolvimento de Sistemas, IFPI Campus Picos

Professor: Rogério Figueredo de Sousa

**Alunos:** 
- José Neres Gomes da Silva Filho
- Tiago Moura e Silva

## Sobre o projeto

O problema das n-rainhas pede para colocar n rainhas em um tabuleiro n × n sem que duas fiquem na mesma linha, coluna ou diagonal.

O programa resolve o problema com dois algoritmos de busca com informação:

- **A\***, com formulação incremental: o estado inicial tem 0 rainhas e cada ação adiciona uma rainha em qualquer casa vazia.
- **Busca Gulosa**, com a mesma formulação.

Nos dois casos, a heurística é a quantidade de pares de rainhas que se atacam, direta ou indiretamente, e o custo de gerar um novo estado é 1.

O relatório (pasta `relatorio`) traz a formulação do problema e a análise da execução com 8, 80 e 800 rainhas, considerando passos (nós expandidos) e tempo, com gráficos.

## Conteúdo da pasta

| Arquivo ou pasta | Descrição |
|---|---|
| `rainhas.py` | O programa. Recebe a quantidade de rainhas e o algoritmo. |
| `experimentos.py` | Repete os testes com 8, 80 e 800 rainhas (opcional, leva cerca de 15 minutos). |
| `graficos.py` | Gera os gráficos do relatório a partir dos resultados (opcional). |
| `resultados/` | Números (`resultados.json`) e gráficos (`.png`) usados no relatório. |
| `relatorio/` | Relatório em Word (`Relatorio_nRainhas.docx`). |

## Requisitos

- Python 3 (testado com a versão 3.12)
- NumPy

```
pip install numpy
```

Só para rodar `graficos.py` é preciso também o matplotlib (`pip install matplotlib`). O `experimentos.py` funciona em Windows, Linux e macOS (só não mede a memória no Windows).

## Como executar

Abra o terminal na pasta do trabalho e rode:

```
python rainhas.py
```

O programa pergunta:

```
Quantidade de rainhas: 8
Algoritmo (1 = A*, 2 = Busca Gulosa): 2
```

Também é possível informar tudo de uma vez:

```
python rainhas.py 8 2
python rainhas.py 80 2
python rainhas.py 800 2
python rainhas.py 8 1
```

Em alguns sistemas o comando é `python3`.

### O que o programa mostra

- se encontrou a solução;
- a quantidade de passos (nós expandidos);
- o tempo gasto;
- a conferência da resposta (pares de rainhas que se atacam, que deve ser 0);
- o tabuleiro, quando n é no máximo 20. Para n maior, as posições são salvas em `solucao_<n>_rainhas.txt`.

## Resultados

Medidos em Python 3.12, com um núcleo de processador. Os tempos mudam de um computador para outro, mas os passos não.

| Algoritmo | Rainhas | Resolveu? | Passos | Tempo |
|---|---|---|---|---|
| A* | 8 | Sim | 2.741.210 | cerca de 6 min |
| A* | 80 | Não (parou em 60 s no teste) | 412.400 até parar | 60 s |
| A* | 800 | Não (parou em 60 s no teste) | 8.800 até parar | 60 s |
| Busca Gulosa | 8 | Sim | 9 | menos de 0,01 s |
| Busca Gulosa | 80 | Sim | 81 | cerca de 0,01 s |
| Busca Gulosa | 800 | Sim | 1.901 (2 tentativas) | cerca de 18 s |

### O que esperar ao executar

- **Busca Gulosa:** resolve 8, 80 e 800 rainhas. Com 800 leva de 10 a 40 segundos. O número de tentativas pode variar um pouco de um computador para outro (depende da versão do NumPy), mas o programa sempre tenta de novo até acertar.
- **Entradas sem solução:** para 2 e 3 rainhas o problema não tem solução, e o programa avisa.
- **A\* com 8 rainhas:** leva alguns minutos e usa cerca de 800 MB de memória. Com 6 rainhas termina em cerca de 1 segundo, se quiser um teste rápido.
- **A\* com 80 ou 800 rainhas:** não termina. O número de nós a expandir cresce de 9 a 14 vezes a cada rainha a mais, então o programa avisa e desiste sozinho depois de 2 minutos. O relatório explica o motivo.

## Detalhes de implementação

- Um estado é a lista (ordenada) das casas com rainha. Estados repetidos, isto é, o mesmo conjunto de rainhas colocado em outra ordem, são descartados.
- A heurística h conta os pares de rainhas na mesma linha, coluna ou diagonal, mesmo que haja outra rainha entre elas. Ao colocar uma rainha, h aumenta pela soma das rainhas já presentes em sua linha, coluna e diagonais. Esse valor é calculado para todas as casas de uma vez com NumPy.
- A* ordena a fronteira por `f = g + h`. A Busca Gulosa ordena por `f = h`. Em empate de f, sai primeiro o estado com mais rainhas.
- Os sucessores de um estado são gerados um por vez, do melhor para o pior. A ordem de expansão é a mesma de quem gera todos de uma vez, mas gasta muito menos memória.
- **Desempate da Busca Gulosa:** muitas casas têm o mesmo h. O programa desempata preferindo a casa cuja linha e coluna têm menos casas livres de ataque, e depois usa uma ordem sorteada por uma semente. Se uma tentativa passa do limite de passos, o programa tenta de novo com a próxima semente. Os passos e o tempo informados somam todas as tentativas.
- Toda solução encontrada é conferida no final, recalculando h do zero.

Mais detalhes, tabelas e gráficos estão no relatório.
