from flask import Flask, render_template, request, url_for
import pandas as pd
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

# Load the dataset
df = pd.read_csv("netflix_titles.csv")

# Ensure the 'release_year' column is numeric and drop NaN values
df['release_year'] = pd.to_numeric(df['release_year'], errors='coerce')
df = df.dropna(subset=['release_year'])
df['release_year'] = df['release_year'].astype(int)

# Ensure static directory exists
if not os.path.exists("static"):
    os.makedirs("static")

# Function to clear old images before regenerating
def clear_old_graphs():
    for file in os.listdir("static"):
        if file.endswith(".png"):
            os.remove(os.path.join("static", file))

# Function to generate and save the graphs
def generate_graphs():
    clear_old_graphs()  # Clear old images first

    # Top 10 Genres
    genre_counts = df['listed_in'].str.split(', ').explode().value_counts().head(10)
    plt.figure(figsize=(10, 5))
    genre_counts.plot(kind='bar', color='skyblue')
    plt.title("Top 10 Genres")
    plt.xlabel("Genre")
    plt.ylabel("Count")
    plt.xticks(rotation=45)
    plt.savefig("static/genres.png")
    plt.close()
    
    # Content Ratings
    rating_counts = df['rating'].value_counts()
    plt.figure(figsize=(10, 5))
    rating_counts.plot(kind='bar', color='salmon')
    plt.title("Content Ratings")
    plt.xlabel("Rating")
    plt.ylabel("Count")
    plt.xticks(rotation=45)
    plt.savefig("static/ratings.png")
    plt.close()
    
    # Trend Over the Years
    year_counts = df['release_year'].value_counts().sort_index()
    plt.figure(figsize=(10, 5))
    year_counts.plot(kind='line', marker='o', color='green')
    plt.title("Trend Over the Years")
    plt.xlabel("Year")
    plt.ylabel("Number of Releases")
    plt.savefig("static/trend.png")
    plt.close()

generate_graphs()

@app.route('/')
def index():
    genres = sorted(set(df['listed_in'].str.split(', ').explode().dropna()))
    selected_genre = request.args.get('genre')

    filtered_trend = None  # Default value
    if selected_genre and selected_genre in genres:
        filtered_df = df[df['listed_in'].str.contains(selected_genre, na=False)]
        year_counts = filtered_df['release_year'].value_counts().sort_index()
        
        plt.figure(figsize=(10, 5))
        year_counts.plot(kind='line', marker='o', color='blue')
        plt.title(f"Trend for {selected_genre}")
        plt.xlabel("Year")
        plt.ylabel("Number of Releases")
        plt.savefig("static/filtered_trend.png")
        plt.close()

        filtered_trend = "static/filtered_trend.png"

    return render_template("index.html", genres=genres, selected_genre=selected_genre, filtered_trend=filtered_trend)

@app.route('/genres_list')
def top_genres():
    top_genres = df['listed_in'].str.split(', ').explode().value_counts().head(10).to_dict()
    return render_template("genres.html", top_genres=top_genres)

@app.route('/ratings_list')
def content_ratings():
    rating_counts = df['rating'].value_counts().to_dict()
    return render_template("ratings.html", ratings=rating_counts)

@app.route('/trend_list')
def trend_years():
    year_counts = df['release_year'].value_counts().sort_index().to_dict()
    return render_template("trends.html", year_counts=year_counts)

if __name__ == '__main__':
    app.run(debug=True)
