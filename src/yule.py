
import numpy as np
import pandas as pd
from typing import List, Dict
from src.stats import compute_stat_witness


def generate_yule_pop(rng, LDA, lda, gamma, mu, Nact, Ninact, n_init, max_pop):
    """
    Génère une population selon le modèle de Yule
    """

    species_count = {i: 1 for i in range(n_init)} if n_init > 0 else {}
    next_species_id = n_init
    
    t = 0
    total_pop = sum(species_count.values())
    
    while t < Nact and total_pop <= max_pop:
        n_new_trees = rng.binomial(1, LDA) if total_pop < max_pop else 0
        
        if n_new_trees:
            next_species_id += 1
            species_count[next_species_id] = 1
            total_pop += 1
        
        new_species_count = species_count.copy()
        
        for species, count in species_count.items():
            if count == 0:
                continue
            
            # Copie simple
            if total_pop < max_pop:
                n_copies = rng.binomial(count, lda)
                if n_copies:
                    new_copies = min(n_copies, max_pop - total_pop)
                    new_species_count[species] += new_copies
                    total_pop += new_copies
            
            # Spéciation
            if total_pop < max_pop:
                n_speciations = rng.binomial(count, gamma)
                if n_speciations:
                    new_specs = min(n_speciations, max_pop - total_pop)
                    next_species_id += 1
                    new_species_count[next_species_id] = new_specs
                    total_pop += new_specs
            
            # Mort
            n_deaths = rng.binomial(count, mu)
            if n_deaths:
                new_species_count[species] = max(0, new_species_count[species] - n_deaths)
                total_pop -= min(n_deaths, new_species_count[species])
        
        # Nettoyage des espèces éteintes
        species_count = {k: v for k, v in new_species_count.items() if v > 0}
        if not species_count:
            return []
        
        total_pop = sum(species_count.values())
        t += 1
    
    # Phase de décimation optimisée
    survival_rate = (1 - mu) ** Ninact
    
    # Application directe du taux de survie
    final_species_count = {}
    for species, count in species_count.items():
        n_survivors = rng.binomial(count, survival_rate)
        if n_survivors > 0:
            final_species_count[species] = n_survivors
    
    return list(final_species_count.values()) if final_species_count else []


def generate_yule_dataset(rng, params, hyperparams, output_path):
    n_init, Nact, Ninact, max_pop = hyperparams.values()
    LDA, lda, gamma, mu = params.values()
    yule_pop = generate_yule_pop(rng, LDA, lda, gamma, mu, Nact, Ninact, n_init, max_pop)
    text_val = []
    witness_val = []
    
    for i, num in enumerate(yule_pop):
        for j in range(num):
            text_val.append(f'T{i}')
            witness_val.append(f'W{i}-{j+1}')
    
    # Créer le dataframe
    df = pd.DataFrame({
        'witness_ID': witness_val,
        'text_ID': text_val
    })
    
    df.to_csv(output_path, sep=";", index=False)
    
    return df

def simulate_tree_stats(rng, LDA, lda, gamma, mu, HYPERPARAMS, size=None):
    """Simule les statistiques d'arbre avec les paramètres donnés"""
    
    n_init, Nact, Ninact, max_pop = HYPERPARAMS.values()

    witness_nb = generate_yule_pop(rng, LDA, lda, gamma, mu,
                                              Nact=Nact, Ninact=Ninact,
                                              n_init=n_init, max_pop=max_pop)
    try:
        if not witness_nb:
            return np.zeros(6)
        stats = compute_stat_witness(witness_nb)
        if not np.all(np.isfinite(stats)):
            return np.zeros(6)
        return stats
    except Exception as e:
        print(f"Error in simulate_tree_stats: {e}")
        print()
        return np.zeros(6)




