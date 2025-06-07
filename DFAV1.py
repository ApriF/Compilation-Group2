import re
from collections import defaultdict

class LiveVariableAnalysis:
    def __init__(self, asm_code):
        self.asm_code = asm_code
        self.instructions = []
        self.variables = set()
        self.live_in = defaultdict(set)
        self.live_out = defaultdict(set)
        self.dataflow_graph = defaultdict(list)
        self.parse_asm()

    def parse_asm(self):
        in_main = False
        for line in self.asm_code.splitlines():
            line = line.strip()
            if line.startswith("main:"):
                in_main = True
            elif in_main and line == "ret":
                break
            elif in_main:
                self.instructions.append(line)
                self.extract_variables(line)

    def extract_variables(self, line):
        matches = re.findall(r"\[([a-zA-Z_][a-zA-Z0-9]*)\]", line)
        self.variables.update(matches)
        # Add "heap" as a variable if push or pop is used
        if "push" in line or "pop" in line:
            self.variables.add("heap")

    def analyze(self):
        for i in reversed(range(len(self.instructions))):
            instr = self.instructions[i]
            self.live_out[i] = set.union(set(), *(self.live_in[succ] for succ in self.dataflow_graph[i]))
            self.live_in[i] = self.live_out[i] - self.defs(instr) | self.uses(instr)

    def defs(self, instr):
        match = re.search(r"mov\s+\[([a-zA-Z_][a-zA-Z0-9]*)\]", instr)
        defs_set = {match.group(1)} if match else set()
        # Handle pop instruction defining "heap"
        if instr.startswith("pop"):
            defs_set.add("heap")
        return defs_set

    def uses(self, instr):
        matches = re.findall(r"\[([a-zA-Z_][a-zA-Z0-9]*)\]", instr)
        # Add "heap" as a used variable for push and pop
        if "push" in instr or "pop" in instr:
            matches.append("heap")
        # Add rsi as a used variable for printf calls
        if "call printf" in instr:
            matches.append("rsi")
        return set(matches)

    def build_dataflow_graph(self):
        for i, instr in enumerate(self.instructions):
            if instr.startswith("jmp"):
                target = self.get_label_index(instr.split()[1])
                self.dataflow_graph[i].append(target)
            elif instr.startswith("jz") or instr.startswith("jnz"):
                target = self.get_label_index(instr.split()[1])
                self.dataflow_graph[i].append(target)
                if i + 1 < len(self.instructions):
                    self.dataflow_graph[i].append(i + 1)
            elif i + 1 < len(self.instructions):
                self.dataflow_graph[i].append(i + 1)

    def get_label_index(self, label):
        for i, instr in enumerate(self.instructions):
            if instr.endswith(f"{label}:"):
                return i
        return -1

    def print_analysis(self):
        print("Instruction-Level Live Variable Analysis:")
        for i, instr in enumerate(self.instructions):
            print(f"{i}: {instr}")
            print(f"  Live In: {self.live_in[i]}")
            print(f"  Live Out: {self.live_out[i]}")

if __name__ == "__main__":
    with open("simple.asm", "r") as f:
        asm_code = f.read()

    lva = LiveVariableAnalysis(asm_code)
    lva.build_dataflow_graph()
    lva.analyze()
    lva.print_analysis()
