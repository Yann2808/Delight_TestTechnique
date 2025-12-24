import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import ast


def clean_genres(df):
    # Quand on lit le CSV, les listes sont lues comme des chaines de caractères "['pop', 'rock']"
    # J'utilise ast.literal_eval pour remettre ça en vraie liste
    if isinstance(df['artist_genres'].iloc[0], str):
        df['artist_genres'] = df['artist_genres'].apply(lambda x: ast.literal_eval(x) if pd.notna(x) else [])
    return df


def graph_correlations(df):
    print("Génération du graphe de corrélations...")
    sns.set_theme(style="whitegrid")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # Artiste Pop vs Followers
    sns.scatterplot(data=df, x='artist_followers', y='artist_popularity', ax=ax1, alpha=0.5)
    ax1.set_xscale('log')  # Echelle log car les écarts sont trop grands
    ax1.set_title("Popularité Artiste vs Followers")
    ax1.set_xlabel("Followers (Log)")
    ax1.set_ylabel("Popularité Artiste")

    # Artiste Pop vs Track Pop
    sns.scatterplot(data=df, x='track_popularity', y='artist_popularity', ax=ax2, color='orange', alpha=0.5)
    ax2.set_title("Popularité Artiste vs Popularité Titre")
    ax2.set_xlabel("Popularité Titre")

    plt.tight_layout()
    plt.savefig("output/graph_correlations.png")

    # Petits calculs pour expliquer
    corr1 = df['artist_popularity'].corr(df['artist_followers'])
    corr2 = df['artist_popularity'].corr(df['track_popularity'])

    print(f"Corrélation Followers/Pop Artiste : {corr1:.2f}")
    print(f"Corrélation Track/Pop Artiste : {corr2:.2f}")


def graph_evolution(df):
    print("Génération du graphe d'évolution...")

    # On "explose" la colonne genres pour avoir une ligne par genre
    df_exploded = df.explode('artist_genres')

    # On prend juste le top 5 global pour que le graphique reste lisible
    top_genres = df_exploded['artist_genres'].value_counts().head(5).index.tolist()

    # On filtre
    df_filtered = df_exploded[df_exploded['artist_genres'].isin(top_genres)]

    # On compte par année
    evo = df_filtered.groupby(['year', 'artist_genres']).size().reset_index(name='count')

    plt.figure(figsize=(12, 6))
    sns.lineplot(data=evo, x='year', y='count', hue='artist_genres', marker='o')
    plt.title("Evolution des 5 genres les plus présents (Top 200)")
    plt.xticks([2020, 2021, 2022, 2023, 2024])
    plt.grid(True)
    plt.savefig("output/graph_evolution.png")