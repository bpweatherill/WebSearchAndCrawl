from pathlib import Path
from typing import AsyncGenerator, Optional, Dict
import aiohttp
import re
from server.config import settings
from server.schemas import DownloadResult
from server.downloader.parsers import parse_file
import logging

logger = logging.getLogger(__name__)

class Downloader:
    def __init__(self):
        self.downloads_dir = Path(settings.downloads_dir)
        self.downloads_dir.mkdir(parents=True, exist_ok=True)

    async def download(
        self,
        domain: str,
        regex: str,
        output_dir: Optional[str] = None
    ) -> AsyncGenerator[DownloadResult, None]:
        """Download documents matching a regex from a domain."""
        domain_dir = self.downloads_dir / domain
        domain_dir.mkdir(parents=True, exist_ok=True)

        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
        else:
            output_path = domain_dir

        # TODO: Integrate with crawler to get matching URLs
        # For now, mock a download
        mock_url = f"https://{domain}/example.pdf"
        mock_filename = output_path / "example.pdf"

        # Mock download
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(mock_url, timeout=settings.request_timeout_seconds) as response:
                    if response.status == 200:
                        content = await response.read()
                        # Save file
                        with open(mock_filename, "wb") as f:
                            f.write(content)
                        # Parse file
                        parsed_text = parse_file(str(mock_filename))
                        yield DownloadResult(
                            filename=str(mock_filename),
                            url=mock_url,
                            parsed_text=parsed_text
                        )
            except Exception as e:
                logger.error(f"Failed to download {mock_url}: {e}")

    async def download_from_url(self, url: str, output_dir: Path) -> Optional[str]:
        """Download a single file from a URL."""
        filename = output_dir / Path(url).name
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=settings.request_timeout_seconds) as response:
                    if response.status == 200:
                        content = await response.read()
                        with open(filename, "wb") as f:
                            f.write(content)
                        return str(filename)
        except Exception as e:
            logger.error(f"Failed to download {url}: {e}")
            return None
        return None
