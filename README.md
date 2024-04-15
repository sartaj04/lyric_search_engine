# Song Search Engine

## Project Overview
This project aims to develop a robust search engine that enables users to find songs based on a variety of search filters such as lyrics, album name, artist name, and song title. The core of this system is an information retrieval platform connected to a MongoDB database, populated with a large dataset of song information gathered through web scraping and various APIs like Spotipy and LyricsGenius.

## Key Features
- **Advanced Search Capabilities**: Users can search by lyrics, artist names, song titles, or album names.
- **Information Retrieval System**: Implements TF-IDF, BM25, and a combined search algorithm to deliver the top 10 most relevant songs based on the user's query.
- **Recommender System**: Utilizes SVM models to provide song recommendations tailored to the user's search queries, enhancing the discovery of new music.

## Technologies Used
- **MongoDB**: For storing and retrieving song data.
- **Spotipy API**: To access Spotify's music database.
- **LyricsGenius API**: For fetching song lyrics.
- **TF-IDF, BM25**: For textual data analysis and relevance scoring.
- **SVM (Support Vector Machines)**: For building the recommender system.
- **Djabgo, HTML, CSS, Javascript**: For Web Development.

## Getting Started
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites
- Python 3.x
- MongoDB
- Libraries: spotipy, lyricsgenius, sklearn, etc.

### Installation
1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/your-repository-name.git
