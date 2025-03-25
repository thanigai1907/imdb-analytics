import streamlit as st
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Database connection
connection = mysql.connector.connect(
    host="gateway01.us-west-2.prod.aws.tidbcloud.com",
    port=4000,
    user="P4iQSrjmBT5xcHr.root",
    password="g9nGrYZlFi6tEsWt",
    database="imdb",
    ssl_ca=r"C:\Users\velut\Downloads\isrgrootx1 (1).pem",  
    ssl_verify_cert=True,
    ssl_verify_identity=True
)

# Custom Header
st.markdown(
    """
    <h1 style="text-align: center; color: #4CAF50; font-size: 50px;">
        IMDb Analytics Dashboard
    </h1>
    <p style="text-align: center; color: #808080; font-size: 20px;">
        Explore and visualize IMDb movie data with ease!
    </p>
    """,
    unsafe_allow_html=True
)

# Streamlit Sidebar for Navigation
choice = st.sidebar.selectbox("Navigation", ["Home", "Visualization", "Filtering Functions"])

# Home Section
if choice == "Home":
    st.title("Welcome to the IMDb Analytics App!")
    st.write("Navigate using the sidebar to explore filtering and visualization options.")

    # Animated Metrics
    cursor = connection.cursor(buffered=True)
    query = "SELECT COUNT(*) AS TotalMovies, AVG(Rating) AS AvgRating, MAX(Votes) AS MaxVotes FROM imdb.movies;"
    cursor.execute(query)
    result = cursor.fetchone()
    st.metric(label="Total Movies", value=result[0])
    st.metric(label="Average Rating", value=round(result[1], 2))
    st.metric(label="Highest Votes", value=result[2])
    cursor.close()

# Filtering Section
elif choice == "Filtering Functions":
    st.title("Filter IMDb Movies")

    cursor = connection.cursor(buffered=True)

    # Fetch movie data
    query = "SELECT * FROM imdb.movies;"
    cursor.execute(query)
    all_movies = cursor.fetchall()

    # Convert to DataFrame
    df = pd.DataFrame(all_movies, columns=["Title", "Duration (mins)", "Rating", "Votes", "Genre"])

    # Filter by Duration
    st.subheader("Filter by Duration")
    duration_filter = st.radio("Select Duration Range:", ["< 120 mins", "120-180 mins", "> 180 mins"])
    if duration_filter == "< 120 mins":
        filtered_df = df[df["Duration (mins)"] < 120]
    elif duration_filter == "120-180 mins":
        filtered_df = df[(df["Duration (mins)"] >= 120) & (df["Duration (mins)"] <= 180)]
    else:
        filtered_df = df[df["Duration (mins)"] > 180]
    st.dataframe(filtered_df)

    # Filter by Genre
    st.subheader("Filter by Genre")
    genre_filter = st.selectbox("Select a Genre:", df["Genre"].unique())
    filtered_df = df[df["Genre"] == genre_filter]
    st.dataframe(filtered_df)

    # Filter by IMDb Rating
    st.subheader("Filter by IMDb Rating")
    filter_type = st.radio("Choose Filter Type:", [">", "<", "="])
    rating_threshold = st.slider("Select IMDb Rating Threshold:", 1.0, 10.0, 8.0, step=0.1)
    query = f"SELECT * FROM imdb.movies WHERE Rating {filter_type} %s;"
    cursor.execute(query, (rating_threshold,))
    rating_filtered_movies = cursor.fetchall()
    df_rating_filtered = pd.DataFrame(rating_filtered_movies, columns=["Title", "Duration (mins)", "Rating", "Votes", "Genre"])
    st.dataframe(df_rating_filtered)

    cursor.close()

# Visualization Section
elif choice == "Visualization":
    st.title("Movie Data Visualizations")

    cursor = connection.cursor(buffered=True)

    query = "SELECT * FROM imdb.movies;"
    cursor.execute(query)
    all_movies = cursor.fetchall()
    df = pd.DataFrame(all_movies, columns=["Title", "Duration (mins)", "Rating", "Votes", "Genre"])

    # Genre Distribution
    st.subheader("Genre Distribution")
    genre_counts = df["Genre"].value_counts()
    st.bar_chart(genre_counts)

    # Rating Distribution
    st.subheader("Rating Distribution")
    fig, ax = plt.subplots()
    sns.histplot(df["Rating"], bins=10, kde=True, ax=ax)
    ax.set_xlabel("Rating")
    ax.set_ylabel("Number of Movies")
    st.pyplot(fig)

    # Average Votes by Genre
    st.subheader("Average Votes by Genre")
    avg_votes_per_genre = df.groupby("Genre")["Votes"].mean()
    st.bar_chart(avg_votes_per_genre)

      # Pie Chart for Genre Distribution
    st.subheader("Pie Chart of Genre Distribution")
    fig, ax = plt.subplots()
    ax.pie(genre_counts, labels=genre_counts.index, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures the pie chart is circular.
    st.pyplot(fig)

    cursor.close()

# Close the database connection at the end
connection.close()