# Data Catalog - B3 Indices de Segmentos Setoriais

Catalogo da composicao dos indices de segmentos e setores da B3, obtida a partir do portfolio diario retornado pela API da B3.

---

## Fonte

### B3

- Origem: `https://sistemaswebb3-listados.b3.com.br/indexProxy/indexCall/GetPortfolioDay/`
- Metodo: requisicao GET com payload codificado em Base64.
- Conteudo: metadados do indice e ativos que compoem sua carteira teorica.
- Indices configurados: definidos em `stage/pipeline_settings.py`.

---

## Dados brutos

Cada arquivo JSON em `raw/json/<INDEX>.json` representa um indice. O nome do arquivo e usado como identificador `index` durante a transformacao.

O objeto bruto possui:

- `page`: informacoes de paginacao da resposta da B3.
- `header`: metadados e totais teoricos do indice.
- `results`: lista de ativos que compoem o indice.

A estrutura `page` nao e persistida nos Parquets intermediarios atuais. Os campos de `header` e `results` sao normalizados nas tabelas descritas abaixo.

---

## Datasets intermediarios

### `indices`

Arquivo: `transform/to_interim/parquet/indices.parquet`.

- Granularidade: uma linha por indice e snapshot.
- Chave pratica: `index`.
- Origem: `header` do JSON, acrescido do identificador derivado do nome do arquivo.

| Campo | Tipo esperado | O que representa |
|---|---|---|
| `index` | `string` | Codigo do indice, derivado do nome do arquivo bruto, por exemplo `AGFS`. |
| `date` | `datetime` | Data de referencia do portfolio, recebida no formato `DD/MM/YY`. |
| `text` | `string` | Descricao do total teorico, normalmente `Quantidade Teorica Total`. |
| `part` | `float64` | Participacao total do indice, convertida do formato brasileiro, por exemplo `100,000`. |
| `partAcum` | `float64` nullable | Participacao acumulada, quando informada pela B3. |
| `textReductor` | `string` | Descricao do redutor, normalmente `Redutor`. |
| `reductor` | `float64` | Fator redutor, com separador de milhar e decimal normalizados. |
| `theoricalQty` | `Int64` | Quantidade teorica total do indice. |

### `composicao`

Arquivo: `transform/to_interim/parquet/composicao.parquet`.

- Granularidade: uma linha por ativo dentro de um indice e snapshot.
- Chave pratica: `index`, `cod`.
- Origem: cada item da lista `results`, acrescido do identificador do indice.

| Campo | Tipo esperado | O que representa |
|---|---|---|
| `index` | `string` | Codigo do indice ao qual o ativo pertence. |
| `segment` | `string` nullable | Segmento informado pela B3, quando disponível. |
| `cod` | `string` | Codigo de negociacao do ativo, por exemplo `ABEV3`. |
| `asset` | `string` | Nome ou descricao do ativo. |
| `type` | `string` | Tipo de ativo e segmento de listagem, por exemplo `ON NM`. |
| `part` | `float64` | Participacao do ativo no indice, convertida do formato brasileiro. |
| `partAcum` | `float64` nullable | Participacao acumulada do ativo, quando informada. |
| `theoricalQty` | `Int64` | Quantidade teorica do ativo no indice. |

---

## Transformacoes e qualidade

- Separadores brasileiros sao normalizados: pontos de milhar sao removidos e virgulas decimais sao convertidas para pontos.
- `part`, `partAcum` e `reductor` sao persistidos como `float64`.
- `theoricalQty` e persistido como inteiro anulavel `Int64`, preservando quantidades sem casas decimais.
- `date` e convertida de `DD/MM/YY` para `datetime`; datas invalidas resultam em `NaT` e sao registradas no checkpoint.
- `segment` e `partAcum` podem ser nulos porque a B3 nao informa esses valores em todos os registros.
- Tickers e codigos de indice sao identificadores textuais e nao devem ser convertidos para numeros.
- O checkpoint do `to_interim` registra falhas de conversao de tipos, datas invalidas e falhas numericas.
- A soma das participacoes dos ativos pode sofrer pequenas diferencas de arredondamento em relacao a `100,000`.
