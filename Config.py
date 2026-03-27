'''
Format d'une solution :
liste avec l'indice de la ville visité ordonnée.
'''

import numpy as np

def distance(A, B):
    return np.sqrt((B[0]-A[0])**2 + (B[1]-A[1])**2)

def distance_Haversine(A,B):
    R = 6371
    a=np.sin(np.abs(A[1]-B[1])/2)**2 + np.cos(A[1]) * np.cos(B[1]) * np.sin(np.abs(A[0]-B[0])/2)
    return 2 * R * np.arcsin(np.sqrt(a))

def fitness(trip:list): # Distance du parcous
    
    for city in trip:
        pass
    pass

def init(cities:list):
    pass