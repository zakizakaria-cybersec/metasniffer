import os
import argparse
from datetime import datetime
from typing import List, Dict
import pandas as pd
from tqdm import tqdm
from telethon import TelegramClient
from telethon.tl.types import Message
import logging
from pathlib import Path
from dotenv import load_dotenv
from tabulate import tabulate
import asyncio
from extractors.metadata_extractor import MetadataExtractor
from telegram.channel_downloader import ChannelDownloader
from utils.file_utils import ensure_dir, cleanup_files

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

#todo: calculate total of odf files analyzed
#todo: keep the files for author with the most occurence
#todo: add another argument to show logs data, else show only progress bar
#todo: add argument to allow save the statistics in a csv file
#todo: insert another stats to show the amount of files the channel posted per day (containing date)
class MetaSniffer:
    def __init__(self, api_id: str, api_hash: str, session_name: str = "meta_sniffer"):
        self.channel_downloader = ChannelDownloader(api_id, api_hash, session_name)
        self.metadata_extractor = MetadataExtractor()
        self.download_dir = Path("downloads")
        ensure_dir(self.download_dir)

    async def analyze_channel(
        self,
        channel: str,
        before_date: datetime = None,
        after_date: datetime = None
    ) -> pd.DataFrame:
        """
        Analyze files from a Telegram channel and extract metadata.
        """
        try:
            # Download files from channel
            downloaded_files = await self.channel_downloader.download_channel_files(
                channel, 
                self.download_dir,
                before_date,
                after_date
            )

            # Extract metadata from files
            results = []
            for file_path in tqdm(downloaded_files, desc="Extracting metadata"):
                metadata = self.metadata_extractor.extract_metadata(file_path)
                if metadata and metadata.get('Author'):
                    results.append({
                        'Author': metadata['Author'],
                        'File': file_path.name,
                        'Creation Date': metadata.get('Creation Date', 'Unknown')
                    })

            # Create DataFrame and generate statistics
            df = pd.DataFrame(results)
            if not df.empty:
                author_stats = df['Author'].value_counts().reset_index()
                author_stats.columns = ['Author', 'Count']
                return author_stats
            return pd.DataFrame(columns=['Author', 'Count'])

        finally:
            # Cleanup downloaded files
            cleanup_files(self.download_dir)

def main():
    parser = argparse.ArgumentParser(description='Extract metadata from Telegram channel files')
    parser.add_argument('channel', help='Telegram channel name or ID')
    parser.add_argument('--before', help='Filter files before date (YYYY-MM-DD)')
    parser.add_argument('--after', help='Filter files after date (YYYY-MM-DD)')
    parser.add_argument('--verbose', action='store_true', help='Display detailed logs instead of progress bar')
    args = parser.parse_args()

     # Configure logging based on verbosity
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.WARNING)


    # Load environment variables
    load_dotenv()
    
    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')
    
    if not api_id or not api_hash:
        logger.error("Please set TELEGRAM_API_ID and TELEGRAM_API_HASH environment variables")
        return

    # Parse dates if provided
    before_date = datetime.strptime(args.before, '%Y-%m-%d') if args.before else None
    after_date = datetime.strptime(args.after, '%Y-%m-%d') if args.after else None

    # Create MetaSniffer instance and run analysis
    sniffer = MetaSniffer(api_id, api_hash)
    results = asyncio.run(sniffer.analyze_channel(args.channel, before_date, after_date))
    
    print("\nAuthor Statistics:")
    if not results.empty:
        # Use tabulate to format the DataFrame
        formatted_table = tabulate(
            results,
            headers="keys",
            tablefmt="grid",
            showindex=False,
            stralign="center"
        )
        print(formatted_table)
    else:
        print("No data available.")

if __name__ == "__main__":
    main()
    