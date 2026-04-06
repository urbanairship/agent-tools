"""Migration guide parsing utilities."""

import re
from typing import Dict, List, Optional, Tuple, Any

from .constants import normalize_version, get_major_version


def get_migration_path(from_version: str, to_version: str) -> List[Tuple[int, int]]:
    """Calculate all intermediate major version transitions.

    For multi-major-version migrations, returns the list of
    version-to-version transitions needed.

    Example:
        get_migration_path("17.0.0", "20.0.0")
        Returns: [(17, 18), (18, 19), (19, 20)]

    Args:
        from_version: Starting version (e.g., "17.0.0")
        to_version: Target version (e.g., "20.0.0")

    Returns:
        List of (from_major, to_major) tuples for each step.
        Empty list if from_version >= to_version.
    """
    from_major = get_major_version(from_version)
    to_major = get_major_version(to_version)

    if from_major >= to_major:
        return []

    return [(i, i + 1) for i in range(from_major, to_major)]


def extract_version_section(content: str, from_major: int, to_major: int) -> str:
    """Extract migration section for a specific version transition.

    Handles common heading patterns found in Airship migration guides:
    - "## 19.x to 20.x"
    - "## Migration from 6 to 7"
    - "# 21.x - 25.x to 26.0.0"
    - "## Version 19 to 20"

    Args:
        content: Full migration guide content
        from_major: Starting major version number
        to_major: Target major version number

    Returns:
        Extracted section content, or empty string if no match found
    """
    # Patterns to match version transition headings
    patterns = [
        # "## 19.x to 20.x" or "## 19.0 to 20.0"
        rf"^(##?\s*{from_major}\.x?\s*to\s*{to_major}\.)",
        # "## Migration from 6 to 7" or "## Migration from 6.x to 7.x"
        rf"^(##?\s*Migration.*{from_major}.*to.*{to_major})",
        # "# 21.x - 25.x to 26.0.0" (range pattern)
        rf"^(##?\s*\d+\.x?\s*-\s*{from_major}\.x?\s*to\s*{to_major}\.)",
        # "## Version 19 to 20"
        rf"^(##?\s*Version\s*{from_major}.*to.*{to_major})",
        # ".NET style: ## 19.x to 20.x"
        rf"^(##?\s*{from_major}\.x\s+to\s+{to_major}\.x)",
    ]

    for pattern in patterns:
        match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
        if match:
            start = match.start()
            # Find the next major heading (## or #) to determine section end
            # Look for next heading that starts a new version section
            remaining = content[match.end() :]
            next_heading = re.search(
                r"^##?\s*(?:\d+\.|\w+\s+\d+)",  # Next version heading
                remaining,
                re.MULTILINE,
            )
            if next_heading:
                end = match.end() + next_heading.start()
            else:
                end = len(content)
            return content[start:end].strip()

    return ""


