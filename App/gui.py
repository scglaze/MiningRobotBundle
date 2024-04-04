import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import tkinter.messagebox
import clingo_solver
import os
import sys


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Scenario Explorer")
        self.root.resizable(False, False)
        
        # Dropdown selector for scenarios
        self.scenario_label = ttk.Label(root, text="Select Scenario:")
        self.scenario_label.grid(row=0, column=0, padx=10, pady=10)
        self.scenario_var = tk.StringVar()
        self.scenario_var.set("Scenario 1")
        self.scenario_dropdown = ttk.Combobox(root, textvariable=self.scenario_var, values=["Scenario 1", "Scenario 2", "Scenario 3", "Scenario 4", "Scenario 5", "Scenario 6", "Scenario 7", "Scenario 8", "Scenario 9", "Scenario 10"])
        self.scenario_dropdown.grid(row=0, column=1, padx=10, pady=10)
        self.scenario_dropdown.bind("<<ComboboxSelected>>", self.on_scenario_change)
        self.scenario_dropdown.state(["readonly"])
        
        # Image display
        self.scenario_image_label = ttk.Label(root)
        self.scenario_image_label.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
        
        # Initial behavior mode dropdown
        self.initial_behavior_label = ttk.Label(root, text="Initial behavior mode:")
        self.initial_behavior_label.grid(row=2, column=0, padx=10, pady=10)
        self.initial_behavior_var = tk.StringVar()
        self.initial_behavior_dropdown = ttk.Combobox(root, textvariable=self.initial_behavior_var, values=["Safe", "Normal", "Risky"])
        self.initial_behavior_dropdown.grid(row=2, column=1, padx=10, pady=10)
        self.initial_behavior_dropdown.state(["readonly"])

        ttk.Separator(root, orient=tk.HORIZONTAL).grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        # Behavior mode changes
        self.behavior_changes_label = ttk.Label(root, text="Behavior mode change(s):")
        self.behavior_changes_label.grid(row=4, column=0, columnspan=2, padx=10)

        ttk.Separator(root, orient=tk.HORIZONTAL).grid(row=5, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

        self.behavior_mode_changes = []
        self.time_step_dropdowns = []
        
        # First behavior mode change
        self.create_behavior_change_widgets(6, self.behavior_mode_changes)
        
        # Horizontal line
        ttk.Separator(root, orient=tk.HORIZONTAL).grid(row=8, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        # Second behavior mode change
        self.create_behavior_change_widgets(9, self.behavior_mode_changes)

        # Horizontal line
        ttk.Separator(root, orient=tk.HORIZONTAL).grid(row=11, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

        # Solve button that calls a function that uses clingo
        self.solve_button = ttk.Button(root, text="Solve", command=self.on_solve)
        self.solve_button.grid(row=12, column=0, columnspan=2, padx=50, pady=5, sticky="ew")
        
        # Text box to display plan
        self.text_box = tk.Text(root, height=10, width=50, wrap=tk.WORD)
        self.text_box.grid(row=13, column=0, columnspan=2, padx=10, pady=(5, 15))
        self.text_box.config(state=tk.DISABLED)
        
        self.show_scenario_image()
        
    def create_behavior_change_widgets(self, row, behavior_mode_changes):
        time_step_label = ttk.Label(self.root, text="Time Step:")
        time_step_label.grid(row=row, column=0, padx=10, pady=5)
        
        time_step_var = tk.StringVar()
        time_step_dropdown = ttk.Combobox(self.root, textvariable=time_step_var, values=[""] + [str(x) for x in range(1, 11)])
        time_step_dropdown.grid(row=row, column=1, padx=10, pady=5)
        time_step_dropdown.state(["readonly"])
        self.time_step_dropdowns.append(time_step_dropdown)
        
        behavior_change_label = ttk.Label(self.root, text="Behavior mode:")
        behavior_change_label.grid(row=row+1, column=0, padx=10, pady=5)
        
        behavior_change_var = tk.StringVar()
        behavior_change_dropdown = ttk.Combobox(self.root, textvariable=behavior_change_var, values=["", "Safe", "Normal", "Risky"])
        behavior_change_dropdown.grid(row=row+1, column=1, padx=10, pady=5)
        behavior_change_dropdown.state(["readonly"])

        behavior_mode_changes.append((time_step_var, behavior_change_var))
          
    def on_scenario_change(self, event):
        self.show_scenario_image()
        self.change_timestep_upperbounds()

    def change_timestep_upperbounds(self):
        # Mapping the scenario number to the correspond n value in each scenario file.
        scenario_to_upperbound_map = {
            1: 10, 2: 10, 3: 10, 4: 15, 5: 10, 6: 10, 7: 10, 8: 10, 9: 10, 10: 12
        }
        new_upperbound = scenario_to_upperbound_map[int(self.scenario_var.get().split()[1])]
        for dropdown in self.time_step_dropdowns:
            dropdown["values"] = [""] + [str(x) for x in range(1, new_upperbound + 1)]

    def show_scenario_image(self):
        image_name = f"Mining_Domain_Scenario{self.scenario_var.get().split()[1]}_Graphic.png"
        image_path = os.path.join(getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__))), image_name)
        original_image = Image.open(image_path)
        original_image.thumbnail(size=(400, 400))
        resized_tk_image = ImageTk.PhotoImage(original_image)
        self.scenario_image_label.configure(image=resized_tk_image)
        self.scenario_image_label.image = resized_tk_image

    def change_displayed_text(self, text):
        self.text_box.config(state=tk.NORMAL)
        self.text_box.delete(1.0, tk.END)
        count_newlines = lambda text: sum(1 for char in text if char == '\n')
        plan_length = count_newlines(text)
        if plan_length > 0:
            self.text_box.insert(tk.END, text)
        else:
            self.text_box.insert(tk.END, "No plan generated. Impossible scenario combined with the given parameters.")
        self.text_box.config(state=tk.DISABLED)

    def clear_displayed_text(self):
        self.change_displayed_text("")

    def show_error_message(self, message):
        tkinter.messagebox.showerror("Error", message)   

    def on_close(self, clingo_solver_obj):
        clingo_solver_obj.delete_temp_file()
        root.destroy()

    def on_solve(self):
        # Validation checking
        if self.behavior_mode_changes:
            initial_behavior_mode = self.initial_behavior_var.get()
            time_step_1 = int(self.behavior_mode_changes[0][0].get()) if self.behavior_mode_changes[0][0].get() else None
            time_step_2 = int(self.behavior_mode_changes[1][0].get()) if self.behavior_mode_changes[1][0].get() else None
            behavior_mode_1 = self.behavior_mode_changes[0][1].get()
            behavior_mode_2 = self.behavior_mode_changes[1][1].get()

            if not initial_behavior_mode:
                self.clear_displayed_text()
                self.show_error_message("Please select an initial behavior mode.")
                return
            if behavior_mode_1 == initial_behavior_mode:
                self.clear_displayed_text()
                self.show_error_message("Invalid behavior mode entered:\n\nFirst behavior mode must be different from the initial behavior mode.")
                return
            if behavior_mode_1 and behavior_mode_2 and behavior_mode_1 == behavior_mode_2:
                self.clear_displayed_text()
                self.show_error_message("Invalid behavior mode entered:\n\nSecond behavior mode must be different from the first behavior mode.")
                return
            if (behavior_mode_2 and not behavior_mode_1) or (time_step_2 and not time_step_1):
                self.clear_displayed_text()
                self.show_error_message("Cannot enter a second behavior mode change if a first is not selected.")
                return
            if (time_step_1 and not behavior_mode_1) or (not time_step_1 and behavior_mode_1):
                self.clear_displayed_text()
                self.show_error_message("Behavior mode changes require both a time step and behavior mode.\n\nMake sure both are entered for the first change.")
                return
            if (time_step_2 and not behavior_mode_2) or (not time_step_2 and behavior_mode_2):
                self.clear_displayed_text()
                self.show_error_message("Behavior mode changes require both a time step and behavior mode.\n\nMake sure both are entered for the second change.")
                return
            if time_step_1 and time_step_2 and time_step_1 >= time_step_2:
                self.clear_displayed_text()
                self.show_error_message("Invalid time step entered:\n\nSecond time step must be greater than the first.")      
                return   
            
            # Solve scenario with given parameters
            text = "Solving with the following parameters:\n"
            text += f"Initial behavior mode: {initial_behavior_mode}\n"
            if time_step_1:
                text += f"Change to {behavior_mode_1} mode at time step {time_step_1}\n"
            if time_step_2:
                text += f"Change to {behavior_mode_2} mode at time step {time_step_2}"
            print(text)

            mining_domain_solver = clingo_solver.MiningDomainSolver(scenario_number=int(self.scenario_var.get().split()[1]), initial_bmode=initial_behavior_mode, bmode_changes=self.behavior_mode_changes)
            plan = mining_domain_solver.generate_plan_with_bmode_changes()
            root.protocol("WM_DELETE_WINDOW", lambda: self.on_close(mining_domain_solver))
            
            # Display generated plan
            self.change_displayed_text(plan)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()