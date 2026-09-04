# Etapa 7 — Publicar e compartilhar (permissões, subscriptions, Genie Space, embedding)

**Pré-requisitos e permissões:** CAN MANAGE para publicar e definir permissões; para agendar/entregar, o admin precisa habilitar e-mail/Slack/Teams no workspace.

### 12.1 Publicar e os dois modelos de dados

Ao publicar, você escolhe **como os visualizadores acessam os dados**:

- **Credenciais do publicador (shared):** os visualizadores rodam as consultas "como você" — não precisam de acesso direto às tabelas. Ideal para compartilhamento amplo.
- **Credenciais do visualizador (individual):** cada um usa as próprias permissões do Unity Catalog — precisa ter acesso às tabelas. Ideal quando você quer respeitar row/column-level security por pessoa.

**Analogia:** credenciais do publicador é como um guia de museu que mostra as salas para todos; credenciais do visualizador é dar a cada pessoa a própria chave — só entra nas salas a que tem direito.

### 12.2 Audiência

Compartilhe com usuários/grupos específicos do workspace, da conta, ou com "Qualquer pessoa da minha conta". Lembre: **os visualizadores não precisam de acesso ao workspace** — qualquer membro registrado na conta pode ver um dashboard publicado.

### 12.3 Schedules e subscriptions

Agende atualizações (frequência ou cron) e entregue snapshots por **e-mail (PDF)**, **Slack** ou **Teams** (PNG no canal). Limite: 100 assinantes por schedule; anexos com limites de tamanho/linhas.

### 12.4 Genie Space (Ask Genie)

Ao publicar com Genie habilitado, é criado um **Genie Space companheiro**: os visualizadores clicam em **Ask Genie** e fazem perguntas em linguagem natural.

**Ressalva de governança (importante):** no Genie Space, o visualizador pode consultar o **resultado completo do dataset**, inclusive **colunas sensíveis que não aparecem nos gráficos**. Por isso, cuidado com o que você traz no dataset (reforça a regra de não usar `SELECT *`) e escolha o modelo de credenciais adequado.

### 12.5 Noção de embedding

Você pode **embutir** o dashboard publicado em sites/apps via iframe. **Básico:** os visualizadores entram com as credenciais Databricks deles. **Externo:** usa um service principal + token OAuth para pessoas sem conta Databricks (mais avançado — veja Etapa 8).

### 12.6 Exercício prático — "Publique e entregue o painel"

**Objetivo:** publicar o dashboard da TabajaraBrasil e configurar uma entrega.

1. Clique em **Publish**. Escolha o modelo de dados: para o workshop, use **credenciais do publicador (shared)** — assim quem receber vê os dados sem precisar de acesso direto às tabelas.
2. Em **Share**, compartilhe com um colega (ou com "Qualquer pessoa da minha conta pode ver") no nível **CAN VIEW**.
3. Copie o **link do dashboard publicado** e abra em uma aba anônima/como visualizador para ver o que o público enxerga.
4. **Subscription:** crie um agendamento (ex.: toda segunda 8h) entregando um snapshot por **e-mail (PDF)**. (Se o admin tiver habilitado Slack/Teams, experimente entregar num canal.)
5. **Ask Genie:** com Genie habilitado na publicação, abra o dashboard publicado e clique em **Ask Genie**; pergunte em linguagem natural, ex.: *"Qual foi a receita da região Sudeste no último trimestre?"*

> **Ponto de governança para discutir:** no Ask Genie o visualizador pode consultar o **resultado completo do dataset** (inclui colunas não mostradas nos gráficos). Por isso trouxemos só as colunas necessárias no dataset (nada de `SELECT *`).

_Capítulo 12 de 14. Notebook-guia do workshop **AI/BI Dashboards**. Dados: `retail_synthetic_data_PT.py` (Etapa 0). Ajuste `<seu_catalogo>`/`<tu_catalogo>` onde indicado._
