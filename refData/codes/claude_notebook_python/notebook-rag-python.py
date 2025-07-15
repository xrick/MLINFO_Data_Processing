import json
import numpy as np
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import gradio as gr
from datetime import datetime
import pandas as pd

# Data structures
@dataclass
class NotebookSpec:
    id: str
    brand: str
    model: str
    category: str
    processor: str
    ram: str
    storage: str
    display: str
    graphics: str
    battery: str
    weight: str
    ports: str
    os: str
    price: str
    description: str
    use_cases: List[str]

@dataclass
class Chunk:
    id: str
    notebook_id: str
    chunk_type: str
    content: str
    metadata: Dict[str, Any]
    embedding: np.ndarray = None

class NotebookRAGSystem:
    def __init__(self):
        # Initialize embedding model
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory="./notebook_rag_db"
        ))
        
        # Create or get collection
        try:
            self.collection = self.chroma_client.create_collection(
                name="notebook_specs",
                metadata={"hnsw:space": "cosine"}
            )
        except:
            self.collection = self.chroma_client.get_collection("notebook_specs")
        
        # Sample notebook data
        self.notebooks = [
            NotebookSpec(
                id="nb1",
                brand="Dell",
                model="XPS 15 9520",
                category="Premium Ultrabook",
                processor="Intel Core i7-12700H (14 cores, up to 4.7GHz)",
                ram="32GB DDR5-4800MHz",
                storage="1TB PCIe NVMe SSD",
                display="15.6\" 3.5K OLED touchscreen, 3456x2160, 400 nits",
                graphics="NVIDIA GeForce RTX 3050 Ti 4GB GDDR6",
                battery="86Wh, up to 13 hours",
                weight="1.96 kg",
                ports="2x Thunderbolt 4, 1x USB-C 3.2, SD card reader, 3.5mm audio",
                os="Windows 11 Pro",
                price="$2,499",
                description="The Dell XPS 15 9520 represents the pinnacle of premium Windows laptops, combining powerful performance with stunning visuals. Its OLED display delivers exceptional color accuracy and deep blacks, making it ideal for creative professionals.",
                use_cases=["Content creation", "Software development", "Video editing", "Professional design"]
            ),
            NotebookSpec(
                id="nb2",
                brand="Apple",
                model="MacBook Pro 16\" M3 Max",
                category="Professional Workstation",
                processor="Apple M3 Max (16-core CPU, 40-core GPU)",
                ram="64GB unified memory",
                storage="2TB SSD",
                display="16.2\" Liquid Retina XDR, 3456x2234, 1600 nits peak",
                graphics="Integrated 40-core GPU",
                battery="100Wh, up to 22 hours",
                weight="2.16 kg",
                ports="3x Thunderbolt 4, HDMI 2.1, SD card, MagSafe 3, 3.5mm audio",
                os="macOS Sonoma",
                price="$4,999",
                description="The MacBook Pro 16\" with M3 Max chip is Apple's most powerful laptop ever created. It delivers unprecedented performance for professional workflows while maintaining exceptional battery life.",
                use_cases=["3D rendering", "Machine learning", "8K video editing", "Music production"]
            ),
            NotebookSpec(
                id="nb3",
                brand="ASUS",
                model="ROG Strix G16",
                category="Gaming Laptop",
                processor="Intel Core i9-13980HX (24 cores, up to 5.6GHz)",
                ram="32GB DDR5-4800MHz",
                storage="1TB PCIe 4.0 NVMe SSD",
                display="16\" QHD+ 240Hz, 2560x1600, 500 nits, 100% DCI-P3",
                graphics="NVIDIA GeForce RTX 4070 8GB GDDR6",
                battery="90Wh, up to 8 hours",
                weight="2.5 kg",
                ports="2x USB-A 3.2, 2x USB-C (1x Thunderbolt 4), HDMI 2.1, RJ45, 3.5mm audio",
                os="Windows 11 Home",
                price="$2,299",
                description="The ASUS ROG Strix G16 is a gaming powerhouse that doesn't compromise on performance. With its high-refresh QHD+ display and RTX 4070 graphics, it delivers smooth gameplay at high settings.",
                use_cases=["AAA gaming", "Game streaming", "3D modeling", "VR applications"]
            ),
            NotebookSpec(
                id="nb4",
                brand="Lenovo",
                model="ThinkPad X1 Carbon Gen 11",
                category="Business Ultrabook",
                processor="Intel Core i7-1365U (10 cores, up to 5.2GHz)",
                ram="16GB LPDDR5-6400MHz",
                storage="512GB PCIe 4.0 NVMe SSD",
                display="14\" 2.8K OLED, 2880x1800, 400 nits, HDR500",
                graphics="Intel Iris Xe Graphics",
                battery="57Wh, up to 15 hours",
                weight="1.12 kg",
                ports="2x Thunderbolt 4, 2x USB-A 3.2, HDMI 2.0b, 3.5mm audio",
                os="Windows 11 Pro",
                price="$1,899",
                description="The ThinkPad X1 Carbon Gen 11 continues Lenovo's tradition of creating the ultimate business laptop. Its legendary keyboard and robust security features make it perfect for professionals.",
                use_cases=["Business productivity", "Remote work", "Presentations", "Light development"]
            ),
            NotebookSpec(
                id="nb5",
                brand="HP",
                model="Spectre x360 14",
                category="2-in-1 Convertible",
                processor="Intel Core i7-1355U (10 cores, up to 5.0GHz)",
                ram="16GB LPDDR4x-4266MHz",
                storage="1TB PCIe NVMe SSD",
                display="13.5\" 3K2K OLED touchscreen, 3000x2000, 400 nits",
                graphics="Intel Iris Xe Graphics",
                battery="66Wh, up to 14 hours",
                weight="1.34 kg",
                ports="2x Thunderbolt 4, 1x USB-A 3.2, microSD, 3.5mm audio",
                os="Windows 11 Home",
                price="$1,699",
                description="The HP Spectre x360 14 is a versatile 2-in-1 that excels in both laptop and tablet modes. Its 3:2 aspect ratio display is perfect for productivity.",
                use_cases=["Digital art", "Note-taking", "Media consumption", "Office work"]
            )
        ]
        
        # Initialize the system
        self._create_chunks_and_index()
    
    def _create_chunks_and_index(self):
        """Create chunks from notebooks and index them"""
        all_chunks = []
        
        for notebook in self.notebooks:
            chunks = self._create_notebook_chunks(notebook)
            all_chunks.extend(chunks)
        
        # Index chunks in ChromaDB
        self._index_chunks(all_chunks)
    
    def _create_notebook_chunks(self, notebook: NotebookSpec) -> List[Chunk]:
        """Create context-preserving chunks from a notebook specification"""
        chunks = []
        
        # 1. Overview chunk
        overview_content = f"{notebook.brand} {notebook.model} - {notebook.category}. {notebook.description}"
        chunks.append(Chunk(
            id=f"{notebook.id}_overview",
            notebook_id=notebook.id,
            chunk_type="overview",
            content=overview_content,
            metadata={
                "brand": notebook.brand,
                "model": notebook.model,
                "category": notebook.category,
                "price": notebook.price
            }
        ))
        
        # 2. Performance specifications chunk
        perf_content = (f"{notebook.brand} {notebook.model} Performance: "
                       f"Processor: {notebook.processor}. "
                       f"RAM: {notebook.ram}. "
                       f"Graphics: {notebook.graphics}.")
        chunks.append(Chunk(
            id=f"{notebook.id}_performance",
            notebook_id=notebook.id,
            chunk_type="performance",
            content=perf_content,
            metadata={
                "brand": notebook.brand,
                "model": notebook.model,
                "processor": notebook.processor,
                "ram": notebook.ram,
                "graphics": notebook.graphics
            }
        ))
        
        # 3. Display and storage chunk
        display_storage_content = (f"{notebook.brand} {notebook.model} Display & Storage: "
                                  f"Display: {notebook.display}. "
                                  f"Storage: {notebook.storage}.")
        chunks.append(Chunk(
            id=f"{notebook.id}_display_storage",
            notebook_id=notebook.id,
            chunk_type="display_storage",
            content=display_storage_content,
            metadata={
                "brand": notebook.brand,
                "model": notebook.model,
                "display": notebook.display,
                "storage": notebook.storage
            }
        ))
        
        # 4. Portability chunk
        portability_content = (f"{notebook.brand} {notebook.model} Portability: "
                              f"Weight: {notebook.weight}. "
                              f"Battery: {notebook.battery}.")
        chunks.append(Chunk(
            id=f"{notebook.id}_portability",
            notebook_id=notebook.id,
            chunk_type="portability",
            content=portability_content,
            metadata={
                "brand": notebook.brand,
                "model": notebook.model,
                "weight": notebook.weight,
                "battery": notebook.battery
            }
        ))
        
        # 5. Connectivity and OS chunk
        connectivity_content = (f"{notebook.brand} {notebook.model} Connectivity: "
                               f"Ports: {notebook.ports}. "
                               f"Operating System: {notebook.os}.")
        chunks.append(Chunk(
            id=f"{notebook.id}_connectivity",
            notebook_id=notebook.id,
            chunk_type="connectivity",
            content=connectivity_content,
            metadata={
                "brand": notebook.brand,
                "model": notebook.model,
                "ports": notebook.ports,
                "os": notebook.os
            }
        ))
        
        # 6. Use cases chunk
        use_cases_content = (f"{notebook.brand} {notebook.model} is ideal for: "
                            f"{', '.join(notebook.use_cases)}.")
        chunks.append(Chunk(
            id=f"{notebook.id}_usecases",
            notebook_id=notebook.id,
            chunk_type="use_cases",
            content=use_cases_content,
            metadata={
                "brand": notebook.brand,
                "model": notebook.model,
                "use_cases": notebook.use_cases
            }
        ))
        
        return chunks
    
    def _index_chunks(self, chunks: List[Chunk]):
        """Index chunks in ChromaDB with embeddings"""
        # Generate embeddings
        contents = [chunk.content for chunk in chunks]
        embeddings = self.encoder.encode(contents).tolist()
        
        # Prepare data for ChromaDB
        ids = [chunk.id for chunk in chunks]
        metadatas = []
        for chunk in chunks:
            metadata = chunk.metadata.copy()
            metadata['chunk_type'] = chunk.chunk_type
            metadata['notebook_id'] = chunk.notebook_id
            metadatas.append(metadata)
        
        # Add to collection
        self.collection.add(
            embeddings=embeddings,
            documents=contents,
            metadatas=metadatas,
            ids=ids
        )
    
    def search(self, query: str, filters: Dict[str, Any] = None, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Search for relevant notebooks based on query
        """
        # Generate query embedding
        query_embedding = self.encoder.encode([query])[0].tolist()
        
        # Build where clause for filters
        where_clause = {}
        if filters:
            if filters.get('category'):
                where_clause['category'] = filters['category']
            if filters.get('brand'):
                where_clause['brand'] = filters['brand']
            if filters.get('max_price'):
                # Note: In production, you'd store price as a numeric field
                pass
        
        # Query ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k * 2,  # Get more results for aggregation
            where=where_clause if where_clause else None
        )
        
        # Aggregate results by notebook
        notebook_results = self._aggregate_results(results)
        
        return notebook_results
    
    def _aggregate_results(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Aggregate chunk results by notebook and calculate relevance scores"""
        notebook_scores = {}
        notebook_chunks = {}
        
        if not results['ids'] or not results['ids'][0]:
            return []
        
        for i, chunk_id in enumerate(results['ids'][0]):
            metadata = results['metadatas'][0][i]
            notebook_id = metadata['notebook_id']
            distance = results['distances'][0][i]
            
            # Convert distance to similarity score (1 - distance for cosine)
            similarity = 1 - distance
            
            if notebook_id not in notebook_scores:
                notebook_scores[notebook_id] = 0
                notebook_chunks[notebook_id] = []
            
            notebook_scores[notebook_id] += similarity
            notebook_chunks[notebook_id].append({
                'chunk_id': chunk_id,
                'chunk_type': metadata['chunk_type'],
                'content': results['documents'][0][i],
                'similarity': similarity
            })
        
        # Get full notebook information
        aggregated_results = []
        for notebook_id, score in notebook_scores.items():
            notebook = next((nb for nb in self.notebooks if nb.id == notebook_id), None)
            if notebook:
                aggregated_results.append({
                    'notebook': notebook,
                    'relevance_score': score / len(notebook_chunks[notebook_id]),  # Average score
                    'matched_chunks': notebook_chunks[notebook_id]
                })
        
        # Sort by relevance score
        aggregated_results.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return aggregated_results
    
    def get_notebook_context(self, notebook_id: str) -> Dict[str, Any]:
        """Get full context for a specific notebook"""
        notebook = next((nb for nb in self.notebooks if nb.id == notebook_id), None)
        if not notebook:
            return None
        
        # Get all chunks for this notebook
        results = self.collection.get(
            where={"notebook_id": notebook_id}
        )
        
        return {
            'notebook': notebook,
            'chunks': results
        }

# Gradio Interface
def create_gradio_interface():
    rag_system = NotebookRAGSystem()
    
    def search_notebooks(query, category_filter, brand_filter, max_price_filter):
        filters = {}
        if category_filter and category_filter != "All":
            filters['category'] = category_filter
        if brand_filter and brand_filter != "All":
            filters['brand'] = brand_filter
        if max_price_filter:
            filters['max_price'] = float(max_price_filter)
        
        results = rag_system.search(query, filters)
        
        # Format results for display
        output = []
        for result in results[:5]:  # Top 5 results
            notebook = result['notebook']
            score = result['relevance_score']
            chunks = result['matched_chunks']
            
            output.append(f"## {notebook.brand} {notebook.model}")
            output.append(f"**Category:** {notebook.category} | **Price:** {notebook.price}")
            output.append(f"**Relevance Score:** {score:.3f}")
            output.append(f"\n{notebook.description}")
            output.append(f"\n**Matched Chunks:** {', '.join([c['chunk_type'] for c in chunks])}")
            output.append("\n**Key Specifications:**")
            output.append(f"- Processor: {notebook.processor}")
            output.append(f"- RAM: {notebook.ram}")
            output.append(f"- Display: {notebook.display}")
            output.append(f"- Weight: {notebook.weight}")
            output.append("\n---\n")
        
        return "\n".join(output) if output else "No results found."
    
    # Get unique categories and brands
    categories = ["All"] + list(set([nb.category for nb in rag_system.notebooks]))
    brands = ["All"] + list(set([nb.brand for nb in rag_system.notebooks]))
    
    # Create interface
    interface = gr.Interface(
        fn=search_notebooks,
        inputs=[
            gr.Textbox(label="Search Query", placeholder="e.g., gaming laptop with RTX, ultrabook for development"),
            gr.Dropdown(choices=categories, label="Category Filter", value="All"),
            gr.Dropdown(choices=brands, label="Brand Filter", value="All"),
            gr.Number(label="Max Price ($)", value=None)
        ],
        outputs=gr.Markdown(label="Search Results"),
        title="Notebook Specifications RAG System",
        description="Search for notebooks using natural language queries with context-aware retrieval",
        examples=[
            ["gaming laptop with good graphics", "All", "All", None],
            ["lightweight laptop for business", "Business Ultrabook", "All", 2000],
            ["laptop for video editing", "All", "Apple", None],
            ["2-in-1 convertible for drawing", "2-in-1 Convertible", "All", None]
        ]
    )
    
    return interface

# Additional utility functions
def export_chunks_to_json(rag_system: NotebookRAGSystem, filename: str = "notebook_chunks.json"):
    """Export all chunks to JSON for analysis"""
    all_chunks = []
    
    for notebook in rag_system.notebooks:
        chunks = rag_system._create_notebook_chunks(notebook)
        for chunk in chunks:
            all_chunks.append({
                'id': chunk.id,
                'notebook_id': chunk.notebook_id,
                'chunk_type': chunk.chunk_type,
                'content': chunk.content,
                'metadata': chunk.metadata
            })
    
    with open(filename, 'w') as f:
        json.dump(all_chunks, f, indent=2)
    
    print(f"Exported {len(all_chunks)} chunks to {filename}")

def analyze_chunk_distribution(rag_system: NotebookRAGSystem):
    """Analyze chunk distribution and statistics"""
    chunk_stats = {
        'total_notebooks': len(rag_system.notebooks),
        'total_chunks': 0,
        'chunks_per_type': {},
        'avg_chunk_length': 0
    }
    
    all_chunks = []
    for notebook in rag_system.notebooks:
        chunks = rag_system._create_notebook_chunks(notebook)
        all_chunks.extend(chunks)
    
    chunk_stats['total_chunks'] = len(all_chunks)
    
    # Count chunks by type
    for chunk in all_chunks:
        chunk_type = chunk.chunk_type
        if chunk_type not in chunk_stats['chunks_per_type']:
            chunk_stats['chunks_per_type'][chunk_type] = 0
        chunk_stats['chunks_per_type'][chunk_type] += 1
    
    # Calculate average chunk length
    total_length = sum(len(chunk.content) for chunk in all_chunks)
    chunk_stats['avg_chunk_length'] = total_length / len(all_chunks)
    
    return chunk_stats

# Main execution
if __name__ == "__main__":
    # Create and launch the Gradio interface
    interface = create_gradio_interface()
    
    # Print system statistics
    rag_system = NotebookRAGSystem()
    stats = analyze_chunk_distribution(rag_system)
    print("RAG System Statistics:")
    print(f"Total Notebooks: {stats['total_notebooks']}")
    print(f"Total Chunks: {stats['total_chunks']}")
    print(f"Average Chunk Length: {stats['avg_chunk_length']:.0f} characters")
    print(f"Chunks per Type: {stats['chunks_per_type']}")
    
    # Launch the interface
    interface.launch()