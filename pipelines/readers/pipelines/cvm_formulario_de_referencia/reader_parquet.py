

from pipelines.shared.interfaces.readers.reader_snapshot_parquet import ReaderSnapshotParquetInterface

from typing import Literal
from datetime import date


class ReaderSnapshotParquet(ReaderSnapshotParquetInterface):
    
    
    def __init__(
        self,
        file_identifiers: Literal[
            "",  # arquivo base: fre_cia_aberta_<ANO>.parquet
            "acao_entregue",
            "administrador_PCD",
            "administrador_declaracao_genero",
            "administrador_declaracao_raca",
            "administrador_membro_conselho_fiscal",
            "ativo_imobilizado",
            "ativo_intangivel",
            "auditor",
            "auditor_responsavel",
            "capital_social",
            "capital_social_aumento",
            "capital_social_aumento_classe_acao",
            "capital_social_classe_acao",
            "capital_social_desdobramento",
            "capital_social_desdobramento_classe_acao",
            "capital_social_reducao",
            "capital_social_reducao_classe_acao",
            "capital_social_titulo_conversivel",
            "direito_acao",
            "distribuicao_capital",
            "distribuicao_capital_classe_acao",
            "distribuicao_dividendos",
            "distribuicao_dividendos_classe_acao",
            "empregado_PCD",
            "empregado_local_declaracao_genero",
            "empregado_local_declaracao_raca",
            "empregado_local_faixa_etaria",
            "empregado_posicao_declaracao_genero",
            "empregado_posicao_declaracao_raca",
            "empregado_posicao_faixa_etaria",
            "empregado_posicao_local",
            "endividamento",
            "grupo_economico_reestruturacao",
            "historico_emissor",
            "informacao_financeira",
            "membro_comite",
            "mercado_estrangeiro",
            "obrigacao",
            "outro_valor_mobiliario",
            "participacao_sociedade",
            "participacao_sociedade_valorizacao_acao",
            "plano_recompra",
            "plano_recompra_classe_acao",
            "politica_negociacao",
            "politica_negociacao_cargo",
            "posicao_acionaria",
            "posicao_acionaria_classe_acao",
            "relacao_familiar",
            "relacao_subordinacao",
            "remuneracao_acao",
            "remuneracao_maxima_minima_media",
            "remuneracao_total_orgao",
            "remuneracao_variavel",
            "responsavel",
            "titular_valor_mobiliario",
            "titulo_exterior",
            "transacao_parte_relacionada",
            "valor_mobiliario_tesouraria_movimentacao",
            "valor_mobiliario_tesouraria_ultimo_exercicio",
            "volume_valor_mobiliario",
        ]
    ) -> None:

        super().__init__(
            pipeline="cvm_formulario_de_referencia",
            subdir_stage="to_processed",
            file_identifiers=f"fre_cia_aberta_{file_identifiers}_2010-{date.today().year}.parquet"
        )