# -*- coding: utf-8 -*-
"""
Transcript Calculator - Modern UI Version with Multi-language Support
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import pdfplumber
import re

# Appearance Settings
ctk.set_appearance_mode("Dark")
BURGUNDY = "#9A1220"
BURGUNDY_HOVER = "#7A0E18"

# Grade Point Scaling
GRADE_POINTS = {
    "AA": 4.00, "BA": 3.50, "BB": 3.00, "CB": 2.50, "CC": 2.00,
    "DC": 1.50, "DD": 1.00, "FD": 0.50, "FF": 0.00, "NA": 0.00,
    "I": 0.00, "S": 0.00, "U": 0.00, "W": 0.00, "NI": 0.00, "EX": 0.00,
}

# Grades excluded from GPA calculation
GPA_EXCLUDED_GRADES = {"NA", "I", "S", "U", "W", "NI", "EX", ""}

# Localization Dictionary
LANGUAGES = {
    "English": {
        "title": "Transcript Calculator",
        "logo": "TRANSCRIPT\nCALCULATOR",
        "btn_upload": "Load PDF",
        "btn_add": "Add New Course",
        "btn_delete": "Delete Selected",
        "appearance_mode": "Appearance Mode:",
        "language_mode": "Language:",
        "gpa_title": "Current GPA",
        "credits_title": "Total Credits",
        "hint": "💡 Tip: Double-click any cell to edit course data.",
        "col_semester": "Semester",
        "col_code": "Course Code",
        "col_name": "Course Name",
        "col_credits": "Credits",
        "col_grade": "Grade",
        "col_points": "Points",
        "error_pdf": "PDF read error",
        "error_credits": "Credits must be numeric!",
        "error_value": "Invalid value!",
        "success_load": "courses loaded successfully!",
        "add_title": "Add Course",
        "edit_title": "Edit Value",
        "save": "Save",
        "cancel": "Cancel",
        "enter_info": "Enter Course Info",
        "placeholder_semester": "Semester (e.g., 2023-2024 Fall)",
        "placeholder_code": "Course Code",
        "placeholder_name": "Course Name",
        "placeholder_credits": "Credits",
        "grading_scale": "Grading Scale: AA=4.00 | BA=3.50 | BB=3.00 | CB=2.50 | CC=2.00 | DC=1.50 | DD=1.00 | FD=0.50 | FF=0.00"
    },
    "Türkçe": {
        "title": "Transkript Hesaplayıcı",
        "logo": "TRANSKRİPT\nHESAPLAYICI",
        "btn_upload": "PDF Yükle",
        "btn_add": "Yeni Ders Ekle",
        "btn_delete": "Seçiliyi Sil",
        "appearance_mode": "Görünüm Modu:",
        "language_mode": "Dil:",
        "gpa_title": "Genel Ortalama (GNO)",
        "credits_title": "Toplam Kredi",
        "hint": "💡 İpucu: Hücrelere çift tıklayarak verileri düzenleyebilirsiniz.",
        "col_semester": "Ders Dönemi",
        "col_code": "Ders Kodu",
        "col_name": "Ders Adı",
        "col_credits": "Kredi",
        "col_grade": "Not",
        "col_points": "Puan",
        "error_pdf": "PDF okuma hatası",
        "error_credits": "Kredi sayısal olmalı!",
        "error_value": "Geçersiz değer!",
        "success_load": "ders başarıyla yüklendi!",
        "add_title": "Ders Ekle",
        "edit_title": "Düzenle",
        "save": "Kaydet",
        "cancel": "İptal",
        "enter_info": "Ders Bilgilerini Girin",
        "placeholder_semester": "Dönem (Örn: 2023-2024 Güz)",
        "placeholder_code": "Ders Kodu",
        "placeholder_name": "Ders Adı",
        "placeholder_credits": "Kredi",
        "grading_scale": "Not Baremi: AA=4.00 | BA=3.50 | BB=3.00 | CB=2.50 | CC=2.00 | DC=1.50 | DD=1.00 | FD=0.50 | FF=0.00"
    }
}

class ModernTranscriptApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.current_lang = "English"
        self.courses = []
        
        # Initial UI Setup
        self.setup_ui_base()
        self.update_ui_text()

    def setup_ui_base(self):
        self.title("Transcript Calculator")
        self.geometry("1400x850")

        # Grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=240, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="", font=ctk.CTkFont(family="Segoe UI Variable Display", size=24, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 30))

        btn_font = ctk.CTkFont(family="Segoe UI Variable Small", size=14, weight="bold")

        self.btn_upload = ctk.CTkButton(self.sidebar_frame, text="", command=self.upload_pdf, font=btn_font, fg_color=BURGUNDY, hover_color=BURGUNDY_HOVER, height=45)
        self.btn_upload.grid(row=1, column=0, padx=20, pady=12)

        self.btn_add = ctk.CTkButton(self.sidebar_frame, text="", command=self.add_course, font=btn_font, fg_color=BURGUNDY, hover_color=BURGUNDY_HOVER, height=45)
        self.btn_add.grid(row=2, column=0, padx=20, pady=12)

        self.btn_delete = ctk.CTkButton(self.sidebar_frame, text="", command=self.delete_course, font=btn_font, fg_color="transparent", border_color=BURGUNDY, border_width=2, hover_color=BURGUNDY_HOVER, height=45)
        self.btn_delete.grid(row=3, column=0, padx=20, pady=12)

        # Language Selection
        self.lang_label = ctk.CTkLabel(self.sidebar_frame, text="", anchor="w", font=ctk.CTkFont(size=12))
        self.lang_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.lang_menu = ctk.CTkOptionMenu(self.sidebar_frame, values=["English", "Türkçe"], command=self.change_language, fg_color=BURGUNDY, button_color=BURGUNDY, button_hover_color=BURGUNDY_HOVER)
        self.lang_menu.grid(row=6, column=0, padx=20, pady=(5, 10))
        self.lang_menu.set("English")

        # Appearance Mode
        self.appearance_label = ctk.CTkLabel(self.sidebar_frame, text="", anchor="w", font=ctk.CTkFont(size=12))
        self.appearance_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.appearance_menu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Dark", "Light", "System"], command=self.change_appearance, fg_color=BURGUNDY, button_color=BURGUNDY, button_hover_color=BURGUNDY_HOVER)
        self.appearance_menu.grid(row=8, column=0, padx=20, pady=(5, 20))

        # Main Content
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, padx=30, pady=30, sticky="nsew")
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Stats Cards
        self.stats_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.stats_frame.grid(row=0, column=0, sticky="ew", pady=(0, 25))
        self.stats_frame.grid_columnconfigure((0, 1), weight=1)

        self.gpa_card = ctk.CTkFrame(self.stats_frame, border_width=1, border_color=BURGUNDY)
        self.gpa_card.grid(row=0, column=0, padx=(0, 15), sticky="nsew")
        self.gpa_title_label = ctk.CTkLabel(self.gpa_card, text="", font=ctk.CTkFont(size=13))
        self.gpa_title_label.pack(pady=(15, 0))
        self.gpa_val_label = ctk.CTkLabel(self.gpa_card, text="--", font=ctk.CTkFont(size=42, weight="bold"), text_color=BURGUNDY)
        self.gpa_val_label.pack(pady=(0, 15))

        self.credits_card = ctk.CTkFrame(self.stats_frame)
        self.credits_card.grid(row=0, column=1, padx=(15, 0), sticky="nsew")
        self.credits_title_label = ctk.CTkLabel(self.credits_card, text="", font=ctk.CTkFont(size=13))
        self.credits_title_label.pack(pady=(15, 0))
        self.credits_val_label = ctk.CTkLabel(self.credits_card, text="--", font=ctk.CTkFont(size=42, weight="bold"))
        self.credits_val_label.pack(pady=(0, 15))

        # Table
        self.table_container = ctk.CTkFrame(self.main_frame)
        self.table_container.grid(row=1, column=0, sticky="nsew")
        self.table_container.grid_rowconfigure(0, weight=1)
        self.table_container.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#1e1e1e", foreground="#dce4ee", fieldbackground="#1e1e1e", bordercolor="#1e1e1e", borderwidth=0, font=("Segoe UI", 12), rowheight=38)
        style.configure("Treeview.Heading", background="#2b2b2b", foreground="white", relief="flat", font=("Segoe UI", 12, "bold"))
        style.map("Treeview", background=[("selected", BURGUNDY)])
        style.map("Treeview.Heading", background=[("active", BURGUNDY_HOVER)])

        self.columns = ("semester", "code", "name", "credits", "grade", "points")
        self.tree = ttk.Treeview(self.table_container, columns=self.columns, show="headings", selectmode="browse")
        self.tree.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        
        self.scrollbar = ctk.CTkScrollbar(self.table_container, command=self.tree.yview, button_color=BURGUNDY, button_hover_color=BURGUNDY_HOVER)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        self.tree.bind("<Double-1>", self.on_double_click)

        # Footer
        self.help_label = ctk.CTkLabel(self.main_frame, text="", font=ctk.CTkFont(family="Segoe UI Variable Text", size=13, slant="italic"))
        self.help_label.grid(row=2, column=0, sticky="w", pady=(15, 0))
        
        self.grading_label = ctk.CTkLabel(self.main_frame, text="", font=ctk.CTkFont(size=11), text_color="gray")
        self.grading_label.grid(row=3, column=0, sticky="w")

    def update_ui_text(self):
        lang = LANGUAGES[self.current_lang]
        self.title(lang["title"])
        self.logo_label.configure(text=lang["logo"])
        self.btn_upload.configure(text=lang["btn_upload"])
        self.btn_add.configure(text=lang["btn_add"])
        self.btn_delete.configure(text=lang["btn_delete"])
        self.lang_label.configure(text=lang["language_mode"])
        self.appearance_label.configure(text=lang["appearance_mode"])
        self.gpa_title_label.configure(text=lang["gpa_title"])
        self.credits_title_label.configure(text=lang["credits_title"])
        self.help_label.configure(text=lang["hint"])
        self.grading_label.configure(text=lang["grading_scale"])

        # Table Headings
        for col, key in zip(self.columns, ["col_semester", "col_code", "col_name", "col_credits", "col_grade", "col_points"]):
            self.tree.heading(col, text=lang[key])
        
        # Table Columns Width
        self.tree.column("semester", width=220, anchor="center")
        self.tree.column("code", width=120, anchor="center")
        self.tree.column("name", width=450, anchor="w")
        self.tree.column("credits", width=90, anchor="center")
        self.tree.column("grade", width=90, anchor="center")
        self.tree.column("points", width=90, anchor="center")

    def change_language(self, new_lang):
        self.current_lang = new_lang
        self.update_ui_text()
        self.refresh_table()

    def change_appearance(self, mode):
        ctk.set_appearance_mode(mode)

    def upload_pdf(self):
        lang = LANGUAGES[self.current_lang]
        filepath = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if not filepath: return
        
        try:
            self.courses = self.parse_pdf(filepath)
            self.refresh_table()
            self.calculate_gpa()
        except Exception as e:
            messagebox.showerror(lang["edit_title"], f"{lang['error_pdf']}: {str(e)}")

    def parse_pdf(self, filepath):
        all_found_courses = []
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                mid_x = page.width / 2
                left_text = page.crop((0, 0, mid_x, page.height)).extract_text() or ""
                right_text = page.crop((mid_x, 0, page.width, page.height)).extract_text() or ""
                
                sections = self.process_column(left_text) + self.process_column(right_text)
                for section in sections:
                    for c in section["courses"]:
                        all_found_courses.append({
                            "semester": section["semester"],
                            "code": c["code"],
                            "name": c["name"],
                            "credits": c["credits"],
                            "grade": c["grade"]
                        })
        
        # Dynamic Chronological Sort
        def get_chronological_rank(sem_str):
            # Extract year (e.g. 2022 from 2022-2023)
            year_match = re.search(r'(\d{4})', sem_str)
            year = int(year_match.group(1)) if year_match else 0
            
            # Rank seasons: Güz < Bahar < Yaz
            rank = 0
            if "Güz" in sem_str: rank = 1
            elif "Bahar" in sem_str: rank = 2
            elif "Yaz" in sem_str: rank = 3
            
            return (year * 10) + rank

        all_found_courses.sort(key=lambda x: get_chronological_rank(x["semester"]))
        
        # Populate course_dict (later chronologically overwrites older ones)
        course_dict = {}
        for c in all_found_courses:
            course_dict[c["code"]] = c
            
        # Return sorted list for UI display
        result = list(course_dict.values())
        result.sort(key=lambda x: get_chronological_rank(x["semester"]))
        return result

    def process_column(self, text):
        result = []
        lines = text.split('\n')
        current_semester, current_courses = None, []
        
        for line in lines:
            line = line.strip()
            if not line: continue
            
            # Semester detection
            sem_match = re.search(r'(\d{4}-\d{4}\s+Yılı?\s*(?:Güz|Bahar|Yaz)\s*Dönemi)', line, re.IGNORECASE)
            if sem_match:
                if current_semester and current_courses: result.append({"semester": current_semester, "courses": current_courses})
                current_semester, current_courses = sem_match.group(1), []
                continue
            
            # Ultra-robust Regex: Handles mashed codes, complex grades, and trailing annotations
            # 1: Code, 2: Name, 3: Credits, 4: Grade (with optional parenthetical info)
            pattern = r'^\s*([A-Z]{2,5}\d{3}[A-Z]?|\d{5,12}(?:\s*\([^)]*\))*)\s*(.*?)\s+(\d+)\s*[|/\s]+\d+\s+([A-Z]{1,2})'
            course_match = re.search(pattern, line)
            
            if course_match and current_semester:
                code = course_match.group(1).strip()
                name = course_match.group(2).strip()
                credits = int(course_match.group(3))
                grade_raw = course_match.group(4).strip()
                
                # Extract only the base letter grade (e.g., "AA" from "AA(12)")
                grade_match = re.match(r'^([A-Z]{1,2})', grade_raw)
                grade = grade_match.group(1) if grade_match else grade_raw
                
                # Targeted noise removal from name
                noise = [
                    r'[\s\-:,\.]+(?:\d{4}[\s\-:,\.]*)?(?:Güz|Bahar|Yaz)[\s\-:,\.]*$',
                    r'\s*\(?Erasmus\)?\s*$',
                    r'resmi işlemlerde kullanılamaz.*$',
                    r'Alınan.*$',
                    r'Tamamlanan.*$',
                    r'Hesaplan.*$',
                    r'Açıklama.*$',
                    r'Tarih :.*$'
                ]
                for p in noise:
                    name = re.sub(p, '', name, flags=re.IGNORECASE).strip()
                
                current_courses.append({
                    "semester": current_semester,
                    "code": code,
                    "name": name,
                    "credits": credits,
                    "grade": grade
                })
            elif current_courses and current_semester:
                # Better Continuation Logic
                system_text = ["Bu belge", "Yarıyıl :", "Genel :", "Ders Kodu", "AKTS", "resmi iş", "Alınan", "Tamamlanan", "Hesaplan", "Puan >", "YNO", "Açıklama", "Tarih :"]
                if any(x in line for x in system_text): continue
                
                # If line is NOT a new course start or semester start
                is_new_course = re.match(r'^[A-Z]{2,5}\d{3}', line) or re.match(r'^\d{5,12}', line)
                is_new_semester = re.search(r'\b\d{4}\b.*\b(?:Güz|Bahar|Yaz)\b', line, re.IGNORECASE)
                
                if not is_new_course and not is_new_semester:
                    clean_line = line.strip()
                    if clean_line and len(clean_line) > 1:
                        # Avoid appending single grades or credits that might be floating
                        if clean_line in GPA_EXCLUDED_GRADES or clean_line in GRADE_POINTS: continue
                        
                        current_courses[-1]["name"] = (current_courses[-1]["name"] + " " + clean_line).strip()
                        # Final cleanup
                        for p in [r'[\s\-:,\.]+(?:\d{4}[\s\-:,\.]*)?(?:Güz|Bahar|Yaz)[\s\-:,\.]*$', r'\s*\(?Erasmus\)?\s*$', r'\s*[:,\-]\s*$']:
                            current_courses[-1]["name"] = re.sub(p, '', current_courses[-1]["name"]).strip()

        if current_semester and current_courses: result.append({"semester": current_semester, "courses": current_courses})
        
        # Final formatting Pass
        for sec in result:
            for c in sec["courses"]:
                # Polish name items
                for p in [r'\bresmi işlemlerde\b.*$', r'\bAlınan\b.*$', r'\bTamamlanan\b.*$', r'\s+Erasmus\s*$']:
                    c["name"] = re.sub(p, '', c["name"], flags=re.IGNORECASE).strip()
                # Unified code format
                c["code"] = re.sub(r'\s*\(Erasmus\)', '(Erasmus)', c["code"], flags=re.IGNORECASE).strip()
                # Remove common duplicate artifacts in code
                c["code"] = re.sub(r'\s*\(\s*([A-Z0-9]+)\s*\)', r' (\1)', c["code"]) 
        return result

    def refresh_table(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        for i, c in enumerate(self.courses):
            val = GRADE_POINTS.get(c["grade"], 0)
            pts = c["credits"] * val if c["grade"] not in GPA_EXCLUDED_GRADES else 0
            self.tree.insert("", tk.END, iid=i, values=(c["semester"], c["code"], c["name"], c["credits"], c["grade"], f"{pts:.2f}" if c["grade"] not in GPA_EXCLUDED_GRADES else "-"))

    def calculate_gpa(self):
        p, k = 0, 0
        for c in self.courses:
            if c["grade"] not in GPA_EXCLUDED_GRADES:
                p += (c["credits"] * GRADE_POINTS.get(c["grade"], 0))
                k += c["credits"]
        self.gpa_val_label.configure(text=f"{p/k:.2f}" if k > 0 else "--")
        self.credits_val_label.configure(text=f"{k}" if k > 0 else "--")

    def delete_course(self):
        selected = self.tree.selection()
        if not selected: return
        # Sort indices in reverse to avoid index shifting problems
        indices = sorted([int(item) for item in selected], reverse=True)
        for idx in indices:
            del self.courses[idx]
        self.refresh_table()
        self.calculate_gpa()

    def add_course(self):
        lang = LANGUAGES[self.current_lang]
        dialog = ctk.CTkToplevel(self)
        dialog.title(lang["add_title"])
        dialog.geometry("400x480")
        dialog.after(100, dialog.lift)
        dialog.grab_set()
        
        ctk.CTkLabel(dialog, text=lang["enter_info"], font=ctk.CTkFont(size=16, weight="bold")).pack(pady=20)
        sem = ctk.CTkEntry(dialog, placeholder_text=lang["placeholder_semester"], width=300); sem.pack(pady=5)
        code = ctk.CTkEntry(dialog, placeholder_text=lang["placeholder_code"], width=300); code.pack(pady=5)
        name = ctk.CTkEntry(dialog, placeholder_text=lang["placeholder_name"], width=300); name.pack(pady=5)
        credits = ctk.CTkEntry(dialog, placeholder_text=lang["placeholder_credits"], width=300); credits.pack(pady=5)
        grade = ctk.CTkOptionMenu(dialog, values=list(GRADE_POINTS.keys()), width=300, fg_color=BURGUNDY, button_color=BURGUNDY, button_hover_color=BURGUNDY_HOVER); grade.pack(pady=5)

        def save():
            try:
                self.courses.append({"semester": sem.get(), "code": code.get(), "name": name.get(), "credits": int(credits.get()), "grade": grade.get()})
                self.refresh_table(); self.calculate_gpa(); dialog.destroy()
            except: messagebox.showerror(lang["edit_title"], lang["error_credits"])
        
        ctk.CTkButton(dialog, text=lang["save"], command=save, fg_color=BURGUNDY, hover_color=BURGUNDY_HOVER).pack(pady=20)

    def on_double_click(self, event):
        lang = LANGUAGES[self.current_lang]
        item = self.tree.identify_row(event.y)
        col_idx = int(self.tree.identify_column(event.x)[1:]) - 1
        if not item or col_idx > 4: return
        
        idx = int(item)
        col_keys = ["semester", "code", "name", "credits", "grade"]
        current_val = self.courses[idx][col_keys[col_idx]]

        dialog = ctk.CTkToplevel(self)
        dialog.title(lang["edit_title"])
        dialog.geometry("350x220")
        dialog.after(100, dialog.lift)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text=f"{lang['edit_title']}", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=15)
        
        if col_idx == 4:
            entry = ctk.CTkOptionMenu(dialog, values=list(GRADE_POINTS.keys()), width=250, fg_color=BURGUNDY, button_color=BURGUNDY, button_hover_color=BURGUNDY_HOVER)
            entry.set(current_val)
        else:
            entry = ctk.CTkEntry(dialog, width=250)
            entry.insert(0, str(current_val))
        entry.pack(pady=10)

        def save_edit():
            try:
                val = entry.get()
                if col_idx == 3: val = int(val)
                self.courses[idx][col_keys[col_idx]] = val
                self.refresh_table(); self.calculate_gpa(); dialog.destroy()
            except: messagebox.showerror(lang["edit_title"], lang["error_value"])
        
        ctk.CTkButton(dialog, text=lang["save"], command=save_edit, fg_color=BURGUNDY, hover_color=BURGUNDY_HOVER).pack(pady=10)

if __name__ == "__main__":
    app = ModernTranscriptApp()
    app.mainloop()
