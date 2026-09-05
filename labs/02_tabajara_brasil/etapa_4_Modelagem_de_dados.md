<img src="../../imagens/header_01.png">

# Etapa 4 — Modelagem de dados (cálculos, LOD, metric views locais, relacionamentos)

**Pré-requisitos e permissões:** iguais à Etapa 1. Alguns recursos avançados (metric views no Unity Catalog) aparecem na Etapa 8.

**O que é "modelagem de dados" num dashboard?** É o trabalho de **transformar os dados crus em métricas e estruturas prontas para analisar** — dar nome e regra de cálculo às coisas que o negócio quer medir (receita, margem, ticket médio), definir como as tabelas se conectam e em que granularidade tudo é somado. Em vez de cada gráfico refazer contas, você **modela uma vez** e reutiliza.

**Por que modelar (em vez de só arrastar colunas)?**
- **Consistência:** "margem" passa a significar a mesma coisa em todos os gráficos e para todo mundo — acaba a divergência de "cada planilha com um número".
- **Reuso:** uma medida bem definida (ex.: `margem`) serve para barras, tabelas, counters e filtros, sem recópia.
- **Manutenção:** se a regra muda (ex.: incluir frete no custo), você ajusta **num lugar só**.
- **Clareza para o negócio (e para a IA):** métricas nomeadas e com sinônimos deixam o Genie responder certo em linguagem natural.

**A Databricks oferece quatro formas de modelar, da mais simples à mais reutilizável:**

- **Datasets** — a consulta base (o que já fizemos na Etapa 1). *Quando usar:* sempre; é o ponto de partida.
- **Cálculos personalizados** — métricas/expressões dentro de um dataset. *Quando usar:* KPIs e transformações rápidas (margem, % do total) sem mexer no SQL.
- **Metric views locais** — uma camada semântica (dimensões + medidas) dentro do dashboard. *Quando usar:* quando você quer padronizar métricas do painel e talvez promover para o Unity Catalog depois.
- **Relacionamentos entre datasets** — joins definidos uma vez e reutilizados. *Quando usar:* quando você tem fato + dimensões separados e quer cruzá-los sem escrever um join gigante em cada consulta.

Nesta etapa vamos do mais simples (cálculos) ao mais estruturado (relacionamentos), usando a TabajaraBrasil.

### 9.1 Cálculos personalizados

**Definição:** são métricas ou transformações criadas **dentro de um dataset**, sem editar o SQL. Existem dois tipos:
- **Medidas** (measures) — **agregadas**, se adaptam ao agrupamento do gráfico. Ex.: `SUM(sales_amount)` vira "receita da categoria" quando o gráfico é por categoria, e "receita da região" quando é por região — a **mesma** medida.
- **Dimensões calculadas** — **não agregadas**, transformam linha a linha. Ex.: uma coluna que classifica o pedido em "com desconto" / "sem desconto".

**Por que usar:** criar KPIs rápidos e reutilizáveis (margem, ticket médio, % do total) sem tocar na consulta. Limite: **200 por dataset**.

**Exemplo (TabajaraBrasil):** a receita já vem em `sales_amount`, mas o **custo não está no fato** — está em `dim_products.unit_cost`. Então a margem precisa multiplicar `quantity * unit_cost`:

Crie estas medidas no dataset `vendas_detalhe` (as colunas já vêm do join, então use `sales_amount`, `quantity` e `unit_cost` diretamente):

```sql
-- Margem (R$): receita menos custo (custo vem de dim_products.unit_cost via join)
SUM(sales_amount) - SUM(quantity * unit_cost)
```

```sql
-- Margem (%): margem sobre receita
(SUM(sales_amount) - SUM(quantity * unit_cost)) / SUM(sales_amount)
```

### 9.2 Level of Detail (LOD) — agregar em outra granularidade

**Definição:** normalmente uma medida é calculada na granularidade do gráfico (por categoria, por mês…). **LOD** permite calcular em uma granularidade **diferente** da do gráfico — tipicamente para comparar o "pedaço" com o "todo".

**Por que usar:** o caso clássico é **percentual do total** — quero, em um gráfico por categoria, mostrar quanto **cada** categoria representa do total **geral**. Para isso o denominador precisa ignorar o agrupamento do gráfico.

**Quando usar:** % de participação, comparação de um item vs. o todo, cohort/segmento, "quanto isto representa do total da empresa".

```sql
-- % da receita: receita do grupo dividida pela receita total (LOD fixo)
SUM(sales_amount) / SUM(SUM(sales_amount)) OVER ()
```

**Como funciona:** o `SUM(sales_amount)` interno é a receita do grupo (a barra); o `SUM(...) OVER ()` calcula o total **global** (a janela `OVER ()` vazia ignora a partição do gráfico). Dividindo um pelo outro, cada barra mostra sua fatia.

