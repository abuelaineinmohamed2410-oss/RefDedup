import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox
from rapidfuzz import fuzz

# ---------------- Parsing Functions ---------------- #
def parse_nbib(file_path):
    records = []
    record = {}
    last_tag = None
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n").strip()
            if not line:
                if record:
                    records.append(record)
                    record = {}
                last_tag = None
                continue
            match = re.match(r"^([A-Z0-9]+)\s*-\s*(.*)$", line)
            if match:
                tag, value = match.groups()
                if tag in record:
                    if isinstance(record[tag], list):
                        record[tag].append(value)
                    else:
                        record[tag] = [record[tag], value]
                else:
                    record[tag] = value
                last_tag = tag
            else:
                if last_tag:
                    if last_tag not in record:
                        record[last_tag] = line
                    elif isinstance(record[last_tag], list):
                        record[last_tag][-1] += " " + line
                    else:
                        record[last_tag] += " " + line
    if record:
        records.append(record)
    return records

def parse_ris(file_path):
    records = []
    record = {}
    last_tag = None
    pattern = r"^([A-Z0-9]{2})  - (.*)$"
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n").strip()
            if line == "ER  -":
                if record:
                    records.append(record)
                    record = {}
                last_tag = None
                continue
            match = re.match(pattern, line)
            if match:
                tag, value = match.groups()
                if tag in record:
                    if isinstance(record[tag], list):
                        record[tag].append(value)
                    else:
                        record[tag] = [record[tag], value]
                else:
                    record[tag] = value
                last_tag = tag
            else:
                if last_tag:
                    if last_tag not in record:
                        record[last_tag] = line
                    elif isinstance(record[last_tag], list):
                        record[last_tag][-1] += " " + line
                    else:
                        record[last_tag] += " " + line
    return records

# ---------------- RIS Export ---------------- #
def record_to_ris(record):
    ris_lines = ["TY  - JOUR"]
    for tag in record:
        value = record[tag]
        if isinstance(value, list):
            for v in value:
                ris_lines.append(f"{tag}  - {v}")
        else:
            ris_lines.append(f"{tag}  - {value}")
    ris_lines.append("ER  -")
    return "\n".join(ris_lines)

# ---------------- Duplicate Removal ---------------- #
def remove_duplicates(records, title_threshold=90):
    cleaned = []
    seen_titles = []
    seen_ids = set()  # for PMID or DOI

    for rec in records:
        pmid = rec.get("PMID", "")
        doi = rec.get("LID", "")
        title = rec.get("TI", "")

        if isinstance(title, list):
            title = " ".join(title)
        if isinstance(doi, list):
            doi = doi[0]
        if isinstance(pmid, list):
            pmid = pmid[0]

        duplicate = False
        if pmid in seen_ids or doi in seen_ids:
            duplicate = True
        else:
            for t in seen_titles:
                if fuzz.ratio(title.lower(), t.lower()) >= title_threshold:
                    duplicate = True
                    break

        if not duplicate:
            cleaned.append(rec)
            seen_titles.append(title)
            if pmid:
                seen_ids.add(pmid)
            if doi:
                seen_ids.add(doi)

    return cleaned

# ---------------- Processing Function ---------------- #
def remove_duplicates_from_folder(folder_path, status_label=None):
    all_records = []
    file_counts = {}
    files = [f for f in os.listdir(folder_path) if f.lower().endswith((".nbib", ".ris"))]

    for idx, file_name in enumerate(files, start=1):
        full_path = os.path.join(folder_path, file_name)
        records_from_file = []
        if file_name.lower().endswith(".nbib"):
            records_from_file = parse_nbib(full_path)
        elif file_name.lower().endswith(".ris"):
            records_from_file = parse_ris(full_path)
        file_counts[file_name] = len(records_from_file)
        all_records.extend(records_from_file)

        # Update GUI status
        if status_label:
            status_label.config(text=f"Processing file {idx}/{len(files)}: {file_name}")
            status_label.update()

    total_records_before = len(all_records)
    cleaned_records = remove_duplicates(all_records, title_threshold=90)
    total_records_after = len(cleaned_records)

    output_file = os.path.join(folder_path, "cleaned_references.ris")
    with open(output_file, "w", encoding="utf-8") as f:
        for rec in cleaned_records:
            f.write(record_to_ris(rec) + "\n\n")

    return file_counts, total_records_before, total_records_after, output_file

# ---------------- GUI ---------------- #
def start_gui():
    window = tk.Tk()
    window.title("Duplicate Checker Removal")
    window.geometry("700x400")

    folder_path = tk.StringVar()

    tk.Label(window, text="Select folder with .nbib and .ris files:", font=("Arial", 12)).pack(pady=10)
    tk.Entry(window, textvariable=folder_path, width=60).pack(pady=5)

    status_label = tk.Label(window, text="", font=("Arial", 10), fg="blue")
    status_label.pack(pady=5)

    def browse_folder():
        path = filedialog.askdirectory()
        folder_path.set(path)

    tk.Button(window, text="Browse", command=browse_folder, width=15).pack(pady=5)

    def start_processing():
        path = folder_path.get()
        if not path:
            messagebox.showwarning("No folder selected", "Please select a folder first!")
            return
        status_label.config(text="Starting processing...")
        window.update()
        file_counts, total_before, total_after, output = remove_duplicates_from_folder(path, status_label)
        per_file = "\n".join([f"{k}: {v} records" for k, v in file_counts.items()])
        status_label.config(text="Processing complete!")
        messagebox.showinfo(
            "Processing Complete",
            f"Per-file record counts:\n{per_file}\n\n"
            f"Total records before removing duplicates: {total_before}\n"
            f"Total records after removing duplicates: {total_after}\n\n"
            f"Cleaned RIS saved as:\n{output}"
        )

    tk.Button(window, text="Start", command=start_processing, width=20, height=2, bg="lightgreen").pack(pady=15)

    # About button
    def about_popup():
        messagebox.showinfo(
            "About Duplicate Checker Removal",
            "Duplicate Checker Removal\n"
            "Version 1.0\n"
            "Developed by: Mohamed Abu Elainien\n"
            "Removes duplicate references from NBIB and RIS files"
        )

    tk.Button(window, text="About", command=about_popup, width=15, bg="lightblue").pack(pady=5)

    window.mainloop()

# ---------------- Run GUI ---------------- #
if __name__ == "__main__":
    start_gui()
