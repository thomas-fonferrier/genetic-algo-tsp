
import random
import requests

def fetch_data(instance):
    data = requests.get(f"https://tsp-sra0.onrender.com/instances/{instance}")
    data.raise_for_status()
    return data.json()

def mutation(individual:list, method:str, n=0):
    if method == "permutation":
        permutation(inp_list=individual, num=n)

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

def fitness(trip:list): # Distance du parcous
    distance=0
    for i in range(len(trip)-1):
        distance += distance_euclidienne(trip[i], trip[i+1])
    return distance

def init(population:list, nb_slt:int):
    solutions=[] # pt utiliser des dictionnaire ?
    for i in range(nb_slt):
        individu=[]
        list_indice=[i for i in range(len(population))]
        for k in range(len(population)):
            indice=rd.randint(0, len(list_indice))
            individu.append(population[indice])
            list_indice.pop(indice)
        solutions.append(individu)
    return solutions