def parse_migration_steps(section_content: str) -> List[Dict]:
    """Parse a migration section into structured steps.

    Extracts headings as step titles, detects code blocks for
    before/after comparisons, and handles tables for API mappings.

    Args:
        section_content: Content of a version-specific migration section

    Returns:
        List of step dictionaries with keys:
        - step_number: Sequential step number
        - title: Step title from heading
        - description: Text description
        - code_before: Code snippet showing old API (if present)
        - code_after: Code snippet showing new API (if present)
    """
    steps = []
    step_number = 0

    # Split by subheadings (### or ## but not the main section heading)
    lines = section_content.split("\n")
    current_step: Optional[Dict] = None
    current_section: List[str] = []
    in_code_block = False
    code_blocks: List[str] = []
    current_code: List[str] = []

    for line in lines:
        # Track code block state
        if line.strip().startswith("```"):
            if in_code_block:
                # End of code block
                code_blocks.append("\n".join(current_code))
                current_code = []
                in_code_block = False
            else:
                # Start of code block
                in_code_block = True
            continue

        if in_code_block:
            current_code.append(line)
            continue

        # Check for subheading (## or ###)
        heading_match = re.match(r"^(#{2,3})\s+(.+)", line)
        if heading_match and not line.startswith("####"):
            # Save previous step
            if current_step is not None:
                current_step["description"] = "\n".join(current_section).strip()
                # Assign code blocks to before/after
                if len(code_blocks) >= 2:
                    current_step["code_before"] = code_blocks[0]
                    current_step["code_after"] = code_blocks[-1]
                elif len(code_blocks) == 1:
                    current_step["code_after"] = code_blocks[0]
                steps.append(current_step)

            # Start new step
            step_number += 1
            current_step = {
                "step_number": step_number,
                "title": heading_match.group(2).strip(),
                "description": "",
                "code_before": "",
                "code_after": "",
            }
            current_section = []
            code_blocks = []
        else:
            # Add to current section description
            current_section.append(line)

    # Save final step
    if current_step is not None:
        current_step["description"] = "\n".join(current_section).strip()
        if len(code_blocks) >= 2:
            current_step["code_before"] = code_blocks[0]
            current_step["code_after"] = code_blocks[-1]
        elif len(code_blocks) == 1:
            current_step["code_after"] = code_blocks[0]
        steps.append(current_step)

    # If no subheadings found, create a single step from all content
    if not steps and section_content.strip():
        steps.append(
            {
                "step_number": 1,
                "title": "Migration Steps",
                "description": section_content.strip(),
                "code_before": "",
                "code_after": "",
            }
        )

    return steps


def generate_rollback_hint(step: Dict) -> str:
    """Generate a rollback hint for a migration step.

    Provides guidance on how to undo a migration step if needed.

    Args:
        step: A step dictionary from parse_migration_steps()

    Returns:
        Rollback hint string
    """
    title = step.get("title", "").lower()
    description = step.get("description", "").lower()
    code_before = step.get("code_before", "")
    code_after = step.get("code_after", "")

    # If we have before/after code, provide specific reversal guidance
    if code_before and code_after:
        return f"Revert: Use the old API pattern instead of the new one"

    # Check for common migration patterns in title/description
    combined = f"{title} {description}"

    if "remove" in combined or "delete" in combined:
        return "Rollback: Restore the removed code/configuration"

    if "add" in combined and ("dependency" in combined or "package" in combined):
        return "Rollback: Remove the added dependency and restore previous version"

    if "update" in combined and ("dependency" in combined or "package" in combined):
        return "Rollback: Downgrade to the previous dependency version"

    if "rename" in combined:
        return "Rollback: Rename back to the original name"

    if "replace" in combined:
        return "Rollback: Restore the original implementation"

    if "deprecated" in combined:
        return "Rollback: Continue using the deprecated API (may be removed in future)"

    if "config" in combined or "configuration" in combined:
        return "Rollback: Restore previous configuration settings"

    # Default hint
    return "Rollback: Undo this change and verify app behavior"


