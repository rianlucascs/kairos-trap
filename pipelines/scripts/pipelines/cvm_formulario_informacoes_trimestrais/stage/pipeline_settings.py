"""
Settings:
    pipeline_settings

Responsabilidades:
    - Definir as configurações do pipeline `cvm_formulario_informacoes_trimestrais`, 
    incluindo a URL base para baixar os arquivos ZIP do site da CVM (Comissão de Valores Mobiliários) 
    e a lista de arquivos ZIP a serem baixados, um para cada ano de 2011 até o ano atual.
    
Notas:
    ...
"""


from datetime import date


# URL base para baixar os arquivos ZIP do site da CVM (Comissão de Valores Mobiliários).
url: str = "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/ITR/DADOS/"


file_prefix: str = "itr_cia_aberta"


start_year: int = 2011


# Lista de arquivos zip a serem baixados, um para cada ano de 2011 até o ano atual.
build_archives_zip: list[str] = [f'{file_prefix}_{year_now}.zip' for year_now in range(start_year, date.today().year + 1)]


# Lista de códigos de demonstrações financeiras padronizadas (CVM) a serem processadas.
file_identifiers: list[str] = [
    'BPA_con', 'BPA_ind', 
    'BPP_con', 'BPP_ind', 
    'DFC_MD_con', 'DFC_MD_ind', 
    'DFC_MI_con', 'DFC_MI_ind', 
    'DMPL_con', 'DMPL_ind', 
    'DRA_con', 'DRA_ind', 
    'DRE_con', 'DRE_ind', 
    'DVA_con', 'DVA_ind'
    ]

