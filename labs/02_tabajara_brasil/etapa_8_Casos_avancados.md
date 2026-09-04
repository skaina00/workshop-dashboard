# Etapa 8 — Casos avançados (bônus completo)

Estes tópicos vão além do workshop ao vivo. Eles respondem à pergunta: *"O painel ficou ótimo — como levo isso a nível de **empresa**: confiável, reutilizável, versionado e monitorado?"*. Aqui saímos do "dashboard bonito no meu workspace" para "plataforma de BI governada".

### 13.1 Metric views no Unity Catalog (camada semântica governada)

**O que é:** uma **metric view** é um objeto no Unity Catalog que define suas métricas (medidas) e dimensões **uma única vez**, de forma **governada** — como uma "planilha-mãe de fórmulas" oficial da empresa. Diferente do cálculo personalizado (que vive dentro de **um** dashboard), a metric view é **compartilhada**: dashboards, Genie, notebooks e ferramentas externas (Power BI, Tableau) consomem a mesma definição.

**Por que usar:** acabar com o "cada área calcula receita/margem de um jeito". A regra fica em um lugar; se mudar, muda para todos. É a diferença entre cada pessoa ter sua receita de bolo e a empresa ter uma receita oficial.

**Como usar:**
- Define-se em **YAML** (ou pela UI). Ao consultar, **toda medida vai dentro de `MEASURE()`**, e **nunca** `SELECT *`. Para juntar com outra tabela, envolva a metric view numa CTE primeiro.

```sql
-- Consumindo a metric view
SELECT category, MEASURE(receita_total) AS receita
FROM dbacademy.workshop_aibi.mv_vendas
GROUP BY category;
```

**Exemplo (TabajaraBrasil):** uma `mv_vendas` com `receita_total = SUM(sales_amount)` e `margem = SUM(sales_amount) - SUM(quantity*unit_cost)` vira a fonte oficial — o time de marketing e o financeiro passam a ver **o mesmo** número de margem.

Recursos que a metric view habilita:
- **Joins:** enriquece o fato com dimensões (star/snowflake), cardinalidade many-to-one por padrão. *Ex.:* ligar `fact_sales` a `dim_products` para medir por categoria.
- **Agent metadata:** *display names*, **sinônimos** e formatação (moeda, %, data). *Por quê:* o Genie entende "faturamento" como `receita_total` e já formata em R$. *Ex.:* sinônimos `["faturamento","vendas","receita"]`.
- **Window measures:** medidas de janela — média móvel 7 dias, YoY (ano contra ano), acumulado — via `order`/`range`. *Ex.:* "crescimento vs. mesmo mês do ano passado".
- **Materialization:** pré-calcula agregações para acelerar (exige serverless + DBR 17.3+). *Quando:* consultas frequentes e pesadas.

### 13.2 Automação (dashboards como código)

**O que é:** tratar o dashboard como um **arquivo/código** que pode ser exportado, versionado e recriado — em vez de algo que só existe clicado na tela.

**Por que usar:** para **migrar** entre workspaces (dev → prod), **versionar** (histórico, reverter, revisar em PR) e **replicar** dashboards em escala. É o mesmo princípio de "infra como código", aplicado a BI.

**Como usar / exemplos:**
- **Import/Export:** exporte o rascunho como **`.lvdash.json`** (contém queries + widgets) e importe em outro workspace. *Ex.:* levar o painel da TabajaraBrasil do workspace de testes para o de produção.
- **Git folders:** versione os rascunhos em Git (histórico, PRs). *Atenção:* só rastreia rascunhos; máx. 100 dashboards/pasta; trocar de branch é destrutivo (o dashboard some nas branches que não o têm).
- **APIs:** **Lakeview API** (objetos de dashboard), **Workspace API** (permissões, export/import) e **Genie API** (conversas). Use `serialized_dashboard`, `etag` (controle otimista) e publique com `embed_credentials`. *Ex.:* um pipeline de CI que publica o dashboard toda vez que a branch `main` muda.

### 13.3 Embedding externo

**O que é:** exibir o dashboard **fora** do Databricks — num site público ou app — para pessoas **sem conta** Databricks.

**Por que usar:** compartilhar indicadores com clientes/parceiros externos, ou embutir num portal da empresa.

**Como usar:** crie um **service principal**, gere segredo OAuth, dê **CAN RUN** ao SP no dashboard e faça a troca por um token de usuário com escopo restrito. Requer domínios aprovados pelo admin. *Limitação:* **Ask Genie indisponível** no embedding externo (use a Genie Conversation API). *Ex.:* a TabajaraBrasil embute um painel de vendas resumido no portal de fornecedores.

> **Básico vs. externo:** o embedding **básico** (Etapa 7) é para quem **tem** conta Databricks; o **externo** é para quem **não tem** — e por isso exige o service principal.

### 13.4 Caching, limites e monitoramento

**O que é e por que importa:** entender como o dashboard se comporta em produção — velocidade, teto de tamanho, e quem está usando.