def extract_replacements(
    guide_content: str,
    from_major: int,
    to_major: int,
) -> List[Dict[str, Any]]:
    """Extract find/replace patterns from migration guide content.

    Parses migration guides to find explicit before/after patterns that can
    be applied via find/replace across a codebase. This enables systematic
    migration instead of guess-and-check building.

    Looks for:
    - Markdown tables with before/after API mappings
    - Before/after code block pairs
    - Explicit "Replace X with Y" or "renamed to" text patterns

    Args:
        guide_content: Full migration guide content (markdown)
        from_major: Starting major version number
        to_major: Target major version number

    Returns:
        List of replacement dictionaries with keys:
        - find: The old API/pattern to search for
        - replace: The new API/pattern to use
        - description: Brief description of the change
        - context: Additional context (e.g., "table", "code_block")
        - version: Version transition string (e.g., "18→19")
        - is_simple: True if this is a simple find/replace, False if needs judgment
    """
    replacements: List[Dict[str, Any]] = []
    version_label = f"{from_major}→{to_major}"

    # 1. Extract from markdown tables
    table_replacements = _extract_from_tables(guide_content, from_major, to_major)
    for r in table_replacements:
        r["version"] = version_label
    replacements.extend(table_replacements)

    # 2. Extract from code block pairs
    code_replacements = _extract_from_code_blocks(guide_content, from_major, to_major)
    for r in code_replacements:
        r["version"] = version_label
    replacements.extend(code_replacements)

    # 3. Extract from text patterns
    text_replacements = _extract_from_text_patterns(guide_content)
    for r in text_replacements:
        r["version"] = version_label
    replacements.extend(text_replacements)

    # Deduplicate by (find, replace) pair
    seen = set()
    unique_replacements = []
    for r in replacements:
        key = (r.get("find", ""), r.get("replace", ""))
        if key not in seen and key[0] and key[1]:
            seen.add(key)
            unique_replacements.append(r)

    return unique_replacements


def _extract_from_tables(
    content: str, from_major: int, to_major: int
) -> List[Dict[str, Any]]:
    """Extract replacements from markdown tables.

    Looks for tables with columns like:
    - "SDK 17.x" | "SDK 18.x"
    - "SDK 18.x ... API" | "SDK 19.x ... API"
    - "Before" | "After"
    """
    replacements = []

    # Pattern to find markdown tables
    # Tables have header row, separator row (with ---), and data rows
    table_pattern = r'\|(.+?)\|\n\|[-:\s|]+\|\n((?:\|.+\|\n?)+)'

    for match in re.finditer(table_pattern, content, re.MULTILINE):
        header_row = match.group(1)
        data_rows = match.group(2)

        # Parse header to identify columns
        headers = [h.strip() for h in header_row.split('|') if h.strip()]
        if len(headers) < 2:
            continue

        # Look for before/after column patterns
        before_col = None
        after_col = None

        for i, header in enumerate(headers):
            header_lower = header.lower()
            # Check for version-specific headers
            if f"sdk {from_major}" in header_lower or f"{from_major}.x" in header_lower:
                before_col = i
            elif f"sdk {to_major}" in header_lower or f"{to_major}.x" in header_lower:
                after_col = i
            # Generic before/after
            elif "before" in header_lower or "old" in header_lower:
                before_col = i
            elif "after" in header_lower or "new" in header_lower or "replacement" in header_lower:
                after_col = i

        if before_col is None or after_col is None:
            continue

        # Parse data rows
        for row in data_rows.strip().split('\n'):
            cells = [c.strip() for c in row.split('|') if c.strip()]
            if len(cells) <= max(before_col, after_col):
                continue

            old_api = cells[before_col].strip()
            new_api = cells[after_col].strip()

            # Skip empty or "REMOVED" entries
            if not old_api or not new_api:
                continue
            if new_api.upper().startswith("REMOVED") or new_api.upper().startswith("_REMOVED"):
                # This is a removal, not a replacement
                replacements.append({
                    "find": _clean_api_string(old_api),
                    "replace": "",
                    "description": f"Removed in SDK {to_major}: {new_api}",
                    "context": "table",
                    "is_simple": False,  # Removals need manual handling
                })
                continue

            # Clean up the API strings
            old_clean = _clean_api_string(old_api)
            new_clean = _clean_api_string(new_api)

            # Skip malformed patterns (e.g., contains arrow from bad parsing)
            if '->' in old_clean or '->' in new_clean:
                continue

            # Skip patterns that look like type signatures, not actual code
            if '{ get' in old_clean or '{ set' in old_clean:
                continue

            if old_clean and new_clean and old_clean != new_clean:
                # Validate it looks like an API pattern and replacement is valid
                if _is_valid_api_pattern(old_clean) and _is_valid_replacement(old_clean, new_clean):
                    replacements.append({
                        "find": old_clean,
                        "replace": new_clean,
                        "description": f"API change: {old_clean} → {new_clean}",
                        "context": "table",
                        "is_simple": _is_simple_replacement(old_clean, new_clean),
                    })

    return replacements


