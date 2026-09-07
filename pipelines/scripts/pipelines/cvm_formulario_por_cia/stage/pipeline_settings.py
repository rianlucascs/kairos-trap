"""
Settings:
    pipeline_settings

Responsabilidades:
    - Definir os códigos de demonstrações financeiras padronizadas (DFP e ITR) a serem processadas.
    
Notas:
    ...
"""


# Lista de códigos de demonstrações financeiras padronizadas (CVM) a serem processadas.
demonstration_codes: list[str] = [
    'BPA_con', 'BPA_ind', 
    'BPP_con', 'BPP_ind', 
    'DFC_MD_con', 'DFC_MD_ind', 
    'DFC_MI_con', 'DFC_MI_ind', 
    'DMPL_con', 'DMPL_ind', 
    'DRA_con', 'DRA_ind', 
    'DRE_con', 'DRE_ind', 
    'DVA_con', 'DVA_ind'
    ]
