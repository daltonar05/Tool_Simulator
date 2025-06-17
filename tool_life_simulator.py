import pandas as pd
from datetime import datetime
import os

def simulate_tool_life(file_path: str, planner_name: str, pieces: int) -> tuple[str, dict]:
    df = pd.read_csv(file_path)

    # Calculate total tools required
    df['Total Tools Required'] = pieces / df['Tool Life (in pieces)']

    result = {}

    # Build result dictionary
    for _, row in df.iterrows():
        component = row['Component Name']
        tool = row['Tool Name']
        shop = row['Operation']
        total = row['Total Tools Required']

        result.setdefault(component, {})
        result[component].setdefault(shop, {})
        result[component][shop][tool] = total

    # Create Excel file with multiple sheets (one per component)
    now = datetime.now().strftime('%d-%B-%Y')
    output_name = f"Tool requirement analytics of {now}.xlsx"
    output_path = os.path.join("results", output_name)

    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        for component in df['Component Name'].unique():
            comp_df = df[df['Component Name'] == component][[
                'Tool Name', 'Operation', 'Tool Life (in pieces)', 'Total Tools Required'
            ]]
            comp_df.to_excel(writer, sheet_name=component[:31], index=False)  # Excel limit: 31 chars

    return output_name, result