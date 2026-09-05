<img src="imagens/header_01.png">

# Workshop Hands-On — AI/BI Dashboards na Databricks

Treinamento **hands-on** na plataforma Databricks com foco em **Análise Exploratória** e **AI/BI Dashboards**. Os participantes constroem, do dado cru ao painel publicado e governado, dashboards interativos usando **Genie Code**, SQL, Unity Catalog e recursos de IA.

---

## ⚠️ Antes do workshop — Etapa de Preparação (time de dados)

> **Esta etapa deve ser executada com antecedência pelo time de dados / administrador do workshop** — **não** durante a sessão ao vivo. Ela cria o catálogo, gera os dados e libera o acesso de leitura a todos os participantes.

A pasta [`preparacao/`](preparacao/) contém os notebooks e o passo a passo completo:

| Notebook | O que faz | Tabelas criadas |
|---|---|---|
| `01_retail_synthetic_data.py` | Gera dados sintéticos de varejo (TabajaraBrasil), 100% PySpark | `dim_customers`, `dim_products`, `dim_stores`, `fact_sales`, `fact_inventory` |
| `02_stocks_real_data.py` | Baixa cotações reais de 9 ações (Yahoo Finance), últimos 2 anos | `stocks` |

Ao final, todo o conteúdo fica no catálogo **`dbacademy`**, schema **`workshop_aibi`**, com **leitura liberada para `account users`**. Consulte o guia detalhado em [`preparacao/README.md`](preparacao/README.md) (pré-requisitos, criação do catálogo, import dos notebooks, execução e validação).

---

## 📚 Laboratórios

Os labs ficam na pasta [`labs/`](labs/) e assumem que a etapa de preparação já foi concluída.

### [Lab 01 — Ações das Big Techs](labs/01_acoes_das_bigtechs/)
Introdução prática aos AI/BI Dashboards usando os dados de **cotações de ações** (`dbacademy.workshop_aibi.stocks`). O participante cria seu primeiro dashboard, adiciona um dataset SQL, gera gráficos com **Genie Code** em linguagem natural, aplica filtros de página e customiza o painel com imagens. Ideal como aquecimento rápido.

### [Lab 02 — TabajaraBrasil (varejo)](labs/02_tabajara_brasil/)
Laboratório completo e aprofundado, guiado por um caso de negócio de varejo (a rede fictícia **TabajaraBrasil**). Vai do zero até um dashboard publicado, compartilhado e governado, cobrindo do básico aos casos avançados. Organizado em etapas sequenciais:

| Etapa | Tema |
|---|---|
| [Etapa 0](labs/02_tabajara_brasil/etapa_0_conhecendo_os_dados.md) | Conhecendo os dados (modelo estrela de retail) |
| [Etapa 1](labs/02_tabajara_brasil/etapa_1_fundamentos.md) | Fundamentos: primeiro dashboard e dataset |
| [Etapa 2](labs/02_tabajara_brasil/etapa_2_exercicioA_genie_code.md) | Exercício A — criação agêntica com IA (Genie Code) |
| [Etapa 3](labs/02_tabajara_brasil/etapa_3_exercicioB_manual.md) | Exercício B — criação manual de visualizações |
| [Etapa 4](labs/02_tabajara_brasil/etapa_4_Modelagem_de_dados.md) | Modelagem de dados (cálculos, LOD, metric views, relacionamentos) |
| [Etapa 5](labs/02_tabajara_brasil/etapa_5_Interatividade.md) | Interatividade (filtros, parâmetros, variáveis, cross-filter) |
| [Etapa 6](labs/02_tabajara_brasil/etapa_6_Customizacao.md) | Customização (temas, textos, mapas) |
| [Etapa 7](labs/02_tabajara_brasil/etapa_7_Publicar_e_compartilhar.md) | Publicar e compartilhar (permissões, subscriptions, Genie Space, embedding) |
| [Etapa 8](labs/02_tabajara_brasil/etapa_8_Casos_avancados.md) | Casos avançados (bônus completo) |

> O material do Lab 02 vai além do que dá tempo de fazer ao vivo — serve também como guia de referência para o participante avançar no próprio ritmo.

---

## 🧭 Ordem sugerida

1. **Time de dados:** executar a [preparação](preparacao/README.md) com antecedência.
2. **Participantes:** [Lab 01](labs/01_acoes_das_bigtechs/) (aquecimento) → [Lab 02](labs/02_tabajara_brasil/) (caso completo).

---

## 📂 Estrutura do repositório

```
.
├── preparacao/     # Notebooks e guia para preparar catálogo, dados e permissões (pré-workshop)
├── labs/           # Laboratórios hands-on
│   ├── 01_acoes_das_bigtechs/
│   └── 02_tabajara_brasil/
└── imagens/        # Imagens e cabeçalhos usados nos materiais
```

## 🔧 Pré-requisitos

- Workspace **Databricks** com **Unity Catalog** habilitado.
- **SQL Warehouse** (ou compute serverless) ativo.
- Acesso de leitura ao catálogo **`dbacademy`** (concedido na etapa de preparação).
