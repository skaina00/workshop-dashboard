# Databricks notebook source
# MAGIC %md
# MAGIC # Geração de Dados Sintéticos — TabajaraBrasil (Brasil)
# MAGIC
# MAGIC Este notebook cria os dados de exemplo da **TabajaraBrasil**, uma rede de **moda** (roupas,
# MAGIC calçados e acessórios) presente em **todo o território brasileiro**. Serve como
# MAGIC **caso de uso guia** para todos os exercícios do workshop de AI/BI Dashboards.
# MAGIC
# MAGIC **5 tabelas Delta (modelo estrela):**
# MAGIC
# MAGIC - `dim_customers` (2.000) — clientes (segmento, cidade, estado, país, idade…)
# MAGIC - `dim_products` (300) — produtos de moda (categoria, subcategoria, estação, marca, custo, preço)
# MAGIC - `dim_stores` (25) — lojas em cidades brasileiras (cidade, estado, região, país, lat/long)
# MAGIC - `fact_sales` (~100.000) — vendas ao longo de 24 meses
# MAGIC - `fact_inventory` (~180.000) — snapshots mensais de estoque por loja/produto
# MAGIC
# MAGIC > **Já tem dados próprios?** Pule este notebook e aponte os exercícios para as **suas tabelas**.
# MAGIC
# MAGIC **100% PySpark nativo** — sem bibliotecas externas.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Pré-requisitos e permissões
# MAGIC
# MAGIC - Um **SQL Warehouse** ou **cluster** ativo para executar este notebook.
# MAGIC - No Unity Catalog, sobre o catálogo/schema de destino você precisa de:
# MAGIC   **`USE CATALOG`**, **`USE SCHEMA`**, **`CREATE TABLE`** e **`SELECT`**.

# COMMAND ----------

# 1) Cria os widgets de parâmetros (catálogo e schema)
dbutils.widgets.text("catalog", "dbacademy", "1. Catálogo (substitua)")
dbutils.widgets.text("schema", "workshop_aibi", "2. Schema (será criado)")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Agora ajuste o widget `catalog` e depois rode a próxima célula
# MAGIC
# MAGIC 1. No **topo do notebook**, no campo **catalog**, apague `<seu_catalogo>` e digite um catálogo onde você tem permissão de escrita (ex.: `main`, `workspace` ou seu catálogo pessoal).
# MAGIC 2. Opcional: ajuste **schema** (padrão `workshop_aibi`, será criado automaticamente).
# MAGIC 3. Só então execute a célula abaixo.

# COMMAND ----------

# 2) Le os widgets e valida (rode DEPOIS de ajustar o catalogo acima)
catalog = dbutils.widgets.get("catalog").strip()
schema = dbutils.widgets.get("schema").strip()

assert catalog and catalog != "<seu_catalogo>", (
    "⚠️ Ajuste o widget 'catalog' (no topo) com um catálogo onde você tem permissão de escrita e rode esta célula novamente."
)

fq = f"`{catalog}`.`{schema}`"
print(f"Destino dos dados: {catalog}.{schema}")

# COMMAND ----------

from pyspark.sql import functions as F

# Escolhe aleatoriamente um valor de uma lista Python (array de literais + element_at por rand).
def pick(values):
    arr = F.array(*[F.lit(v) for v in values])
    idx = (F.floor(F.rand() * F.lit(len(values))) + F.lit(1)).cast("int")
    return F.element_at(arr, idx)

# COMMAND ----------

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {fq}")
spark.sql(f"USE CATALOG `{catalog}`")
spark.sql(f"USE SCHEMA `{schema}`")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. `dim_customers` — 2.000 clientes (Brasil)

# COMMAND ----------

first_names = ["Ana","Bruno","Carla","Diego","Elena","Felipe","Giulia","Hugo","Isabela","João",
               "Karina","Lucas","Marina","Nuno","Olívia","Pedro","Rafaela","Sofia","Thiago","Valentina"]
