import os
import pandas as pd
import duckdb
from pymilvus import connections, utility, Collection, CollectionSchema, FieldSchema, DataType
from sentence_transformers import SentenceTransformer
from typing import List, Dict

class DBIngestor:
    def __init__(self):
        self.MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
        self.MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")
        self.DUCKDB_FILE = "sales_specs.db"
        self.COLLECTION_NAME = "sales_notebook_specs"
        self.EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
        self.EMBEDDING_DIM = 384
        self.embedding_model = SentenceTransformer(self.EMBEDDING_MODEL_NAME)
        self.ALL_FIELDS = ['modeltype', 'version', 'modelname', 'mainboard', 'devtime', 'pm', 'structconfig', 'lcd', 'touchpanel', 'iointerface', 'ledind', 'powerbutton', 'keyboard', 'webcamera', 'touchpad', 'fingerprint', 'audio', 'battery', 'cpu', 'gpu', 'memory', 'lcdconnector', 'storage', 'wifislot', 'thermal', 'tpm', 'rtc', 'wireless', 'lan', 'bluetooth', 'softwareconfig', 'ai', 'accessory', 'certifications', 'otherfeatures']
        self.VECTOR_FIELDS = ['modeltype', 'modelname', 'audio', 'battery', 'cpu', 'gpu', 'memory', 'storage', 'wifislot', 'thermal', 'wireless', 'lan', 'bluetooth', 'ai', 'certifications']

    def ingest(self, data: List[Dict[str, str]]):
        if not data:
            raise ValueError("Input data cannot be empty")
        df = pd.DataFrame(data)
        df = df.astype(str)

        duckdb_count = self._ingest_to_duckdb(df)
        milvus_count = self._ingest_to_milvus(df)

        return duckdb_count, milvus_count

    def _ingest_to_duckdb(self, df: pd.DataFrame) -> int:
        print("--- Ingesting to DuckDB ---")
        con = duckdb.connect(database=self.DUCKDB_FILE, read_only=False)
        con.execute(f"CREATE TABLE IF NOT EXISTS specs ({', '.join([f'{col} VARCHAR' for col in self.ALL_FIELDS])})")
        con.execute("INSERT INTO specs SELECT * FROM df")
        con.close()
        print(f"Successfully appended {len(df)} rows to DuckDB 'specs' table.")
        return len(df)

    def _ingest_to_milvus(self, df: pd.DataFrame) -> int:
        print("--- Ingesting to Milvus ---")
        connections.connect("default", host=self.MILVUS_HOST, port=self.MILVUS_PORT)

        if not utility.has_collection(self.COLLECTION_NAME):
            print(f"Collection '{self.COLLECTION_NAME}' not found. Creating new collection...")
            fields = [FieldSchema(name="pk", dtype=DataType.INT64, is_primary=True, auto_id=True)]
            for col_name in self.ALL_FIELDS:
                fields.append(FieldSchema(name=col_name, dtype=DataType.VARCHAR, max_length=2048))
            fields.append(FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.EMBEDDING_DIM))
            schema = CollectionSchema(fields, "Notebook Specifications Knowledge Base")
            collection = Collection(self.COLLECTION_NAME, schema)
            
            index_params = {"metric_type": "L2", "index_type": "IVF_FLAT", "params": {"nlist": 128}}
            collection.create_index("embedding", index_params)
        else:
            print(f"Found existing collection '{self.COLLECTION_NAME}'.")
            collection = Collection(self.COLLECTION_NAME)

        texts_to_embed = df[self.VECTOR_FIELDS].apply(lambda row: ' '.join([f"{col}: {val}" for col, val in row.items()]), axis=1).tolist()
        vectors = self.embedding_model.encode(texts_to_embed, show_progress_bar=True)
        
        entities = [df[col].tolist() for col in self.ALL_FIELDS]
        entities.append(vectors)
        
        collection.insert(entities)
        collection.flush()
        print(f"Successfully inserted {len(df)} entities into Milvus.")
        return len(df)