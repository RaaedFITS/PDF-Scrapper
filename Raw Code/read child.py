import pdfplumber
import pandas as pd

def extract_all_tables(pdf_path):
    """
    Reads ALL pages from the PDF and extracts the FIRST table found on each page.
    Concatenates them into one DataFrame.
    Returns an empty DataFrame if no tables are found.
    """
    all_dfs = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                # table[0] is the header row, table[1:] is the data
                df = pd.DataFrame(table[1:], columns=table[0])
                all_dfs.append(df)
    if not all_dfs:
        print(f"No tables found in {pdf_path}. Returning empty DataFrame.")
        return pd.DataFrame()
    return pd.concat(all_dfs, ignore_index=True)

def clean_cell(value):
    """
    Replaces literal '\\n' with space and strips leading/trailing whitespace.
    """
    if isinstance(value, str):
        return value.replace('\\n', ' ').strip()
    return value

if __name__ == "__main__":
    # 1) Provide paths for TWO parent PDFs and ONE child PDF
    parent_pdf_1 = "Parent.pdf"
    parent_pdf_2 = "Parent (2).pdf"
    child_pdf    = "Child.pdf"

    # 2) Extract/concatenate all pages/tables from both Parent PDFs
    df_parent_1 = extract_all_tables(parent_pdf_1)
    df_parent_2 = extract_all_tables(parent_pdf_2)
    df_parent = pd.concat([df_parent_1, df_parent_2], ignore_index=True)

    # Extract from Child
    df_child = extract_all_tables(child_pdf)

    if df_parent.empty:
        print("Both parent PDFs produced no data. Exiting.")
        exit()
    if df_child.empty:
        print("Child PDF produced no data. We'll still output all parent rows, no duplication from child info.")

    # 3) Clean data
    df_parent = df_parent.apply(lambda col: col.map(clean_cell))
    df_child  = df_child.apply(lambda col: col.map(clean_cell))

    # 4) Display columns for debug
    print("Parent columns:", df_parent.columns.tolist())
    print("Child columns:", df_child.columns.tolist())

    # 5) Rename columns
    #    In parent: "HAWB\nNumber" => "HAWB"
    rename_parent = {
        "HAWB\nNumber": "HAWB",
    }
    df_parent.rename(columns=rename_parent, inplace=True)

    #    In child: "HAWB\nShipment" => "HAWB", "Secondary Tracking Numbers" => "secondary"
    #    We ignore 'Pcs' entirely now, as requested
    rename_child = {
        "HAWB\nShipment": "HAWB",
        "Secondary Tracking Numbers": "secondary"
    }
    df_child.rename(columns=rename_child, inplace=True)

    # 6) Merge with how="left" so all Parent rows remain
    if "HAWB" not in df_parent.columns:
        print("No 'HAWB' column in the parent after rename. Check 'HAWB\\nNumber'.")
        exit()

    if not df_child.empty and "HAWB" not in df_child.columns:
        print("No 'HAWB' column in the child after rename. Check 'HAWB\\nShipment'.")
        exit()

    df_merged = pd.merge(
        df_parent,
        df_child,
        on="HAWB",
        how="left",
        suffixes=("_parent", "_child")
    )
    # This leaves child columns (like 'secondary') as NaN if no match.

    # 7) We'll expand each row based on the number of 'secondary' items
    #    If 'secondary' is missing, create an empty column
    if "secondary" not in df_merged.columns:
        df_merged["secondary"] = ""

    final_rows = []

    for _, row in df_merged.iterrows():
        row_dict = row.to_dict()

        # parse 'secondary' => split on commas
        sec_str = row_dict.get("secondary", "")
        if pd.isna(sec_str):
            sec_str = ""
        secondary_list = [s.strip() for s in sec_str.split(",") if s.strip()]

        # if no match or empty => produce 1 row => Type = 'Master'
        # if secondary_list has N items => produce N+1 rows
        total_copies = len(secondary_list) + 1

        for i in range(total_copies):
            new_row = row_dict.copy()
            # We'll add a new "Type" column
            if i == 0:
                # first row => parent's original HAWB
                new_row["Type"] = "Master"
            else:
                # subsequent => replace HAWB with a secondary
                new_row["Type"] = "Baby"
                idx_in_sec = i - 1
                if idx_in_sec < len(secondary_list):
                    new_row["HAWB"] = secondary_list[idx_in_sec]
                else:
                    new_row["HAWB"] = ""  # or skip if you prefer

            final_rows.append(new_row)

    df_expanded = pd.DataFrame(final_rows)

    # 8) Keep the parent's columns plus the new "Type" in final output
    parent_columns_order = [
        "#",
        "Origin",
        "HAWB",
        "Pcs",                # parent's Pcs if present
        "Weight",
        "Shipper Details",
        "Dest",
        "Bill\nTerm",
        "Consignee Details",
        "Description\nof Goods",
        "Total\nValue",
        "Total\nValue(LKR)"
    ]
    # Insert "Type" at the end (or wherever you prefer)
    final_cols = parent_columns_order + ["Type"]

    # Filter to columns that actually exist
    existing_cols = [c for c in final_cols if c in df_expanded.columns]
    df_final = df_expanded[existing_cols]

    # 9) Save to Excel
    df_final.to_excel("final_output.xlsx", index=False)
    print("All parent rows included, with duplication based on 'secondary', plus 'Type' column added.")
    print("Output saved to final_output.xlsx.\n")

    # Show sample
    print("Sample of final DataFrame:")
    print(df_final.head(10).to_string(index=False))