def _extract_from_code_blocks(
    content: str, from_major: int, to_major: int
) -> List[Dict[str, Any]]:
    """Extract replacements from consecutive code blocks labeled as before/after.

    Looks for patterns like:
    - Code blocks preceded by "17.x:" and "18.x:" labels
    - Code blocks preceded by "Before:" and "After:" labels
    """
    replacements = []

    # Pattern to find labeled code blocks
    # Look for "17.x:" or "Before:" followed by code block, then "18.x:" or "After:" with code block
    before_labels = [
        rf'{from_major}\.x:',
        rf'SDK {from_major}\.x:',
        r'Before:',
        r'Old:',
    ]
    after_labels = [
        rf'{to_major}\.x:',
        rf'SDK {to_major}\.x:',
        r'After:',
        r'New:',
    ]

    # Find code blocks
    code_block_pattern = r'```(?:\w+)?\n(.*?)```'
    blocks = list(re.finditer(code_block_pattern, content, re.DOTALL))

    for i, block in enumerate(blocks):
        block_start = block.start()
        block_content = block.group(1).strip()

        # Look for before label before this block
        text_before = content[max(0, block_start - 200):block_start]

        is_before_block = False
        for label in before_labels:
            if re.search(label, text_before, re.IGNORECASE):
                is_before_block = True
                break

        if not is_before_block:
            continue

        # Look for the next code block as the "after" block
        if i + 1 < len(blocks):
            next_block = blocks[i + 1]
            text_between = content[block.end():next_block.start()]

            is_after_block = False
            for label in after_labels:
                if re.search(label, text_between, re.IGNORECASE):
                    is_after_block = True
                    break

            if is_after_block:
                after_content = next_block.group(1).strip()

                # Extract key API patterns from the code
                old_apis = _extract_api_calls(block_content)
                new_apis = _extract_api_calls(after_content)

                # Match old to new based on similarity
                for old_api in old_apis:
                    for new_api in new_apis:
                        if _apis_are_related(old_api, new_api):
                            replacements.append({
                                "find": old_api,
                                "replace": new_api,
                                "description": f"Code pattern: {old_api} → {new_api}",
                                "context": "code_block",
                                "is_simple": _is_simple_replacement(old_api, new_api),
                            })

    return replacements


def _is_valid_api_pattern(pattern: str) -> bool:
    """Check if a pattern looks like a valid API name (not common English word)."""
    # Reject patterns that are too short
    if len(pattern) < 8:
        return False

    # Reject common English words and programming terms that appear in docs
    common_words = {
        'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had',
        'her', 'was', 'one', 'our', 'out', 'has', 'have', 'been', 'will',
        'from', 'they', 'this', 'that', 'with', 'which', 'their', 'there',
        'these', 'those', 'then', 'than', 'when', 'where', 'what', 'named',
        'method', 'class', 'function', 'property', 'value', 'type', 'now',
        'instead', 'use', 'using', 'used', 'removed', 'added', 'changed',
        'navigation', 'controlled', 'inproduction', 'requires',
    }
    if pattern.lower() in common_words:
        return False

    # API names typically have:
    # - Dots (like MessageCenter.shared) - STRONG indicator
    # - Underscores
    # - Start with capital letter AND have more capitals (PascalCase class names)
    # - Contains specific SDK prefixes

    # Strong indicators - definitely an API
    if '.' in pattern:
        return True

    # SDK-specific prefixes
    sdk_prefixes = ('UA', 'Airship', 'Message', 'Preference', 'Feature', 'InApp', 'Custom')
    if any(pattern.startswith(prefix) for prefix in sdk_prefixes):
        return True

    # PascalCase class/type names (starts with capital, has more capitals)
    if pattern[0].isupper():
        # Count capital letters - class names typically have 2+
        caps = sum(1 for c in pattern if c.isupper())
        if caps >= 2:
            return True

    return False


