"""
Build tools integration for migration verification.

Provides platform-specific build verification by mounting external MCP servers
(like XcodeBuildMCP) or falling back to instructions when not available.
"""

import re
import shutil
from dataclasses import dataclass
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum


class BuildPlatform(Enum):
    """Supported build platforms."""
    IOS = "iOS"
    ANDROID = "Android"


@dataclass
class BuildToolsStatus:
    """Status of available build tools."""
    ios_available: bool = False
    ios_tool_prefix: Optional[str] = None
    android_available: bool = False
    android_tool_prefix: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ios": {
                "available": self.ios_available,
                "tool_prefix": self.ios_tool_prefix,
            },
            "android": {
                "available": self.android_available,
                "tool_prefix": self.android_tool_prefix,
            }
        }


def check_xcode_mcp_available() -> bool:
    """Check if XcodeBuildMCP can be invoked via npx."""
    # Check if npx is available
    if not shutil.which("npx"):
        return False
    return True


def check_gradle_available() -> bool:
    """Check if Gradle wrapper or gradle is available."""
    return shutil.which("gradle") is not None


def get_xcode_mcp_command() -> Tuple[str, List[str]]:
    """Get the command and args to invoke XcodeBuildMCP."""
    return "npx", ["-y", "xcode-mcp-server"]


def get_ios_build_instructions() -> Dict[str, Any]:
    """Get manual instructions for iOS build verification."""
    return {
        "platform": "iOS",
        "available": False,
        "manual_instructions": [
            "XcodeBuildMCP is not mounted. To enable automatic build verification:",
            "1. Install: npm install -g xcode-mcp-server",
            "2. Or use xcodebuild directly:",
            "   cd /path/to/project",
            "   xcodebuild -resolvePackageDependencies -project Project.xcodeproj",
            "   xcodebuild -project Project.xcodeproj -scheme Scheme -destination 'generic/platform=iOS Simulator' build",
        ],
        "xcodebuild_commands": {
            "resolve_packages": "xcodebuild -resolvePackageDependencies -project {project_path}",
            "build": "xcodebuild -project {project_path} -scheme {scheme} -destination 'generic/platform=iOS Simulator' build",
            "clean_build": "xcodebuild -project {project_path} -scheme {scheme} clean build",
        }
    }


def get_android_build_instructions() -> Dict[str, Any]:
    """Get manual instructions for Android build verification."""
    return {
        "platform": "Android",
        "available": False,
        "manual_instructions": [
            "Run these commands in your Android project directory:",
            "1. ./gradlew assembleDebug  (debug build)",
            "2. ./gradlew build  (full build with tests)",
            "3. Check output for errors",
        ],
        "gradle_commands": {
            "debug_build": "./gradlew assembleDebug",
            "release_build": "./gradlew assembleRelease",
            "full_build": "./gradlew build",
            "clean_build": "./gradlew clean assembleDebug",
        }
    }


# Common iOS build error patterns and suggestions
IOS_ERROR_PATTERNS = {
    "unable to find module": {
        "pattern": r"unable to find module[:\s]+['\"]?(\w+)",
        "suggestion": "Missing module dependency. Ensure the package is added to your project and linked to this target.",
        "fix_hint": "Add the missing package dependency in Xcode or Package.swift",
    },
    "no such module": {
        "pattern": r"no such module '(\w+)'",
        "suggestion": "Module not found. Check that SPM packages are resolved and the module is linked.",
        "fix_hint": "Run 'xcodebuild -resolvePackageDependencies' and verify target dependencies",
    },
    "deployment target": {
        "pattern": r"deployment target.*?(\d+\.\d+)",
        "suggestion": "Deployment target mismatch. Update IPHONEOS_DEPLOYMENT_TARGET in build settings.",
        "fix_hint": "Set deployment target to at least iOS 16.0 for Airship SDK 18+",
    },
    "has been renamed": {
        "pattern": r"'(\w+)' has been renamed to '(\w+)'",
        "suggestion": "API renamed in new SDK version. Update to the new name.",
        "fix_hint": "Replace the old API name with the new one shown in the error",
    },
    "cannot find in scope": {
        "pattern": r"cannot find '(\w+)' in scope",
        "suggestion": "Symbol not found. May be renamed, moved, or removed in new version.",
        "fix_hint": "Check migration guide for API changes",
    },
    "type mismatch": {
        "pattern": r"cannot convert.*?'(\w+)'.*?to.*?'(\w+)'",
        "suggestion": "Type changed in new SDK version.",
        "fix_hint": "Check if the API return type changed and update accordingly",
    },
}


def analyze_build_error(error_message: str) -> Dict[str, Any]:
    """Analyze a build error and provide suggestions."""
    error_lower = error_message.lower()

    for error_type, info in IOS_ERROR_PATTERNS.items():
        if error_type in error_lower:
            match = re.search(info["pattern"], error_message, re.IGNORECASE)
            return {
                "error_type": error_type,
                "matched": match.groups() if match else None,
                "suggestion": info["suggestion"],
                "fix_hint": info["fix_hint"],
            }

    return {
        "error_type": "unknown",
        "suggestion": "Review the error message and check the migration guide for related changes.",
        "fix_hint": None,
    }


def parse_xcode_build_errors(output: str) -> List[Dict[str, Any]]:
    """Parse xcodebuild output for errors with file locations."""
    errors = []
    # Pattern: /path/to/file.swift:123:45: error: message
    pattern = r'^(.+?):(\d+):(\d+):\s*(error|warning):\s*(.+)$'

    for line in output.split('\n'):
        match = re.match(pattern, line.strip())
        if match:
            file_path, line_num, col, level, message = match.groups()
            if level == "error":
                analysis = analyze_build_error(message)
                errors.append({
                    "file": file_path,
                    "line": int(line_num),
                    "column": int(col),
                    "message": message,
                    "analysis": analysis,
                })

    return errors
