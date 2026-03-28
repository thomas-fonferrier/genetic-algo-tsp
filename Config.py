
import random
import requests
import numpy as np
import random as rd

def fetch_data(instance):
    """Va chercher une instance sur le serveur du TP ; on récupère le JSON (villes, etc.)."""
    data = requests.get(f"https://tsp-sra0.onrender.com/instances/{instance}")
    data.raise_for_status()
    return data.json()

def upload_result(student_id, instance_id, initial_instances, result):
    """Poste la solution : on envoie l’ordre des villes sous forme d’indices pour le serveur."""
    if len(initial_instances) != len(result):
        raise ValueError("initial_instances et result doivent avoir la même taille.")

    point_to_indices = {}
    for idx, point in enumerate(initial_instances):
        key = tuple(point)
        point_to_indices.setdefault(key, []).append(idx)

    tour = []
    for point in result:
        key = tuple(point)
        if key not in point_to_indices or not point_to_indices[key]:
            raise ValueError(
                "result doit contenir exactement les mêmes points que initial_instances."
            )
        tour.append(point_to_indices[key].pop(0))

    if any(remaining for remaining in point_to_indices.values()):
        raise ValueError(
            "result doit contenir exactement les mêmes points que initial_instances."
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
    """À partir des parents choisis par la sélection, on refait une population en mutant."""
    if not select_pop:
        raise ValueError("la sélection a renvoyé une population vide.")

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
    """On tire quelques positions et on échange les villes : idée de petite perturbation locale."""
    indices = random.sample(range(len(inp_list)), num)

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

    out_list = inp_list.copy()
    for a, b in mapping.items():
        out_list[a] = inp_list[b]

    return out_list

def evaluation(population):
    """Pour chaque trajet, on calcule sa distance ; on garde le couple (trajet, fitness)."""
    list = []
    for individual in population:
        list.append((individual, fitness(individual)))
    return list

## Croisement :
def cs_fix(fils, p):
    """Quand le croisement crée des doublons, on complète avec ce qu’il reste du parent."""
    vu=[]
    for k in range(len(fils)):
        if fils[k] not in vu:
            vu.append(fils[k])
            p.remove(fils[k])
        else:
            vu.append(p[0])
    return vu

def croisement_simple(p1:list, p2:list, pts_croisement:int):
    """Un point de coupe : on prend un bout chez papa, la suite chez maman (et l’inverse)."""
    fils_1 = p1[:pts_croisement] + p2[pts_croisement:]
    fils_2 = p2[:pts_croisement] + p1[pts_croisement:]
    return cs_fix(fils_1, p1.copy()), cs_fix(fils_2, p2.copy())
        
def crossover(population:list, method:str, parameters:list):
    """Mélange les parents deux par deux ; si la méthode n’est pas gérée, on renvoie la population telle quelle."""
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
    

## Distance : calcul + évaluation

def distance_euclidienne(A, B):
    """Distance habituelle entre deux points du plan (comme sur une carte en 2D)."""
    return np.sqrt((B[0]-A[0])**2 + (B[1]-A[1])**2)

def distance_Haversine(A,B):
    """Distance sur une sphère (rayon Terre) ; pratique si les coords sont en lat/lon radians."""
    R = 6371
    a=np.sin(np.abs(A[1]-B[1])/2)**2 + np.cos(A[1]) * np.cos(B[1]) * np.sin(np.abs(A[0]-B[0])/2)
    return 2 * R * np.arcsin(np.sqrt(a))

def fitness(trip:list):
    """Fitness = longueur du tour : on fait le tour des villes puis on revient au départ."""
    distance=0
    for i in range(len(trip)-1):
        distance += distance_euclidienne(trip[i], trip[i+1])
    return distance + distance_euclidienne(trip[-1], trip[0])

## Initialisation :

def init(instances:list, nb_slt:int):
    """On fabrique plein de trajets différents en restant raisonnable : on suit souvent un voisin proche."""
    if not instances:
        return []

    solutions = []
    n_cities = len(instances)
    nearest_pool_size = min(3, n_cities - 1) if n_cities > 1 else 0

    for _ in range(nb_slt):
        unvisited = list(range(n_cities))
        start_idx = rd.choice(unvisited)
        route_idx = [start_idx]
        unvisited.remove(start_idx)
        current_idx = start_idx

        while unvisited:
            ranked_candidates = sorted(
                unvisited,
                key=lambda idx: distance_euclidienne(
                    instances[current_idx], instances[idx]
                ),
            )

            if nearest_pool_size > 0:
                pool = ranked_candidates[:nearest_pool_size]
                next_idx = rd.choice(pool)
            else:
                next_idx = ranked_candidates[0]

            route_idx.append(next_idx)
            unvisited.remove(next_idx)
            current_idx = next_idx

        solutions.append([instances[idx] for idx in route_idx])

    return solutions

## Fonctions de sélection :

def roulette(population_fit:list):
    """Tirage au sort biaisé : les trajets courts ont plus de chances d’être choisis."""
    n=len(population_fit)
    selection = []
    weights = [1.0 / (item[1] + 1e-12) for item in population_fit]
    sum_fit = sum(weights)
    for k in range(n):
        proba = weights[k] / sum_fit
        if rd.random() < proba:
            selection.append(population_fit[k])
    if not selection:
        best = min(population_fit, key=lambda x: x[1])
        selection = [best]
    return selection

def tri_pivot(l:list):
    """Petit tri récursif pour classer les individus selon leur distance (fitness)."""
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
    """On garde seulement le haut du classement ; si n est trop petit, on force au moins un survivant."""
    if n <= 0:
        n = 1
    pop_triee=tri_pivot(population_fit)
    return pop_triee[:n]
        
def selection(population_fit:list, methode:str, parameters:list):
    """Branche vers la roulette ou l’élitisme ; en secours, on prend le meilleur si la liste est vide."""
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
    
def main(instances:list, selection_method:str, crossover_method=None, mutation_method:str=None,
          n_loop:int=100, n_individus:int=1000, n_perm=0, n_elitism=0, n_crossover:int=0):
    """C’est le moteur : plusieurs générations, puis on renvoie le meilleur trajet trouvé."""
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
