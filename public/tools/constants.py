"""Constants for Airship SDK migration assistant."""

# Supported platforms for migration
SUPPORTED_PLATFORMS = [
    "iOS",
    "Android",
    "React Native",
    "Flutter",
    "Capacitor",
    "Cordova",
    ".NET",
]

# Map display names to repo keys
PLATFORM_TO_REPO_ID = {
    "iOS": "ios",
    "Android": "android",
    "React Native": "react-native",
    "Flutter": "flutter",
    "Capacitor": "capacitor",
    "Cordova": "cordova",
    ".NET": "dotnet",
}

# Official Airship SDK repositories (independent copy for this package)
SDK_REPOS = {
    "ios": "urbanairship/ios-library",
    "android": "urbanairship/android-library",
    "flutter": "urbanairship/airship-flutter",
    "react-native": "urbanairship/react-native-airship",
    "capacitor": "urbanairship/capacitor-airship",
    "cordova": "urbanairship/urbanairship-cordova",
    "dotnet": "urbanairship/airship-dotnet",
}

# Migration document paths per platform
# Based on research: iOS/Android use dedicated folders, others use root MIGRATION.md
MIGRATION_DOC_PATHS = {
    "ios": {
        "type": "folder",
        "base_path": "Documentation/Migration",
        "file_pattern": "migration-guide-{from_major}-{to_major}.md",
    },
    "android": {
        "type": "folder",
        "base_path": "documentation/migration",
        "file_pattern": "migration-guide-{from_major}-{to_major}.md",
    },
    "flutter": {"type": "root_file", "path": "MIGRATION.md"},
    "react-native": {"type": "root_file", "path": "MIGRATION.md"},
    "cordova": {"type": "root_file", "path": "MIGRATION.md"},
    "dotnet": {"type": "root_file", "path": "MIGRATION.md"},
    "capacitor": {"type": "changelog", "path": "CHANGELOG.md"},
}


# ---------------------------------------------------------------------------
# Shared version utilities
# Centralised here so migration_fetcher and migration_parser don't duplicate
# ---------------------------------------------------------------------------

def normalize_version(version: str) -> str:
    """Normalize a version string by stripping any leading 'v' prefix."""
    return version[1:] if version.startswith("v") else version


def get_major_version(version: str) -> int:
    """Return the major version number from a version string."""
    return int(normalize_version(version).split(".")[0])
