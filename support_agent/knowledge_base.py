"""
Knowledge Base Management for Support Agent

This module manages the static knowledge base documents that feed into
the RAG system. It loads, organizes, and provides access to category-specific
support documentation for accurate response generation.

The knowledge base includes:
- Billing policies and procedures
- Technical troubleshooting guides
- Security guidelines and protocols
- General FAQ and help documentation
"""

import json
import os
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class KnowledgeBase:
    """
    Knowledge base manager for support documentation.
    
    This class loads and organizes support documents by category,
    making them available for RAG retrieval and response generation.
    """
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize the knowledge base with document loading.
        
        Args:
            data_dir: Directory containing knowledge base files
        """
        self.data_dir = data_dir
        self.documents = {}
        
        # Load all category documents
        self._load_documents()
    
    def _load_documents(self):
        """
        Load all knowledge base documents from JSON files.
        
        Expects files named: {category}_docs.json in the data directory.
        Each file should contain a list of documents with 'content' and metadata.
        """
        categories = ['billing', 'technical', 'security', 'general']
        
        for category in categories:
            try:
                filename = f"{category}_docs.json"
                filepath = os.path.join(self.data_dir, filename)
                
                if os.path.exists(filepath):
                    with open(filepath, 'r', encoding='utf-8') as f:
                        docs = json.load(f)
                    
                    # Validate document structure
                    validated_docs = []
                    for doc in docs:
                        if isinstance(doc, dict) and 'content' in doc:
                            # Ensure all required fields
                            validated_doc = {
                                'content': doc['content'],
                                'source': doc.get('source', f'{category}_doc'),
                                'category': category.title(),
                                'tags': doc.get('tags', []),
                                'priority': doc.get('priority', 'normal')
                            }
                            validated_docs.append(validated_doc)
                    
                    self.documents[category.title()] = validated_docs
                    logger.info(f"Loaded {len(validated_docs)} documents for {category}")
                    
                else:
                    logger.warning(f"Knowledge base file not found: {filepath}")
                    self.documents[category.title()] = []
                    
            except Exception as e:
                logger.error(f"Error loading {category} documents: {str(e)}")
                self.documents[category.title()] = []
    
    def get_category_documents(self, category: str) -> List[Dict[str, Any]]:
        """
        Get all documents for a specific category.
        
        Args:
            category: Category name (Billing, Technical, Security, General)
            
        Returns:
            List of document dictionaries for the category
        """
        return self.documents.get(category, [])
    
    def get_all_documents(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get all documents organized by category.
        
        Returns:
            Dictionary mapping category names to document lists
        """
        return self.documents.copy()
    
    def search_documents(self, query: str, category: str = None) -> List[Dict[str, Any]]:
        """
        Simple text search across documents.
        
        This provides basic keyword search functionality as a fallback
        when vector search is not available or for debugging purposes.
        
        Args:
            query: Search query string
            category: Optional category to limit search to
            
        Returns:
            List of documents containing the query terms
        """
        query_lower = query.lower()
        results = []
        
        # Determine which categories to search
        categories_to_search = [category] if category else self.documents.keys()
        
        for cat in categories_to_search:
            if cat in self.documents:
                for doc in self.documents[cat]:
                    # Simple text matching
                    if query_lower in doc['content'].lower():
                        # Add relevance score based on match frequency
                        content_lower = doc['content'].lower()
                        match_count = content_lower.count(query_lower)
                        
                        result_doc = doc.copy()
                        result_doc['text_relevance'] = match_count
                        results.append(result_doc)
        
        # Sort by relevance (match frequency)
        results.sort(key=lambda x: x.get('text_relevance', 0), reverse=True)
        
        return results
    
    def get_stats(self) -> Dict[str, int]:
        """Get statistics about loaded documents."""
        return {category: len(docs) for category, docs in self.documents.items()}
    
    def get_document_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the knowledge base.
        
        Returns:
            Dictionary containing knowledge base statistics
        """
        stats = {
            'total_documents': 0,
            'categories': {},
            'total_content_length': 0
        }
        
        for category, docs in self.documents.items():
            doc_count = len(docs)
            content_length = sum(len(doc['content']) for doc in docs)
            
            stats['categories'][category] = {
                'document_count': doc_count,
                'total_content_length': content_length,
                'average_document_length': content_length // max(doc_count, 1)
            }
            
            stats['total_documents'] += doc_count
            stats['total_content_length'] += content_length
        
        return stats
    
    def add_document(self, category: str, content: str, source: str = "manual", **metadata) -> bool:
        """
        Add a new document to the knowledge base.
        
        Args:
            category: Category to add document to
            content: Document content
            source: Source identifier
            **metadata: Additional metadata fields
            
        Returns:
            True if document was added successfully
        """
        try:
            if category not in self.documents:
                self.documents[category] = []
            
            new_doc = {
                'content': content,
                'source': source,
                'category': category,
                'tags': metadata.get('tags', []),
                'priority': metadata.get('priority', 'normal')
            }
            
            # Add any additional metadata
            for key, value in metadata.items():
                if key not in new_doc:
                    new_doc[key] = value
            
            self.documents[category].append(new_doc)
            logger.info(f"Added document to {category} category")
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding document: {str(e)}")
            return False
    
    def save_documents(self):
        """
        Save all documents back to JSON files.
        
        This allows persistence of dynamically added documents.
        """
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            
            for category, docs in self.documents.items():
                filename = f"{category.lower()}_docs.json"
                filepath = os.path.join(self.data_dir, filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(docs, f, indent=2, ensure_ascii=False)
                
                logger.info(f"Saved {len(docs)} documents to {filepath}")
                
        except Exception as e:
            logger.error(f"Error saving documents: {str(e)}")
    
    def reload_documents(self):
        """
        Reload all documents from files.
        
        Useful for picking up external changes to the knowledge base.
        """
        logger.info("Reloading knowledge base documents...")
        self.documents.clear()
        self._load_documents()
        logger.info("Knowledge base reloaded")

# Example documents for testing and development
def get_sample_documents() -> Dict[str, List[Dict[str, Any]]]:
    """
    Get sample documents for testing when actual knowledge base is not available.
    
    Returns:
        Dictionary of sample documents by category
    """
    return {
        'Billing': [
            {
                'content': 'For billing inquiries, please review your account statement. Refunds are processed within 5-7 business days after approval.',
                'source': 'billing_policy.md',
                'category': 'Billing',
                'tags': ['refund', 'billing', 'policy'],
                'priority': 'high'
            },
            {
                'content': 'Subscription charges occur on the same date each month. You can view your billing history in the account settings.',
                'source': 'subscription_info.md',
                'category': 'Billing',
                'tags': ['subscription', 'charges', 'history'],
                'priority': 'normal'
            }
        ],
        'Technical': [
            {
                'content': 'If you experience login issues, first clear your browser cache and cookies. Try using an incognito/private window.',
                'source': 'login_troubleshooting.md',
                'category': 'Technical',
                'tags': ['login', 'troubleshooting', 'browser'],
                'priority': 'high'
            },
            {
                'content': 'Mobile app crashes can often be resolved by updating to the latest version from your device app store.',
                'source': 'mobile_troubleshooting.md',
                'category': 'Technical',
                'tags': ['mobile', 'crash', 'update'],
                'priority': 'normal'
            }
        ],
        'Security': [
            {
                'content': 'If you suspect unauthorized access to your account, immediately change your password and enable two-factor authentication.',
                'source': 'security_guidelines.md',
                'category': 'Security',
                'tags': ['security', 'password', '2fa'],
                'priority': 'critical'
            },
            {
                'content': 'Never share your login credentials with anyone. Our support team will never ask for your password.',
                'source': 'security_best_practices.md',
                'category': 'Security',
                'tags': ['credentials', 'best_practices'],
                'priority': 'high'
            }
        ],
        'General': [
            {
                'content': 'You can update your profile information in the account settings section. Changes take effect immediately.',
                'source': 'account_management.md',
                'category': 'General',
                'tags': ['profile', 'settings', 'account'],
                'priority': 'normal'
            },
            {
                'content': 'For urgent issues, please contact our priority support line available 24/7 for premium customers.',
                'source': 'support_info.md',
                'category': 'General',
                'tags': ['urgent', 'priority', 'contact'],
                'priority': 'normal'
            }
        ]
    }
