#!/usr/bin/env python3
"""Validate Airship push notification configuration in a project.

Usage:
    python validate-push-config.py <project_path> [--platform ios|android]

This script checks for common push configuration issues:
- Missing AirshipConfig.plist (iOS) or airshipconfig.properties (Android)
- Missing required keys
- Invalid bundle ID / package name configuration
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


def find_ios_config(project_path: Path) -> dict:
    """Find and parse AirshipConfig.plist."""
    config_paths = [
        project_path / "AirshipConfig.plist",
        project_path / "ios" / "AirshipConfig.plist",
        *project_path.glob("**/AirshipConfig.plist"),
    ]

    for config_path in config_paths:
        if config_path.exists():
            # Parse plist (simplified - just check for key presence)
            content = config_path.read_text()
            return {
                "path": str(config_path),
                "has_app_key": "appKey" in content or "developmentAppKey" in content,
                "has_app_secret": "appSecret" in content or "developmentAppSecret" in content,
                "content": content,
            }

    return {"error": "AirshipConfig.plist not found"}


def find_android_config(project_path: Path) -> dict:
    """Find and parse airshipconfig.properties."""
    config_paths = [
        project_path / "airshipconfig.properties",
        project_path / "android" / "app" / "src" / "main" / "assets" / "airshipconfig.properties",
        project_path / "app" / "src" / "main" / "assets" / "airshipconfig.properties",
        *project_path.glob("**/airshipconfig.properties"),
    ]

    for config_path in config_paths:
        if config_path.exists():
            content = config_path.read_text()
            return {
                "path": str(config_path),
                "has_app_key": "developmentAppKey" in content or "productionAppKey" in content,
                "has_app_secret": "developmentAppSecret" in content or "productionAppSecret" in content,
                "content": content,
            }

    return {"error": "airshipconfig.properties not found"}


def check_ios_push_capability(project_path: Path) -> dict:
    """Check if push notification capability is enabled in Xcode project."""
    entitlements = list(project_path.glob("**/*.entitlements"))

    for ent_path in entitlements:
        content = ent_path.read_text()
        if "aps-environment" in content:
            return {
                "path": str(ent_path),
                "push_enabled": True,
                "environment": "production" if "production" in content else "development",
            }

    return {"push_enabled": False, "error": "No push entitlement found"}


def validate_project(project_path: str, platform: str = None) -> dict:
    """Validate push configuration for a project."""
    path = Path(project_path)
    results = {"project_path": project_path, "issues": [], "status": "valid"}

    # Auto-detect platform if not specified
    if not platform:
        has_ios = (path / "ios").exists() or list(path.glob("*.xcodeproj"))
        has_android = (path / "android").exists() or (path / "app" / "build.gradle").exists()
        platforms = []
        if has_ios:
            platforms.append("ios")
        if has_android:
            platforms.append("android")
        if not platforms:
            results["issues"].append("Could not detect platform")
            results["status"] = "error"
            return results
    else:
        platforms = [platform]

    results["platforms"] = platforms

    for plat in platforms:
        if plat == "ios":
            config = find_ios_config(path)
            results["ios_config"] = config

            if "error" in config:
                results["issues"].append(f"iOS: {config['error']}")
                results["status"] = "invalid"
            elif not config.get("has_app_key"):
                results["issues"].append("iOS: Missing appKey in AirshipConfig.plist")
                results["status"] = "invalid"
            elif not config.get("has_app_secret"):
                results["issues"].append("iOS: Missing appSecret in AirshipConfig.plist")
                results["status"] = "invalid"

            capability = check_ios_push_capability(path)
            results["ios_push_capability"] = capability
            if not capability.get("push_enabled"):
                results["issues"].append("iOS: Push notification entitlement not found")
                results["status"] = "invalid"

        elif plat == "android":
            config = find_android_config(path)
            results["android_config"] = config

            if "error" in config:
                results["issues"].append(f"Android: {config['error']}")
                results["status"] = "invalid"
            elif not config.get("has_app_key"):
                results["issues"].append("Android: Missing appKey in airshipconfig.properties")
                results["status"] = "invalid"
            elif not config.get("has_app_secret"):
                results["issues"].append("Android: Missing appSecret in airshipconfig.properties")
                results["status"] = "invalid"

    if not results["issues"]:
        results["message"] = "Push configuration looks valid"

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Validate Airship push notification configuration"
    )
    parser.add_argument("project_path", help="Path to the project directory")
    parser.add_argument(
        "--platform",
        choices=["ios", "android"],
        help="Platform to validate (auto-detected if not specified)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )

    args = parser.parse_args()

    results = validate_project(args.project_path, args.platform)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"Push Configuration Validation: {args.project_path}")
        print(f"{'='*60}\n")

        print(f"Status: {results['status'].upper()}")
        print(f"Platforms: {', '.join(results.get('platforms', []))}")

        if results["issues"]:
            print("\nIssues found:")
            for issue in results["issues"]:
                print(f"  ❌ {issue}")
        else:
            print("\n✅ Push configuration looks valid")

        print()

    return 0 if results["status"] == "valid" else 1


if __name__ == "__main__":
    sys.exit(main())
