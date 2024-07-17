import os, time, json
#----
#---
from main_functions import (
    get_files, 
    get_model, 
    ask_reachability_radius,
    interaction_graph,
    mutual_r_reachability_graph,
    r_strongly_connected_components,
    r_proximity_graph,
    agony_scores,
    autonomous_pairs,
)
#------------------------------------------------------------------------------------------------------------------------
#-----                                                  Constants                                                   -----
#------------------------------------------------------------------------------------------------------------------------
# 
BOLD = "\033[1m"     #ANSI escape code for bold text
RESET = "\033[0m"    #Reset ANSI escape code
GREEN = "\033[32m"              # Enzymes for MM
BLUE = "\033[34m"               # Substrates for MM  &&  Highlighting
RED = "\033[31m"                # Products for MM
ORANGE = "\033[38;5;214m"       # Intermediate for MM
MAGENTA = "\033[35m"           # Reaction ID
#------------------------------------------------------------------------------------------------------------------------
#-----                                         File manipulation functions                                          -----
#------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    #===========
    #Ask the reader to provide the reachability radius
    r = ask_reachability_radius (verbose=1)
    #===========
    #Get files paths and files names
    files_path, files_names = get_files()
    #---
    #Define the file path for the json file
    directory_path = directory_path = filedialog.askdirectory(title='Select Directory to Save Output')
    os.makedirs(directory_path, exist_ok=True)
    #---
    #Open the file for benchmarking
    f = open(directory_path + os.sep + "Benchmarking data.csv", "w")
    f.write(f"Biomodel name,Number of species,Number of reactions,Number of edges,Number of r-sccs,Species in r-sccs,Execution time\n")
    #---
    # g = open(directory_path + os.sep + "Benchmarking data.csv", "w")
    # g.write(f"Biomodels, Number of edges\n")
    #---
    for file_path, file_name in zip(files_path, files_names):
        #---
        try:
            print()
            print(f"{BOLD}\tExtracted biomodel: {RESET}{BLUE} {file_name}{RESET}")
            #Read the sbml file and extract the model
            sbml_model, sbml_document = get_model(file_path)
            #---
            #Get the species
            species = [species.getId() for species in sbml_model.getListOfSpecies()]
            #===========
            #===========
            #Record start time
            start_time_1 = time.perf_counter()
            #-------------------------------------------------------
            #Get interaction graph
            G = interaction_graph(sbml_model, file_name, verbose = 0)
            #------------------- 
            #Calculate elapsed time
            elapsed_time_1 = time.perf_counter() - start_time_1
            print(f"{BOLD}\t  Execution time for computing interaction graph: {RESET}{BLUE} {elapsed_time_1}{RESET}")
            #===========
            #Record start time
            start_time_2 = time.perf_counter()
            #Get the mutual r-reachability graph
            H =  mutual_r_reachability_graph (G, r, file_name, verbose=0)
            #Calculate elapsed time
            elapsed_time_2 = time.perf_counter() - start_time_2
            print(f"{BOLD}\t  Execution time for computing mutual r-reachability graph: {RESET}{BLUE} {elapsed_time_2}{RESET}")
            #===========
            #Record start time
            start_time_3 = time.perf_counter()
            #Get r-strongly connected components
            r_sccs_index, r_sccs_species = r_strongly_connected_components (H, species, verbose=0)
            #Calculate elapsed time
            elapsed_time_3 = time.perf_counter()- start_time_3
            print(f"{BOLD}\t  Execution time for computing the r-sccs: {RESET}{BLUE} {elapsed_time_3}{RESET}")
            #===========
            #Record start time
            start_time_4 = time.perf_counter()
            #Get the r-proximity graph
            Q =  r_proximity_graph (G, r_sccs_index, file_name, verbose=0)
            #Calculate elapsed time
            elapsed_time_4 = time.perf_counter() - start_time_4
            print(f"{BOLD}\t  Execution time for computing r-proximity graph: {RESET}{BLUE} {elapsed_time_4}{RESET}")
            #===========
            #Record start time
            start_time_5 = time.perf_counter()
            #Get the agony scores
            r_sccs_and_scores, hierarchy, r_sccs_scores = agony_scores(Q, verbose=0)
            #Calculate elapsed time
            elapsed_time_5 = time.perf_counter() - start_time_5
            print(f"{BOLD}\t  Execution time for abony based hierarchical ranking: {RESET}{BLUE} {elapsed_time_5}{RESET}")
            #===========
            #Record start time
            start_time_6 = time.perf_counter()
            #Autonomous pairs
            AP_index, AP_names = autonomous_pairs (r_sccs_species, r_sccs_index, r_sccs_scores)
            #Calculate elapsed time
            elapsed_time_6 = time.perf_counter() - start_time_6
            print(f"{BOLD}\t  Execution time for computing hierarchical decomposition: {RESET}{BLUE} {elapsed_time_6}{RESET}")
            #===========
            elapsed_time = elapsed_time_1+elapsed_time_2+elapsed_time_3+elapsed_time_4+elapsed_time_5+elapsed_time_6
            print(f"{BOLD}\t  Total execution time: {RESET}{BLUE} {elapsed_time}{RESET}")
            #===========
            max_length = max(len(lst) for lst in AP_index + AP_names)
            #===========
            # # Create the dictionary
            d = {}
            for i in range(len(AP_index)):
                d[f"AP{i+1} indexes"] = AP_index[i]
                d[f"AP{i+1} names"] = AP_names[i]
            #===========
            #Save as json file
            selected_outputs = {
                                "Species": {
                                    "Species": species
                                },
                                "Interaction graph": {
                                    "Source nodes": [item[0] for item in G.edges],
                                    "Target nodes": [item[1] for item in G.edges]
                                },
                                "Quotient graph": {
                                    "Source nodes": [item[0] for item in Q.edges],
                                    "Target nodes": [item[1] for item in Q.edges]
                                },
                                "r-sccs": {
                                    "Indices": r_sccs_index,
                                    "Names": r_sccs_species,
                                    "Number of species": [len(item) for item in r_sccs_index],
                                    "Ranks": r_sccs_scores
                                },
                                "Autonomous pairs": d
                                }
            #===========
            with open(os.path.join(directory_path, str(file_name) + ".json"), "w", encoding='utf-8') as file:
                json.dump(selected_outputs, file, ensure_ascii=False, indent=4)
            #===========
            num_sp_rscc = [len(item) for item in r_sccs_index]
            num_sp_rscc_str = '; '.join(map(str, num_sp_rscc)) 
            #===========
            #Save benchmarking as .csv
            f.write(f"{file_name},{len(species)},{len(sbml_model.getListOfReactions())},{len(G.edges)},{len(r_sccs_index)},{[num_sp_rscc_str]}, {elapsed_time}\n")
            #===========
        except:
            continue
    # #===========
    #===========
    f.close()
    input()
 
