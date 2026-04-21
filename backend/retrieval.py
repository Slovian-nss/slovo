"""
Retrieval engine for finding similar translations.
Uses example_sentences.json and semantic similarity.
"""

import json
from typing import List, Dict, Tuple, Optional
from pathlib import Path

class RetrieverEngine:
    """
    Retrieval-Augmented Translation engine.
    Finds similar examples and contexts for better translation quality.
    """
    
    def __init__(self, examples_file: Optional[str] = None):
        self.examples = []
        self.index = {}
        
        if examples_file:
            self.load_examples(examples_file)
    
    def load_examples(self, examples_file: str):
        """Load example sentences from JSON file"""
        try:
            with open(examples_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    self.examples = data
                    self._build_index()
                    print(f"Loaded {len(self.examples)} example sentences")
        except Exception as e:
            print(f"Error loading examples: {e}")
    
    def _build_index(self):
        """Build search indices for fast retrieval"""
        # Index by words in Polish text
        for idx, example in enumerate(self.examples):
            polish = example.get("polish", "").lower()
            slovian = example.get("slovian", "")
            
            if polish:
                words = polish.split()
                for word in words:
                    if word not in self.index:
                        self.index[word] = []
                    self.index[word].append(idx)
    
    def _similarity_score(self, query_words: List[str], example: Dict) -> float:
        """
        Calculate similarity between query and example.
        Simple word overlap score; can be enhanced with embeddings.
        """
        polish_text = example.get("polish", "").lower()
        example_words = set(polish_text.split())
        query_set = set(query_words)
        
        if not query_set or not example_words:
            return 0.0
        
        intersection = len(query_set & example_words)
        union = len(query_set | example_words)
        
        return intersection / union if union > 0 else 0.0
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Retrieve top-k most similar examples for a query.
        
        Args:
            query: Input text (Polish)
            top_k: Number of examples to return
            
        Returns:
            List of similar examples with similarity scores
        """
        query_words = query.lower().split()
        
        # Quick filtering using index
        candidate_indices = set()
        for word in query_words:
            if word in self.index:
                candidate_indices.update(self.index[word])
        
        # Score and rank
        scored = []
        for idx in candidate_indices:
            example = self.examples[idx]
            score = self._similarity_score(query_words, example)
            scored.append({
                "example": example,
                "score": score,
                "index": idx
            })
        
        # Sort by score and return top-k
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]
    
    def retrieve_by_context(self, context_words: List[str], top_k: int = 3) -> List[Dict]:
        """
        Find examples with similar surrounding context.
        Useful for understanding translation in context.
        """
        results = []
        
        for idx, example in enumerate(self.examples):
            polish = example.get("polish", "").lower().split()
            
            # Count overlapping context words
            overlap = len(set(context_words) & set(polish))
            
            if overlap > 0:
                results.append({
                    "example": example,
                    "overlap": overlap,
                    "index": idx
                })
        
        results.sort(key=lambda x: x["overlap"], reverse=True)
        return results[:top_k]
    
    def get_example_by_translation(self, slovian_text: str) -> Optional[Dict]:
        """Find exact example by Slovian translation"""
        slovian_normalized = slovian_text.lower().strip()
        
        for example in self.examples:
            if example.get("slovian", "").lower().strip() == slovian_normalized:
                return example
        
        return None
    
    def suggest_corrections(self, input_text: str, model_output: str, 
                           user_correction: str) -> Dict:
        """
        Learn from user corrections for future improvements.
        Could feed into active learning system.
        """
        suggestion = {
            "input": input_text,
            "model_output": model_output,
            "user_correction": user_correction,
            "similar_examples": self.retrieve(input_text, top_k=3)
        }
        
        return suggestion