"""
Build semantic search index for Garmin running data.
"""
import pandas as pd
import pickle
import os
import faiss
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# Initialize OpenAI client
# Try SUPER_MIND_API_KEY first, then AI_BUILDER_TOKEN (for deployment platform)
SUPER_MIND_API_KEY = os.getenv("SUPER_MIND_API_KEY") or os.getenv("AI_BUILDER_TOKEN")
SUPER_MIND_BASE_URL = os.getenv("SUPER_MIND_BASE_URL", "https://space.ai-builders.com/backend/v1")

if not SUPER_MIND_API_KEY:
    raise ValueError("SUPER_MIND_API_KEY or AI_BUILDER_TOKEN environment variable not set! Please configure it in .env file or deployment config.")

openai_client = OpenAI(
    api_key=SUPER_MIND_API_KEY,
    base_url=SUPER_MIND_BASE_URL
)


def parse_pace_to_seconds(pace_str):
    """
    Convert pace string (e.g., "8:15") to seconds per mile (float).
    
    Args:
        pace_str: Pace string in format "MM:SS" or "H:MM:SS"
        
    Returns:
        Seconds per mile as float, or None if invalid
    """
    if pd.isna(pace_str) or pace_str == '':
        return None
    
    try:
        # Convert to string and strip whitespace
        pace_str = str(pace_str).strip()
        
        # Handle different formats
        parts = pace_str.split(':')
        
        if len(parts) == 2:
            # Format: MM:SS
            minutes = int(parts[0])
            seconds = int(parts[1])
            return minutes * 60 + seconds
        elif len(parts) == 3:
            # Format: H:MM:SS
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = int(parts[2])
            return hours * 3600 + minutes * 60 + seconds
        else:
            print(f"Warning: Invalid pace format: {pace_str}")
            return None
    except Exception as e:
        print(f"Warning: Error parsing pace '{pace_str}': {e}")
        return None


def clean_numeric_column(value):
    """
    Remove commas and convert to integer.
    
    Args:
        value: String or numeric value
        
    Returns:
        Integer value, or None if invalid
    """
    if pd.isna(value):
        return None
    
    try:
        # Convert to string, remove commas, then convert to int
        cleaned = str(value).replace(',', '').strip()
        return int(float(cleaned)) if cleaned else None
    except Exception as e:
        print(f"Warning: Error cleaning numeric value '{value}': {e}")
        return None


def create_run_summary(row):
    """
    Create a text summary for a run.
    
    Args:
        row: DataFrame row containing run data
        
    Returns:
        Formatted summary string
    """
    date = row.get('Date', 'Unknown')
    distance = row.get('Distance', 'N/A')
    avg_hr = row.get('Avg HR', 'N/A')
    avg_pace = row.get('Avg Pace', 'N/A')
    aerobic_te = row.get('Aerobic TE', 'N/A')
    
    return f"Date: {date}, Dist: {distance}, HR: {avg_hr}, Pace: {avg_pace}, Effort: {aerobic_te}"


def embed_text(text, model="text-embedding-3-small"):
    """
    Get embedding for text using OpenAI API.
    
    Args:
        text: Text to embed
        model: Embedding model name
        
    Returns:
        Embedding vector as numpy array
    """
    try:
        response = openai_client.embeddings.create(
            model=model,
            input=text
        )
        return np.array(response.data[0].embedding, dtype=np.float32)
    except Exception as e:
        print(f"Error embedding text: {e}")
        raise


def build_index(csv_path="Garmin_Runing.csv"):
    """
    Build semantic search index from Garmin CSV file.
    
    Args:
        csv_path: Path to the Garmin CSV file
    """
    print(f"Loading CSV file: {csv_path}")
    
    # Check if file exists
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    # Load CSV
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} rows")
    print(f"Columns: {df.columns.tolist()}")
    
    # Clean data
    print("\nCleaning data...")
    
    # Convert Date to datetime
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        print(f"Converted Date column to datetime")
    
    # Convert Avg Pace to seconds per mile
    if 'Avg Pace' in df.columns:
        df['Avg Pace (seconds)'] = df['Avg Pace'].apply(parse_pace_to_seconds)
        print(f"Converted Avg Pace to seconds per mile")
    
    # Clean numeric columns (remove commas)
    numeric_columns = ['Calories', 'Steps']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = df[col].apply(clean_numeric_column)
            print(f"Cleaned {col} column")
    
    # Create summaries
    print("\nCreating run summaries...")
    summaries = []
    valid_indices = []
    
    for idx, row in df.iterrows():
        summary = create_run_summary(row)
        summaries.append(summary)
        valid_indices.append(idx)
    
    print(f"Created {len(summaries)} summaries")
    
    # Vectorize summaries
    print("\nVectorizing summaries with OpenAI embeddings...")
    embeddings = []
    
    for i, summary in enumerate(summaries):
        if (i + 1) % 10 == 0:
            print(f"  Processing {i + 1}/{len(summaries)}...")
        
        try:
            embedding = embed_text(summary)
            embeddings.append(embedding)
        except Exception as e:
            print(f"  Error embedding summary {i + 1}: {e}")
            # Use zero vector as fallback
            embeddings.append(np.zeros(1536, dtype=np.float32))  # text-embedding-3-small dimension
    
    # Convert to numpy array
    embeddings_array = np.array(embeddings).astype('float32')
    print(f"Created embeddings array with shape: {embeddings_array.shape}")
    
    # Build FAISS index
    print("\nBuilding FAISS index...")
    dimension = embeddings_array.shape[1]
    
    # Use L2 (Euclidean) distance index
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings_array)
    
    print(f"FAISS index built with {index.ntotal} vectors")
    
    # Save FAISS index
    index_path = "garmin.index"
    faiss.write_index(index, index_path)
    print(f"Saved FAISS index to {index_path}")
    
    # Save cleaned DataFrame (only valid rows)
    df_cleaned = df.iloc[valid_indices].copy()
    
    # Convert StringDtype columns to object before saving (for compatibility)
    print("\nConverting StringDtype columns to object dtype for compatibility...")
    for col in df_cleaned.columns:
        dtype_str = str(df_cleaned[col].dtype)
        if 'string' in dtype_str.lower() or 'StringDtype' in dtype_str:
            df_cleaned[col] = df_cleaned[col].astype('object')
            print(f"  Converted column '{col}' from {dtype_str} to object")
    
    data_path = "garmin_data.pkl"
    with open(data_path, 'wb') as f:
        pickle.dump(df_cleaned, f)
    print(f"Saved cleaned DataFrame to {data_path}")
    
    print("\n" + "="*60)
    print("Index building completed successfully!")
    print("="*60)
    print(f"Index file: {index_path}")
    print(f"Data file: {data_path}")
    print(f"Total runs indexed: {len(df_cleaned)}")
    print("="*60)


if __name__ == "__main__":
    try:
        build_index()
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
