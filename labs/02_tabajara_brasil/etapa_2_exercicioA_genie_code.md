# Etapa 2 — Exercício A: criação agêntica com IA (Genie Code)

**Pré-requisitos e permissões:** Genie Code habilitado no workspace; as mesmas permissões da Etapa 1. Para o Genie encontrar as tabelas, você precisa de `SELECT` nelas.

### 7.1 A ideia

O **Genie Code** (também chamado de dashboard agent, no modo Agent) transforma um **pedido em linguagem natural** em datasets, consultas e visualizações — inclusive uma página inteira. É como ter um analista que monta o rascunho para você; depois você refina.

### 7.2 Passo a passo

**1.** Em um dashboard novo (ou no mesmo), clique no ícone de **Genie / sparkle** para abrir o Genie Code.




**2.** Envie o prompt abaixo (você pode marcar tabelas com `@`):

```
Crie uma página de visão geral de vendas usando as tabelas
dbacademy.workshop_aibi.fact_sales, dim_products, dim_stores e dim_customers.
Mostre: 1) counters de Receita total (soma de sales_amount), Nº de pedidos e Ticket médio;
2) receita por mês em gráfico de linha usando sale_date;
3) top 10 produtos por receita em barras;
4) receita por região (dim_stores.region);
5) receita por segmento de cliente (dim_customers.segment) em pizza.
Nomeie o dataset principal como 'vendas_overview' e adicione um texto explicativo no topo.
```

**3.** O Genie vai propor uma estrutura (datasets + widgets). Revise e aprove.

**4.** **Refine iterativamente** — mande pedidos como:

   - "Adicione um KPI de ticket médio ao lado da receita total."
   - "Explique a variação de receita em dezembro."
   - "Troque o gráfico de pizza por um de barras horizontais."

**Dica de bom prompt:** seja específico sobre entradas (tabelas), saídas (quais gráficos), nomes (do dataset) e peça esclarecimento quando não tiver certeza. Prompts vagos geram resultados vagos.

**[SUBSTITUA AQUI]** se usar dados próprios, cite as suas tabelas e colunas no prompt.


[FIM]