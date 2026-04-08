"""Migration guide fetcher from GitHub."""

import asyncio
import httpx
import logging
from typing import Optional

from .constants import SDK_REPOS, MIGRATION_DOC_PATHS, PLATFORM_TO_REPO_ID, normalize_version, get_major_version

logger = logging.getLogger(__name__)


class MigrationFetcher:
    """Fetches migration guides from Airship SDK repositories."""

    async def fetch_latest_version(self, platform: str) -> Optional[str]:
        """Fetch the latest SDK version for a platform from GitHub.

        Args:
            platform: Platform ID (e.g., "ios", "android") or display name

        Returns:
            Latest version string (e.g., "19.5.0"), or None if not found
        """
        repo_id = PLATFORM_TO_REPO_ID.get(platform, platform.lower())
        repo = SDK_REPOS.get(repo_id)
        if not repo:
            logger.warning(f"Unknown platform for version lookup: {platform}")
            return None

        # Try GitHub releases API first
        releases_url = f"https://api.github.com/repos/{repo}/releases/latest"
        logger.info(f"Fetching latest version from {releases_url}")

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(
                    releases_url,
                    headers={"Accept": "application/vnd.github.v3+json"}
                )
                if resp.status_code == 200:
                    data = resp.json()
                    tag = data.get("tag_name", "")
                    version = normalize_version(tag)
                    if version:
                        logger.info(f"Latest {repo_id} version: {version}")
                        return version

                # Fallback to tags API if no releases
                tags_url = f"https://api.github.com/repos/{repo}/tags"
                resp = await client.get(
                    tags_url,
                    headers={"Accept": "application/vnd.github.v3+json"}
                )
                if resp.status_code == 200:
                    tags = resp.json()
                    if tags:
                        tag = tags[0].get("name", "")
                        version = normalize_version(tag)
                        if version:
                            logger.info(f"Latest {repo_id} version (from tags): {version}")
                            return version

        except Exception as e:
            logger.error(f"Error fetching latest version for {repo_id}: {e}")

        return None

    async def fetch_all_latest_versions(self) -> dict:
        """Fetch latest versions for all supported platforms."""
        results = {}
        tasks = []
        platforms = list(SDK_REPOS.keys())

        for platform in platforms:
            tasks.append(self.fetch_latest_version(platform))

        versions = await asyncio.gather(*tasks, return_exceptions=True)

        for platform, version in zip(platforms, versions):
            if isinstance(version, str):
                results[platform] = version
            else:
                results[platform] = None

        return results

    async def fetch_migration_guide(
        self, platform: str, from_version: str, to_version: str
    ) -> str:
        """Fetch migration guide content for a version transition.

        Args:
            platform: Platform ID or display name
            from_version: Starting version (e.g., "19.0.0")
            to_version: Target version (e.g., "20.0.0")

        Returns:
            Migration guide content as string, or empty string if not found
        """
        repo_id = PLATFORM_TO_REPO_ID.get(platform, platform.lower())
        repo = SDK_REPOS.get(repo_id)
        if not repo:
            raise ValueError(
                f"Unknown platform: {platform}. Supported: {list(SDK_REPOS.keys())}"
            )

        doc_config = MIGRATION_DOC_PATHS.get(repo_id)
        if not doc_config:
            raise ValueError(f"No migration doc config for platform: {repo_id}")

        from_version = normalize_version(from_version)
        to_version = normalize_version(to_version)
        from_major = get_major_version(from_version)
        to_major = get_major_version(to_version)

        # Build path based on doc type
        doc_type = doc_config["type"]
        if doc_type == "folder":
            filename = doc_config["file_pattern"].format(
                from_major=from_major, to_major=to_major
            )
            path = f"{doc_config['base_path']}/{filename}"
        else:
            path = doc_config["path"]

        url = f"https://raw.githubusercontent.com/{repo}/main/{path}"
        logger.info(f"Fetching migration guide from {url}")

        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                resp = await client.get(url)
                if resp.status_code == 404:
                    logger.warning(f"Migration guide not found: {url}")
                    return ""
                resp.raise_for_status()
                return resp.text

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching migration guide: {e}")
            return ""
        except Exception as e:
            logger.error(f"Error fetching migration guide: {e}")
            return ""