def _is_valid_replacement(find: str, replace: str) -> bool:
    """Check if a find/replace pair is valid (not a parsing artifact)."""
    # Replacement shouldn't be a single character or very short
    if len(replace) < 3:
        return False

    # Replacement shouldn't be common words
    if replace.lower() in {'a', 'an', 'the', 'to', 'or', 'and', 'is', 'it', 'as', 'on', 'in'}:
        return False

    return True


def _extract_from_text_patterns(content: str) -> List[Dict[str, Any]]:
    """Extract replacements from explicit text patterns.

    Looks for phrases like:
    - "Replace X with Y"
    - "X has been renamed to Y"
    - "Use Y instead of X"
    - "X → Y"
    """
    replacements = []

    # Pattern: "Replace X with Y"
    replace_pattern = r'[Rr]eplace\s+[`"]?([^`"\s]+)[`"]?\s+with\s+[`"]?([^`"\s.]+)[`"]?'
    for match in re.finditer(replace_pattern, content):
        old_val = match.group(1).strip('`"')
        new_val = match.group(2).strip('`"')
        if old_val and new_val and _is_valid_api_pattern(old_val) and _is_valid_replacement(old_val, new_val):
            replacements.append({
                "find": old_val,
                "replace": new_val,
                "description": f"Replace {old_val} with {new_val}",
                "context": "text",
                "is_simple": True,
            })

    # Pattern: "X has been renamed to Y" or "X is now Y"
    renamed_pattern = r'[`"]?(\w+(?:\.\w+)*)[`"]?\s+(?:has been renamed|is now|renamed|is now named)\s+(?:to\s+)?[`"]?(\w+(?:\.\w+)*)[`"]?'
    for match in re.finditer(renamed_pattern, content, re.IGNORECASE):
        old_val = match.group(1).strip('`"')
        new_val = match.group(2).strip('`"')
        if old_val and new_val and old_val != new_val and _is_valid_api_pattern(old_val) and _is_valid_replacement(old_val, new_val):
            replacements.append({
                "find": old_val,
                "replace": new_val,
                "description": f"Renamed: {old_val} → {new_val}",
                "context": "text",
                "is_simple": True,
            })

    # Pattern: "Use Y instead of X"
    instead_pattern = r'[Uu]se\s+[`"]?(\w+(?:\.\w+)*)[`"]?\s+instead\s+of\s+[`"]?(\w+(?:\.\w+)*)[`"]?'
    for match in re.finditer(instead_pattern, content):
        new_val = match.group(1).strip('`"')
        old_val = match.group(2).strip('`"')
        if old_val and new_val and _is_valid_api_pattern(old_val) and _is_valid_replacement(old_val, new_val):
            replacements.append({
                "find": old_val,
                "replace": new_val,
                "description": f"Use {new_val} instead of {old_val}",
                "context": "text",
                "is_simple": True,
            })

    return replacements


def _clean_api_string(api_str: str) -> str:
    """Clean an API string from a markdown table.

    Removes markdown formatting, backticks, and normalizes whitespace.
    """
    # Remove backticks
    cleaned = api_str.strip('`')
    # Remove markdown bold/italic
    cleaned = re.sub(r'\*+', '', cleaned)
    # Remove leading/trailing whitespace
    cleaned = cleaned.strip()
    # Remove common prefixes like "class func" or "var"
    cleaned = re.sub(r'^(class\s+func|static\s+func|func|var|let|init)\s+', '', cleaned)
    # Normalize whitespace
    cleaned = ' '.join(cleaned.split())
    return cleaned


