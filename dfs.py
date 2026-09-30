graph = {
    'A': ['B', 'C'],
    'B': ['D', 'E'],
    'C': ['F', 'G'],
    'D': ['H'],
    'E': [],
    'F': [],
    'G': [],
    'H': []
}


def dfs(graph, current_element, target_element, visited=None, path=None):
    if visited is None:
        visited = set()
    if path is None:
        path = []

    visited.add(current_element)
    path.append([])

    if current_element == target_element:
        

    


