import os
import collector
import analyzer
import pandas as pd

FILE_NAME = "output/data_spotify.csv"


def main():
    # 1. Collecte
    if not os.path.exists(FILE_NAME):
        print("Lancement de la récupération des données...")
        df = collector.run_collection()
        df.to_csv(FILE_NAME, index=False)
        print("Sauvegarde terminée.")
    else:
        print("Le fichier existe déjà, on passe directement à l'analyse.")

    # 2. Analyse
    df = pd.read_csv(FILE_NAME)

    # Nettoyage des listes de genres
    df = analyzer.clean_genres(df)

    # Création des images
    analyzer.graph_correlations(df)
    analyzer.graph_evolution(df)

    print("Fini ! Les images sont générées.")


if __name__ == "__main__":
    main()