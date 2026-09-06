

from pipelines.shared.interfaces.pipelines.stage.transform.to_interim.to_interim_workers import ToInterimWorkersInterface
from pipelines.shared.checkpoint_values import Stage, Step, Status
from pipelines.shared.utils.io_utils import clear_directory

import json
import pandas as pd
import gc


class ToInterimWorkerA(ToInterimWorkersInterface):


    process: str = "to_interim_worker_a"


    def __init__(
        self,
        *,
        pipeline: str,
    ) -> None:
        
        super().__init__(
            pipeline=pipeline
        )


    def _columns_to_cast(self) -> dict[str, str]:
        return {
            "index": "string",
            "segment": "string",
            "cod": "string",
            "asset": "string",
            "type": "string",
            "text": "string",
            "textReductor": "string",
        }


    def _columns_to_parse_dates(self) -> list[str]:
        return [
            "date",
        ]
        
        
    def _columns_to_cast_to_numeric(self) -> list[str]:
        # theoricalQty fica de fora: já é convertido para Int64 em _parse_b3_numbers,
        # e o cast genérico da interface força float64, o que descartaria o tipo inteiro.
        return [
            "part",
            "partAcum",
            "reductor",
        ]


    @staticmethod
    def _parse_b3_numbers(df: pd.DataFrame) -> pd.DataFrame:
        for column in ("part", "partAcum", "reductor"):
            if column in df.columns:
                df[column] = pd.to_numeric(
                    df[column].astype("string").str.replace(".", "", regex=False).str.replace(",", ".", regex=False),
                    errors="coerce",
                )

        if "theoricalQty" in df.columns:
            df["theoricalQty"] = pd.to_numeric(
                df["theoricalQty"].astype("string").str.replace(".", "", regex=False),
                errors="coerce",
            ).astype("Int64")

        return df
    
    
    def _worker(self, ctx):
        
        raw_json_path = ctx.build_raw_path(
            ctx.current_snapshot_path(self.pipeline), 
            subdir_format="json"
        )

        interim_parquet_path = ctx.prepare_transformed_path(
            ctx.current_snapshot_path(self.pipeline), 
            subdir_stage="to_interim", 
            subdir_format="parquet"
        )

        clear_directory(interim_parquet_path, logger=self.logger, remove_root=False)

        records = [
            (path.stem, json.loads(path.read_text(encoding="utf-8")))
            for path in raw_json_path.glob("*.json")
        ]

        indices = []
        composicao = []
        for index, record in records:
            
            header = record.get("header", {}).copy()
            header["index"] = index
            indices.append(header)

            for result in record.get("results", []):
                result = result.copy()
                result["index"] = index
                composicao.append(result)

        df_indices = pd.DataFrame(indices)
        df_composicao = pd.DataFrame(composicao)

        if "date" in df_indices.columns:
            df_indices["date"] = pd.to_datetime(
                df_indices["date"], format="%d/%m/%y", errors="coerce"
            )

        df_indices = self._parse_b3_numbers(df_indices)
        df_composicao = self._parse_b3_numbers(df_composicao)

        df_indices, cast_failed_indices = self._cast_columns(df_indices)
        df_indices, invalid_dates_indices = self._parse_dates(df_indices)
        df_indices, cast_failed_numeric_indices = self._cast_columns_numeric(df_indices)

        df_composicao, cast_failed_composicao = self._cast_columns(df_composicao)
        df_composicao, cast_failed_numeric_composicao = self._cast_columns_numeric(df_composicao)

        df_indices.to_parquet(interim_parquet_path / "indices.parquet", index=False, engine="pyarrow")
        df_composicao.to_parquet(interim_parquet_path / "composicao.parquet", index=False, engine="pyarrow")

        del df_indices, df_composicao
        gc.collect()

        self._write_checkpoint(
            ctx=ctx,
            stage=Stage.TO_INTERIM,
            step=Step.PARSE,
            filename="to_interim_worker_a.success.json",
            status=Status.SUCCESSFUL,
            source=getattr(self.settings, "url", self.pipeline),
            extra={
                "parse_invalid_dates": invalid_dates_indices,
                "cast_failed_columns_indices": cast_failed_indices,
                "cast_failed_columns_composicao": cast_failed_composicao,
                "cast_failed_numeric_indices": cast_failed_numeric_indices,
                "cast_failed_numeric_composicao": cast_failed_numeric_composicao,
            },
        )
