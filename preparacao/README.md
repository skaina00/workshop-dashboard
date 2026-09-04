# Preparação do Ambiente — Workshop AI/BI Dashboards

Este diretório contém os notebooks que **preparam os dados** usados no workshop de
AI/BI Dashboards. Siga os passos abaixo, **na ordem**, para deixar o ambiente pronto.

| Notebook | O que faz | Tabelas criadas |
|---|---|---|
| `01_retail_synthetic_data.py` | Gera dados sintéticos de varejo (TabajaraBrasil) — 100% PySpark | `dim_customers`, `dim_products`, `dim_stores`, `fact_sales`, `fact_inventory` |
| `02_stocks_real_data.py` | Baixa cotações reais de 9 ações (Yahoo Finance / `yfinance`), últimos 2 anos | `stocks` |

Ao final, todo o conteúdo fica no catálogo **`dbacademy`**, schema **`workshop_aibi`**.

---

## Pré-requisitos

- Acesso a um **workspace Databricks** com **Unity Catalog** habilitado.
- Um **cluster** ou **compute serverless** ativo para executar notebooks Python/PySpark.
- Para o notebook `02` (cotações reais): o compute precisa de **acesso de saída à internet**
  (o driver acessa o Yahoo Finance). Em workspaces com rede restrita, use como alternativa
  a versão com dados embutidos, se disponível.
- Permissão para **criar catálogo** no metastore (perfil de administrador do workshop),
  ou peça ao administrador que execute o Passo 1.

---

## Passo 1 — Criar o catálogo `dbacademy` e liberar leitura para todos

> Execute como **administrador** do workshop (no editor de SQL ou numa célula de notebook).

Crie o catálogo:

```sql
CREATE CATALOG IF NOT EXISTS dbacademy
  COMMENT 'Catálogo do workshop AI/BI Dashboards';
```

Conceda **permissão de leitura a todos os participantes** (o grupo `account users`
representa todos os usuários da conta). Isso cobre as tabelas atuais **e futuras**
do catálogo:

```sql
GRANT USE CATALOG ON CATALOG dbacademy TO `account users`;
GRANT USE SCHEMA  ON CATALOG dbacademy TO `account users`;
GRANT SELECT      ON CATALOG dbacademy TO `account users`;
```

> Assim, qualquer participante consegue **ler** (SELECT) os dados, mas apenas quem
> tem permissão de escrita (você/admin) consegue gerar/atualizar as tabelas.

---

## Passo 2 — Importar os notebooks para o workspace

1. No workspace, entre na pasta desejada (ex.: `/Workspace/workshop/preparacao`).
2. **Import** → selecione `01_retail_synthetic_data.py` e `02_stocks_real_data.py`
   (formato *source* — são reconhecidos como notebooks automaticamente).

> Alternativa via CLI:
> ```bash
> databricks workspace import-dir preparacao /Workspace/workshop/preparacao --profile <SEU_PERFIL>
> ```

---

## Passo 3 — Executar `01_retail_synthetic_data.py`

1. Abra o notebook e conecte a um compute.
2. No topo, confira os **widgets**:
   - `catalog` = **`dbacademy`**
   - `schema`  = **`workshop_aibi`** (criado automaticamente)
3. **Run all**.

Ao final, o schema `dbacademy.workshop_aibi` terá as 5 tabelas do modelo estrela:
`dim_customers`, `dim_products`, `dim_stores`, `fact_sales`, `fact_inventory`.

---

## Passo 4 — Executar `02_stocks_real_data.py`

1. Abra o notebook e conecte a um compute **com acesso à internet**.
2. Confira os **widgets**:
   - `catalog` = **`dbacademy`**
   - `schema`  = **`workshop_aibi`**
   - `table`   = **`stocks`**
   - `anos`    = **`2`** (janela dos últimos 2 anos, dinâmica)
3. **Run all** (a primeira célula instala o `yfinance` e reinicia o Python).

Ao final, a tabela `dbacademy.workshop_aibi.stocks` terá o fechamento diário de 9 ações
(Amazon, Apple, Meta, Microsoft, NVIDIA, Oracle, Tesla, Nubank e Snowflake).

---

## Passo 5 — Conferir o conteúdo no Unity Catalog

**Pela interface:** menu **Catalog** → `dbacademy` → `workshop_aibi` → confira as 6 tabelas
e clique em **Sample Data** / **Details** para validar.

**Por SQL:**

```sql
-- Lista as tabelas criadas
SHOW TABLES IN dbacademy.workshop_aibi;

-- Sanidade rápida das contagens
SELECT 'dim_customers'  AS tabela, COUNT(*) AS linhas FROM dbacademy.workshop_aibi.dim_customers
UNION ALL SELECT 'dim_products',   COUNT(*) FROM dbacademy.workshop_aibi.dim_products
UNION ALL SELECT 'dim_stores',     COUNT(*) FROM dbacademy.workshop_aibi.dim_stores
UNION ALL SELECT 'fact_sales',     COUNT(*) FROM dbacademy.workshop_aibi.fact_sales
UNION ALL SELECT 'fact_inventory', COUNT(*) FROM dbacademy.workshop_aibi.fact_inventory
UNION ALL SELECT 'stocks',         COUNT(*) FROM dbacademy.workshop_aibi.stocks;
```

**Confirme as permissões** de leitura concedidas:

```sql
SHOW GRANTS ON CATALOG dbacademy;
```

---

## Resumo esperado

| Tabela | Linhas aproximadas |
|---|---|
| `dim_customers` | 2.000 |
| `dim_products` | 300 |
| `dim_stores` | 25 |
| `fact_sales` | ~100.000 |
| `fact_inventory` | ~180.000 |
| `stocks` | ~4.500 (9 ações × ~500 pregões) |

Com isso o ambiente está pronto para os exercícios de dashboards do workshop. ✅
