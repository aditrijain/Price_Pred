import os
import glob
import pandas as pd
import ast  # For safely evaluating string representations of lists
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Sentiment Analyzer
analyzer = SentimentIntensityAnalyzer()

# Function to convert 'K' and 'M' to numerical values
def convert_to_numeric(value):
    if pd.isna(value):
        return 0.0
    elif isinstance(value, str):
        if 'K' in value:
            return float(value.replace('K', '').replace(',', '').strip()) * 1000
        elif 'M' in value:
            return float(value.replace('M', '').replace(',', '').strip()) * 1000000
        else:
            return float(value.replace(',', '').strip())
    return value

# Function to process each tweet and extract sentiment + other useful features
def process_tweet_data(tweet_df):
    # Sentiment analysis
    tweet_df['sentiment'] = tweet_df['tweet'].apply(lambda x: analyzer.polarity_scores(str(x))['compound'])

    # Parse hashtags and cashtags from string representations
    tweet_df['hashtags'] = tweet_df['hashtags'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) and x else [])
    tweet_df['cashtags'] = tweet_df['cashtags'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) and x else [])

    # Feature: Number of hashtags
    tweet_df['num_hashtags'] = tweet_df['hashtags'].apply(len)

    # Feature: Number of mentions
    tweet_df['num_mentions'] = tweet_df['mentions'].apply(lambda x: len(ast.literal_eval(x)) if isinstance(x, str) and x else 0)

    # Feature: Number of cashtags
    tweet_df['num_cashtags'] = tweet_df['cashtags'].apply(len)

    # Feature: Total engagement (replies + retweets + likes)
    tweet_df['total_engagement'] = tweet_df['replies_count'].apply(convert_to_numeric) + tweet_df['retweets_count'].apply(convert_to_numeric) + tweet_df['likes_count'].apply(convert_to_numeric)

    # Feature: Whether the tweet is a retweet
    tweet_df['is_retweet'] = tweet_df['retweet'].apply(lambda x: 1 if pd.notnull(x) else 0)

    # Feature: Presence of media (photos or videos)
    tweet_df['has_media'] = tweet_df[['photos', 'video']].apply(lambda x: 1 if pd.notnull(x['photos']) or x['video'] > 0 else 0, axis=1)

    # Group by date and aggregate features
    aggregated_features = tweet_df.groupby('datetime').agg({
        'sentiment': 'mean',
        'num_hashtags': 'sum',
        'num_mentions': 'sum',
        'num_cashtags': 'sum',
        'total_engagement': 'sum',
        'is_retweet': 'sum',
        'has_media': 'sum'
    }).reset_index()

    return aggregated_features

def process_tweet_data2(new_tweet_df):
    # Extracting features
    new_tweet_df['sentiment'] = new_tweet_df['Text'].apply(lambda x: analyzer.polarity_scores(str(x))['compound'])

    # Parse hashtags and cashtags from the text
    new_tweet_df['hashtags'] = new_tweet_df['Text'].str.findall(r'#\w+').apply(list)  # Extract hashtags from the Text
    new_tweet_df['cashtags'] = new_tweet_df['Text'].str.findall(r'\$\w+').apply(list)  # Extract cashtags from the Text

    # Feature: Number of hashtags
    new_tweet_df['num_hashtags'] = new_tweet_df['hashtags'].apply(len)

    # Feature: Number of mentions (no mentions column in the new df, assumed to be 0)
    new_tweet_df['num_mentions'] = 0  # Set to 0 as there is no mentions data

    # Feature: Number of cashtags
    new_tweet_df['num_cashtags'] = new_tweet_df['cashtags'].apply(len)

    # Feature: Total engagement (comments + retweets + likes)
    new_tweet_df['total_engagement'] = new_tweet_df['Comments'].apply(convert_to_numeric) + new_tweet_df['Retweets'].apply(convert_to_numeric) + new_tweet_df['Likes'].apply(convert_to_numeric)


    # Feature: Whether the tweet is a retweet (assuming no retweets in the new df)
    new_tweet_df['is_retweet'] = 0  # Set to 0 as there is no retweet data

    # Feature: Presence of media (photos or videos)
    new_tweet_df['has_media'] = new_tweet_df[['Image link']].apply(lambda x: 1 if x['Image link'] else 0, axis=1)

        # Group by date and aggregate features
    aggregated_features = new_tweet_df.groupby('datetime').agg({
        'sentiment': 'mean',
        'num_hashtags': 'sum',
        'num_mentions': 'sum',
        'num_cashtags': 'sum',
        'total_engagement': 'sum',
        'is_retweet': 'sum',
        'has_media': 'sum'
    }).reset_index()

    return aggregated_features

