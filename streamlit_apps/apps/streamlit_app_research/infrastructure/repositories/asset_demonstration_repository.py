

from pipelines.domain.cvm_formulario_por_cia.demonstrations import Demonstration

from typing import Literal


class AssetDemonstrationRepository:
    
    
    def __init__(
        self,
        cd_cvm: str,
        demonstration_code: Literal[
            'BPA_con', 'BPA_ind', 'BPP_con', 'BPP_ind', 'DFC_MD_con', 'DFC_MD_ind', 'DFC_MI_con', 
            'DFC_MI_ind', 'DMPL_con', 'DMPL_ind', 'DRA_con', 'DRA_ind', 'DRE_con', 'DRE_ind', 'DVA_con', 'DVA_ind'
            ],
        prefix: Literal['itr', 'dfp', 'itr+dfp', 'dfp+itr']
        ):
        
        self.demonstration = Demonstration(cd_cvm=cd_cvm, demonstration_code=demonstration_code, prefix=prefix)
        
    
    def get_demonstration(
        self, 
        ordem_exerc: str = "ÚLTIMO",
        cd_conta: str = "1"
    ) -> Demonstration:
        
        return (self.demonstration
            .read()
            .concatenate()
            .filter_by_ordem_exerc(ordem_exerc=ordem_exerc)
            .filter_by_account(cd_conta=cd_conta)
            .calculate_aggregated_values()
            )


    def get_demonstration_by_description(
        self,
        ds_conta_contains: str,
        cd_conta_prefix: str | None = None,
        ordem_exerc: str = "ÚLTIMO",
    ) -> Demonstration:

        return (self.demonstration
            .read()
            .concatenate()
            .filter_by_ordem_exerc(ordem_exerc=ordem_exerc)
            .filter_by_account_contains(ds_conta_contains=ds_conta_contains, cd_conta_prefix=cd_conta_prefix)
            .calculate_aggregated_values()
            )