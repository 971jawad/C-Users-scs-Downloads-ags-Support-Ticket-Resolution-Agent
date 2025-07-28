"""
RAG (Retrieval-Augmented Generation) System for Support Agent

This module implements a lightweight retrieval system using TF-IDF vectorization
with category-specific document collections. It provides context-aware document 
retrieval to ground the support agent responses in factual information.

Key features:
- Category-specific TF-IDF vectorizers for better retrieval accuracy
- Cosine similarity scoring for document relevance
- Dynamic query enhancement with ticket context
- Production-ready error handling and logging
"""

import os
import json
import logging
import numpy as np
from typing import List, Dict, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from support_agent.knowledge_base import KnowledgeBase
from support_agent.state import ContextDocument

logger = logging.getLogger(__name__)

class RAGSystem:
    """
    Lightweight RAG system using TF-IDF vectorization for document retrieval.
    
    This class manages category-specific document collections and provides
    semantic search using cosine similarity on TF-IDF vectors.
    """
    
    def __init__(self):
        """
        Initialize the RAG system with TF-IDF vectorization.
        """
        self.knowledge_base = KnowledgeBase()
        
        # Category-specific vectorizers and document stores
        self.vectorizers = {}
        self.document_stores = {}
        self.document_vectors = {}
        
        # Initialize all category indexes
        self._initialize_indexes()
    
    def _initialize_indexes(self):
        """
        Initialize TF-IDF vectorizers for all supported categories.
        
        Creates separate document collections and vectorizers for each 
        ticket category to improve retrieval accuracy.
        """
        categories = ['Billing', 'Technical', 'Security', 'General']
        
        for category in categories:
            try:
                logger.info(f"Initializing TF-IDF vectorizer for category: {category}")
                
                # Load category documents
                documents = self.knowledge_base.get_category_documents(category)
                
                if not documents:
                    logger.warning(f"No documents found for category: {category}")
                    # Create empty stores for consistency
                    self.vectorizers[category] = TfidfVectorizer(
                        stop_words='english',
                        max_features=1000,
                        ngram_range=(1, 2)
                    )
                    self.document_stores[category] = []
                    self.document_vectors[category] = None
                    continue
                
                # Extract document texts
                texts = [doc['content'] for doc in documents]
                logger.info(f"Processing {len(texts)} documents for {category}...")
                
                # Create and fit TF-IDF vectorizer
                vectorizer = TfidfVectorizer(
                    stop_words='english',
                    max_features=1000,
                    ngram_range=(1, 2),
                    lowercase=True
                )
                
                # Fit vectorizer and transform documents
                document_vectors = vectorizer.fit_transform(texts)
                
                # Store vectorizer, documents, and vectors
                self.vectorizers[category] = vectorizer
                self.document_stores[category] = documents
                self.document_vectors[category] = document_vectors
                
                logger.info(f"TF-IDF vectorizer created for {category}: {len(documents)} documents")
                
            except Exception as e:
                logger.error(f"Failed to initialize vectorizer for {category}: {str(e)}")
                # Create empty stores as fallback
                self.vectorizers[category] = TfidfVectorizer(
                    stop_words='english',
                    max_features=1000,
                    ngram_range=(1, 2)
                )
                self.document_stores[category] = []
                self.document_vectors[category] = None
    
    async def retrieve_context(
        self, 
        query: str, 
        category: str, 
        top_k: int = 3,
        include_related: bool = False,
        min_relevance: float = 0.1
    ) -> List[ContextDocument]:
        """
        Retrieve relevant context documents for a query.
        
        This method performs semantic search across category-specific
        document collections to find the most relevant information
        for response generation.
        
        Args:
            query: Search query (usually ticket subject + description)
            category: Primary category to search in
            top_k: Number of documents to retrieve
            include_related: Whether to search related categories too
            min_relevance: Minimum relevance score threshold
            
        Returns:
            List of context documents with relevance scores
        """
        try:
            logger.info(f"Retrieving context for category: {category}, query: {query[:100]}...")
            
            all_results = []
            
            # Primary category search
            if category in self.vectorizers and self.document_vectors[category] is not None:
                results = self._search_category(query, category, top_k, min_relevance)
                all_results.extend(results)
            else:
                logger.warning(f"Unknown category or no documents: {category}, searching General")
                if 'General' in self.vectorizers and self.document_vectors['General'] is not None:
                    results = self._search_category(query, 'General', top_k, min_relevance)
                    all_results.extend(results)
            
            # Include related categories if requested and primary search is weak
            if include_related and len(all_results) < top_k:
                related_categories = self._get_related_categories(category)
                remaining_k = top_k - len(all_results)
                
                for related_cat in related_categories:
                    if (related_cat in self.vectorizers and 
                        self.document_vectors[related_cat] is not None):
                        related_results = self._search_category(
                            query, related_cat, remaining_k, min_relevance
                        )
                        all_results.extend(related_results)
                        
                        if len(all_results) >= top_k:
                            break
            
            # Sort by relevance and limit results
            all_results.sort(key=lambda x: x['relevance_score'], reverse=True)
            final_results = all_results[:top_k]
            
            logger.info(f"Retrieved {len(final_results)} context documents")
            
            return final_results
            
        except Exception as e:
            logger.error(f"Error in context retrieval: {str(e)}")
            return []
    
    def _search_category(
        self, 
        query: str, 
        category: str, 
        top_k: int,
        min_relevance: float
    ) -> List[ContextDocument]:
        """
        Search within a specific category using TF-IDF similarity.
        
        Args:
            query: Search query
            category: Category to search in
            top_k: Number of results to return
            min_relevance: Minimum relevance threshold
            
        Returns:
            List of context documents with relevance scores
        """
        try:
            vectorizer = self.vectorizers[category]
            document_vectors = self.document_vectors[category]
            documents = self.document_stores[category]
            
            if document_vectors is None or len(documents) == 0:
                return []
            
            # Transform query using the same vectorizer
            query_vector = vectorizer.transform([query])
            
            # Calculate cosine similarity
            similarities = cosine_similarity(query_vector, document_vectors).flatten()
            
            # Get top-k results above threshold
            results = []
            for idx, similarity in enumerate(similarities):
                if similarity >= min_relevance:
                    doc = documents[idx]
                    context_doc = ContextDocument(
                        content=doc['content'],
                        source=doc.get('source', f"{category}_doc_{idx}"),
                        relevance_score=float(similarity),
                        category=category
                    )
                    results.append(context_doc)
            
            # Sort by similarity and take top-k
            results.sort(key=lambda x: x['relevance_score'], reverse=True)
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"Error searching category {category}: {str(e)}")
            return []
    
    def _get_related_categories(self, primary_category: str) -> List[str]:
        """
        Get related categories for cross-category search.
        
        This provides fallback categories when primary search yields
        insufficient results.
        
        Args:
            primary_category: The primary ticket category
            
        Returns:
            List of related category names
        """
        category_relations = {
            'Billing': ['General'],
            'Technical': ['General', 'Security'],
            'Security': ['Technical', 'General'],
            'General': ['Billing', 'Technical', 'Security']
        }
        
        return category_relations.get(primary_category, ['General'])
    
    def enhance_query(self, subject: str, description: str) -> str:
        """
        Enhance the search query by combining and processing ticket information.
        
        This method optimizes the search query for better retrieval by
        combining subject and description with appropriate weighting.
        
        Args:
            subject: Ticket subject line
            description: Detailed ticket description
            
        Returns:
            Enhanced search query string
        """
        # Combine subject and description with emphasis on subject
        enhanced = f"{subject} {subject} {description}"
        
        # Basic preprocessing
        enhanced = enhanced.lower().strip()
        
        return enhanced
    
    def get_category_stats(self) -> Dict[str, int]:
        """
        Get statistics about document counts per category.
        
        Returns:
            Dictionary mapping category names to document counts
        """
        stats = {}
        for category, documents in self.document_stores.items():
            stats[category] = len(documents)
        return stats