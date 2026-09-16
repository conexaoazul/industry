# DIGIMANO ONE — MVP 0.1

POC em Odoo 19 para validar continuidade do cuidado entre responsáveis/turnos.

## First Value

Um responsável:

1. identifica-se e assume o cuidado de um paciente;
2. registra eventos rápidos e estruturados durante o turno;
3. prepara a entrega com resumo cronológico;
4. informa o próximo responsável;
5. o próximo responsável confirma o recebimento e inicia um novo ciclo de cuidado.

Fluxo: **IDENTIFICAR → ASSUMIR → AVALIAR → REGISTRAR → ACOMPANHAR → ENTREGAR → RECEBER → CONTINUAR**.

## Escopo da POC

- paciente mínimo: primeiro nome + idade;
- responsável: usuário Odoo + função;
- avaliação inicial rápida;
- registros fechados/rápidos para medicamentos, alimentação, hidratação, humor, estado geral, intercorrências e observações;
- linha temporal via registros e chatter;
- handoff com resumo e confirmação;
- autoria, data e hora dos registros.

## Fora do escopo da POC

- prontuário eletrônico completo;
- prescrição clínica;
- faturamento hospitalar;
- integrações HL7/FHIR;
- dispositivos médicos;
- portal de família;
- validação regulatória para uso clínico em produção.

## Referências e dependências

O módulo `digimano_one` depende somente de `base` e `mail` do Odoo. As verticais `mental_therapy`, `physical_therapy` e demais apps do `odoo/industry` podem servir como referência de configuração/UX, mas não são dependências do núcleo.

O repositório `OCA/vertical-medical` pode ser estudado como referência de domínio. No momento da criação desta POC, sua branch padrão é 18.0, portanto qualquer reutilização em Odoo 19 exige avaliação técnica, de compatibilidade e licença.

## Próximos critérios de validação

- instalação limpa no Odoo 19;
- teste do ciclo completo de turno com dois usuários;
- impedir entrega sem próximo responsável;
- confirmar rastreabilidade de autor/data/hora;
- revisar permissões e record rules antes de qualquer uso com dados reais;
- usar somente dados fictícios na POC.