- **Caching:** cache de resultados por até 24h; servir do cache **não liga** o warehouse (mais barato e rápido). *Exemplo prático:* 50 pessoas abrindo o mesmo dashboard publicado batem no cache compartilhado — o warehouse nem acorda.
- **Limites (principais):** 15 páginas/dashboard; 100 datasets/dashboard; 100 widgets/página; filtros até 100.000 valores distintos; gráficos até 10.000 linhas, tabelas até 100.000. *Por quê saber:* evita surpresas ao escalar (ex.: uma tabela gigante não renderiza além do limite).
- **Monitoramento de uso:** consulte `system.access.audit` (ações `createDashboard`, `getPublishedDashboard`…) para ver **quem acessou** e **quais dashboards são populares**. *Ex.:* justificar a manutenção de um painel mostrando 300 acessos/mês. Exige acesso a system tables (admin de conta/metastore).

### 13.5 Admin (o que um admin configura ao redor do workshop)

**O que é:** as configurações de **plataforma** que habilitam ou restringem o que os autores/visualizadores podem fazer — normalmente feitas por um **workspace admin**, não pelo autor do dashboard.

**Exemplos:** temas de workspace (branding padrão), domínios de embedding aprovados, destinos de Slack/Teams para subscriptions, entitlements (Databricks SQL vs. Consumer), restrições de download de SQL, IP access lists e enforcement de **row/column-level security** (cada pessoa vê só as linhas/colunas que pode). *Por quê importa:* muitos recursos das etapas anteriores (temas, Slack, embedding) **dependem** de o admin ter habilitado antes.

### 13.6 Exercício prático — "Suba a TabajaraBrasil para nível de produção"

**Objetivo:** experimentar três recursos avançados sobre o painel já criado. (A metric view requer DBR 17.3+/serverless.)

**Parte 1 — Criar uma metric view governada (`mv_vendas_metric_view`).**

Importante: Esse passo **somente** pode ser executado por um administrador do schema onde o metric view será gravado.

1. No workspace, vá em **New → Query** (ou abra o SQL Editor). Vamos criar a metric view em **YAML**, direto por SQL:
   ```sql
   CREATE VIEW dbacademy.workshop_aibi.mv_vendas_metric_view
   WITH METRICS
   LANGUAGE YAML
   AS $$
   version: 0.1
   source: |
     SELECT f.*, p.unit_cost, p.category, p.season, s.region, c.segment
     FROM dbacademy.workshop_aibi.fact_sales f
     JOIN dbacademy.workshop_aibi.dim_products  p ON f.product_id  = p.product_id
     JOIN dbacademy.workshop_aibi.dim_stores    s ON f.store_id    = s.store_id
     JOIN dbacademy.workshop_aibi.dim_customers c ON f.customer_id = c.customer_id
   dimensions:
     - name: category
       expr: category
     - name: region
       expr: region
     - name: segment
       expr: segment
   measures:
     - name: receita_total
       expr: SUM(sales_amount)
       synonyms: ["faturamento", "vendas", "receita"]
     - name: margem
       expr: SUM(sales_amount) - SUM(quantity * unit_cost)
   $$;
   ```
2. **Consulte** a metric view (repare no `MEASURE()`):
   ```sql
   SELECT category, MEASURE(receita_total) AS receita, MEASURE(margem) AS margem
   FROM dbacademy.workshop_aibi.mv_vendas_metric_view
   GROUP BY category
   ORDER BY receita DESC
   ```
3. **Use no dashboard:** crie um **Add SQL dataset** com essa consulta, ou selecione a `mv_vendas` diretamente em **Add data**. Agora "receita" e "margem" vêm da fonte oficial.
4. **Genie entende os sinônimos:** no Ask Genie, pergunte *"qual o faturamento por categoria?"* — graças ao sinônimo, ele mapeia "faturamento" → `receita_total`.

**Parte 2 — Dashboard como código (export).**

5. No rascunho do dashboard, **⋮ → File actions → Export** e baixe o **`.lvdash.json`**. Abra o arquivo: ele contém as queries + widgets. É esse arquivo que você versiona no Git ou importa em outro workspace (**Import dashboard**).

**Parte 3 — Monitoramento de uso (se tiver acesso a system tables).**

6. Rode:
   ```sql
   SELECT action_name, COUNT(*) AS eventos
   FROM system.access.audit
   WHERE action_name IN ('createDashboard','getPublishedDashboard')
     AND event_date >= current_date() - INTERVAL 7 DAYS
   GROUP BY action_name
   ```
   Isso mostra quantos dashboards foram criados e quantas vezes os publicados foram abertos na última semana.

> **A grande ideia da Etapa 8:** sair de "um dashboard bonito no meu workspace" para "**métrica oficial, versionada e monitorada**, reutilizável pela empresa inteira". A metric view é o coração disso — a mesma definição de receita/margem alimenta dashboards, Genie e BI externas.

[FIM]