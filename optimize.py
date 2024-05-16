import googlemaps
from itertools import combinations
import pandas as pd
import numpy as np
import random
import math
import os
from dotenv import load_dotenv

waypoint_distances = {}
waypoint_durations = {}
all_waypoints = []
all_drivers = []

def calculate_distances():
    gmaps = googlemaps.Client(os.getenv('GOOGLE_DISTANCE_MATRIX_KEY'))

    for (waypoint1, waypoint2) in combinations(all_waypoints+all_drivers, 2):
        try:
            route = gmaps.distance_matrix(origins=[waypoint1],
                                        destinations=[waypoint2],
                                        mode="driving", 
                                        language="English",
                                        units="metric")

            distance = route["rows"][0]["elements"][0]["distance"]["value"]

            duration = route["rows"][0]["elements"][0]["duration"]["value"]

            waypoint_distances[frozenset([waypoint1, waypoint2])] = distance
            waypoint_durations[frozenset([waypoint1, waypoint2])] = duration
        
        except Exception as e:
            print("%s: Error with finding the route between %s and %s." % (e, waypoint1, waypoint2))

    with open("route_matrix.tsv", "w") as out_file:
        out_file.write("\t".join(["waypoint1",
                                "waypoint2",
                                "distance_m",
                                "duration_s"]))
        
        for (waypoint1, waypoint2) in waypoint_distances.keys():
            out_file.write("\n" +
                        "\t".join([waypoint1,
                                    waypoint2,
                                    str(waypoint_distances[frozenset([waypoint1, waypoint2])]),
                                    str(waypoint_durations[frozenset([waypoint1, waypoint2])])]))

def load_waypoints():
    waypoint_data = pd.read_csv("route_matrix.tsv", sep="\t")

    for i, row in waypoint_data.iterrows():
        waypoint_distances[frozenset([row.waypoint1, row.waypoint2])] = row.distance_m
        waypoint_durations[frozenset([row.waypoint1, row.waypoint2])] = row.duration_s
    #    all_waypoints.update([row.waypoint1, row.waypoint2])

def compute_fitness(solution, detail=False):
    solution_fitness = 0.0
    subfitness = 0.0
    
#    for driver in all_drivers:
#        print(".",end="")
#        for waypoint in solution[driver]:
#            print("#",end="")

    for key in solution.keys():
        lastwaypoint = key
        subfitness = 0
        for waypoint in solution[key]:
            subfitness += waypoint_durations[frozenset([lastwaypoint, waypoint])]+300
#            print("%s:%s - %s = %d"%(key,lastwaypoint,waypoint,subfitness))
            lastwaypoint = waypoint
        if (len(solution[key])>1):
            subfitness += waypoint_durations[frozenset([waypoint, key])]
        if (detail!=0):
            hours, remainder = divmod(subfitness, 3600)
            minutes, seconds = divmod(remainder, 60)
            print("%s: = %d stops, %d:%02d:%02d" % (key,len(solution[key]),int(hours), int(minutes), int(seconds)))
        solution_fitness+=subfitness
        if (subfitness>2.75*60*60):
            solution_fitness+=60*60
	
#    print("=== %d ==="% (solution_fitness))
    return solution_fitness

def generate_random_agent():
    new_random_agent={}
    shuffled = list(all_waypoints)
    random.shuffle(shuffled)

    for i in range(0,len(all_drivers)):
        new_random_agent[all_drivers[i]] = []

    for i in range(0,len(shuffled)):
        driver = random.randint(0,len(all_drivers)-1)
        new_random_agent[all_drivers[driver]].append(shuffled[i])

    return new_random_agent

def grab(agent_genome, index):
    ct = 0
    for key in agent_genome.keys():
       for item in agent_genome[key]:
           if (ct==index):
               return(item)
           ct+=1
    return ""

def swap(agent_genome, index1, index2):
    i1 = grab(agent_genome,index1)    
    i2 = grab(agent_genome,index2)    

    for key in agent_genome.keys():
       agent_genome[key][:] = ["I2" if x==i2 else x for x in list(agent_genome[key])]
       agent_genome[key][:] = ["I1" if x==i1 else x for x in list(agent_genome[key])]

    for key in agent_genome.keys():
       agent_genome[key][:] = [i1 if x=="I2" else x for x in list(agent_genome[key])]
       agent_genome[key][:] = [i2 if x=="I1" else x for x in list(agent_genome[key])]

    return agent_genome

