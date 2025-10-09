# RefDedup
A Python-powered desktop tool for detecting and removing duplicate references in RIS/NBIB files. Designed for systematic reviews and meta-analysis workflows.
# RefDedup: Duplicate Checker Removal

## Features

* Supports **RIS** and **NBIB** formats (compatible with PubMed, EndNote, Zotero, Rayyan, and others).
* Detects duplicates based on **title, authors, year, and DOI/PMID**.
* Smart text normalization (case-insensitive, punctuation removal, spacing normalization).
* Adjustable **similarity threshold** (default: 90%) for fuzzy matching.
* Exports a clean `.ris` file with duplicates removed.
* Simple **graphical user interface (GUI)** – no coding required.
* Runs as a standalone `.exe` file (no need to install Python).

---

##  Installation

### Option 1: Run Executable

1. Download the latest release from the [Releases](../../releases) page.
2. Extract the `.zip` file.
3. Run `app.exe`.

### Option 2: Run from Source

1. Clone this repository:

   ```bash
   git clone git clone https://github.com/abuelaineinmohamed2410-oss/RefDedup.git
   cd RefDedup
   ```
2. Install requirements:

   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:

   ```bash
   python app.py
   ```

---

##  Usage

1. Open the app.
2. Paste the folder path containing your `.ris` / `.nbib` files.
3. Press **Enter** to process.
4. The app will show:

   * Total number of records
   * Number of duplicates detected
   * Final count after deduplication
5. The cleaned file will be saved as `deduplicated_output.ris` in the same folder.

---

## Example

Input: 3083 records
Output: 2025 unique references (1058 duplicates removed).

---

## License

This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.

---

##  Credits

Developed by **Mohamed Abu Elainien**.

---
