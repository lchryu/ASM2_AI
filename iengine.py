import sys  # For handling command line arguments
from itertools import product  # To generate all possible True/False combinations


class KnowledgeBase:
    def __init__(self):
        self.facts = set()      # Store individual facts (e.g., "a", "b", "p2")
        self.rules = []         # Store rules (e.g., "p=>q", "a&b=>c")
        self.symbols = set()    # Store all variables appearing in KB

    def tell(self, sentence):
        """
        Process sentences in TELL section, separate into facts and rules
        Input: "p2=> p3; p3 => p1; a; b; p2;"
        """
        # Split into individual clauses by semicolon
        clauses = sentence.split(';')
        
        for clause in clauses:
            clause = clause.strip()  # Remove excess whitespace
            if not clause:  # Skip empty clauses
                continue
                
            if '=>' in clause:  # If contains => then this is a rule
                # Split into premise and conclusion
                premise, conclusion = clause.split('=>')
                
                # Thêm rule vào KB
                self.rules.append((premise, conclusion))
                
                # Thêm các symbols từ rule vào tập symbols
                if '&' in premise:  # Nếu premise có phép AND
                    self.symbols.update(p.strip() for p in premise.split('&'))
                else:
                    self.symbols.add(premise)
                self.symbols.add(conclusion)
            else:  # Nếu không có => thì đây là fact đơn lẻ
                self.facts.add(clause)
                self.symbols.add(clause)

    def evaluate(self, expression, model):
        """
        Evaluate the value of an expression with given model
        model is a dictionary containing True/False values of symbols
        """
        if isinstance(expression, bool):  # If expression is already boolean
            return expression

        if '&' in expression:  # Handle AND operation
            conjuncts = expression.split('&')
            # Return True if all components are True
            return all(self.evaluate(c.strip(), model) for c in conjuncts)
            
        elif '=>' in expression:  # Xử lý phép kéo theo p=>q
            premise, conclusion = expression.split('=>')
            p_value = self.evaluate(premise.strip(), model)
            q_value = self.evaluate(conclusion.strip(), model)
            # p=>q tương đương với (NOT p) OR q
            return (not p_value) or q_value
        else:
            # Expression là một symbol đơn lẻ, lấy giá trị từ model
            return model.get(expression.strip(), False)

    def evaluate_rule(self, premise, conclusion, model):
        """Đánh giá một rule cụ thể p=>q"""
        p_value = self.evaluate(premise, model)
        q_value = self.evaluate(conclusion, model)
        return (not p_value) or q_value

    def check_kb(self, model):
        """
        Check if model satisfies KB
        Model satisfies when all facts and rules are true
        """
        # Check all facts must be True in model
        for fact in self.facts:
            if not model[fact]:
                return False
                
        # Kiểm tra tất cả rules phải True trong model
        for premise, conclusion in self.rules:
            if not self.evaluate_rule(premise, conclusion, model):
                return False
                
        return True

    def ask_tt(self, query):
        """
        Truth Table method
        Returns YES/NO and number of models if YES
        """
        if query not in self.symbols:  # If query doesn't appear in KB
            return "NO"
            
        models_count = 0  # Count number of models satisfying KB
        
        # Generate all possible assignments for symbols
        # Example with 2 variables: TT, TF, FT, FF
        for values in product([True, False], repeat=len(self.symbols)):
            # Tạo model từ assignment
            model = dict(zip(self.symbols, values))
            
            # Kiểm tra nếu model thỏa mãn KB
            if self.check_kb(model):
                models_count += 1
                # Nếu tìm thấy model thỏa mãn KB mà query false
                # thì return NO vì không thể suy ra query
                if not model[query]:
                    return "NO"
        
        if models_count > 0:
            return f"YES: {models_count}"
        return "NO"
    
    
    def ask_fc(self, query):
        """Forward Chaining method"""
        # Set of inferred facts
        inferred = self.facts.copy()
        # List of facts in order of inference
        inferred_list = list(inferred)

        while True:
            new_fact = False
            for premise, conclusion in self.rules:
                if conclusion not in inferred:  # Chưa suy ra conclusion
                    if "&" in premise:
                        # Nếu premise có AND
                        premises = premise.split("&")
                        if all(p.strip() in inferred for p in premises):
                            inferred.add(conclusion)
                            inferred_list.append(conclusion)
                            new_fact = True
                    else:
                        # Premise đơn lẻ
                        if premise in inferred:
                            inferred.add(conclusion)
                            inferred_list.append(conclusion)
                            new_fact = True

            if not new_fact:  # Không suy ra được fact mới
                break

        if query in inferred:
            return f"YES: {', '.join(inferred_list)}"
        return "NO"


    def ask_bc(self, query):
        """Backward Chaining method"""

        def bc_helper(goal, visited=None):
            if visited is None:
                visited = set()

            if goal in visited:  # Avoid infinite loops
                return False

            visited.add(goal)

            if goal in self.facts:  # Goal là fact
                return True

            # Tìm rules có thể suy ra goal
            for premise, conclusion in self.rules:
                if conclusion == goal:
                    if "&" in premise:
                        # Nếu premise có AND
                        premises = premise.split("&")
                        if all(bc_helper(p.strip(), visited.copy()) for p in premises):
                            return True
                    else:
                        if bc_helper(premise, visited.copy()):
                            return True

            return False

        def get_proof(goal, visited=None):
            if visited is None:
                visited = set()

            if goal in self.facts:
                return [goal]

            for premise, conclusion in self.rules:
                if conclusion == goal and goal not in visited:
                    visited.add(goal)
                    if "&" in premise:
                        premises = premise.split("&")
                        all_proofs = []
                        for p in premises:
                            proofs = get_proof(p.strip(), visited.copy())
                            if proofs:
                                all_proofs.extend(proofs)
                        if all_proofs:
                            all_proofs.append(goal)
                            return all_proofs
                    else:
                        proofs = get_proof(premise, visited.copy())
                        if proofs:
                            proofs.append(goal)
                            return proofs
            return []

        if bc_helper(query):
            proof = get_proof(query)
            return f"YES: {', '.join(proof)}"
        return "NO"


def main():
    # Check command line input
    if len(sys.argv) != 3:
        print("Usage: python script.py <filename_testcase> <method>")
        return

    filename = sys.argv[1]  # Input filename
    method = sys.argv[2]    # Reasoning method (TT, FC, BC)

    kb = KnowledgeBase()
    
    # Read input file
    with open(filename, 'r') as file:
        # Read each line and remove whitespace
        lines = [line.strip() for line in file.readlines()]
        
        # Find positions of TELL and ASK
        tell_index = lines.index('TELL')
        ask_index = lines.index('ASK')
        
        # Process TELL section
        tell_sentences = ''.join(lines[tell_index+1:ask_index]).strip()
        kb.tell(tell_sentences)
        
        # Process ASK section
        query = lines[ask_index+1].strip()

    # Perform reasoning based on the selected method
    if method == 'TT' or method == 'tt':
        print(kb.ask_tt(query))
    elif method == 'FC' or method == 'fc':
        print(kb.ask_fc(query))
    elif method == 'BC' or method == 'bc':
        print(kb.ask_bc(query))
    else:
        print("Invalid method. Please choose TT, FC, or BC.")

if __name__ == "__main__":
    main()