**Analogia:** é como perguntar "quanto esta categoria representa do bolo inteiro?" — o denominador olha o bolo todo, não só a fatia.

### 9.3 Metric views locais

**Definição:** uma **metric view local** é uma **camada semântica dentro do dashboard** — você define dimensões, medidas e joins de forma visual, num só lugar, e todos os gráficos passam a consumir dali (em vez de cada um ter sua conta).

**Por que usar:** padronizar as métricas do painel ("receita", "margem" definidas uma vez) e prototipar sem precisar de permissão de escrita no Unity Catalog.

**Quando usar:** quando o painel cresce e você quer uma "fonte da verdade" de métricas; ou quando pretende **promover** depois essa lógica para o Unity Catalog (metric view governada — Etapa 8), reutilizável por toda a organização.

### 9.4 Relacionamentos entre datasets

**Definição:** em vez de pré-juntar tudo num único SQL, você carrega as tabelas como datasets separados e **define os relacionamentos uma vez** (Public Preview); o motor resolve os joins em tempo de execução.

**Por que usar:** evita reescrever o mesmo join em cada consulta, e os filtros passam a **propagar** entre os datasets conectados (filtrar região afeta os gráficos de vendas, produtos, etc.).

**Quando usar:** modelos multi-fato / multi-granularidade (ex.: cruzar `fact_sales` com `fact_inventory`), ou quando você quer manter as dimensões como datasets reutilizáveis.

- Relacione `fact_sales` (Muitos) → `dim_products` / `dim_stores` / `dim_customers` (Um). Cardinalidade **Many-to-One** (fato para dimensão).
- **Atenção à ordem dos campos:** o primeiro campo ancora o grafo da consulta; os demais se resolvem em relação a ele.

**Analogia:** definir o relacionamento uma vez é como registrar "todo pedido pertence a um cliente" no sistema — depois qualquer relatório entende essa ligação sem você reexplicar.

### 9.5 Exercício prático — "A TabajaraBrasil está lucrando?"

**Objetivo:** criar a medida de **margem** e ver a lucratividade por categoria.

1. Abra o dataset **`vendas_detalhe`** e clique em **Run** (para ver o resultado). O botão **`+ Add custom calculation`** fica no **canto superior direito da área do Result Table** (ao lado de *See performance / Optimize*) — **não** no menu ⋮ do dataset. Clique nele, nomeie **`margem`** e cole:
   ```sql
   SUM(sales_amount) - SUM(quantity * unit_cost)
   ```
2. Crie outra medida, **`margem_pct`**:
   ```sql
   (SUM(sales_amount) - SUM(quantity * unit_cost)) / SUM(sales_amount)
   ```
3. No **Canvas**, crie um gráfico **Bar**: eixo X = `category`, eixo Y = **`margem`**. Para **ordenar decrescente**: no painel direito, clique no ícone **⋮** ao lado de **X axis** (o do campo `category`) → **Sort** → ordene **por `margem`**, direção **Descending**. (A ordenação fica no eixo de categoria/X, não no Y. As setas ↕ entre X e Y apenas **invertem** os eixos, não ordenam.)
4. Adicione uma segunda medida ao mesmo gráfico (ou um Counter): **`margem_pct`** formatada como **porcentagem**.
5. **Leia o resultado:** quais categorias dão mais margem em R$ e quais têm a melhor margem **%**? (Às vezes a que mais fatura não é a mais lucrativa.)

> **Desafio (LOD):** crie a medida **`pct_receita`** = `SUM(sales_amount) / SUM(SUM(sales_amount)) OVER ()` e coloque numa tabela por `category` para ver a participação de cada uma no total.

**Resolução do Desafio — SPOILER (tente sozinho antes de ler!)**

<details>

1. No dataset `vendas_detalhe`, clique em **`+ Add custom calculation`** (canto superior direito do Result Table).
2. Nomeie **`pct_receita`** e cole a expressão:
   ```sql
   SUM(sales_amount) / SUM(SUM(sales_amount)) OVER ()
   ```
3. (Opcional) formate a medida como **porcentagem** nas opções do campo.
4. No **Canvas**, crie uma visualização **Table** com o dataset `vendas_detalhe`.
5. Colunas: **`category`** e **`pct_receita`** (e, se quiser, `sales_amount` para comparar valor absoluto vs. participação).
6. Ordene por `pct_receita` decrescente (clique no cabeçalho da coluna, na visualização Table).
7. **Leitura:** a soma da coluna `pct_receita` deve dar **100%** — cada linha mostra a fatia daquela categoria no total. Compare com a margem do exercício anterior: uma categoria pode ter **alta participação na receita** mas **margem baixa** (vende muito, lucra pouco), e vice-versa.

**Por que funciona:** o `OVER ()` vazio faz o denominador ser o **total geral** (ignora o agrupamento por `category` da tabela), então cada linha vira "parte / todo".

</details>

[FIM]