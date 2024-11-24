# performance_test.py
import time
from iengine import KnowledgeBase

def generate_large_kb(n):
    """
    Generate a large knowledge base with n variables
    Example: for n=100, creates p1=>p2; p2=>p3;...; p99=>p100; p1;
    """
    rules = [f"p{i}=>p{i+1}" for i in range(1, n)]
    # Add complex rules
    for i in range(1, n-2, 2):
        rules.append(f"p{i}&p{i+1}=>p{i+2}")
    # Add initial fact
    rules.append("p1")
    return "; ".join(rules)

def measure_performance(kb_str, query, iterations=100):
    """
    Measure average execution time over multiple iterations
    """
    kb = KnowledgeBase()
    kb.tell(kb_str)
    results = {}
    
    for method in ['TT', 'FC', 'BC']:
        total_time = 0
        for _ in range(iterations):
            start = time.perf_counter()  # Use perf_counter for higher precision
            
            if method == 'TT':
                result = kb.ask_tt(query)
            elif method == 'FC':
                result = kb.ask_fc(query)
            else:
                result = kb.ask_bc(query)
                
            total_time += time.perf_counter() - start
            
        # Calculate average time and convert to microseconds
        avg_time = (total_time / iterations) * 1_000_000
        
        results[method] = {
            'time': round(avg_time, 2),  # microseconds
            'result': result
        }
    
    return results

def run_analysis():
    # Test cases with different sizes
    sizes = [5, 6, 7, 8, 9]
    
    print("Performance Analysis Results:\n")
    print("Time measured in microseconds (µs)")
    print("-" * 60)
    
    for size in sizes:
        print(f"\nTest Case: Knowledge Base with {size} variables")
        kb_str = generate_large_kb(size)
        query = f"p{size}"  # Query the last variable
        
        results = measure_performance(kb_str, query)
        
        print("\nResults:")
        print("Method  |  Time (µs)  |  Result")
        print("-" * 60)
        for method, data in results.items():
            print(f"{method:6} | {data['time']:10.2f} | {data['result']}")
        print("-" * 60)

if __name__ == "__main__":
    run_analysis()