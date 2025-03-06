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
                df = pd.DataFrame(table[1:], columns=table[0])
                all_dfs.append(df)
    if not all_dfs:
        print(f"No tables found in {pdf_path}. Returning empty DataFrame.")
        return pd.DataFrame()
    return pd.concat(all_dfs, ignore_index=True)

def clean_cell(value):
    """
    Replaces literal '\\n' with a space and strips leading/trailing whitespace.
    """
    if isinstance(value, str):
        return value.replace('\\n', ' ').strip()
    return value

if __name__ == "__main__":
    parent_pdf_1 = "Parent.pdf"
    parent_pdf_2 = "Parent (2).pdf"
    child_pdf = "CHILD.pdf"

    df_parent_1 = extract_all_tables(parent_pdf_1)
    df_parent_2 = extract_all_tables(parent_pdf_2)
    df_parent = pd.concat([df_parent_1, df_parent_2], ignore_index=True)

    df_child = extract_all_tables(child_pdf)

    if df_parent.empty:
        print("Parent PDFs produced no data. Exiting.")
        exit()
    if df_child.empty:
        print("Child PDF produced no data. We'll still produce the parent rows without duplication.")

    df_parent = df_parent.apply(lambda col: col.map(clean_cell))
    df_child = df_child.apply(lambda col: col.map(clean_cell))

    print("\nParent columns (raw):", df_parent.columns.tolist())
    print("Child columns (raw):", df_child.columns.tolist())

    rename_parent = {}
    if "HAWB\nNumber" in df_parent.columns:
        rename_parent["HAWB\nNumber"] = "HAWB"

    # Ensure "Origin" is retained correctly
    if "Origin" not in df_parent.columns:
        candidate_origin = [col for col in df_parent.columns if "origin" in col.lower()]
        if len(candidate_origin) == 1:
            rename_parent[candidate_origin[0]] = "Origin"

    df_parent.rename(columns=rename_parent, inplace=True)

    rename_child = {}
    if "HAWB\nShipment" in df_child.columns:
        rename_child["HAWB\nShipment"] = "HAWB"
    if "Secondary Tracking Numbers" in df_child.columns:
        rename_child["Secondary Tracking Numbers"] = "secondary"

    df_child.rename(columns=rename_child, inplace=True)

    if "HAWB" not in df_parent.columns:
        print("No 'HAWB' column found in the parent after rename. Check 'HAWB\\nNumber'.")
        exit()

    if not df_child.empty and "HAWB" not in df_child.columns:
        print("No 'HAWB' column found in child after rename. Check 'HAWB\\nShipment'.")
        exit()

    df_merged = pd.merge(
        df_parent,
        df_child,
        on="HAWB",
        how="left",
        suffixes=("_parent", "_child")
    )

    # Ensure Origin is retained after merging
    if "Origin" not in df_merged.columns:
        df_merged["Origin"] = df_parent.set_index("HAWB")["Origin"].reindex(df_merged["HAWB"]).values

    if "secondary" not in df_merged.columns:
        df_merged["secondary"] = ""

    final_rows = []
    for _, row in df_merged.iterrows():
        row_dict = row.to_dict()
        sec_str = row_dict.get("secondary", "")
        if pd.isna(sec_str):
            sec_str = ""
        secondary_list = [s.strip() for s in sec_str.split(",") if s.strip()]

        total_copies = len(secondary_list) + 1

        for i in range(total_copies):
            new_row = row_dict.copy()
            if i == 0:
                new_row["Type"] = "Master"
            else:
                new_row["Type"] = "Baby"
                idx_in_sec = i - 1
                if idx_in_sec < len(secondary_list):
                    new_row["HAWB"] = secondary_list[idx_in_sec]
                else:
                    new_row["HAWB"] = ""
            final_rows.append(new_row)

    df_expanded = pd.DataFrame(final_rows)

    # Force "Origin" to be the first column
    parent_columns_order = [
        "Origin",
        "#",
        "HAWB",
        "Pcs",
        "Weight",
        "Shipper Details",
        "Dest",
        "Bill\nTerm",
        "Consignee Details",
        "Description\nof Goods",
        "Total\nValue",
        "Total\nValue(LKR)"
    ]

    final_cols = parent_columns_order + ["Type"]

    existing_cols = [c for c in final_cols if c in df_expanded.columns]
    df_final = df_expanded[existing_cols]

    # Debugging: Check if Origin exists in final DataFrame
    print("\nFinal DataFrame columns before saving:", df_final.columns.tolist())

    df_final.to_excel("final_output.xlsx", index=False)
    print("\nDone! Excel file with 'Origin' first and 'Type' column added has been saved as final_output.xlsx.")

    print("\nSample of final DataFrame:")
    print(df_final.head(10).to_string(index=False))
