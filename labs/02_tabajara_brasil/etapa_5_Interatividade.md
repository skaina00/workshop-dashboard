<img src="../../imagens/header_01.png">

# Etapa 5 — Interatividade (filtros, parâmetros, variáveis, cross-filter)

**Pré-requisitos e permissões:** iguais à Etapa 1.

**O que é "interatividade" num dashboard?** É dar ao **quem consome** o painel o poder de explorar os dados sozinho — recortar por período, região, categoria — sem pedir um novo relatório. Em vez de um retrato fixo, o dashboard vira uma ferramenta de investigação.

**Por que investir nisso:**
- **Autonomia:** o gestor responde as próprias perguntas ("e só no Sudeste?", "e no verão?") na hora.
- **Um painel serve a muitos:** o mesmo dashboard atende diretor, gerente regional e analista — cada um filtra o seu recorte.
- **Menos retrabalho:** você não precisa clonar o dashboard para cada visão.

A Databricks oferece quatro mecanismos, do mais simples ao mais poderoso: **filtros de campo → parâmetros → cross-filter → variáveis de dashboard**. Abaixo, o que é cada um e **quando** usar.

### 10.1 Filtros de campo (field filters)

**Definição:** um controle que filtra por uma **coluna** do dataset. É aplicado **no navegador**, sobre os dados já carregados.

**Por que/quando usar:** é o filtro do dia a dia — rápido de configurar e ideal para volumes pequenos/médios. Um mesmo filtro pode se conectar a **vários datasets** ao mesmo tempo, e filtros podem **cascatear** (escolher uma região ajusta os valores disponíveis em outro filtro).

**Exemplos (TabajaraBrasil):**
- **Date Range Picker** ligado a `sale_date` (preset "últimos 12 meses").
- Filtro de **valor único/múltiplo** em `region` ou em `season`.

### 10.2 Parâmetros

**Definição:** um valor **injetado no SQL** do dataset em tempo de execução, com a sintaxe `:nome`. Diferente do filtro de campo, o parâmetro age **antes da agregação**, dentro da consulta.

**Por que/quando usar:** ideal para **dados grandes** (filtra no banco, não no navegador — mais performático) e quando o filtro precisa entrar em pontos específicos do SQL (um `WHERE`, um `TOP N`, um cálculo). Também dá uma lista de opções **validada**.

```sql
-- Exemplo de dataset parametrizado
SELECT c.segment, SUM(f.sales_amount) AS receita
FROM dbacademy.workshop_aibi.fact_sales    f
JOIN dbacademy.workshop_aibi.dim_customers c ON f.customer_id = c.customer_id
WHERE c.segment = :segment
GROUP BY c.segment;
```

Depois adicione um widget de filtro conectado ao parâmetro `:segment` e defina um valor padrão. Para uma lista validada de opções, crie um segundo dataset com os valores distintos de `segment`.

> **Campo vs. parâmetro — regra prática:** dados pequenos e filtro "solto" → **filtro de campo**; dados grandes ou filtro que precisa entrar no SQL → **parâmetro**.

### 10.3 Tipos de filtro

**Definição:** o **formato do controle** que o usuário vê. Escolha conforme o tipo de campo:
- **Múltiplos valores / valor único** — listas (ex.: `region`, `segment`).
- **Date picker / Date range picker** — datas e períodos (ex.: `sale_date`), com presets.
- **Entrada de texto** (contém / exato / começa com) — busca livre (ex.: `product_name`).
- **Range slider** — faixas numéricas (ex.: `unit_price` entre X e Y).

### 10.4 Cross-filtering e drill-through

**Definição:** **cross-filter** = clicar em um ponto de um gráfico (ex.: uma barra de categoria) filtra automaticamente os demais gráficos por aquela seleção. **Drill-through** = navegar de uma visão geral para o detalhe.

**Por que/quando usar:** exploração rápida e intuitiva — o usuário "clica e investiga" sem configurar filtro. O estado dos filtros fica na **URL**, então você pode **salvar/compartilhar** uma visão já filtrada (ex.: mandar o link já no recorte "Cono Sur, verão").

### 10.5 Dashboard variables (troca de métrica)

