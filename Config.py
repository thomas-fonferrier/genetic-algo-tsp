import requests

def fetch_data(instance):
    data = requests.get(f"https://tsp-sra0.onrender.com/instances/{instance}")
    data.raise_for_status()
    return data.json()

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
        