last_names = ["Silva","Santos","Oliveira","Souza","Lima","Costa","Pereira","Rodrigues","Almeida",
              "Nascimento","Carvalho","Gomes","Martins","Araújo","Melo","Barbosa","Ribeiro","Alves"]
segments = ["Consumer", "Corporate", "Home Office"]
genders = ["Feminino", "Masculino", "Outro"]

# Geografia coerente (cidade, estado) escolhida pelo MESMO índice
cust_cities = ["São Paulo","Rio de Janeiro","Belo Horizonte","Curitiba","Porto Alegre","Salvador",
               "Recife","Fortaleza","Manaus","Belém","Brasília","Goiânia"]
cust_states = ["SP","RJ","MG","PR","RS","BA","PE","CE","AM","PA","DF","GO"]
n_cust_geo = len(cust_cities)

def by_idx(values, idx_col):
    arr = F.array(*[F.lit(v) for v in values])
    return F.element_at(arr, idx_col)

dim_customers = (
    spark.range(2000)
    .withColumn("customer_id", (F.col("id") + 1).cast("int"))
    .withColumn("_geo", (F.floor(F.rand() * F.lit(n_cust_geo)) + F.lit(1)).cast("int"))
    .withColumn("first_name", pick(first_names))
    .withColumn("last_name", pick(last_names))
    .withColumn("email", F.lower(F.concat(F.col("first_name"), F.lit("."), F.col("last_name"),
                                          F.col("customer_id").cast("string"), F.lit("@example.com"))))
    .withColumn("city", by_idx(cust_cities, F.col("_geo")))
    .withColumn("state", by_idx(cust_states, F.col("_geo")))
    .withColumn("country", F.lit("Brasil"))
    .withColumn("segment", pick(segments))
    .withColumn("gender", pick(genders))
    .withColumn("age", (F.lit(18) + F.floor(F.rand() * F.lit(60))).cast("int"))
    .withColumn("signup_date", F.expr("date_sub(current_date(), cast(rand()*1460 as int))"))
    .drop("id", "_geo")
)
dim_customers.write.mode("overwrite").saveAsTable(f"{fq}.dim_customers")
display(spark.table(f"{fq}.dim_customers").limit(5))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. `dim_products` — 300 produtos de moda
# MAGIC
# MAGIC Categorias de **roupas, calçados e acessórios**: Feminino, Masculino, Infantil, Moda Íntima,
# MAGIC Esportes, Calçados, Acessórios e Praia — com **subcategoria** coerente e **estação** (season).

# COMMAND ----------

categories = ["Feminino","Masculino","Infantil","Moda Íntima","Esportes","Calçados","Acessórios","Praia"]
brands = ["TabajaraBasics","TabajaraSport","TabajaraKids","TabajaraDenim","TabajaraBeach","Tabajara Premium","TabajaraUrban","TabajaraCozy"]
seasons = ["Primavera","Verão","Outono","Inverno","Ano todo"]

sub_fem = ["Vestido","Blusa","Saia","Calça Jeans","Legging","Casaco de Inverno"]
sub_mas = ["Camisa Social","Camiseta","Calça Jeans","Bermuda","Moletom","Jaqueta de Frio"]
sub_inf = ["Camiseta Infantil","Conjunto Infantil","Vestido Infantil","Bermuda Infantil","Pijama Infantil"]
sub_int = ["Cueca","Calcinha","Sutiã","Meia","Pijama"]
sub_esp = ["Legging Esportiva","Camiseta Dry","Regata","Short Esportivo","Tênis de Corrida"]
sub_cal = ["Tênis Esportivo","Sandália","Chinelo","Bota","Sapatênis"]
sub_ace = ["Boné","Bolsa","Cinto","Óculos de Sol","Mochila"]
sub_pra = ["Biquíni","Sunga","Saída de Praia","Chinelo de Praia","Óculos de Sol"]

