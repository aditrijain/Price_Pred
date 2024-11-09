# Dataset:
The following datasets were given to us; they contain prices and tweet data for 40 coins with periods of missing data in between.</br>
`public_dataset` folder: [pub](https://drive.google.com/drive/folders/1D8P_FbvU3pNVz6IGnWXXEAdn7FQGFnbk?usp=drive_link)</br>
`test_price_data`: [test](https://drive.google.com/drive/folders/12KBPtgpdEQreae4hCTbD77ko3vHYY3HC?usp=drive_link)</br>
`train_price_data`: [train](https://drive.google.com/drive/folders/19UTES3MGs9gIzDtTzJ8t1L0l3AlwmU9T?usp=drive_link)</br>
The problem statement was to make use of multimodal AI models to fill in those missing values of closing prices.</br>
# Approach:
The files `extract_tweet_data.py` and `tweetdbreset.py` process the sentiment data from the tweets given in `public_dataset` and adds the processed sentiment and tweet values to create the `test_price_data` and the `train_price_data` files.</br>
The processed data is then trained on using ensemble learning with Linear Regression, Random Forest, and XGBoost. The trained models are then sequentially run to generate the missing values over the timeframe for each of the 40 coins.</br>
