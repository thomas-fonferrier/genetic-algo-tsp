
import random
import requests
import numpy as np
import random as rd

def fetch_data(instance):
    data = requests.get(f"https://tsp-sra0.onrender.com/instances/{instance}")
    data.raise_for_status()
    return data.json()

def upload_result(student_id, instance_id, initial_instances, result):
    if len(initial_instances) != len(result):
        raise ValueError("initial_instances and result must have the same length.")

    # Build point -> indices map to support repeated coordinates.
    point_to_indices = {}
    for idx, point in enumerate(initial_instances):
        key = tuple(point)
        point_to_indices.setdefault(key, []).append(idx)

    tour = []
    for point in result:
        key = tuple(point)
        if key not in point_to_indices or not point_to_indices[key]:
            raise ValueError(
                "result must contain exactly the same points as initial_instances."
            )
        tour.append(point_to_indices[key].pop(0))

    # Ensure all initial points were consumed exactly once.
    if any(remaining for remaining in point_to_indices.values()):
        raise ValueError(
            "result must contain exactly the same points as initial_instances."
        )

    payload = {
        "student_id": student_id,
        "instance_id": instance_id,
        "tour": tour,
    }
    response = requests.post(
        "https://tsp-sra0.onrender.com/submit",
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


## Mutation :

def mutation(select_pop:list, method:str, n_individus_tot, n_perm=0):
    if not select_pop:
        raise ValueError("selection returned an empty population.")

    # selection stores tuples (individual, fitness), keep only individuals
    selected_individuals = [item[0] if isinstance(item, tuple) else item for item in select_pop]
    new_pop = selected_individuals.copy()
    if method == "permutation":
        while len(new_pop) < n_individus_tot:
            for individual in selected_individuals:
                new_pop.append(permutation(inp_list=individual, num=n_perm))
                if len(new_pop) >= n_individus_tot:
                    break
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

def main(instances:list, selection_method:str, crossover_method=None, mutation_method:str=None,
          n_loop:int=100, n_individus:int=1000, n_perm=0, n_elitism=0, n_crossover:int=0):
    population = init(instances=instances, nb_slt=n_individus)
    for i in range(n_loop):
        population_fit = evaluation(population)
        ind_select = selection(population_fit, selection_method, [n_elitism])
        if crossover_method:
            population = crossover(population, crossover_method, [n_crossover])
        if mutation_method:
            population = mutation(ind_select, mutation_method, n_individus, n_perm)

    final_population = evaluation(population)
    index = 0
    min = final_population[0][1]
    for i in range(len(final_population)):
        if final_population[i][1] < min:
            min = final_population[i][1]
            index = i
    return final_population[index][0]



def evaluation(population):
    list = []
    for individual in population:
        list.append((individual, fitness(individual)))
    return list

## Croisement : 
def cs_fix(fils, p):
    vu=[]
    for k in range(len(fils)):
        if fils[k] not in vu:
            vu.append(fils[k])
            p.remove(fils[k])
        else:
            vu.append(p[0])
            p.pop(0)
    return vu

def croisement_simple(p1:list, p2:list, pts_croisement:int):
    fils_1 = p1[:pts_croisement] + p2[pts_croisement:]
    fils_2 = p2[:pts_croisement] + p1[pts_croisement:]
    return cs_fix(fils_1, p1.copy()), cs_fix(fils_2, p2.copy())
        
def crossover(population:list, method:str, parameters:list):
    if method=="simple":
        n=len(population)//2
        new_population = []
        for k in range(n):
            c1, c2 = croisement_simple(population[2*k], population[2*k + 1], parameters[0])
            new_population.extend([c1, c2])
        if len(population) % 2 == 1:
            new_population.append(population[-1])
        return new_population
    else:
        return population
    

## Distance : calul + evalutation

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
            i=rd.randint(0, len(list_indice)-1)
            indice=list_indice[i]
            individu.append(instances[indice])
            list_indice.remove(indice)
        solutions.append(individu)
    return solutions

## Fonctions de séléction :

def roulette(population_fit:list):
    n=len(population_fit)
    selection = []
    # Lower fitness = better route, so convert distances to positive weights.
    weights = [1.0 / (item[1] + 1e-12) for item in population_fit]
    sum_fit = sum(weights)
    for k in range(n):
        proba = weights[k] / sum_fit
        if rd.random() < proba:
            selection.append(population_fit[k])
    if not selection:
        # Keep at least one parent to avoid empty-population loops.
        best = min(population_fit, key=lambda x: x[1])
        selection = [best]
    return selection

def tri_pivot(l:list):
    if l==[]:
        return []
    elif len(l)==1:
        return l
    pivot=l[0]
    l1=[]
    l2=[]
    for k in range(1,len(l)):
        if l[k][1] < pivot[1]:
            l1.append(l[k])
        else :
            l2.append(l[k])
    return tri_pivot(l1) + [pivot] + tri_pivot(l2)

def elitisme(population_fit:list, n:int):
    if n <= 0:
        n = 1
    pop_triee=tri_pivot(population_fit)
    return pop_triee[:n]
        
def selection(population_fit:list, methode:str, parameters:list):
    if methode=="roulette":
        selected = roulette(population_fit)
        if not selected:
            return [min(population_fit, key=lambda x: x[1])]
        return selected
    elif methode=="elitisme":
        n = parameters[0] if parameters else 1
        selected = elitisme(population_fit, n)
        if not selected:
            return [min(population_fit, key=lambda x: x[1])]
        return selected
    