dim_products = (
    spark.range(300)
    .withColumn("product_id", (F.col("id") + 1).cast("int"))
    .withColumn("category", pick(categories))
    .withColumn("subcategory",
        F.when(F.col("category") == "Feminino", pick(sub_fem))
         .when(F.col("category") == "Masculino", pick(sub_mas))
         .when(F.col("category") == "Infantil", pick(sub_inf))
         .when(F.col("category") == "Moda Íntima", pick(sub_int))
         .when(F.col("category") == "Esportes", pick(sub_esp))
         .when(F.col("category") == "Calçados", pick(sub_cal))
         .when(F.col("category") == "Acessórios", pick(sub_ace))
         .otherwise(pick(sub_pra)))
    .withColumn("season",
        F.when(F.col("category") == "Praia", F.lit("Verão"))
         .when(F.col("subcategory").rlike("Inverno|Frio|Bota|Moletom|Casaco|Jaqueta"), F.lit("Inverno"))
         .otherwise(pick(seasons)))
    .withColumn("brand", pick(brands))
    .withColumn("product_name", F.concat(F.col("brand"), F.lit(" "), F.col("subcategory")))
    .withColumn("unit_cost", F.round(F.lit(5) + F.rand() * F.lit(145), 2))
    .withColumn("unit_price", F.round(F.col("unit_cost") * (F.lit(1.4) + F.rand() * F.lit(0.8)), 2))
    .drop("id")
)
dim_products.write.mode("overwrite").saveAsTable(f"{fq}.dim_products")
display(spark.table(f"{fq}.dim_products").limit(8))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. `dim_stores` — 25 lojas (cidades do Brasil)

# COMMAND ----------

store_cities = ["São Paulo","Rio de Janeiro","Belo Horizonte","Campinas","Vitória",
                "Curitiba","Porto Alegre","Florianópolis","Caxias do Sul","Londrina",
                "Salvador","Recife","Fortaleza","Natal","São Luís","Maceió","João Pessoa",
                "Manaus","Belém","Porto Velho","Palmas",
                "Brasília","Goiânia","Campo Grande","Cuiabá"]
store_states = ["SP","RJ","MG","SP","ES","PR","RS","SC","RS","PR",
                "BA","PE","CE","RN","MA","AL","PB","AM","PA","RO","TO","DF","GO","MS","MT"]
store_regions = ["Sudeste","Sudeste","Sudeste","Sudeste","Sudeste","Sul","Sul","Sul","Sul","Sul",
                 "Nordeste","Nordeste","Nordeste","Nordeste","Nordeste","Nordeste","Nordeste",
                 "Norte","Norte","Norte","Norte","Centro-Oeste","Centro-Oeste","Centro-Oeste","Centro-Oeste"]
store_lat = [-23.55,-22.91,-19.92,-22.91,-20.32,-25.43,-30.03,-27.59,-29.17,-23.31,
             -12.97,-8.05,-3.73,-5.79,-2.53,-9.66,-7.12,-3.12,-1.46,-8.76,-10.18,-15.79,-16.69,-20.47,-15.60]
store_lon = [-46.63,-43.17,-43.94,-47.06,-40.34,-49.27,-51.23,-48.55,-51.18,-51.16,
             -38.51,-34.88,-38.52,-35.21,-44.30,-35.73,-34.86,-60.02,-48.50,-63.90,-48.33,-47.88,-49.26,-54.62,-56.10]

def by_store(values):
    arr = F.array(*[F.lit(v) for v in values])
    return F.element_at(arr, F.col("store_id"))

