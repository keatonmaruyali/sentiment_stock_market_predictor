from nltk.sentiment.vader import SentimentIntensityAnalyzer

class VaderSentimentService:
    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()
    
    def __call__(self, text: str):
        return self.vader.polarity_scores(text)['compound']
