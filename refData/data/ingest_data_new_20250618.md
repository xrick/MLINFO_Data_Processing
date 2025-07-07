```python
import pandas as pd
import os
import duckdb
import pandas as pd
from pymilvus import connections, utility, Collection, CollectionSchema, FieldSchema, DataType
from langchain_community.embeddings import HuggingFaceEmbeddings
from tqdm import tqdm
```

### 注意，請不要使用csv檔，會出現資料有大量的NoN


```python
# 將上傳的檔案讀取為 pandas DataFrame
file_path = 'data/nb_data_clean_cayman.xlsx'
df = pd.read_excel(file_path)

# 獲取標題列 (欄位名稱)
header_columns = df.columns.tolist()
print("從 XLSX 檔案中讀取到的標題列如下：")
print(header_columns)
print(f"一列共有：{len(header_columns)}欄")
```

    從 XLSX 檔案中讀取到的標題列如下：
    ['modeltype', 'version', 'modelname', 'mainboard', 'devtime', 'pm', 'structconfig', 'lcd', 'touchpanel', 'iointerface', 'ledind', 'powerbutton', 'keyboard', 'webcamera', 'touchpad', 'fingerprint', 'audio', 'battery', 'cpu', 'gpu', 'memory', 'lcdconnector', 'storage', 'wifislot', 'thermal', 'tpm', 'rtc', 'wireless', 'lan', 'bluetooth', 'softwareconfig', 'ai', 'accessory', 'certfications', 'otherfeatures']
    一列共有：35欄



```python
table_titles = [
                    'modeltype', 'version', 'modelname', 'mainboard', 'devtime',
                    'pm', 'structconfig', 'lcd', 'touchpanel', 'iointerface', 
                    'ledind', 'powerbutton', 'keyboard', 'webcamera', 'touchpad', 
                    'fingerprint', 'audio', 'battery', 'cpu', 'gpu', 'memory', 
                    'lcdconnector', 'storage', 'wifislot', 'thermal', 'tpm', 'rtc', 
                    'wireless', 'lan', 'bluetooth', 'softwareconfig', 'ai', 'accessory', 
                    'certfications', 'otherfeatures'
               ]
Fields_Types = DataType.VARCHAR
ColFieldsForVector = [
    'modeltype',
    'modelname',
    'audio', 
    'battery', 
    'cpu', 
    'gpu', 
    'memory',
    'storage', 
    'wifislot', 
    'thermal',
    'wireless', 
    'lan', 
    'bluetooth', 
    'ai',
    'certfications'
]
```


```python
# --- 設定 ---
MILVUS_HOST = "localhost"
MILVUS_PORT = "19530"
DUCKDB_FILE = "sales_rag_app/db/sales_specs.db"
COLLECTION_NAME = "sales_notebook_specs" # 使用新的 Collection 名稱以避免混淆
EMBEDDING_MODEL = "all-MiniLM-L6-v2" # SentenceTransformer 模型
EMBEDDING_DIM = 384 # all-MiniLM-L6-v2 的維度
# CSV_FILE_PATH = "data/nb_data_clean_cayman.csv" # 您的 CSV 檔案路徑
XLSX_FILE_PATH = "data/nb_data_clean_cayman.xlsx" # 您的 CSV 檔案路徑
```


