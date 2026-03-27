import Config 

student_id="Thomas & Loris"
instance_id="random_50"


data=Config.fetch_data(instance_id)

print(data)

instance=data["cities"]
s_m="elitisme"
c_m="simple"
m_m=""

n_l=100
n_i=1000
n_p=0
n_e=100
n_c=24

result = Config.main(instance, selection_method=s_m, crossover_method=c_m, mutation_method=m_m,
                        n_loop=n_l, n_individus=n_i, n_perm=n_p, n_elitism=n_e, n_crossover=n_c)

response = Config.upload_result(student_id=student_id, instance_id=instance_id, initial_instances=data["cities"], result=result)

print(response)