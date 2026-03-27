import Config

student_id = "Thomas & Loris"
instance_id = "regions"

data = Config.fetch_data(instance_id)
result = Config.main(instances=data["cities"], selection_method="elitisme", mutation_method="permutation", n_loop=1000, n_individus=1000, n_perm=3)
response = Config.upload_result(student_id=student_id, instance_id=instance_id, initial_instances=data["cities"], result=result)
print(response)



