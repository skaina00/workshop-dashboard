# Workshop Hands-On AI/BI Dashboards — Laboratorio 1

Treinamento Hands-on na plataforma Databricks com foco nas funcionalidades de Análise Exploratória e Painéis.
</br></br>

## Objetivos do Exercício

O objetivo desse laboratório é montar um Painel, utilizando os dados de ações das Big Tech da NASDAQ.</br> 
</br></br>


## Exercício 01 - Criando o Dashboard

No Menu Lateral, escolha a opção DASHBOARDS:

Clique na opção **CREATE DASHBOARD**

Na tela do Dashboard, clique na ABA **"Data"** para adicionar uma fonte de dados:

<img src="../../imagens/lab01_img02.png" style="height: 300px;"></br>

1 - Escolha a opção *"Create from SQL"*

2 - Copie a consulta abaixo e cole no editor (não se esqueça de incluir seu banco de dados)
```sql
SELECT * 
  FROM dbacademy.workshop_aibi.stocks
```

3 - Clique em *"Run"*

<img src="../../imagens/lab01_img03.png" style="height: 300px;">


Vá para a aba de dashboard *"Untitled page"*.  </br>

No canto superior direito, selecione o ícone da Genie Code.

Na caixa de diálogo insira a seguinte informação:
``` md
gráfico de linhas do valor de fechamento por dia e por empresa
```

<img src="../../imagens/lab01_img04.png" style="height: 500px;">

</br></br>
Um gráfico foi gerado como no exemplo abaixo:
<img src="../../imagens/lab01_img05.png" width="800px">
</br></br></br>

## Exercício 02 - Adicionando um FILTRO de página

Clique no menu azul suspenso no ícone de FILTRO.</br>
Escolha o atributo (Field):  "**company**"
</br></br>
<img src="../../imagens/lab01_img06.png" width="850px">
</br></br></br>


## Exercício 03 - Alterando o título do painel por uma imagem

Crie agora um novo objeto do tipo TEXT. No box que foi criado </br>
insira o código (markdown) abaixo: </br>
</br>

``` sql
![image](https://raw.githubusercontent.com/Databricks-BR/genie_ai_bi/main/images/header_painel.png)
```

</br></br>
<img src="../../imagens/lab01_img07.png" width="700px">
</br></br></br>


Organize o layout do dashboard para que fique com a aparência da imagem abaixo.</br>
Faça o devido alinhamento do gráfico no layout.</br>
Altere o nome do Dashboard na barra superior.</br>
Clique no botão "**Publish**" para publicar o Painel.
</br></br>
<img src="../../imagens/lab01_img08.png" width="700px">
</br></br></br>


## Exercício 04 - Criando um NOVO contexto de dados com Genie Code

Vamos criar agora um novo contexto de dados.</br>
Para isso, selecione novamente o ícone da Genie Code, </br>
No campo de diálogo, copie o texto abaixo, cole(ajuste para o seu banco de dados) e execute a instrução</br>
Clique em *"Allow (Permitir)"* caso seja necessário</br>

``` 
Considerando o seguinte database:
dbacademy.<seu_database>.stock_bigtech

Crie um novo dataset:
Selecione o nome da empresa, stock,
mínimo valor de fechamento, máximo valor de fechamento
e percentual de variação entre o mínimo e o máximo valor de fechamento
da tabela dbacademy.<seu_nome>.stock_bigtech
agrupando por empresa e stock.
Use a coluna company para achar o nome da empresa
```
Aguarde a execução terminar 
</br>
</br>
<img src="../../imagens/lab01_img09.png" width="700px">
</br></br></br>

Vá até *"Data (Dados)"*
Selecione o novo dataset criado e acrescente ao resultado a linha de concatenação com o nome da ação (STOCK), </br>
com o LINK (URL) de uma imagem. </br>

``` sql

SELECT 
  "https://raw.githubusercontent.com/Databricks-BR/genie_ai_bi/main/images/" || stock || ".png" AS image,
  company,
  stock,
  MIN(close) AS min_close,
  MAX(close) AS max_close,
  ((MAX(close) - MIN(close)) / MIN(close) * 100) AS percentual_variacao
FROM dbacademy.workshop_aibi.stocks
GROUP BY company, stock;

```
</br>
Ao executar a query (botão RUN),</br>
o resultado esperado é o mostrado abaixo:</br>
<img src="../../imagens/lab01_img10.png" width="700px">
</br></br></br>

## Exercício 05 - Adicionando um novo Gráfico com o contexto novo de dados

1. Clique no menu azul suspenso na posição inferior do painel, </br>
no botão com o ícone de gráfico </br>
2. Na barra de configuração (lateral direita do painel),</br>
escolha o nome do Dataset (que veio do Genie Code).</br> 
3. Configure o tipo de Visualização para "Table"(Tabela).</br>
4. Na opção Columns (Colunas) clique no sinal "+".
5. Selecione a opção "Add all (Adicionar todos)"

</br></br>
<img src="../../imagens/lab01_img11.png" width="900px">
</br></br></br>

6. Passe o mouse na coluna image e selecione a seta para baixo.</br>
7. Clique em "Style (Estilo)".
8. Em "Display Type" selecione a opção "Image (Imagem)"
9. Em "Height (Altura)" digite o valor 25
</br></br>
<img src="../../imagens/lab01_img12.png" width="400px">
</br></br></br>

Como resultado esperado, teremos a figura abaixo.</br>
Salve (Publique) novamente o Painel.
</br></br>
<img src="../../imagens/lab01_img13.png" width="700px">
</br></br></br>






