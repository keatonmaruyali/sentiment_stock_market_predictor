def calc_sentiment_change(intervaled_sentiment):
    sentiment_change = [
        intervaled_sentiment[i] - intervaled_sentiment[(i-1)]
        for i in range(1, len(intervaled_sentiment))
    ]
    sentiment_change.insert(0, 0)
    return sentiment_change
