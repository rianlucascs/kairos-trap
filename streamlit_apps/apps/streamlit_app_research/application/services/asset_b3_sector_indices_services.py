

from infrastructure.repositories.asset_b3_sector_indices import AssetB3SectorIndicesRepository


class AssetB3SectorIndicesService:
    
    def __init__(self):
        
        self._b3_indices_repository_cls = AssetB3SectorIndicesRepository


    def get_composition_by_index(self, index):
        
        df = self._b3_indices_repository_cls(file_identifiers="composicao.parquet").get_data()
        
        return df[df["index"] == index].reset_index(drop=True)