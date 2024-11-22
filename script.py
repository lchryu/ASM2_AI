import sys  # Để xử lý command line arguments
from itertools import product  # Để tạo tất cả các tổ hợp True/False có thể

class KnowledgeBase:
    def __init__(self):
        self.facts = set()      # Lưu các fact đơn lẻ (ví dụ: "a", "b", "p2")
        self.rules = []         # Lưu các rules (ví dụ: "p=>q", "a&b=>c")
        self.symbols = set()    # Lưu tất cả các biến xuất hiện trong KB

    def tell(self, sentence):
        """
        Xử lý câu trong phần TELL, tách thành facts và rules
        Input: "p2=> p3; p3 => p1; a; b; p2;"
        """
        # Tách thành các mệnh đề riêng lẻ bằng dấu ;
        clauses = sentence.split(';')
        
        for clause in clauses:
            clause = clause.strip()  # Loại bỏ khoảng trắng thừa
            if not clause:  # Bỏ qua các clause rỗng
                continue
                
            if '=>' in clause:  # Nếu có dấu => thì đây là rule
                # Tách thành premise (điều kiện) và conclusion (kết luận)
                premise, conclusion = clause.split('=>')
                premise = premise.strip()
                conclusion = conclusion.strip()
                
                # Thêm rule vào KB
                self.rules.append((premise, conclusion))
                
                # todo: should check -------------------------------------------------------------------
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
        Đánh giá giá trị của một expression với model đã cho
        model là dictionary chứa giá trị True/False của các symbols
        """
        if isinstance(expression, bool):  # Nếu expression đã là boolean
            return expression
            
        if '&' in expression:  # Xử lý phép AND
            conjuncts = expression.split('&')
            # Trả về True nếu tất cả các thành phần đều True
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
        Kiểm tra xem model có thỏa mãn KB không
        Model thỏa mãn khi tất cả facts và rules đều đúng
        """
        # Kiểm tra tất cả facts phải True trong model
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
        Trả về YES/NO và số models nếu YES
        """
        if query not in self.symbols:  # Nếu query không xuất hiện trong KB
            return "NO"
            
        models_count = 0  # Đếm số models thỏa mãn KB
        
        # Tạo tất cả assignments có thể cho các symbols
        # Ví dụ với 2 biến sẽ có: TT, TF, FT, FF
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

def main():
    # Kiểm tra đầu vào command line
    if len(sys.argv) != 3:
        print("Usage: python script.py <filename> <method>")
        return

    filename = sys.argv[1]  # Tên file input
    method = sys.argv[2]    # Phương pháp suy luận (TT, FC, BC)

    kb = KnowledgeBase()
    
    # Đọc file input
    with open(filename, 'r') as file:
        # Đọc từng dòng và loại bỏ khoảng trắng
        lines = [line.strip() for line in file.readlines()]
        
        # Tìm vị trí của TELL và ASK
        tell_index = lines.index('TELL')
        ask_index = lines.index('ASK')
        
        # Xử lý phần TELL
        tell_sentences = ''.join(lines[tell_index+1:ask_index]).strip()
        kb.tell(tell_sentences)
        
        # Xử lý phần ASK
        query = lines[ask_index+1].strip()

    # Thực hiện suy luận theo method được chọn
    if method == 'TT':
        print(kb.ask_tt(query))
    elif method == 'FC':
        print("FC not implemented yet")
    else:
        print("BC not implemented yet")

if __name__ == "__main__":
    main()