```python
# --- 主執行流程 ---
def main():
    # --- 檢查檔案是否存在 ---
    if not os.path.exists(XLSX_FILE_PATH):
        print(f"錯誤: 找不到指定的檔案 '{XLSX_FILE_PATH}'。請確認檔案路徑是否正確。")
        return

    print(f"正在讀取資料來源: {XLSX_FILE_PATH}")
    df = pd.read_excel(XLSX_FILE_PATH)
    # 確保所有欄位都是字串類型，避免後續處理出錯
    df = df.astype(str)
    header_columns = df.columns.tolist()
    print(f"成功讀取 {len(df)} 筆資料。")

    # --- 1. 處理結構化資料 (DuckDB) ---
    print("\n--- 正在處理結構化規格資料並存入 DuckDB ---")
    if os.path.exists(DUCKDB_FILE):
        print(f"找到舊的 DuckDB 檔案 '{DUCKDB_FILE}'，正在刪除...")
        os.remove(DUCKDB_FILE)

    con = duckdb.connect(database=DUCKDB_FILE, read_only=False)
    # 直接從 DataFrame 建立資料表，更簡單高效
    con.execute("CREATE TABLE specs AS SELECT * FROM df")
    print(f"成功將 {len(df)} 筆規格資料存入 DuckDB 的 'specs' 資料表中。")
    con.close()

    # --- 2. 處理並存入非結構化資料 (Milvus) ---
    print("\n--- 正在處理文本資料並存入 Milvus ---")
    connections.connect("default", host=MILVUS_HOST, port=MILVUS_PORT)

    if utility.has_collection(COLLECTION_NAME):
        print(f"找到舊的 Milvus Collection '{COLLECTION_NAME}'，正在刪除...")
        utility.drop_collection(COLLECTION_NAME)

    # 動態建立 Collection Schema
    print("正在根據 CSV 標題列建立新的 Milvus Schema...")
    # a. 主鍵 (Primary Key)
    fields = [
        FieldSchema(name="pk", dtype=DataType.INT64, is_primary=True, auto_id=True)
    ]
    # b. 根據 XLSX 標題列建立其他資料欄位
    for col_name in header_columns:
        # Milvus 欄位名稱有一些限制，例如不能有 '-'，這裡做簡單替換
        safe_col_name = col_name.replace('-', '_').replace('(', '').replace(')', '')
        fields.append(FieldSchema(name=safe_col_name, dtype=DataType.VARCHAR, max_length=2500))
    
    # c. 嵌入向量欄位
    fields.append(FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=EMBEDDING_DIM))
    
    schema = CollectionSchema(fields, "銷售筆電規格知識庫 (從XLSX導入)")
    collection = Collection(COLLECTION_NAME, schema)
    print(f"成功建立 Schema，Collection: '{COLLECTION_NAME}'")

    # 準備要插入的資料
    # 將每一列的所有欄位合併成一個長字串，用於生成嵌入向量
    print("正在準備要嵌入的文本資料...")
    # texts_to_embed = df.apply(lambda row: ' '.join([f"{col}: {val}" for col, val in row.items()]), axis=1).tolist()
    
    filtered_df = df[ColFieldsForVector]
    # 只組合這些欄位的資料
    texts_to_embed = filtered_df.apply(
        lambda row: ' '.join([f"{col}: {row[col]}" for col in ColFieldsForVector]),
        axis=1
    ).tolist()
    # print(texts_to_embed)
    # 產生嵌入向量
    print(f"正在使用 '{EMBEDDING_MODEL}' 模型產生嵌入向量 (共 {len(texts_to_embed)} 筆)...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vectors = []
    # 使用 tqdm 顯示進度條
    for text in tqdm(texts_to_embed, desc="Embedding Progress"):
        vectors.append(embeddings.embed_query(text))

    # 準備插入 Milvus 的實體 (Entities)
    entities = []
    # 根據 Schema 順序（除了 pk 和 embedding）準備資料
    for col_name in header_columns:
        entities.append(df[col_name].tolist())
    entities.append(vectors) # 最後加入 embedding 向量

    # 插入資料
    print("正在將資料插入 Milvus...")
    collection.insert(entities)
    collection.flush() # 確保資料寫入
    print(f"成功將 {collection.num_entities} 筆資料導入 Milvus。")

    # 創建索引以加速搜尋
    print("正在為向量創建索引 (IVF_FLAT)...")
    index_params = {
        "metric_type": "L2",
        "index_type": "IVF_FLAT",
        "params": {"nlist": 128}
    }
    collection.create_index("embedding", index_params)
    collection.load()
    print("索引創建完成，Collection 已載入記憶體。")

    print("\n資料導入完成！")

# if __name__ == "__main__":
#     main()
```


```python
main()
```

    正在讀取資料來源: data/nb_data_clean_cayman.xlsx
    成功讀取 15 筆資料。
    
    --- 正在處理結構化規格資料並存入 DuckDB ---
    找到舊的 DuckDB 檔案 'sales_rag_app/db/sales_specs.db'，正在刪除...
    成功將 15 筆規格資料存入 DuckDB 的 'specs' 資料表中。
    
    --- 正在處理文本資料並存入 Milvus ---
    找到舊的 Milvus Collection 'sales_notebook_specs'，正在刪除...
    正在根據 CSV 標題列建立新的 Milvus Schema...
    成功建立 Schema，Collection: 'sales_notebook_specs'
    正在準備要嵌入的文本資料...
    正在使用 'all-MiniLM-L6-v2' 模型產生嵌入向量 (共 15 筆)...


    /tmp/ipykernel_29290/1146746367.py:68: LangChainDeprecationWarning: The class `HuggingFaceEmbeddings` was deprecated in LangChain 0.2.2 and will be removed in 1.0. An updated version of the class exists in the :class:`~langchain-huggingface package and should be used instead. To use it run `pip install -U :class:`~langchain-huggingface` and import as `from :class:`~langchain_huggingface import HuggingFaceEmbeddings``.
      embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    /home/mapleleaf/.conda/envs/salseragenv/lib/python3.11/site-packages/tqdm/auto.py:21: TqdmWarning: IProgress not found. Please update jupyter and ipywidgets. See https://ipywidgets.readthedocs.io/en/stable/user_install.html
      from .autonotebook import tqdm as notebook_tqdm
    Embedding Progress: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 15/15 [00:00<00:00, 36.25it/s]


    正在將資料插入 Milvus...
    成功將 15 筆資料導入 Milvus。
    正在為向量創建索引 (IVF_FLAT)...
    索引創建完成，Collection 已載入記憶體。
    
    資料導入完成！



```python

```
