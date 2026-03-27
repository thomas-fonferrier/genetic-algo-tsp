import Config 

instances=0
s_m="elitisme"
c_m="simple"
m_m=""

n_l=100
n_i=1000
n_p=0
n_e=100

solution = Config.main(instances, selection_method=s_m, crossover_method=c_m, mutation_method=m_m,
                        n_loop=n_l, n_individus=n_i, n_perm=n_p, n_elitism=n_e)

print(solution)