def _is_simple_replacement(old_api: str, new_api: str) -> bool:
    """Determine if a replacement is simple (direct find/replace) or needs judgment.

    Simple replacements:
    - Same basic structure with name change (e.g., MessageCenter.shared → Airship.messageCenter)
    - Type renames (UANotificationOptions → UNAuthorizationOptions)

    Complex replacements:
    - Signature changes (different parameters)
    - Async/await additions
    - Throws additions
    """
    # If the new API contains "async" or "throws" that old doesn't have, it's complex
    if ("async" in new_api.lower() and "async" not in old_api.lower()):
        return False
    if ("throws" in new_api.lower() and "throws" not in old_api.lower()):
        return False

    # If parameter lists differ significantly, it's complex
    old_params = re.findall(r'\([^)]*\)', old_api)
    new_params = re.findall(r'\([^)]*\)', new_api)
    if old_params != new_params:
        # Check if it's just adding/removing throws
        if len(old_params) > 0 and len(new_params) > 0:
            old_p = old_params[0]
            new_p = new_params[0]
            # If params are very different, it's complex
            if len(old_p) > 0 and len(new_p) > 0:
                # Simple heuristic: if param count differs a lot
                old_count = old_p.count(',')
                new_count = new_p.count(',')
                if abs(old_count - new_count) > 1:
                    return False

    # Check for pure renames: similar word-count signals a name-only change
    old_parts = re.findall(r'\w+', old_api)
    new_parts = re.findall(r'\w+', new_api)

    if len(old_parts) > 0 and len(new_parts) > 0:
        if abs(len(old_parts) - len(new_parts)) <= 2:
            return True

    # Structural difference is too large to be a safe find/replace
    return False


def _extract_api_calls(code: str) -> List[str]:
    """Extract API call patterns from code.

    Looks for common Swift/Kotlin API patterns:
    - ClassName.methodName
    - ClassName.shared.methodName
    - variable.methodName(args)
    """
    apis = []

    # Pattern for static method calls: ClassName.methodName or ClassName.shared.method
    static_pattern = r'\b([A-Z]\w+(?:\.\w+)+)'
    for match in re.finditer(static_pattern, code):
        api = match.group(1)
        # Filter out common non-API patterns
        if not api.startswith('UI') or 'Airship' in api or 'UA' in api:
            apis.append(api)

    # Pattern for notification names
    notif_pattern = r'\.(\w+Notification|\w+Event)'
    for match in re.finditer(notif_pattern, code):
        apis.append(match.group(0))

    return apis


def _apis_are_related(old_api: str, new_api: str) -> bool:
    """Check if two APIs are related (likely a rename or refactor).

    Compares API strings to see if they represent the same concept.
    """
    # Extract the base class/type names
    old_parts = old_api.split('.')
    new_parts = new_api.split('.')

    # Check for common words
    old_words = set(re.findall(r'[A-Z][a-z]+', old_api))
    new_words = set(re.findall(r'[A-Z][a-z]+', new_api))

    # If they share significant words, they're related
    common = old_words & new_words
    if len(common) >= 1:
        return True

    # Check if last part (method name) is similar
    if old_parts and new_parts:
        old_last = old_parts[-1].lower()
        new_last = new_parts[-1].lower()
        # Simple similarity: same first 4 characters
        if len(old_last) >= 4 and len(new_last) >= 4:
            if old_last[:4] == new_last[:4]:
                return True

    return False


def categorize_replacements(
    replacements: List[Dict[str, Any]]
) -> Dict[str, List[Dict[str, Any]]]:
    """Categorize replacements into simple vs complex.

    Args:
        replacements: List of replacement dictionaries from extract_replacements()

    Returns:
        Dictionary with keys:
        - simple: Replacements that can be done via find/replace
        - complex: Replacements that need manual review
        - removals: APIs that were removed (need manual handling)
    """
    result = {
        "simple": [],
        "complex": [],
        "removals": [],
    }

    for r in replacements:
        if not r.get("replace"):
            result["removals"].append(r)
        elif r.get("is_simple", True):
            result["simple"].append(r)
        else:
            result["complex"].append(r)

    return result
