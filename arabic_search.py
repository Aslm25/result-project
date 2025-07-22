import pandas as pd
import re
from typing import List, Dict, Any
import logging
from difflib import SequenceMatcher

class ArabicSearchEngine:
    """Search engine for Arabic text with fuzzy matching capabilities"""
    
    def __init__(self, data: pd.DataFrame, columns: List[str]):
        self.data = data
        self.columns = columns
        self.name_column = None
        self.id_column = None
        
        # Try to identify name and ID columns
        self._identify_columns()
        
        # Create search indices for better performance
        self._create_indices()
    
    def _identify_columns(self):
        """Identify which columns contain names and IDs"""
        for col in self.columns:
            col_str = str(col).strip().lower()
            
            # Look for name column
            if any(keyword in col_str for keyword in ['اسم', 'name']) and not self.name_column:
                self.name_column = col
                logging.info(f"Identified name column: {col}")
            
            # Look for ID column
            if any(keyword in col_str for keyword in ['رقم', 'جلوس', 'id', 'number']) and not self.id_column:
                self.id_column = col
                logging.info(f"Identified ID column: {col}")
        
        # Fallback: if not found, use first few columns
        if not self.name_column and len(self.columns) > 0:
            # Look for column with most Arabic text
            for col in self.columns:
                sample = self.data[col].dropna().head(10)
                arabic_count = sum(1 for val in sample if self._contains_arabic(str(val)))
                if arabic_count > 5:  # At least 5 Arabic entries in sample
                    self.name_column = col
                    logging.info(f"Fallback name column: {col}")
                    break
        
        if not self.id_column and len(self.columns) > 1:
            # Look for numeric column
            for col in self.columns:
                if col != self.name_column:
                    sample = self.data[col].dropna().head(10)
                    numeric_count = 0
                    for val in sample:
                        try:
                            float(val)
                            numeric_count += 1
                        except:
                            pass
                    if numeric_count > 7:  # Most values are numeric
                        self.id_column = col
                        logging.info(f"Fallback ID column: {col}")
                        break
    
    def _create_indices(self):
        """Create search indices for better performance"""
        self.name_index = {}
        self.id_index = {}
        
        logging.info(f"Creating indices for {len(self.data)} records...")
        
        if self.name_column:
            # Create normalized name index with progress logging
            logging.info(f"Indexing name column: {self.name_column}")
            for idx in range(len(self.data)):
                if idx % 10000 == 0 and idx > 0:
                    logging.info(f"Processed {idx} names...")
                
                try:
                    name = str(self.data.iloc[idx][self.name_column])
                    normalized_name = self._normalize_for_search(name)
                    if normalized_name:
                        if normalized_name not in self.name_index:
                            self.name_index[normalized_name] = []
                        self.name_index[normalized_name].append(idx)
                except Exception as e:
                    logging.warning(f"Error processing name at index {idx}: {e}")
                    continue
        
        if self.id_column:
            # Create ID index with progress logging
            logging.info(f"Indexing ID column: {self.id_column}")
            for idx in range(len(self.data)):
                if idx % 10000 == 0 and idx > 0:
                    logging.info(f"Processed {idx} IDs...")
                
                try:
                    id_val = str(self.data.iloc[idx][self.id_column]).strip()
                    if id_val and id_val != 'nan' and id_val != '':
                        if id_val not in self.id_index:
                            self.id_index[id_val] = []
                        self.id_index[id_val].append(idx)
                except Exception as e:
                    logging.warning(f"Error processing ID at index {idx}: {e}")
                    continue
        
        logging.info(f"Indexing complete. Names: {len(self.name_index)}, IDs: {len(self.id_index)}")
    
    def _contains_arabic(self, text: str) -> bool:
        """Check if text contains Arabic characters"""
        if not isinstance(text, str):
            return False
        arabic_pattern = r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]'
        return bool(re.search(arabic_pattern, text))
    
    def _normalize_for_search(self, text: str) -> str:
        """Normalize Arabic text for search"""
        if pd.isna(text) or not isinstance(text, str):
            return ""
        
        # Remove diacritics
        text = re.sub(r'[\u064B-\u0652]', '', text)
        
        # Normalize Arabic letters
        text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
        text = text.replace('ة', 'ه')
        text = text.replace('ي', 'ى').replace('ئ', 'ى').replace('ؤ', 'و')
        
        # Remove extra spaces and convert to lowercase
        text = re.sub(r'\s+', ' ', text).strip().lower()
        
        return text
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two Arabic texts"""
        if not text1 or not text2:
            return 0.0
        
        # Normalize both texts
        norm1 = self._normalize_for_search(text1)
        norm2 = self._normalize_for_search(text2)
        
        # Check for exact match first
        if norm1 == norm2:
            return 1.0
        
        # Check if one contains the other
        if norm1 in norm2 or norm2 in norm1:
            return 0.8
        
        # Use sequence matcher for similarity
        similarity = SequenceMatcher(None, norm1, norm2).ratio()
        
        # Boost similarity for partial word matches
        words1 = set(norm1.split())
        words2 = set(norm2.split())
        
        if words1.intersection(words2):
            similarity = max(similarity, 0.6)
        
        return similarity
    
    def _calculate_compound_similarity(self, query_words: List[str], target_name: str) -> float:
        """Calculate similarity for compound names with flexible word matching"""
        if not query_words or not target_name:
            return 0.0
        
        target_words = target_name.split()
        
        # Check for exact match first
        if ' '.join(query_words) == target_name:
            return 1.0
        
        # Check if all query words exist in target (any order)
        query_words_set = set(query_words)
        target_words_set = set(target_words)
        
        # Calculate word overlap
        common_words = query_words_set.intersection(target_words_set)
        
        if not common_words:
            # No word overlap, use regular similarity
            return self._calculate_similarity(' '.join(query_words), target_name)
        
        # Perfect word match (all query words found)
        if len(common_words) == len(query_words):
            return 0.95
        
        # Partial word match - boost based on how many words match
        word_match_ratio = len(common_words) / len(query_words)
        base_similarity = self._calculate_similarity(' '.join(query_words), target_name)
        
        # Give higher score for partial word matches
        compound_similarity = max(base_similarity, word_match_ratio * 0.8)
        
        # Check for partial word matches (one word contains another)
        for query_word in query_words:
            for target_word in target_words:
                if len(query_word) >= 3 and len(target_word) >= 3:
                    if query_word in target_word or target_word in query_word:
                        compound_similarity = max(compound_similarity, 0.6)
        
        return compound_similarity
    
    def search_by_id(self, query: str) -> List[Dict[str, Any]]:
        """Search by ID number (رقم الجلوس)"""
        results = []
        
        if not self.id_column:
            logging.warning("No ID column identified")
            return results
        
        query = query.strip()
        
        # Try exact match first
        if query in self.id_index:
            for idx in self.id_index[query]:
                row = self.data.iloc[idx].to_dict()
                row['_match_type'] = 'exact'
                row['_similarity'] = 1.0
                results.append(row)
        
        # If no exact match, try partial matches
        if not results:
            for id_val in self.id_index:
                if query in id_val or id_val in query:
                    for idx in self.id_index[id_val]:
                        row = self.data.iloc[idx].to_dict()
                        row['_match_type'] = 'partial'
                        row['_similarity'] = 0.8
                        results.append(row)
        
        return results[:100]  # Limit results
    
    def search_by_name(self, query: str) -> List[Dict[str, Any]]:
        """Search by name (الاسم) with flexible compound name matching"""
        results = []
        
        if not self.name_column:
            logging.warning("No name column identified")
            return results
        
        normalized_query = self._normalize_for_search(query)
        
        if not normalized_query:
            return results
        
        # Split query into words for compound name matching
        query_words = normalized_query.split()
        
        # Collect all potential matches with similarity scores
        candidates = []
        
        # Search through the name index
        for name in self.name_index:
            similarity = self._calculate_compound_similarity(query_words, name)
            
            if similarity >= 0.3:  # Lower threshold for compound matching
                for idx in self.name_index[name]:
                    candidates.append((idx, similarity, name))
        
        # Sort by similarity (descending)
        candidates.sort(key=lambda x: x[1], reverse=True)
        
        # Convert to result format
        for idx, similarity, matched_name in candidates[:100]:  # Limit to 100 results
            row = self.data.iloc[idx].to_dict()
            row['_match_type'] = 'fuzzy' if similarity < 1.0 else 'exact'
            row['_similarity'] = similarity
            row['_matched_name'] = matched_name
            results.append(row)
        
        return results
    
    def get_column_info(self) -> Dict[str, Any]:
        """Get information about detected columns"""
        return {
            'name_column': self.name_column,
            'id_column': self.id_column,
            'total_columns': len(self.columns),
            'all_columns': self.columns
        }
