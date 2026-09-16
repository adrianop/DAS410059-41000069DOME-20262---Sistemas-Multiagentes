# CNP em MASPY

Implementação do Contract Net Protocol em [MASPY](https://github.com/laca-is/MASPY),
alternativa em Python ao Jason/JaCaMo (pasta `../np1.3`), para comparação das
duas linguagens conforme pedido no enunciado (`../tp-cnp.pdf`, seção
"Alternativa").

## Requisitos

MASPY (`maspy-ml` no PyPI) exige **Python 3.12+**. Se só houver versões
anteriores instaladas, instale o 3.12 (ex.: `winget install Python.Python.3.12`
no Windows) e crie um venv dedicado:

```bash
py -3.12 -m venv .venv-maspy
.venv-maspy/Scripts/activate      # Windows
pip install -r requirements.txt
```

## Executar

```bash
python cnp_maspy.py --n 3 --m 4 --i 1
```

- `n`: número de agentes *Initiator* (1 < n < 200)
- `m`: número de agentes *Participant* (1 < m < 50)
- `i`: contratos paralelos por Initiator (0 < i < 10)

## O que o script faz

- `Initiator`: para cada um dos `i` contratos, envia `cfp` (call for proposal)
  em broadcast para todos os `Participant`s, espera `CFP_TIMEOUT` segundos,
  escolhe a proposta de menor preço, envia `award` ao vencedor e `reject` aos
  demais.
- `Participant`: responde a `cfp` com `propose` usando uma de três estratégias
  de preço rotacionadas entre os agentes (`fixed_price`, `randomized_price`,
  `eager_price` — fica mais barato a cada proposta), atendendo ao pedido do
  enunciado por "estratégias de proposta diferenciadas". Ao ganhar (`award`),
  "executa" o serviço e envia `completed`.

Os `i` contratos de um mesmo Initiator rodam de fato em paralelo (uma thread
por contrato, via `max_intentions` do MASPY), assim como os `n` Initiators e
`m` Participants (cada Agent MASPY roda em sua própria thread).
