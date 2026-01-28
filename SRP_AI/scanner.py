# Save this as: scanner.py
import ast

def get_class_metrics(class_node):
    # 1. Get Methods
    methods = [n for n in class_node.body if isinstance(n, ast.FunctionDef)]
    
    # 2. Get Attributes
    all_attributes = set()
    for node in ast.walk(class_node):
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            if node.value.id == "self":
                all_attributes.add(node.attr)

    # 3. Calculate Cohesion
    usage_list = []
    for m in methods:
        used_here = {n.attr for n in ast.walk(m) if isinstance(n, ast.Attribute) and getattr(n.value, 'id', '') == 'self'}
        usage_list.append(used_here)

    shared = 0
    total_pairs = 0
    for i in range(len(usage_list)):
        for j in range(i + 1, len(usage_list)):
            total_pairs += 1
            if usage_list[i] & usage_list[j]:
                shared += 1
    
    cohesion = shared / total_pairs if total_pairs > 0 else 1.0

    # 4. Check Responsibilities
    logic_words = {'calc', 'compute', 'math', 'process', 'logic', 'update', 'modify'}
    io_words = {'print', 'show', 'display', 'send', 'sms', 'email', 'message'}
    storage_words = {'save', 'store', 'db', 'database', 'write', 'record', 'log'}

    has_logic = 0
    has_io = 0
    has_storage = 0

    for m in methods:
        name = m.name.lower()
        if any(word in name for word in logic_words): has_logic = 1
        if any(word in name for word in io_words): has_io = 1
        if any(word in name for word in storage_words): has_storage = 1

    res_count = has_logic + has_io + has_storage
    if res_count == 0 and len(methods) > 0: res_count = 1

    return [len(methods), len(all_attributes), cohesion, res_count]

def analyze_code_content(code_content):
    """
    Parses a string of Python code and returns metrics for all classes found.
    """
    try:
        tree = ast.parse(code_content)
        results = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                metrics = get_class_metrics(node)
                results.append({
                    "Class Name": node.name,
                    "Methods": metrics[0],
                    "Attributes": metrics[1],
                    "Cohesion": metrics[2],
                    "Responsibilities": metrics[3],
                    "Features": metrics # Keep the raw list for the AI
                })
        return results
    except Exception as e:
        return str(e)