def mutate_agent(agent_genome, max_mutations=3):
    num_mutations = random.randint(1, max_mutations)
    
    for mutation in range(num_mutations):
        swap_index1 = random.randint(0, len(all_waypoints) - 1)
        swap_index2 = swap_index1

        while swap_index1 == swap_index2:
            swap_index2 = random.randint(0, len(agent_genome) - 1)

        swap(agent_genome, swap_index1, swap_index2)
    return agent_genome

def shuffle_mutation(agent_genome):   
    overload = len(all_waypoints)/len(all_drivers)*2.0
   
    start_driver = random.randint(0, len(all_drivers) - 1)
    while len(agent_genome[all_drivers[start_driver]])==0:
        start_driver = random.randint(0, len(all_drivers) - 1)

    start_index = random.randint(0, len(agent_genome[all_drivers[start_driver]]) - 1)

    length = random.randint(1, min(len(agent_genome[all_drivers[start_driver]])-start_index,20))
    target_driver = random.randint(0, len(all_drivers) - 1)
    while (length+len(agent_genome[all_drivers[target_driver]])>overload):
        length = random.randint(1, min(len(agent_genome[all_drivers[start_driver]])-start_index,20))
        target_driver = random.randint(0, len(all_drivers) - 1)

    genome_subset = agent_genome[all_drivers[start_driver]][start_index:start_index + length]

    target_index = 0
    if (len(agent_genome[all_drivers[target_driver]])>0):
        target_index = random.randint(0, len(agent_genome[all_drivers[target_driver]])-1)

    agent_genome[all_drivers[start_driver]] = agent_genome[all_drivers[start_driver]][:start_index] + agent_genome[all_drivers[start_driver]][start_index + length:]
    agent_genome[all_drivers[target_driver]] = agent_genome[all_drivers[target_driver]][:target_index] + genome_subset + agent_genome[all_drivers[target_driver]][target_index:]

    return agent_genome

def generate_random_population(pop_size):
    random_population = []

    for agent in range(pop_size):
        random_population.append(generate_random_agent())
    return random_population
    
def freeze(d):
    if isinstance(d, dict):
        return frozenset((key, freeze(value)) for key, value in d.items())
    elif isinstance(d, list):
        return tuple(freeze(value) for value in d)
    return d

def unfreeze(d):
    if isinstance(d, frozenset):
        return dict((key, unfreeze(value)) for key, value in d)
    elif isinstance(d, tuple):
        return list(unfreeze(value) for value in d)
    return d

def run_genetic_algorithm(generations=5000, population_size=100):
    population_subset_size = int(population_size / 10.)
    generations_10pct = int(generations / 20.)
    
    # Create a random population of `population_size` number of solutions.
    population = generate_random_population(population_size)

    # For `generations` number of repetitions...
    for generation in range(generations):
       
        # Compute the fitness of the entire current population
        population_fitness = {}

        for agent_genome in population:
            if freeze(agent_genome) in population_fitness:
                continue

            population_fitness[freeze(agent_genome)] = compute_fitness(agent_genome)

        # Take the top 10% shortest road trips and produce offspring each from them
        new_population = []
        for rank, agent_genome in enumerate(sorted(population_fitness,
                                                   key=population_fitness.get)[:population_subset_size]):
            
            if (generation % generations_10pct == 0 or generation == generations - 1) and rank == 0:
                print("Generation %d best: %d | Unique genomes: %d" % (generation,
                                                                       population_fitness[agent_genome],
                                                                       len(population_fitness)))
                print(unfreeze(agent_genome))
		
                s = compute_fitness(unfreeze(agent_genome),True)
                hours, remainder = divmod(s, 3600)
                minutes, seconds = divmod(remainder, 60)
                print("%d:%02d:%02d" % (int(hours), int(minutes), int(seconds)))
                print("")

            # Create 1 exact copy of each of the top road trips
            new_population.append(unfreeze(agent_genome))

            # Create 7 offspring with 1-3 point mutations
            for offspring in range(7):
                new_population.append(mutate_agent(unfreeze(agent_genome), 3))
                
            # Create 2 offspring with a single shuffle mutation
            for offspring in range(2):
                new_population.append(shuffle_mutation(unfreeze(agent_genome)))

        # Replace the old population with the new population of offspring 
        for i in range(len(population))[::-1]:
            del population[i]

        population = new_population

load_dotenv()

with open("waypoints.tsv", 'r') as file:
    all_waypoints = file.readlines()
all_waypoints = [all_waypoints.strip() for all_waypoints in all_waypoints]    

with open("drivers.tsv", 'r') as file:
    all_drivers = file.readlines()
all_drivers = [all_drivers.strip() for all_drivers in all_drivers]    

if not os.path.exists("route_matrix.tsv"):
    calculate_distances()
else:
    load_waypoints()

run_genetic_algorithm(generations=20000, population_size=200)
