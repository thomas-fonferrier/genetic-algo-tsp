
import random
import requests

def fetch_data(instance):
    data = requests.get(f"https://tsp-sra0.onrender.com/instances/{instance}")
    data.raise_for_status()
    return data.json()

## Mutation :

def mutation(individual:list, method:str, n=0):
    if method == "permutation":
        while len(new_pop) < n_individus_tot:
            for individual in select_pop:
                new_pop.append(permutation(inp_list=individual[0], num=n_perm))
        return new_pop[:n_individus_tot]

def permutation(inp_list:list, num:int):
    # obtain list of indices that will be shuffled
    indices = random.sample(range(len(inp_list)), num)

    # keep trying to build up a dictionary of mappings
    # between old and new position, until it is successful
    #
    # Define "succcess" as meaning that no item is back in 
    # its original position
    #
    shuffled_indices = indices.copy()
    success = False
    while not success:
        random.shuffle(shuffled_indices)
        mapping = { a:b for a, b in zip(indices, shuffled_indices) }
        for a, b in mapping.items():
            if a == b:
                success = False
                break
        else:
            success = True

    # Now apply the mappings

    out_list = inp_list.copy()
    for a, b in mapping.items():
        out_list[a] = inp_list[b]

    return out_list

def main(population:list, mutation_method:str, selection_method:str, n:int=10000):
    pass


## Croisement : 
def cs_fix(fils, p):
    pass

def croisement_simple(p1:list, p2:list, pts_croisement:int):
    fils_1=[p1[:pts_croisement] + p2[pts_croisement+1:]]
    fils_2=[p2[:pts_croisement] + p1[pts_croisement+1:]]
    return cs_fix(fils_1, p1), cs_fix(fils_2, p2)
    pass
        


## Distance : calul + evalutation
'''
Format d'une solution :
liste avec l'indice de la ville visité ordonnée.
'''

import numpy as np
import random as rd

def distance_euclidienne(A, B):
    return np.sqrt((B[0]-A[0])**2 + (B[1]-A[1])**2)

def distance_Haversine(A,B):
    R = 6371
    a=np.sin(np.abs(A[1]-B[1])/2)**2 + np.cos(A[1]) * np.cos(B[1]) * np.sin(np.abs(A[0]-B[0])/2)
    return 2 * R * np.arcsin(np.sqrt(a))

def fitness(trip:list): # Distance du parcouru
    distance=0
    for i in range(len(trip)-1):
        distance += distance_euclidienne(trip[i], trip[i+1])
    return distance + distance_euclidienne(trip[-1], trip[0])

## Initialisation :

def init(instances:list, nb_slt:int):
    solutions=[] # pt utiliser des dictionnaire ?
    for i in range(nb_slt):
        individu=[]
        list_indice=[i for i in range(len(instances))]
        for k in range(len(instances)):
            indice=rd.randint(0, len(list_indice))
            individu.append(instances[indice])
            list_indice.pop(indice)
        solutions.append(individu)
    return solutions

## Fonctions de séléction :

def roulette(population_fit:list):
    n=len(population_fit)
    selection = []
    sum_fit=0
    for k in range(n):
        sum_fit+=population_fit[k][0]
    for k in range(n):
        proba=population_fit[k][0]/sum_fit
        if rd.randint(0,100) < proba:
            selection.append(population_fit[k])
    return selection

def tri_pivot(l:list,p):
    if len(l)==1:
        return l
    l1=[]
    l2=[]
    for k in range(1,len(l1)):
        if l[k][0]<p:
            l1.append(l[k])
        else :
            l2.append(l[k])
    return tri_pivot(l1, l1[0][0]) + p + tri_pivot(l2, l2[0][0])

def elitisme(population_fit:list, n:int):
    pop_triee=tri_pivot(population_fit,population_fit[0][0])
    return pop_triee[:n]
        
def selection(population_fit:list, methode:str, parameters:list):
    if methode=="roulette":
        return roulette(population_fit)
    elif methode=="elitisme":
        return elitisme(population_fit, parameters[0])
    
