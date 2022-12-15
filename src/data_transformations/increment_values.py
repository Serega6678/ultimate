import pandas as pd


def main() -> None:
    df = pd.read_csv("data/dvc_practice_data/initial.csv")
    df += 1
    df.to_csv("data/dvc_practice_data/transformed.csv", index=False)


if __name__ == "__main__":
    main()
