---
name: migration
description: Migrate Airship SDK to a newer version. Use when upgrading SDK versions, fixing deprecation warnings, or updating after a major SDK release.
license: Copyright Airship. All rights reserved.
---

# Airship SDK Migration

This skill guides you through migrating Airship SDK to a newer version.

## When to Use

- Upgrading to a new major SDK version (e.g., 19.x → 20.x)
- Fixing deprecation warnings after updating dependencies
- Preparing for a new SDK release
- Troubleshooting post-migration build errors

## Migration Workflow

### Step 1: Start Migration

**If the `airship-mcp` server is available** ([github.com/urbanairship/agent-tools](https://github.com/urbanairship/agent-tools)), use the interactive migration wizard — it auto-detects your platform and SDK version, fetches the migration guide, and applies code changes:

```
Use MCP tool: airship.start_migration()
```

**Without MCP:**
1. Ask the user for their platform and current SDK version
2. Locate the migration guide for the platform:

| Platform | Migration Guide Location |
|----------|--------------------------|
| iOS | `Documentation/Migration/migration-guide-{from}-{to}.md` in [urbanairship/ios-library](https://github.com/urbanairship/ios-library) |
| Android | `documentation/migration/migration-guide-{from}-{to}.md` in [urbanairship/android-library](https://github.com/urbanairship/android-library) |
| React Native | `MIGRATION.md` in [urbanairship/react-native-airship](https://github.com/urbanairship/react-native-airship) — or use local copy at `../sdk-reference/references/setup/react-native/setup/MIGRATION.md` |
| Flutter | `MIGRATION.md` in [urbanairship/airship-flutter](https://github.com/urbanairship/airship-flutter) — or use local copy at `../sdk-reference/references/setup/flutter/setup/MIGRATION.md` |
| Capacitor | `CHANGELOG.md` in [urbanairship/capacitor-airship](https://github.com/urbanairship/capacitor-airship) (no dedicated migration file — filter for breaking changes) |
| Cordova | `MIGRATION.md` in [urbanairship/urbanairship-cordova](https://github.com/urbanairship/urbanairship-cordova) |
| .NET / MAUI | `MIGRATION.md` in [urbanairship/airship-dotnet](https://github.com/urbanairship/airship-dotnet) |

3. Fetch or read the guide, then follow it step by step applying each change to the codebase

### Step 2: Apply Migration Steps

For EACH step in the migration guide:

1. **Search the codebase** for the deprecated pattern
2. **Replace ALL occurrences** (not just the first)
3. **Mark complete** before moving to next step

**CRITICAL**: A successful build does NOT mean migration is complete. You must address ALL steps.

### Step 3: Build and Verify

After applying all migration steps, verify the build.

**If the `airship-mcp` server is available:**
```
Use MCP tool: airship.verify_build(project_path="<path>")
```

**Otherwise, run the platform build command:**

| Platform | Build Command |
|----------|---------------|
| iOS | `xcodebuild -scheme <scheme> -sdk iphonesimulator build` |
| Android | `./gradlew assembleDebug` |
| React Native | `npx react-native run-ios` or `npx react-native run-android` |
| Flutter | `flutter build apk` or `flutter build ios` |
| Capacitor | `npx cap build ios` or `npx cap build android` |
| Cordova | `cordova build ios` or `cordova build android` |

Fix any build errors and re-verify.

### Step 4: Test Features

After build succeeds, test the migrated features:

- **Push**: Use the `push` skill to test push delivery
- **Message Center**: Use the `message-center` skill to verify inbox

## MCP Tools (Optional)

These tools are available if the `airship-mcp` server is configured. The skill works without them using the fallbacks above.

| Tool | Purpose |
|------|---------|
| `start_migration` | Interactive wizard: auto-detects platform/version, fetches guide, applies changes |
| `migrate_sdk` | Non-interactive migration with explicit `project_path`, `platform`, `from_version`, `to_version` |
| `verify_build` | Build the project and check for errors |
| `check_build_tools` | Show available build tools |

## Platform Support

- iOS (CocoaPods, SPM)
- Android (Gradle)
- React Native
- Flutter
- Capacitor
- Cordova
- .NET

## Common Issues

### Build succeeds but app crashes

Check for:
- Removed APIs still being called at runtime
- Changed initialization patterns
- Missing configuration updates

### Deprecation warnings remain

The migration guide includes ALL changes. Search for each deprecated pattern explicitly.

### Multi-version migration (e.g., 17→20)

Complete each major version step sequentially:
1. 17.x → 18.x
2. 18.x → 19.x
3. 19.x → 20.x
