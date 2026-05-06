import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json

GRADE_REMARKS = {
    1.00: "Excellent",
    1.25: "Very Good",
    1.50: "Very Good",
    1.75: "Above Average",
    2.00: "Above Average",
    2.25: "Average",
    2.50: "Average",
    2.75: "Passing",
    3.00: "Passing",
    3.25: "Conditional",
    3.50: "Conditional",
    3.75: "Failed",
    4.00: "Failed",
    4.25: "Failed",
    4.50: "Failed",
    4.75: "Failed",
    5.00: "Failed",
}

SPECIAL_GRADES = {
    "INC": "Incomplete",
    "W": "Withdrawn",
    "D/F": "Dropped with Failure",
}

HONORS_GRADUATING = [
    (1.00, 1.25, "Summa Cum Laude"),
    (1.26, 1.50, "Magna Cum Laude"),
    (1.51, 1.75, "Cum Laude"),
]

HONORS_NONGRAD = [
    (1.00, 1.25, "First Honor"),
    (1.26, 1.50, "Second Honor"),
    (1.51, 1.75, "Third Honor"),
]

RETENTION_STATUS = [
    (0, 5, "Good standing"),
    (6, 6, "Warning"),
    (9, 999, "Probation / Mandatory review"),
]


class GradeSystemApp:
    def __init__(self, root):
        self.root = root
        self.root.title("USTP Grading System")
        self.root.geometry("980x620")
        self.root.minsize(980, 620)
        self.root.resizable(True, True)
        self.root.configure(bg='#eef3f8')

        self.create_menu()

        self.style = ttk.Style(self.root)
        try:
            self.style.theme_use('clam')
        except tk.TclError:
            pass

        accent = '#2f6fbf'
        panel_bg = '#ffffff'
        base_text = '#2f3f5c'
        muted_text = '#5a6b8c'
        tree_alt = '#f3f6fc'

        self.style.configure('Section.TLabelframe', background=panel_bg, bordercolor='#d8dee7', relief='groove', borderwidth=1)
        self.style.configure('Section.TLabelframe.Label', font=('Segoe UI', 11, 'bold'), foreground=accent, background=panel_bg)
        self.style.configure('Custom.TLabel', font=('Segoe UI', 11), foreground=base_text, background=panel_bg)
        self.style.configure('Custom.TEntry', font=('Segoe UI', 11), foreground=base_text, fieldbackground='#f7f9fd', background='#f7f9fd', bordercolor='#c8d1e3', lightcolor=accent, padding=6)
        self.style.configure('Custom.TCheckbutton', font=('Segoe UI', 11), foreground=base_text, background=panel_bg, padding=4)
        self.style.configure('Accent.TButton', font=('Segoe UI', 11, 'bold'), foreground='#ffffff', background=accent, borderwidth=0, focusthickness=3, focuscolor=accent, padding=10)
        self.style.map('Accent.TButton', background=[('active', '#2456a0'), ('pressed', '#1f4f85')], relief=[('pressed', 'sunken'), ('!pressed', 'raised')])
        self.style.configure('Custom.Treeview', font=('Segoe UI', 11), background='#ffffff', fieldbackground='#ffffff', foreground=base_text, rowheight=28, bordercolor='#d8dee7', borderwidth=1)
        self.style.configure('Custom.Treeview.Heading', background=accent, foreground='#ffffff', font=('Segoe UI', 11, 'bold'), relief='flat')
        self.style.map('Custom.Treeview.Heading', background=[('active', '#244e91')])
        self.style.configure('TCombobox', fieldbackground='#f7f9fd', background='#f7f9fd', foreground=base_text, font=('Segoe UI', 11), bordercolor='#c8d1e3', padding=4)

        self.build_student_frame()
        self.build_course_frame()
        self.build_summary_frame()
        self.create_course_list()

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save Data", command=self.save_data)
        file_menu.add_command(label="Load Data", command=self.load_data)
        file_menu.add_separator()
        file_menu.add_command(label="Export Summary", command=self.export_summary)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

    def save_data(self):
        if not self.courses:
            messagebox.showwarning("Save", "No data to save.")
            return
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", ".json"), ("All files", ".*")]
        )
        if not filepath:
            return
        data = {
            "student": {
                "name": self.name_var.get(),
                "id": self.id_var.get(),
                "program": self.program_var.get(),
                "term": self.term_var.get(),
                "graduating": self.grad_var.get(),
                "standing": self.standing_var.get(),
            },
            "courses": self.courses,
        }
        try:
            with open(filepath, "w") as f:
                json.dump(data, f, indent=2)
            messagebox.showinfo("Save", "Data saved successfully.")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    def load_data(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("JSON files", ".json"), ("All files", ".*")]
        )
        if not filepath:
            return
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
            student = data.get("student", {})
            self.name_var.set(student.get("name", ""))
            self.id_var.set(student.get("id", ""))
            self.program_var.set(student.get("program", ""))
            self.term_var.set(student.get("term", ""))
            self.grad_var.set(student.get("graduating", False))
            self.standing_var.set(student.get("standing", "1st Year"))

            self.tree.delete(*self.tree.get_children())
            self.courses.clear()
            for course in data.get("courses", []):
                self.courses.append(course)
                self.tree.insert("", tk.END, values=(
                    course["course"],
                    course["units"],
                    course["grade_input"],
                    course["grade"],
                    course["remark"],
                ))
            self.summary_text.config(state=tk.NORMAL)
            self.summary_text.delete("1.0", tk.END)
            self.summary_text.config(state=tk.DISABLED)
            messagebox.showinfo("Load", "Data loaded successfully.")
        except Exception as e:
            messagebox.showerror("Load Error", str(e))

    def export_summary(self):
        if not self.courses:
            messagebox.showwarning("Export", "No data to export.")
            return
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", ".txt"), ("All files", ".*")]
        )
        if not filepath:
            return
        summary_content = self.summary_text.get("1.0", tk.END).strip()
        if not summary_content:
            messagebox.showwarning("Export", "No summary to export.")
            return
        try:
            with open(filepath, "w") as f:
                f.write(summary_content)
            messagebox.showinfo("Export", "Summary exported successfully.")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    def build_student_frame(self):
        frame = ttk.LabelFrame(self.root, text="Student and Term Information", style="Section.TLabelframe")
        frame.pack(fill=tk.X, padx=12, pady=(12, 6))
        frame.pack_propagate(False)

        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(3, weight=1)
        frame.columnconfigure(5, weight=1)

        ttk.Label(frame, text="Student Name:", style="Custom.TLabel").grid(row=0, column=0, padx=8, pady=8, sticky="w")
        self.name_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.name_var, width=28, style="Custom.TEntry").grid(row=0, column=1, padx=4, pady=8, sticky="ew")

        ttk.Label(frame, text="Student ID:", style="Custom.TLabel").grid(row=0, column=2, padx=8, pady=8, sticky="w")
        self.id_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.id_var, width=18, style="Custom.TEntry").grid(row=0, column=3, padx=4, pady=8, sticky="ew")

        ttk.Label(frame, text="Program:", style="Custom.TLabel").grid(row=0, column=4, padx=8, pady=8, sticky="w")
        self.program_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.program_var, width=22, style="Custom.TEntry").grid(row=0, column=5, padx=4, pady=8, sticky="ew")

        ttk.Label(frame, text="Academic Term:", style="Custom.TLabel").grid(row=1, column=0, padx=8, pady=6, sticky="w")
        self.term_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.term_var, width=22, style="Custom.TEntry").grid(row=1, column=1, padx=4, pady=6, sticky="ew")

        ttk.Label(frame, text="Graduating Student:", style="Custom.TLabel").grid(row=1, column=2, padx=8, pady=6, sticky="w")
        self.grad_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frame, variable=self.grad_var, style="Custom.TCheckbutton").grid(row=1, column=3, padx=4, pady=6, sticky="w")

        ttk.Label(frame, text="Class Standing:", style="Custom.TLabel").grid(row=1, column=4, padx=8, pady=6, sticky="w")
        self.standing_var = tk.StringVar()
        standing_combo = ttk.Combobox(frame, textvariable=self.standing_var, width=18, state="readonly", style="Custom.TEntry")
        standing_combo["values"] = ["1st Year", "2nd Year", "3rd Year", "4th Year", "5th Year", "Graduate"]
        standing_combo.current(0)
        standing_combo.grid(row=1, column=5, padx=4, pady=6, sticky="ew")

    def build_course_frame(self):
        frame = ttk.LabelFrame(self.root, text="Course Entry", style="Section.TLabelframe")
        frame.pack(fill=tk.X, padx=12, pady=(0, 6))
        frame.pack_propagate(False)

        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(3, weight=0)
        frame.columnconfigure(5, weight=0)
        frame.columnconfigure(7, weight=1)

        ttk.Label(frame, text="Course Code:", style="Custom.TLabel").grid(row=0, column=0, padx=8, pady=6, sticky="w")
        self.course_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.course_var, width=26, style="Custom.TEntry").grid(row=0, column=1, padx=4, pady=6, sticky="ew")

        ttk.Label(frame, text="Units:", style="Custom.TLabel").grid(row=0, column=2, padx=8, pady=6, sticky="w")
        self.units_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.units_var, width=8, style="Custom.TEntry").grid(row=0, column=3, padx=4, pady=6, sticky="w")

        ttk.Label(frame, text="Grade (1.00–5.00):", style="Custom.TLabel").grid(row=0, column=4, padx=8, pady=6, sticky="w")
        self.grade_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.grade_var, width=10, style="Custom.TEntry").grid(row=0, column=5, padx=4, pady=6, sticky="w")

        ttk.Label(frame, text="Or Grade Code:", style="Custom.TLabel").grid(row=0, column=6, padx=8, pady=6, sticky="w")
        self.grade_code_var = tk.StringVar()
        grade_codes = ["", "INC", "W", "D/F"]
        ttk.Combobox(frame, textvariable=self.grade_code_var, values=grade_codes, width=8, state="readonly", style="Custom.TEntry").grid(row=0, column=7, padx=4, pady=6, sticky="w")

        ttk.Button(frame, text="Add Course", command=self.add_course, style="Accent.TButton").grid(row=0, column=8, padx=8, pady=6)
        ttk.Button(frame, text="Remove Selected", command=self.remove_selected, style="Accent.TButton").grid(row=0, column=9, padx=8, pady=6)

        ttk.Label(frame, text="Note: Enter a direct grade value or select a special grade code.", style="Custom.TLabel").grid(row=1, column=0, columnspan=10, padx=8, pady=6, sticky="w")
        ttk.Separator(frame, orient=tk.HORIZONTAL).grid(row=2, column=0, columnspan=10, sticky="ew", padx=8, pady=(0, 6))

        table_frame = ttk.Frame(frame)
        table_frame.grid(row=3, column=0, columnspan=10, sticky="nsew", padx=8, pady=6)
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(table_frame, columns=("course", "units", "grade_input", "grade", "remark"), show="headings", height=5, style="Custom.Treeview")
        self.tree.heading("course", text="Course Code")
        self.tree.heading("units", text="Units")
        self.tree.heading("grade_input", text="Entered Grade")
        self.tree.heading("grade", text="Grade")
        self.tree.heading("remark", text="Remark")
        self.tree.column("course", width=220, anchor="center")
        self.tree.column("units", width=70, anchor="center")
        self.tree.column("grade_input", width=110, anchor="center")
        self.tree.column("grade", width=90, anchor="center")
        self.tree.column("remark", width=430, anchor="center")
        self.tree.grid(row=0, column=0, sticky="nsew")

        tree_scroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        tree_scroll.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=tree_scroll.set)

        self.summary_button = ttk.Button(frame, text="Compute Summary", command=self.compute_summary, style="Accent.TButton")
        self.summary_button.grid(row=4, column=0, padx=8, pady=8, sticky="w")

        self.clear_button = ttk.Button(frame, text="Clear All Courses", command=self.clear_courses, style="Accent.TButton")
        self.clear_button.grid(row=4, column=1, padx=8, pady=8, sticky="w")

    def build_summary_frame(self):
        frame = ttk.LabelFrame(self.root, text="Summary", style="Section.TLabelframe")
        frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        self.summary_text = tk.Text(
            frame,
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=("Segoe UI", 12),
            bg="#f8fbff",
            fg="#223247",
            relief="flat",
            padx=10,
            pady=10,
            insertbackground="#2f6fbf",
            spacing3=4,
            bd=0,
        )
        self.summary_text.grid(row=0, column=0, sticky="nsew")

        summary_scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.summary_text.yview)
        summary_scrollbar.grid(row=0, column=1, sticky="ns")
        self.summary_text.config(yscrollcommand=summary_scrollbar.set)

        summary_hscroll = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=self.summary_text.xview)
        summary_hscroll.grid(row=1, column=0, sticky="ew")
        self.summary_text.config(xscrollcommand=summary_hscroll.set)

    def create_course_list(self):
        self.courses = []

    def add_course(self):
        course_code = self.course_var.get().strip()
        units_text = self.units_var.get().strip()
        grade_text = self.grade_var.get().strip()
        grade_code = self.grade_code_var.get().strip()

        if not course_code:
            messagebox.showwarning("Validation", "Please enter a course code.")
            return
        if not units_text:
            messagebox.showwarning("Validation", "Please enter unit value.")
            return
        try:
            units = float(units_text)
            if units <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Validation", "Units must be a positive number.")
            return

        if grade_code and grade_text:
            messagebox.showwarning("Validation", "Enter only one of direct grade or special grade code.")
            return
        if not grade_code and not grade_text:
            messagebox.showwarning("Validation", "Enter a direct grade or select a special grade code.")
            return

        if grade_code:
            grade, remark = self.get_special_grade(grade_code)
            grade_display = grade_code
            special = grade_code
        else:
            try:
                grade_value = float(grade_text)
                if grade_value < 1.0 or grade_value > 5.0 or (grade_value * 100) % 25 != 0:
                    raise ValueError
            except ValueError:
                messagebox.showwarning("Validation", "Grade must be a number from 1.00 to 5.00 in 0.25 increments.")
                return
            grade = f"{grade_value:.2f}"
            remark = self.get_remark_from_grade(grade_value)
            grade_display = grade
            special = None

        self.courses.append({
            "course": course_code,
            "units": units,
            "grade_input": grade_display,
            "grade": grade,
            "remark": remark,
            "special": special,
        })

        self.tree.insert("", tk.END, values=(course_code, units, grade_display, grade, remark))
        self.course_var.set("")
        self.units_var.set("")
        self.grade_var.set("")
        self.grade_code_var.set("")

    def remove_selected(self):
        selected = self.tree.selection()
        if not selected:
            return
        index = self.tree.index(selected[0])
        self.tree.delete(selected[0])
        self.courses.pop(index)

    def clear_courses(self):
        self.tree.delete(*self.tree.get_children())
        self.courses.clear()
        self.summary_text.config(state=tk.NORMAL)
        self.summary_text.delete("1.0", tk.END)
        self.summary_text.config(state=tk.DISABLED)

    def get_remark_from_grade(self, grade_value):
        return GRADE_REMARKS.get(grade_value, "Unknown")

    def get_special_grade(self, grade_code):
        if grade_code == "INC":
            return "INC", "Incomplete"
        if grade_code == "W":
            return "W", "Withdrawn"
        if grade_code == "D/F":
            return "D/F", "Dropped with Failure"
        return "", ""

    def compute_summary(self):
        if not self.courses:
            messagebox.showinfo("Summary", "Add at least one course first.")
            return

        total_units = 0.0
        weighted_sum = 0.0
        failed_units = 0.0
        incomplete_count = 0
        dropped_fail_count = 0
        withdrawn_count = 0

        for course in self.courses:
            units = course["units"]
            total_units += units
            grade = course["grade"]
            special = course.get("special")

            if special == "INC":
                incomplete_count += 1
                continue
            if special == "W":
                withdrawn_count += 1
                continue
            if special == "D/F":
                dropped_fail_count += units
                failed_units += units
                continue

            try:
                grade_value = float(grade)
            except ValueError:
                grade_value = None

            if grade_value is not None:
                if grade_value >= 3.75 or grade_value == 5.0:
                    failed_units += units
                weighted_sum += grade_value * units
            else:
                failed_units += units

        gpa = weighted_sum / total_units if total_units > 0 else 0.0
        gpa_display = f"{gpa:.2f}" if total_units > 0 else "N/A"

        honors = self.determine_honors(gpa, total_units)
        retention = self.determine_retention(failed_units)
        inc_message = self.incomplete_message(incomplete_count)

        summary_lines = [
            f"Student: {self.name_var.get().strip() or 'N/A'}",
            f"Student ID: {self.id_var.get().strip() or 'N/A'}",
            f"Program: {self.program_var.get().strip() or 'N/A'}",
            f"Term: {self.term_var.get().strip() or 'N/A'}",
            "",
            f"Total Units Entered: {total_units:.2f}",
            f"Computed GPA: {gpa_display}",
            f"Honors / Academic Recognition: {honors}",
            f"Retention Status: {retention}",
            f"Failed or D/F Units: {failed_units:.2f}",
            f"Incomplete Courses: {incomplete_count}",
            f"Withdrawn Courses: {withdrawn_count}",
            f"Dropped with Failure Courses: {dropped_fail_count}",
            "",
            "Grade rules used:",
            "  1.00 -> Excellent",
            "  1.25 -> Very Good",
            "  1.50 -> Very Good",
            "  1.75 -> Above Average",
            "  2.00 -> Above Average",
            "  2.25 -> Average",
            "  2.50 -> Average",
            "  2.75 -> Passing",
            "  3.00 -> Passing",
            "  3.25 -> Conditional",
            "  3.50 -> Conditional",
            "  3.75 - 5.00 -> Failed",
            "  INC    -> Incomplete",
            "  W      -> Withdrawn",
            "  D/F    -> Dropped with Failure",
        ]

        if inc_message:
            summary_lines.append("")
            summary_lines.append(f"Note: {inc_message}")

        self.summary_text.config(state=tk.NORMAL)
        self.summary_text.delete("1.0", tk.END)
        self.summary_text.insert(tk.END, "\n".join(summary_lines))
        self.summary_text.config(state=tk.DISABLED)

    def determine_honors(self, gpa, total_units):
        if total_units <= 0:
            return "No courses entered"
        if self.grad_var.get():
            for low, high, title in HONORS_GRADUATING:
                if low <= gpa <= high:
                    return title
            return "No honors"
        else:
            for low, high, title in HONORS_NONGRAD:
                if low <= gpa <= high:
                    return title
            return "No honors or not eligible"

    def determine_retention(self, failed_units):
        if failed_units >= 12:
            return "Permanent separation or mandatory exit review"
        if failed_units >= 9:
            return "Mandatory exit from program or probation"
        if failed_units >= 6:
            return "Probation / Warning"
        return "Good standing"

    def incomplete_message(self, incomplete_count):
        if incomplete_count == 0:
            return ""
        return "INC must be completed within one academic year or converts to 5.0."


if __name__ == "__main__":
    root = tk.Tk()
    app = GradeSystemApp(root)
    root.mainloop()