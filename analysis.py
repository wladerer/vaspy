import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# There will be four files in the data folder
# 1. Data from slabs without SOC resources/slabs.csv
# 2. Data from slabs with SOC resources/slabs_soc.csv
# 3. Data from slabs with adsorbates resources/slabs_adsorbates.csv
# 4. Data from adsorbates resources/adsorbates.csv

# Read the data from the files
slabs = pd.read_csv('resources/slabs.csv')
slabs_soc = pd.read_csv('resources/slabs_soc.csv')
slabs_adsorbates = pd.read_csv('resources/slabs_adsorbates.csv')
adsorbates = pd.read_csv('resources/adsorbates.csv')

#create a dictionary of adsorbates and their corresponding Energy
adsorbates_dict = dict(zip(adsorbates['Adsorbate'], adsorbates['Energy']))

def make_adsorbate_dict(adsorbates_df: pd.DataFrame) -> dict:
    return dict(zip(adsorbates_df['Adsorbate'], adsorbates_df['Energy']))

def find_system(slabs_adsorbed_df: pd.DataFrame) -> str:
    # if the substrings Bi and Se are in "Directory", then the System is Bi2Se3
   #If the substrings Bi and Te are in "Directory", then the System is Bi2Te3
   # If the substrings Sb and Se are in "Directory", then the System is Sb2Se3
   # If the substrings Sb and Te are in "Directory", then the System is Sb2Te3
    if 'Bi' in slabs_adsorbed_df['Directory'] and 'Se' in slabs_adsorbed_df['Directory']:
        return 'Bi2Se3'
    elif 'Bi' in slabs_adsorbed_df['Directory'] and 'Te' in slabs_adsorbed_df['Directory']:
        return 'Bi2Te3'
    elif 'Sb' in slabs_adsorbed_df['Directory'] and 'Se' in slabs_adsorbed_df['Directory']:
        return 'Sb2Se3'
    elif 'Sb' in slabs_adsorbed_df['Directory'] and 'Te' in slabs_adsorbed_df['Directory']:
        return 'Sb2Te3'
    else:
        raise ValueError('System not found')

def format_adsorbates_dataframe(slabs_adsorbed_df: pd.DataFrame) -> pd.DataFrame:
    #update the dataframe with a new column called "System"
    slabs_adsorbed_df['System'] = slabs_adsorbed_df.apply(find_system, axis=1)

    return slabs_adsorbed_df


def E_adsorption(E_system: float, E_adsorbate: float, E_slab: float) -> float:

    return -1 * (E_system - E_adsorbate - E_slab)


def E_slab(slab_df: pd.DataFrame, system: str) -> float:
    return slab_df[slab_df['System'] == system]['Energy'].values[0]

def E_adsorbate(adsorbate: str, adsorbates_dict: dict) -> float:
    return adsorbates_dict[adsorbate]

def E_system(slab_df: pd.DataFrame, system: str, adsorbate: str) -> float:
    return slab_df[ ( slab_df['System'] == system ) & ( slab_df['Adsorbate'] == adsorbate)]['Energy'].values[0]


format_adsorbates_dataframe(slabs_adsorbates) 

def calc_E_adsorption(slabs_df: pd.DataFrame, adsorbates_df: pd.DataFrame, adsorbed_slabs_df: pd.DataFrame) -> pd.DataFrame:
    # Create a dictionary of adsorbates and their corresponding energy
    adsorbates_dict = make_adsorbate_dict(adsorbates_df)

    # Format the adsorbed slabs dataframe
    adsorbed_slabs_df = format_adsorbates_dataframe(adsorbed_slabs_df)
    
    # Create a new dataframe with the adsorption energy
    adsorption_energy_df = adsorbed_slabs_df.copy()
    E_sys = adsorption_energy_df.apply(lambda x: E_system(adsorbed_slabs_df, x['System'], x['Adsorbate']), axis=1)
    E_slb = adsorption_energy_df.apply(lambda x: E_slab(slabs_df, x['System']), axis=1)
    E_ads = adsorption_energy_df.apply(lambda x: E_adsorbate(x['Adsorbate'], adsorbates_dict), axis=1)
    adsorption_energy_df['Adsorption Energy'] = ( E_sys - E_slb - E_ads ) * -1

    return adsorption_energy_df

adsorption_energy_df = calc_E_adsorption(slabs, adsorbates, slabs_adsorbates)

#plot the adsorption energy
fig = px.scatter(adsorption_energy_df, x='Adsorbate', y='Adsorption Energy', color='System', hover_data=['Directory'])
fig.show()







