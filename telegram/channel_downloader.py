from pathlib import Path
from telethon import TelegramClient
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class ChannelDownloader:
    def __init__(self, api_id: str, api_hash: str, session_name: str):
        self.client = TelegramClient(session_name, api_id, api_hash)
        
    async def download_channel_files(self, channel: str, download_dir: Path, before_date=None, after_date=None):
        downloaded_files = []
        try:
            await self.client.start()

            # Ensure download_dir is a Path object and exists
            download_dir = Path(download_dir)
            download_dir.mkdir(parents=True, exist_ok=True)

            # Convert dates to UTC timezone-aware datetime objects if provided
            if before_date:
                before_date = before_date.astimezone(timezone.utc)
            if after_date:
                after_date = after_date.astimezone(timezone.utc)

            async for message in self.client.iter_messages(channel):
                if (
                    message.file
                    and message.file.name
                    and message.file.name.endswith(".pdf")
                    and message.file.mime_type == "application/pdf"
                    and (before_date is None or message.date < before_date)
                    and (after_date is None or message.date > after_date)
                ):
                    try:
                        file_path = download_dir / message.file.name
                        logger.info(f"Downloading PDF file: {message.file.name}")
                        await self.client.download_media(message, file_path)
                        downloaded_files.append(file_path)
                    except Exception as e:
                        logger.error(f"Failed to download {message.file.name}: {e}")
                else:
                    logger.debug(f"Skipped message ID {message.id}: No valid PDF file or outside date range.")

        except Exception as e:
            logger.error(f"Error downloading from channel: {e}")

        finally:
            await self.client.disconnect()

        return downloaded_files