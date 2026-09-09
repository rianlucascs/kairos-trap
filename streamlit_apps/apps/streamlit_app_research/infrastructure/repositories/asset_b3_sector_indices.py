

from pipelines.readers.pipelines.b3_indices_segmentos_setoriais.reader_parquet import ReaderSnapshotParquet as b3_indices

from typing import Literal


class AssetB3SectorIndicesRepository:
    
    
    def __init__(
        self,
        file_identifiers = Literal["composicao.parquet", "indices.parquet"]
    ) -> None:
        
        self.b3_sector_indices = b3_indices(file_identifiers=file_identifiers)
        
    
    
    def get_data(self):
        
        return self.b3_sector_indices.read()