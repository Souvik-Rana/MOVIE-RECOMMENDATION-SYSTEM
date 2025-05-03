import pandas as pd

# Fix 1: Use raw string for path (r'...')
# Fix 2: Point directly to the CSV file

data = pd.read_csv(r'D:\MACHINE LEARNING PROJECTS\MOVIE RECOMMENDATION SYSTEM\top10K-TMDB-movies.csv')
print(data)