dim_stores = (
    spark.range(25)
    .withColumn("store_id", (F.col("id") + 1).cast("int"))
    .withColumn("city", by_store(store_cities))
    .withColumn("state", by_store(store_states))
    .withColumn("region", by_store(store_regions))
    .withColumn("country", F.lit("Brasil"))
    .withColumn("latitude", by_store(store_lat).cast("double"))
    .withColumn("longitude", by_store(store_lon).cast("double"))
    .withColumn("store_name", F.concat(F.lit("TabajaraBrasil "), F.col("city")))
    .withColumn("open_date", F.expr("date_sub(current_date(), cast(rand()*3650 as int))"))
    .drop("id")
)
dim_stores.write.mode("overwrite").saveAsTable(f"{fq}.dim_stores")
display(spark.table(f"{fq}.dim_stores"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. `fact_sales` — ~100.000 vendas (24 meses)
# MAGIC
# MAGIC `sales_amount = quantity * unit_price * (1 - discount_pct)`; `unit_price` vem de `dim_products`.

# COMMAND ----------

sales_base = (
    spark.range(100000)
    .withColumn("sale_id", (F.col("id") + 1).cast("int"))
    .withColumn("customer_id", (F.floor(F.rand() * F.lit(2000)) + 1).cast("int"))
    .withColumn("product_id", (F.floor(F.rand() * F.lit(300)) + 1).cast("int"))
    .withColumn("store_id", (F.floor(F.rand() * F.lit(25)) + 1).cast("int"))
    .withColumn("sale_date", F.expr("date_sub(current_date(), cast(rand()*730 as int))"))
    .withColumn("quantity", (F.floor(F.rand() * F.lit(5)) + 1).cast("int"))
    .withColumn("discount_pct", (F.floor(F.rand() * F.lit(5)) * F.lit(0.05)).cast("double"))
    .drop("id")
)
fact_sales = (
    sales_base
    .join(spark.table(f"{fq}.dim_products").select("product_id", "unit_price"), on="product_id", how="left")
    .withColumn("sales_amount",
                F.round(F.col("quantity") * F.col("unit_price") * (F.lit(1) - F.col("discount_pct")), 2))
    .select("sale_id", "sale_date", "customer_id", "product_id", "store_id",
            "quantity", "unit_price", "discount_pct", "sales_amount")
)
fact_sales.write.mode("overwrite").saveAsTable(f"{fq}.fact_sales")
display(spark.table(f"{fq}.fact_sales").limit(10))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. `fact_inventory` — snapshots mensais de estoque

# COMMAND ----------

months = (
    spark.range(24)
    .withColumn("snapshot_date",
                F.expr("last_day(add_months(date_sub(current_date(), 730), cast(id as int)))"))
    .select("snapshot_date")
)
fact_inventory = (
    spark.table(f"{fq}.dim_stores").select("store_id")
    .crossJoin(spark.table(f"{fq}.dim_products").select("product_id"))
    .crossJoin(months)
    .withColumn("units_on_hand", (F.floor(F.rand() * F.lit(500))).cast("int"))
    .withColumn("units_reserved", (F.floor(F.rand() * F.lit(50))).cast("int"))
    .select("snapshot_date", "store_id", "product_id", "units_on_hand", "units_reserved")
)
fact_inventory.write.mode("overwrite").saveAsTable(f"{fq}.fact_inventory")
display(spark.table(f"{fq}.fact_inventory").limit(10))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Validação
# MAGIC **Estas são as tabelas que os exercícios do workshop (e o dashboard) vão usar.**

# COMMAND ----------

for t in ["dim_customers", "dim_products", "dim_stores", "fact_sales", "fact_inventory"]:
    n = spark.table(f"{fq}.{t}").count()
    print(f"{t:<16} -> {n:>8,} linhas")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Vendas por regiao e categoria de moda (TabajaraBrasil Brasil)
# MAGIC SELECT s.region, p.category, ROUND(SUM(f.sales_amount), 2) AS total_vendas
# MAGIC FROM IDENTIFIER(:catalog || '.' || :schema || '.fact_sales') f
# MAGIC JOIN IDENTIFIER(:catalog || '.' || :schema || '.dim_stores')  s ON f.store_id = s.store_id
# MAGIC JOIN IDENTIFIER(:catalog || '.' || :schema || '.dim_products') p ON f.product_id = p.product_id
# MAGIC GROUP BY s.region, p.category
# MAGIC ORDER BY total_vendas DESC;

# COMMAND ----------

# MAGIC %md
# MAGIC ### Pronto!
# MAGIC Os dados da **TabajaraBrasil (Brasil)** estão em `{catalog}.{schema}`. Volte ao material do workshop
# MAGIC e siga os exercícios usando estas tabelas. Se você usa **dados próprios**, aponte cada exercício
# MAGIC para as suas tabelas.
