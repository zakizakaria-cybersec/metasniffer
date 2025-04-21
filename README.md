# MetaSniffer

MetaSniffer is an OSINT (Open Source Intelligence) tool designed to extract Author metadata from pdf files shared in Telegram channels. It downloads PDF files from a specified Telegram channel and analyzes them to extract metadata such as the author then tabulate it to show the counts.

The idea behind this is that to correlate the author with the highest occurence with the telegram channel owner. Thus increasing the chance to identify the real owner of the telegram channel and at the same time getting to know who's reaching out to the channel or where the channel get their sources from.

## Features

- Downloads PDF files from Telegram channels.
- Extracts metadata using `exiftool`.
- Generates statistics on authors and other metadata fields.
- Cleans up downloaded files after processing.

## Requirements

- Python 3.8 or higher
- A Telegram API ID and API Hash (see [Telegram API Documentation](https://core.telegram.org/api/obtaining_api_id) for details)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/metasniffer.git
   cd metasniffer