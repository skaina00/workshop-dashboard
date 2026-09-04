# Databricks notebook source
# MAGIC %md
# MAGIC # Geração ATUALIZADA da tabela `stocks` (últimos 2 anos, ao vivo)
# MAGIC
# MAGIC Este notebook **baixa os dados em tempo real** do Yahoo Finance (via `yfinance`),
# MAGIC sempre pegando os **últimos 2 anos** a partir da data em que ele é executado,
# MAGIC monta um **DataFrame Spark** e grava em uma tabela Delta gerenciada no Unity Catalog.
# MAGIC
# MAGIC - **Destino:** `vhd_techsummit_catalog.default.stocks`
# MAGIC - **Papéis:** Amazon, Apple, Meta Facebook, Microsoft, NVIDIA, ORACLE, Tesla
# MAGIC - **Período:** últimos 2 anos (dinâmico — recalculado a cada execução)
# MAGIC - **Colunas:** `market, stock, company, date, close, volume, open, high, low`
# MAGIC
# MAGIC > ⚠️ Requer **acesso à internet** a partir do cluster (o driver acessa o Yahoo Finance).
# MAGIC > Em workspaces com saída de rede restrita, esta chamada pode falhar.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Pré-requisitos e permissões
# MAGIC
# MAGIC - Um **cluster** ativo com **acesso de saída à internet**.
# MAGIC - No Unity Catalog, sobre `vhd_techsummit_catalog.default`:
# MAGIC   **`USE CATALOG`**, **`USE SCHEMA`**, **`CREATE TABLE`** e **`SELECT`**.

# COMMAND ----------

# MAGIC %pip install --quiet yfinance
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

dbutils.widgets.text("catalog", "dbacademy", "1. Catalogo")
dbutils.widgets.text("schema", "workshop_aibi", "2. Schema")
dbutils.widgets.text("table", "stocks", "3. Tabela")
dbutils.widgets.text("anos", "2", "4. Janela (anos)")

catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
table = dbutils.widgets.get("table")
anos = int(dbutils.widgets.get("anos"))

fqn = f"`{catalog}`.`{schema}`.`{table}`"
print(f"Destino: {fqn}  |  janela: últimos {anos} ano(s)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Baixa os dados (últimos N anos)

# COMMAND ----------

import yfinance as yf
from datetime import date
from dateutil.relativedelta import relativedelta

# ticker -> (market, company)
STOCKS = {
    "AMZN": ("NASDAQ", "Amazon"),
    "AAPL": ("NASDAQ", "Apple"),
    "META": ("NASDAQ", "Meta Facebook"),
    "MSFT": ("NASDAQ", "Microsoft"),
    "NVDA": ("NASDAQ", "NVIDIA"),
    "ORCL": ("NYSE",   "ORACLE"),
    "TSLA": ("NASDAQ", "Tesla"),
}

end = date.today()
start = end - relativedelta(years=anos)
print(f"Janela: {start} -> {end}")

registros = []
for ticker, (market, company) in STOCKS.items():
    hist = yf.download(
        ticker, start=start.isoformat(), end=end.isoformat(),
        auto_adjust=False, progress=False,
    )
    if hist.empty:
        print(f"AVISO: sem dados para {ticker}")
        continue
    # normaliza colunas (yfinance pode devolver MultiIndex p/ 1 ticker)
    if hasattr(hist.columns, "get_level_values"):
        hist.columns = hist.columns.get_level_values(0)
    for idx, r in hist.iterrows():
        registros.append((
            market, ticker, company,
            idx.strftime("%m/%d/%Y"),
            round(float(r["Close"]), 2),
            int(r["Volume"]),
            round(float(r["Open"]), 2),
            round(float(r["High"]), 2),
            round(float(r["Low"]), 2),
        ))
    print(f"{ticker}: {len(hist)} pregões  ({hist.index.min().date()} -> {hist.index.max().date()})")

print(f"\nTOTAL de linhas: {len(registros)}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Monta o DataFrame Spark

# COMMAND ----------

from pyspark.sql import functions as F
from pyspark.sql.types import (
    StructType, StructField, StringType, DoubleType, LongType
)

schema_df = StructType([
    StructField("market", StringType(), True),
    StructField("stock", StringType(), True),
    StructField("company", StringType(), True),
    StructField("date", StringType(), True),
    StructField("close", DoubleType(), True),
    StructField("volume", LongType(), True),
    StructField("open", DoubleType(), True),
    StructField("high", DoubleType(), True),
    StructField("low", DoubleType(), True),
])

df = (
    spark.createDataFrame(registros, schema=schema_df)
    .withColumn("date", F.to_date("date", "MM/dd/yyyy"))
)

print(f"Linhas: {df.count()}")
df.printSchema()
display(df.orderBy("stock", F.col("date").desc()).limit(5))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Grava a tabela Delta

# COMMAND ----------

spark.sql(f"CREATE SCHEMA IF NOT EXISTS `{catalog}`.`{schema}`")

(
    df.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(fqn)
)
print(f"Tabela gravada: {fqn}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Validação

# COMMAND ----------

display(spark.sql(f"""
    SELECT stock, company,
           COUNT(*)  AS pregoes,
           MIN(date) AS primeira_data,
           MAX(date) AS ultima_data
    FROM {fqn}
    GROUP BY stock, company
    ORDER BY stock
"""))

# COMMAND ----------

display(spark.sql(f"SELECT * FROM {fqn} ORDER BY stock, date DESC LIMIT 10"))
