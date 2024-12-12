!pip install fuzzywuzzy
!pip install python-Levenshtein
!pip install networkx
!pip install matplotlib
!pip1 install pandas
!pip install tqdm

# prompt: mount drive

import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
from fuzzywuzzy import fuzz


citations_df = pd.read_json('./combined_citations_with_casenumber_updated_2.jsonl', lines=True)

citations_df.head()

citations_df.shape



graph = nx.DiGraph()

# Parse the data and add nodes and edges
for _, row in citations_df.iterrows():
    case_id = row["source"]
    citations = row["target"]

    # Add the case as a node
    graph.add_node(case_id)

    # If citations exist and are not "no cases cited"
    if citations != "no cases cited":
        graph.add_edge(case_id, citations)

# # Visualize the graph
# plt.figure(figsize=(50, 40))

# # Position nodes
# pos = nx.spring_layout(graph)

# # Draw the network
# nx.draw_networkx_nodes(graph, pos, node_size=70, node_color="lightblue")
# nx.draw_networkx_edges(graph, pos, arrowstyle="->", arrowsize=2)
# # nx.draw_networkx_labels(graph, pos, font_size=10, font_color="black")

# # Title for the graph
# plt.title("Case Citations Network", fontsize=16)

# # Display the graph
# plt.show()

in_degree = graph.in_degree()
out_degree = graph.out_degree()
centrality = nx.degree_centrality(graph)

highest_in_degree = sorted(in_degree, key=lambda x: x[1], reverse=True)[:100]
print("Highest In-Degree Nodes:")
for node, degree in highest_in_degree:
    print(f"{node} -> {degree}")


# Initialize an empty DataFrame
in_data_df = pd.DataFrame(columns=['nodes', 'as_citations','no of cases appeared'])

# Find the nodes with the highest centrality
highest_in_degree = sorted(in_degree, key=lambda x: x[1], reverse=True)[:100]

# Iterate over the highest centrality nodes and populate the DataFrame
for node, centrality_value in highest_in_degree:
    as_citations = citations_df[citations_df['target'] == node]['source'].tolist()  # Filter sources where target matches the node
    as_citations_no = len(as_citations)
    # Append the data as a new row in the DataFrame
    # as_cases = citations_df[citations_df['source'] == node]['target'].tolist()
    # as_cases_no = len(as_cases)
    in_data_df = pd.concat([in_data_df, pd.DataFrame({'nodes': [node], 'as_citations': [as_citations], 'no of cases appeared' : [as_citations_no]})], ignore_index=True)

in_data_df.head()

main_data = pd.read_json('./Copy of merged_sc_ca_sd_sslr_nlr_collection_oct_24.jsonl', lines=True)

def find_matching_case_number(word, cutoff=70):
    # Convert the word to lowercase for case-insensitive matching
    word_lower = word.lower()

    # Initialize variables to store the best match and highest score
    best_match = None
    highest_score = 0

    # Iterate through the rows of main_data
    for index, row in main_data.iterrows():
        # Get the nameofparties and convert to lowercase
        nameofparties_lower = row['nameofparties'].lower()

        # Compute the fuzzy match score
        score = fuzz.UQRatio(word_lower, nameofparties_lower)

        # Update the best match if the current score is higher than the highest score
        if score > highest_score and score >= cutoff:
            highest_score = score
            best_match = row['standard_casenumber']
        elif score > highest_score:
            highest_score = score
            best_match = f">>{row['standard_casenumber']}"


    return best_match



from tqdm import tqdm

# Apply the function with progress tracking
tqdm.pandas()
in_data_df['node_casenumber'] = in_data_df['nodes'].progress_apply(find_matching_case_number)

print(in_data_df.head())


