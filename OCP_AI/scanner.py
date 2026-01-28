import ast

def analyze_code_content(code_content):
    feature_sets = []
    visited_nodes = set()

    try:
        node = ast.parse(code_content)

        for item in ast.walk(node):
            if isinstance(item, ast.If) and item not in visited_nodes:
                is_ocp_risk = 0 # We only flag it if it's an OCP-style comparison
                branch_count = 1
                
                # Check the comparison
                if isinstance(item.test, ast.Compare):
                    # Check the RIGHT side (the comparators)
                    for comparator in item.test.comparators:
                        # If comparing to a String (e.g., "paypal"), it's an OCP risk
                        if isinstance(comparator, ast.Constant) and isinstance(comparator.value, str):
                            is_ocp_risk = 1
                
                # Dig through the chain
                current = item
                while current.orelse and isinstance(current.orelse[0], ast.If):
                    branch_count += 1
                    current = current.orelse[0]
                    visited_nodes.add(current)
                
                feature_sets.append([branch_count, is_ocp_risk])

    except Exception as e:
        print(f"Error: {e}")
        
    return feature_sets
