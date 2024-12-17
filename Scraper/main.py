import argparse

from src.scraper import VLRGGScraper

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename", required=False, type=str, default="./VLRGG_Scraping_Dataset.json", help="The name of the output file with data collected by the WebScraper")
    args = parser.parse_args()

    app = VLRGGScraper(args.filename)
    code = app.run()

    exit(code)