**Definição:** um controle que troca **qual campo/métrica** um gráfico exibe (não filtra linhas — troca o que é medido).

**Por que/quando usar:** quando você quer um único gráfico que o usuário alterna entre métricas — ex.: ver a mesma tendência mensal como **receita** (`sales_amount`), **quantidade** (`quantity`) ou **margem**. Economiza espaço e evita três gráficos quase iguais. Todos os widgets ligados à variável se atualizam juntos.

### 10.6 Exercício prático — "Deixe o painel explorável"

**Objetivo:** tornar o dashboard da TabajaraBrasil interativo.

**Como adicionar um filtro (vale para todos abaixo):**

1. No **Canvas**, na barra de ferramentas inferior, clique no ícone de **filtro** (funil) e desenhe o widget na tela. O painel de configuração abre à direita.
2. Em **Filter** (topo do painel), escolha o **tipo** de controle no dropdown: *Multiple values, Single value, Date picker, Date range picker, Text entry, Range slider*.
3. Na seção **Fields**, clique no **+** e escolha o **dataset** (`vendas_detalhe`) e a **coluna** que o filtro vai controlar. (Um mesmo filtro pode conectar várias colunas/datasets — repita o **+**.)
4. Marque **Title** e nomeie o filtro.

**Agora crie estes quatro filtros:**

**a) Filtro de data.** Tipo **Date range picker** → Fields **+** → `vendas_detalhe` → **`sale_date`**. Nas opções do widget, ative um preset como "últimos 12 meses". Title = "Período". Teste: mude o intervalo e veja todos os gráficos se ajustarem.

**b) Filtro de região.** Tipo **Multiple values** → Fields **+** → `vendas_detalhe` → **`region`**. Title = "Região". Selecione uma (Sudeste/Sul/Nordeste/Norte/Centro-Oeste) e observe.

**c) Filtro por estação.** Tipo **Single value** (ative "Allow All" se quiser uma opção "Todas") → Fields **+** → **`season`**. Title = "Estação". Compare "Verão" vs. "Inverno".

**d) Cross-filter.** Não é um widget: no gráfico de barras "Receita por categoria", clique numa barra. Os outros widgets filtram por aquela categoria. (Se não reagir, no menu **⋮** do gráfico confira se o cross-filter está ativo.) Clique de novo na barra para desativar.

**e) Parâmetro `:segment` (opcional, avançado).**
- Crie um novo **Add SQL dataset** com a consulta da seção 10.2 (a que tem `WHERE c.segment = :segment`) e rode-a; a Databricks detecta o parâmetro `:segment`.
- Adicione um filtro (tipo **Single value**) e, em **Fields +**, conecte-o ao **parâmetro** `segment` (aparece junto às colunas). Defina um valor padrão.
- Teste alternando Consumer / Corporate / Home Office.

> **Desafio (variável de métrica):** crie uma dashboard variable que alterna entre `sales_amount`, `quantity` e `margem`, e ligue-a ao eixo Y do gráfico de linha — um só controle troca a métrica de todos os gráficos conectados.

**Resolução do Desafio — SPOILER (tente sozinho antes de ler!)**

<details>

1. Adicione um **widget de filtro** (ícone de funil) e escolha o tipo **Single value**.
2. Em **Fields +**, em vez de uma coluna, use a opção de criar/usar uma **variável**: defina um conjunto de campos selecionáveis — adicione **`sales_amount`**, **`quantity`**. Nomeie a variável, ex.: `metrica`.
3. Para cada campo, defina a **transformação/agregação** (SUM) e um **Display name** ("Receita", "Quantidade", "Margem").
4. Abra o **gráfico de linha** (receita por mês). No **eixo Y**, em vez de fixar `sales_amount`, selecione a **variável `metrica`**.
5. Agora o controle da variável, no topo do dashboard, alterna as três métricas — e o eixo Y do gráfico muda ao vivo. Conecte a mesma variável a outros gráficos para todos mudarem juntos.

**Ideia-chave:** uma variável de dashboard **não filtra linhas** — troca *o que é medido*. Por isso ela se conecta ao **eixo/encoding** do gráfico, não a um `WHERE`.

</details>

[FIM]