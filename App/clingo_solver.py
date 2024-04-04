import re
import clingo
import os
import sys

class MiningDomainSolver:
    def __init__(self, scenario_number, initial_bmode, bmode_changes):
        base_path = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
        self.bmode_file_map = {
            "safe": f"{base_path}/Safe_BMode.txt",
            "normal": f"{base_path}/Normal_BMode.txt",
            "risky": f"{base_path}/Risky_BMode.txt"
        }
        self.initial_bmode = initial_bmode
        self.behavior_modes = []
        if bmode_changes[0][1].get():
            self.behavior_modes.append(bmode_changes[0][1].get())
            if bmode_changes[1][1].get():
                self.behavior_modes.append(bmode_changes[1][1].get())
        self.bmode_change_timesteps = []
        if bmode_changes[0][0].get():
            self.bmode_change_timesteps.append(bmode_changes[0][0].get())
            if bmode_changes[1][0].get():
                self.bmode_change_timesteps.append(bmode_changes[1][0].get())
        self.control = clingo.Control()
        self.bmode_change_number = 0
        self.learned_information = ""
        self.domain_file = f"{base_path}/Mining_Robot_Planning_Domain.txt"
        self.policy_file = f"{base_path}/Mining_Robot_Policies.txt"
        self.plan_file = f"{base_path}/Mining_Robot_Scenario{scenario_number}.txt"
        self.behavior_file = self.bmode_file_map[initial_bmode.lower()]
        self.plan_and_learned_info = []
        self.temp_asp_filename = "Temp_ASP_File.txt"


    def solve(self):

        def on_model(model):
            self.plan_and_learned_info = model.__str__().split(" ")

        with open(self.domain_file, "r") as domain_file:
            domain_file_content = domain_file.read()
        with open(self.policy_file, "r") as policy_file:
            policy_file_content = policy_file.read()
        with open(self.plan_file, "r") as plan_file:
            plan_file_content = plan_file.read()
        with open(self.behavior_file, "r") as behavior_file:
            behavior_file_content = behavior_file.read()

        asp_program = f"#const n1 = {0 if self.bmode_change_number == 0 else self.bmode_change_timesteps[self.bmode_change_number-1]}.\n"
        asp_program += (domain_file_content + "\n\n" +
                        policy_file_content + "\n\n" + 
                        plan_file_content + "\n\n" + 
                        behavior_file_content + "\n\n" + 
                        self.learned_information)

        with open(self.temp_asp_filename, "w") as file:
            file.write(asp_program)

        self.control.load(self.temp_asp_filename)
        self.control.ground([("base", [])])
        self.control.solve(on_model=on_model)

    def delete_temp_file(self):
        if os.path.exists(self.temp_asp_filename):
            os.remove(self.temp_asp_filename)

    def get_timestep_of_fact(self, fact):
        """
        :param fact: An ASP fact
        :return: the time step the fact occured in, or -1 if no numbers are present in fact
        Uses a regular expression to aquire the final number in fact.
        Using our ASP code conventions, this is the time step.
        """
        nums_in_fact = re.findall(r'(\d+)', fact)
        return int(nums_in_fact[-1]) if nums_in_fact else -1

    def get_predicate_of_fact(self, fact):
        return fact[:fact.find("(")].strip()
    
    def record_fact(self, fact):
        predicate, timestep = self.get_predicate_of_fact(fact), self.get_timestep_of_fact(fact)

        # Not the final behavior mode change
        if self.bmode_change_number < len(self.bmode_change_timesteps):
            if predicate == "occurs" and timestep < int(self.bmode_change_timesteps[self.bmode_change_number]):
                return True
            elif predicate == "holds" and timestep <= int(self.bmode_change_timesteps[self.bmode_change_number]):
                return True

        # Final behavior mode change
        else:
            if predicate == "occurs" or predicate == "holds":
                return True

        return False
    
    def extract_plan_from_learned_information(self):
        occurs = []
        facts = self.learned_information.split("\n")
        for fact in facts:
            predicate = self.get_predicate_of_fact(fact)
            if predicate == "occurs":
                occurs.append(fact)
        occurs_sorted = sorted(set(occurs), key=self.get_timestep_of_fact)
        plan = ""
        action_num = 0
        for o in occurs_sorted:
            non_wait_action = re.search(r'occurs\((\w+)\(([^)]*)\),', o)
            wait_action = r'occurs\(wait,\d+\)'
            if non_wait_action:
                action_word = non_wait_action.group(1)
                parameters = non_wait_action.group(2).split(',')
                if action_word == "move":
                    plan += f"{action_num}. Move from {parameters[0]} to {parameters[1]}\n"
                elif action_word == "collect":
                    plan += f"{action_num}. Collect {parameters[0]}\n"
            elif wait_action:
                plan += f"{action_num}. Wait\n"
            if non_wait_action or wait_action:
                action_num += 1
        return plan

    def annotate_plan_with_bmode_changes(self, plan):
        modified_plan = []
        plan_array = plan.split("\n")
        plan_array[0] = f"*** Begin in {self.initial_bmode} Mode ***\n{plan_array[0]}"
        for i, action in enumerate(plan_array):
            for j, timestep in enumerate(self.bmode_change_timesteps):
                if i + 1 == int(timestep):
                    action += f"\n*** Change to {self.behavior_modes[j]} Mode ***"
            modified_plan.append(action)
        annotated_plan = "\n".join(modified_plan)
        return annotated_plan

    def generate_plan_with_bmode_changes(self):
        for i in range(len(self.behavior_modes) + 1):
            self.solve()
            for fact in self.plan_and_learned_info:
                if self.record_fact(fact):
                    self.learned_information += f"{fact}.\n"
            
            self.plan_and_learned_info = []
            self.bmode_change_number += 1

            if i < len(self.behavior_modes):
                self.behavior_file = self.bmode_file_map[self.behavior_modes[self.bmode_change_number-1].lower()]
                self.control = clingo.Control()

        plan = self.extract_plan_from_learned_information()
        plan = self.annotate_plan_with_bmode_changes(plan)
        return plan