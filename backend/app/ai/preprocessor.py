
import re
import string

class TextPreprocessor:
    """
    Handles text cleaning and normalization for the AI pipeline.
    """
    
    def __init__(self):
        # We could load NLTK stopwords here if needed, but keeping it lightweight for now
        self.stopwords = {
            "a", "an", "the", "and", "but", "or", "if", "because", "as", "what",
            "which", "this", "that", "these", "those", "then", "just", "so", "than",
            "such", "both", "through", "about", "for", "is", "of", "while", "during",
            "to", "from", "in", "out", "on", "off", "over", "under", "again", "further",
            "once", "here", "there", "when", "where", "why", "how", "all", "any", "both",
            "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not",
            "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will",
            "just", "don", "should", "now"
        }

    def clean_text(self, text: str) -> str:
        """
        Cleans and normalizes input text.
        """
        if not text:
            return ""
            
        # Lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'https?://\S+|www\.\S+', '', text)
        
        # Remove HTML tags
        text = re.sub(r'<.*?>', '', text)
        
        # Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))
        
        # Remove numbers (optional, but often good for clustering topics)
        # text = re.sub(r'\d+', '', text)
        
        # Remove extra whitespaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    def remove_stopwords(self, text: str) -> str:
        """
        Removes common stopwords from the text.
        """
        words = text.split()
        filtered_words = [word for word in words if word not in self.stopwords]
        return " ".join(filtered_words)

    def preprocess(self, text: str) -> str:
        """
        Full preprocessing pipeline.
        """
        text = self.clean_text(text)
        text = self.remove_stopwords(text)
        return text

preprocessor = TextPreprocessor()
