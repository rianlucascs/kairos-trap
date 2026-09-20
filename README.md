<p align="center">
  <img src="assets/banner.png" alt="Banner do kairos-trap" width="600" height="236">
</p>

# kairos-trap

**Dados do mercado financeiro brasileiro, coletados, validados e versionados por snapshots, prontos para consumo em Python.**

> **Status:** em desenvolvimento ativo. Parte dos pipelines está em produção (agendados) e parte ainda em desenvolvimento (marcados como *dev*).

![Python 3.10](https://img.shields.io/badge/Python-3.10-3776AB?style=flat&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)
![DuckDB](https://img.shields.io/badge/DuckDB-FFF000?style=flat&logo=duckdb&logoColor=black)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat&logo=sqlite&logoColor=white)
![Selenium](https://img.shields.io/badge/Selenium-43B02A?style=flat&logo=selenium&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=flat&logo=ubuntu&logoColor=white)

## Índice

- [Visão geral](#visão-geral)
- [Pipelines](#pipelines)
- [Agenda de execução](#agenda-de-execução)
- [Uso de armazenamento](#uso-de-armazenamento)
- [Data Providers](#data-providers)
- [Research](#research)
- [Como utilizar](#como-utilizar)
- [Infraestrutura](#infraestrutura)
- [Licença](#licença)

---

## Visão geral

O `kairos-trap` transforma fontes públicas do mercado financeiro brasileiro, como CVM e B3, em uma base histórica estruturada e reproduzível. Cada fonte é tratada por um pipeline ETL independente, com regras próprias de origem, formato e processamento, mas todos seguem convenções comuns e compartilham a infraestrutura de extração, validação, checkpoints, retenção e armazenamento.

A separação entre dados brutos, intermediários e processados, com snapshots e readers dedicados, permite rastrear a origem dos dados, reprocessar etapas específicas e consumi-los de forma consistente em pesquisas financeiras e aplicações Streamlit.

---

## Pipelines

A camada de pipelines é responsável pela aquisição, preparação e persistência dos dados.

### Processos ETL

| Processo | Descrição |
|---|---|
| `extract` | Aquisição dos dados de origem e armazenamento dos arquivos brutos. |
| `to_interim` | Padronização inicial dos dados e organização em uma camada intermediária. |
| `to_processed` | Transformação e consolidação dos dados para a camada processada. |
| `load` | Persistência dos dados no destino configurado do pipeline. |
| `compare` | Comparação entre snapshots para identificar alterações e diferenças. |
| `retention` | Aplicação da política de retenção de dados e logs do projeto. |

### Pipelines disponíveis

| Pipeline | Fonte dos dados | Descrição |
| ------------------------------------------------------- | ------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| `cvm_formulario_informacoes_trimestrais`                | [CVM](https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/ITR/DADOS/)                                   | Extração e processamento dos dados do formulário ITR.                                            |
| `cvm_formulario_demonstracoes_financeiras_padronizadas` | [CVM](https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/)                                   | Extração e processamento dos dados do formulário DFP.                                            |
| `cvm_cias_abertas_informacao_cadastral`                 | [CVM](https://dados.cvm.gov.br/dataset/cia_aberta-cad)                                            | Extração e processamento das informações cadastrais de companhias abertas.                       |
| `cvm_formulario_por_cia`                         | [CVM](https://dados.cvm.gov.br/)                                                                  | Organização das demonstrações ITR e DFP processadas por companhia aberta.                        |
| `cvm_formulario_de_referencia`                          | [CVM](https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FRE/DADOS/)                                   | Extração e processamento dos dados do formulário FRE.                                            |
| `cvm_informacoes_periodicas_e_eventuais` — *dev*        | [CVM](https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/IPE/DADOS/)                                   | Extração e processamento das informações periódicas e eventuais divulgadas pelas companhias.     |
| `cvm_formulario_cadastral` — *dev*                      | [CVM](https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FCA/DADOS/)                                   | Extração e processamento dos dados do formulário FCA.                                            |
| `cvm_valores_mobiliarios_ofertados` — *dev*             | [CVM](https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/VLMO/DADOS/)                                  | Extração e processamento dos dados de valores mobiliários ofertados.                             |
| `google_noticias_mercado` — *dev*                       | [Google](https://news.google.com/)                                                                | Extração e processamento de notícias relacionadas ao mercado financeiro.                         |
| `b3_enriquecimento_cadastral_ativos`                    | [B3](https://www.b3.com.br/)                                                                       | Extração e processamento de informações complementares para enriquecimento cadastral e identificação de ativos financeiros. |
| `b3_indices_segmentos_setoriais`                        | [B3](https://www.b3.com.br/pt_br/market-data-e-indices/indices/indices-de-segmentos-e-setoriais/) | Extração e processamento da composição dos índices de segmentos e setoriais.                     |
| `social_monitoramento_agentes_de_mercado` — *dev*       | Redes sociais                                                                                      | Monitoramento e processamento de publicações de agentes de mercado em redes sociais.             |

### Agenda de execução

| Pipeline | Frequência | Horário |
|---|---|---|
| `cvm_formulario_demonstracoes_financeiras_padronizadas` | Diária | 08:00 |
| `cvm_formulario_informacoes_trimestrais` | Diária | 08:30 |
| `cvm_cias_abertas_informacao_cadastral` | Diária | 09:10 |
| `cvm_formulario_por_cia` | Diária | 09:15 |
| `cvm_formulario_de_referencia` | Diária | 09:30 |
| `b3_enriquecimento_cadastral_ativos` | Manual | Sob demanda |
| `b3_indices_segmentos_setoriais` | Manual | Sob demanda |
| `cvm_informacoes_periodicas_e_eventuais` — *dev* | Sem agendamento | — |
| `cvm_formulario_cadastral` — *dev* | Sem agendamento | — |
| `cvm_valores_mobiliarios_ofertados` — *dev* | Sem agendamento | — |
| `google_noticias_mercado` — *dev* | Sem agendamento | — |
| `social_monitoramento_agentes_de_mercado` — *dev* | Sem agendamento | — |

> **Política de atualização e confiabilidade:** os dados são processados conforme a agenda acima, a partir das fontes oficiais indicadas na tabela de pipelines. Os horários seguem o fuso de Brasília (`America/Sao_Paulo`, UTC−03:00). A disponibilidade do dado mais recente depende da publicação pela fonte de origem e da conclusão bem-sucedida do pipeline. Execuções manuais podem ser realizadas sob demanda.

Os detalhes de operação dos timers estão disponíveis em [docs/operations/systemd.md](docs/operations/systemd.md).

### Uso de armazenamento

| Pipeline | Volume dos dados processados |
|---|---:|
| `cvm_formulario_informacoes_trimestrais` | 23 GB |
| `cvm_formulario_demonstracoes_financeiras_padronizadas` | 7,9 GB |
| `cvm_formulario_de_referencia` | 3,1 GB |
| `cvm_formulario_por_cia` | 740 MB |
| `cvm_cias_abertas_informacao_cadastral` | 4,2 MB |
| `b3_enriquecimento_cadastral_ativos` | 1,5 MB |
| `b3_indices_segmentos_setoriais` | 624 KB |
| `cvm_informacoes_periodicas_e_eventuais` — *dev* | Não implementado |
| `cvm_formulario_cadastral` — *dev* | Não implementado |
| `cvm_valores_mobiliarios_ofertados` — *dev* | Não implementado |
| `google_noticias_mercado` — *dev* | Não implementado |
| `social_monitoramento_agentes_de_mercado` — *dev* | Não implementado |

> **Nota:** os volumes representam exclusivamente o espaço em disco ocupado pelos dados processados em `pipelines/data`. Não incluem logs, checkpoints, dados históricos, imagens ou cache do Docker. Última medição: 20/09/2026.

---

## Data Providers

A camada de Data Providers é responsável pela integração com bibliotecas e APIs externas de dados de mercado, encapsulando requisições, tratamento, validação e normalização das respostas antes de disponibilizá-las ao restante do projeto.

| Componente                   | Descrição                                                                                         |
| ---------------------------- | ------------------------------------------------------------------------------------------------- |
| `yfinance_price_provider.py` | Integração com o yfinance para obtenção, validação, tratamento e normalização de dados de preços. |

---

## Research

A camada de Research é responsável pelo consumo e utilização dos dados produzidos pelos pipelines.

| Componente | Descrição |
|---|---|
| `research/` | Exploração e análise dos dados gerados pelos pipelines. |
| `streamlit_apps/` | Consumo e visualização dos dados em interface analítica. |

---

### Apps disponíveis

| App | Descrição | Funcionalidades |
|---|---|---|
| [`streamlit_app_pipelines`](docs/streamlit_apps/preview/streamlit_app_pipelines/page_overview.pdf) | Monitoramento operacional dos pipelines ETL | •&nbsp;Consulta&nbsp;de&nbsp;pipelines&nbsp;disponíveis<br>•&nbsp;Logs&nbsp;de&nbsp;execução<br>•&nbsp;Checkpoints&nbsp;organizados&nbsp;por&nbsp;pipeline,&nbsp;stage&nbsp;e&nbsp;step |
| [`streamlit_app_research`](docs/streamlit_apps/preview/streamlit_app_research/) | Aplicação analítica para pesquisa de mercado | •&nbsp;Monitoramento&nbsp;geral&nbsp;e&nbsp;setorial<br>•&nbsp;Acompanhamento&nbsp;de&nbsp;preços,&nbsp;retornos&nbsp;e&nbsp;balanço<br>•&nbsp;Avaliação&nbsp;de&nbsp;estratégias&nbsp;de&nbsp;investimento<br>•&nbsp;Análise&nbsp;de&nbsp;conjuntos&nbsp;de&nbsp;ativos<br>•&nbsp;Consulta&nbsp;de&nbsp;notícias&nbsp;por&nbsp;ativo<br>•&nbsp;Configuração&nbsp;de&nbsp;alertas |

---

## Como utilizar

### 1. Clonar o projeto

```bash
git clone https://github.com/rianlucascs/kairos-trap
cd kairos-trap
```

### 2. Instalar dependências

```bash
pip install -e .
```

### 3. Executar um pipeline manualmente

```bash
python pipelines/scripts/pipelines/<nome_do_pipeline>/stage/pipeline.py
```

### 4. Agendar execuções no servidor

Para rodar os pipelines automaticamente via `systemd timers`, siga o passo a passo em [`docs`](docs).

### 5. Consumir os dados

Utilize os apps em `streamlit_apps` para monitorar pipelines e explorar os dados processados, ou os [`notebooks`](research/) em `research` para análises exploratórias mais livres.

```bash
# Execução local do dashboard Streamlit
cd kairos-trap

# research
streamlit run streamlit_apps/apps/streamlit_app_research/app.py

# pipelines
streamlit run streamlit_apps/apps/streamlit_app_pipelines/app.py
```

### 6. Leitura isolada dos dados

O repositório não inclui dados. Eles são gerados pelos pipelines e gravados em `pipelines/data` como snapshots. Depois que um snapshot existe, o reader dedicado o lê em formato parquet sem reexecutar o pipeline.

> **Antes de ler, gere o snapshot.** Este exemplo usa o pipeline ITR, que é o maior do projeto (cerca de 23 GB processados, veja [Uso de armazenamento](#uso-de-armazenamento)), então a primeira execução leva tempo e ocupa disco. Para um teste leve, use `cvm_cias_abertas_informacao_cadastral` (cerca de 4,2 MB).

**1. Gerar o snapshot (uma vez):**

```bash
python pipelines/scripts/pipelines/cvm_formulario_informacoes_trimestrais/stage/pipeline.py
```

**2. Ler o snapshot:**

```python
from pipelines.readers.pipelines.cvm_formulario_informacoes_trimestrais.reader_parquet import ReaderSnapshotParquet

 # DRE consolidada, filtrando companhia (CD_CVM) e conta (3.01 = receita de venda)
reader = ReaderSnapshotParquet(demonstration_code="DRE_con")
df = reader.query_parquet(filters={"CD_CVM": 16330, "CD_CONTA": "3.01"})

df[["CD_CVM", "DT_REFER", "DT_INI_EXERC", "DT_FIM_EXERC", "DS_CONTA", "VL_CONTA"]].tail(3)
```

Para outros pipelines, troque `cvm_formulario_informacoes_trimestrais` pelo nome desejado; os parâmetros do reader variam conforme o pipeline.

Resultado:

| CD_CVM | DT_REFER | DT_INI_EXERC | DT_FIM_EXERC | DS_CONTA | VL_CONTA |
|---|---|---|---|---|---|
| 016330 | 2011-09-30 | 2010-07-01 | 2010-09-30 | Receita de Venda de Bens e/ou Serviços | 452306.0 |
| 016330 | 2011-09-30 | 2011-01-01 | 2011-09-30 | Receita de Venda de Bens e/ou Serviços | 395294.0 |
| 016330 | 2011-09-30 | 2011-07-01 | 2011-09-30 | Receita de Venda de Bens e/ou Serviços | 0.0 |

> Para outros pipelines, troque `cvm_formulario_informacoes_trimestrais` pelo nome desejado; os parâmetros do reader variam conforme o pipeline.

---

## Infraestrutura

| Componente | Detalhe |
|---|---|
| OS | Ubuntu Server LTS |
| Acesso remoto | OpenSSH + VS Code Remote-SSH |
| Execução | Docker e Docker Compose |
| Armazenamento compartilhado | Samba — `/srv/data` |
| Agendamento | systemd timers |


--- 

## Aviso legal

- **Não é recomendação de investimento.** Os dados, indicadores, alertas e análises produzidos por este projeto têm caráter informativo e de pesquisa. Decisões de investimento são de responsabilidade de quem as toma.
- **Fontes de terceiros.** Os dados vêm de fontes externas (CVM, B3, yfinance, Google Notícias, entre outras). O uso deve respeitar os termos de cada fonte, e a disponibilidade e a precisão dos dados dependem delas.
- **Sem garantias.** O software é fornecido "como está", conforme a licença do repositório.

---

## Licença

O código é distribuído sob a licença [MIT](LICENSE). Ela não se aplica aos dados obtidos de fontes de terceiros, que seguem os termos de cada fonte.