# Function to iterate through the tweets folder structure
def process_coin_tweets(coin_folder):
    all_tweet_features = []
    
    # Iterate over all date CSVs in the coin's tweet folder
    for tweet_file in glob.glob(os.path.join(coin_folder, '*.csv')):
        # Load tweet data
        tweet_df = pd.read_csv(tweet_file)
        print(" >", tweet_file)

        if 'date' in tweet_df.columns:            
            # Convert date and created_at to datetime
            tweet_df['datetime'] = pd.to_datetime(tweet_df['date']).dt.date

            # Process the tweet data for this file (for a particular day)
            daily_tweet_features = process_tweet_data(tweet_df)
        
        else:
            # Convert date and created_at to datetime
            tweet_df['datetime'] = pd.to_datetime(os.path.basename(tweet_file)[:-4]).date()

            # Process the tweet data for this file (for a particular day)
            daily_tweet_features = process_tweet_data2(tweet_df)
        
        
        all_tweet_features.append(daily_tweet_features)

    # Combine all days' tweet features
    if all_tweet_features:
        tweet_features = pd.concat(all_tweet_features, ignore_index=True)
    else:
        tweet_features = pd.DataFrame(columns=['datetime', 'sentiment', 'num_hashtags', 'num_mentions', 'num_cashtags', 'total_engagement', 'is_retweet', 'has_media'])
    
    return tweet_features

# Function to merge the processed tweet features with the price data for a coin
def merge_with_price_data(price_data_file, tweet_features):
    # Load the price data
    price_df = pd.read_csv(price_data_file)
    price_df['datetime'] = pd.to_datetime(price_df['datetime']).dt.date  # Ensure date is in proper format

    # Merge price data with tweet features on date
    merged_df = pd.merge(price_df, tweet_features, how='left', on='datetime')
    
    # Fill missing tweet-related features with 0
    for col in ['sentiment', 'num_hashtags', 'num_mentions', 'num_cashtags', 'total_engagement', 'is_retweet', 'has_media']:
        try:
            merged_df[col] = merged_df[col].fillna(0)
        except Exception:
            print(merged_df.columns)
            print(tweet_features)
            raise
    
    return merged_df

# Main function to process tweets and update price data for all coins
def update_all_coins_data(train_folder):
    coins = [coin for coin in os.listdir(os.path.join(train_folder, "tweets"))] # if coin not in ['LEND', 'DAI', 'BNT', 'YEE', 'ZEN', 'CKB']]

    for coin in coins:
        print(f"Processing coin: {coin}")
        
        coin_tweet_folder = os.path.join(train_folder, 'tweets', coin)
        coin_price_file = os.path.join(train_folder, 'price_data', f'{coin}.csv')

        # Process tweet data for this coin
        tweet_features = process_coin_tweets(coin_tweet_folder)
        tweet_features.to_csv(coin_tweet_folder + ".csv", index=False)
        
        # Merge tweet features with price data and save the result
        merged_data = merge_with_price_data(coin_price_file, tweet_features)
        merged_data.to_csv(coin_price_file, index=False)  # Overwrite the price file with updated data

# Example usage:
train_folder = './public_dataset/train'
test_folder = './public_dataset/test'
update_all_coins_data(train_folder)
update_all_coins_data(test_folder)
