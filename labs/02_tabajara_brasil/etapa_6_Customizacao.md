# Etapa 6 — Customização (temas, textos, mapas)

**Pré-requisitos e permissões:** iguais à Etapa 1; temas de workspace exigem admin (veja Etapa 8).

### 11.1 Temas e branding

Em **Settings**, aplique um tema (do workspace, um preset, ou cores/fontes customizadas). Ajuste também o **locale** (formatação de números e datas) e o comportamento dos filtros (instantâneo vs. botão "Aplicar" — o botão melhora performance ao reduzir execuções).

### 11.2 Text widgets

Adicione **textos em Markdown** para dar contexto: títulos, seções e narrativa de dados. Você pode inserir links e imagens (de Volumes do Unity Catalog ou URLs públicas — para imagens em Volume, é preciso conceder acesso ao arquivo).

### 11.3 Mapas

- **Choropleth:** colore regiões por um valor agregado — por exemplo, receita por `state` (os valores precisam bater com nomes reconhecidos).
- **Point map:** plota marcadores a partir de `latitude` e `longitude` — perfeito para as lojas em `dim_stores`.

### 11.4 Exercício prático — "Deixe o painel com a cara da TabajaraBrasil"

**Objetivo:** aplicar identidade visual, contexto e um mapa.

1. **Tema:** em **Settings**, aplique um tema (preset ou cores da marca). Repare como os gráficos existentes mudam de cor.
2. **Text widget (título/narrativa):** adicione no topo um widget de texto em Markdown, por exemplo:
   `## TabajaraBrasil — Painel de Vendas` e uma linha explicando o período e a fonte dos dados.
3. **Mapa de lojas (Point map) — passo a passo.**

   Um *point map* coloca um ponto por par latitude/longitude. Ele precisa de **uma linha por loja** com as coordenadas e uma métrica; por isso, primeiro criamos um dataset agregado por loja.

   a. **Data → Add SQL dataset**, cole isto e renomeie para **`vendas_por_loja`**:
   ```sql
   SELECT
     s.store_id, s.store_name, s.city, s.state,
     s.latitude, s.longitude,
     SUM(f.sales_amount) AS total_vendas
   FROM dbacademy.workshop_aibi.fact_sales f
   JOIN dbacademy.workshop_aibi.dim_stores s ON f.store_id = s.store_id
   GROUP BY s.store_id, s.store_name, s.city, s.state, s.latitude, s.longitude
   ```
   b. No **Canvas**, adicione uma visualização → **Visualization: Point map**. Dataset: **`vendas_por_loja`**.
   c. No painel direito, mapeie as coordenadas: **Latitude** = `latitude`, **Longitude** = `longitude` (são os campos que posicionam cada ponto no mapa).
   d. **Size** (tamanho do ponto) = `total_vendas` → as lojas que mais vendem aparecem como pontos maiores. (Opcional: **Color** = `state`.)
   e. **Tooltip:** adicione `store_name` e `total_vendas` para, ao passar o mouse, ver o nome e a receita.
   f. Title = "Lojas por receita".

4. **Mapa por estado (Choropleth) — passo a passo.**

   Um *choropleth* colore áreas geográficas (estados, países…) conforme um valor. Aqui, receita por estado.

   a. Você pode usar o dataset **`vendas_detalhe`** direto (tem `state` e `sales_amount`).
   b. Adicione uma visualização → **Visualization: Choropleth map**. Dataset: `vendas_detalhe`.
   c. **Region** (canto superior direito): deixe **Administrative**.
   d. No slot **State/Province**, clique no **+** e escolha o campo **`state`** (as siglas SP, RJ, MG…). **Importante:** coloque em **State/Province**, não em Country. (Se quiser colorir por país, use `country` no slot **Country** — mas no Brasil o interessante é por estado.)
   e. Ao adicionar o campo, defina o **Geographic role = `2-letter`** (sigla de 2 letras), porque `state` está em siglas. Selecione o país **Brasil** se o mapa pedir o contexto.
   f. **Color** = `sales_amount` com agregação **SUM** → estados com mais receita ficam mais escuros.
   g. Title = "Receita por estado".

   > **Troubleshooting "unknowns":** se o mapa mostrar "unknowns" ou não colorir, quase sempre é (1) campo no slot errado, ou (2) **Geographic role** que não bate com o formato do dado (sigla → `2-letter`; nome completo → `Name`). Um pequeno "unknowns" residual na legenda é só a fatia sem região reconhecida e não afeta o mapa.

> **Dica:** ative o botão "Aplicar" nos filtros (em vez de instantâneo) se o painel tiver muitos widgets — reduz execuções e melhora a performance ao vivo.

[FIM]