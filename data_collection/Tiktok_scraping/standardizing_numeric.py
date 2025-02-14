import pandas as pd

# Load the cleaned dataset
file_path = "tiktok_trending_cleaned.csv"
df = pd.read_csv(file_path)

def convert_k_to_number(value):
    """Convert values like '12k' to 12000 and '2.3m' to 2300000."""
    if isinstance(value, str):
        value = value.lower().replace(',', '')  # Ensure uniform format
        if 'k' in value:
            return int(float(value.replace('k', '')) * 1000)
        elif 'm' in value:
            return int(float(value.replace('m', '')) * 1000000)
    try:
        return int(value)  # Convert normal numeric strings
    except ValueError:
        return value  # Return as is if conversion fails

# Apply transformation to relevant columns
columns_to_fix = ['views', 'likes', 'shares', 'comments_count']
for col in columns_to_fix:
    df[col] = df[col].astype(str).apply(convert_k_to_number)

# Save the updated dataset
cleaned_file_path = "tiktok_trending_final.csv"
df.to_csv(cleaned_file_path, index=False)

# Return the updated file path
cleaned_file_path
