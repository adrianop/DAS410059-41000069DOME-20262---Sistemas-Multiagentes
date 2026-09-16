# Contract Net Protocol em JaCaMo

Esta aplicação implementa o trabalho prático do PDF usando Jason dentro do JaCaMo 1.3.1.

## Modelo

- `n = 3`: `initiator1`, `initiator2` e `initiator3`.
- `m = 4`: quatro participants, todos oferecendo o serviço `delivery`.
- `i = 3`: cada initiator abre três CNPs em paralelo com objetivos Jason assíncronos (`!!contract`).
- Cada CFP é enviado aos quatro participants.
- O participant responde com uma proposta de preço fixa, permitindo estratégias diferentes: 30, 22, 27 e 18.
- O initiator coleta as propostas por mensagens, conserva a menor oferta, envia `reject` aos participantes e `award` ao vencedor.
- O vencedor simula a execução e envia `completed`.

O identificador `task(initiator, numero)` mantém contratos de initiators diferentes independentes, mesmo quando são executados simultaneamente.

## Execução

```powershell
./gradlew.bat run
```

A saída registra CFPs, propostas, adjudicações e conclusões. O aviso sobre `jason.jar` pode aparecer quando existe uma configuração global do Jason; a execução usa a versão resolvida pelo Gradle.

## Métricas e comparação

Para a análise pedida no relatório, variar `n`, `m` e `i` no arquivo `.jcm` e nos wrappers dos agentes. Para cada configuração, repetir a execução e coletar:

- tempo entre o primeiro CFP e o último `completed`;
- número de mensagens por contrato: 4 CFPs, até 4 propostas, 4 rejeições, 1 award e 1 conclusão;
- taxa de contratos concluídos;
- preço médio e menor preço escolhido;
- número de agentes e contratos simultâneos.

O critério de comparação recomendado é o tempo total por contrato concluído, acompanhado do volume de mensagens e da taxa de sucesso. Isso permite avaliar escalabilidade e custo de coordenação sem confundir desempenho com a estratégia de preço.

## Organização

- `src/agt/cnp_initiator.asl`: protocolo do initiator.
- `src/agt/cnp_participant.asl`: estratégias e resposta dos participants.
- `my1st_app.jcm`: população do SMA.
