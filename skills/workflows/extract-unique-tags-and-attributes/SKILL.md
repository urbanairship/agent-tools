---
name: extract-unique-tags-and-attributes
description: Extract a metadata-only JSON object of unique tags grouped by tag group (including synthetic device_tags), unique attribute keys, unique device attribute keys, and unique subscription lists from audience data. Use when you need a taxonomy catalog without exporting audience identities.
---

# Extract Unique Tags and Attributes Workflow

This workflow composes the audience retrieval approach and outputs a single metadata-only JSON object. It is designed for taxonomy discovery, governance, and integration planning, while explicitly excluding channel-level and user-level identifiers from output.

## Prerequisites

- Airship account with API access
- Ability to call channel listing endpoints (directly or via workflow composition)
- JSON processing capability (Python, JavaScript, jq, or similar)
- Agreement on normalization policy (for example `ios` and `IOS` collapse to `ios`)

## Skills Required

- **[Download Entire Audience Workflow](../download-entire-audience/SKILL.md)** - Retrieve audience data efficiently
- **[Channel Listing](../../../skills/api/channel-listing/SKILL.md)** - Underlying paginated source endpoint

## Output Contract

Produce one JSON object with this structure:

```json
{
  "tag_groups": {
    "device_tags": ["imported_token", "tag_example"],
    "ua_mobile_platform": ["android", "ios"],
    "ua_opt_in": ["false", "true"],
    "named_user_id": []
  },
  "attributes": ["cid"],
  "device_attributes": ["ua_named_user_id", "ua_device_os"],
  "subscription_lists": ["list_a", "list_b"],
  "excluded": {
    "tag_group_values": ["named_user_id"]
  }
}
```

## Privacy Rules

- Do not output channel IDs, named user IDs, aliases, push addresses, timestamps, or any per-row audience objects.
- Include `named_user_id` as a tag group key if present, but do not include its values.
- Keep only deduplicated metadata values in the final JSON object.

## Step 1: Retrieve Audience Data

Use the Download Entire Audience workflow to fetch channels at scale. You can execute this in parallel as documented there, but this workflow only keeps metadata fields during processing.

Expected channel fields of interest:

- `tags` (top-level array)
- `tag_groups` (object of group -> array of values)
- `attributes` (object keys only)
- `device_attributes` (object keys only)
- `subscription_lists` (array)

## Step 2: Initialize Aggregation Sets

Initialize in-memory sets (or equivalent deduplicated collections):

- `tag_groups_map`: map of `group_name -> set(values)`
- `attributes_set`
- `device_attributes_set`
- `subscription_lists_set`

Also initialize:

- synthetic tag group `device_tags` inside `tag_groups_map`
- excluded tag groups set: `{"named_user_id"}`

## Step 3: Extract and Normalize Metadata

For each channel record:

1. Fold top-level `tags` into `tag_groups_map["device_tags"]`.
2. Iterate `tag_groups`:
   - Normalize group name (recommended: lowercase).
   - If group name is `named_user_id`, create/retain the group key but skip values.
   - Otherwise add normalized values into that group set.
3. Add keys from `attributes` into `attributes_set`.
4. Add keys from `device_attributes` into `device_attributes_set`.
5. Add each entry in `subscription_lists` into `subscription_lists_set`.

Recommended value normalization:

- Trim whitespace
- Normalize case for platform-like/system values (`IOS` -> `ios`)
- Ignore empty strings / nulls

## Step 4: Build Final JSON Object

Convert each set to a sorted array for deterministic output:

- `tag_groups[group]` -> sorted array
- `attributes` -> sorted array
- `device_attributes` -> sorted array
- `subscription_lists` -> sorted array

Include explicit exclusions metadata:

```json
"excluded": {
  "tag_group_values": ["named_user_id"]
}
```

## Step 5: Validate Output Safety and Completeness

Validation checklist:

- Output is a single JSON object
- No audience identifiers or per-channel rows are present
- `tag_groups.device_tags` exists (even if empty)
- `named_user_id` appears as a group key with an empty array when observed in source data
- Arrays are deduplicated and sorted

## Outcomes

- Single metadata-only JSON artifact ready for taxonomy analysis
- Unique tags grouped by tag group (plus synthetic `device_tags`)
- Unique attribute and device attribute key catalogs
- Unique subscription list catalog
- Privacy-safe output without audience identity leakage

## Use Cases

- Build governance dictionaries for tags and attributes
- Review segmentation vocabulary across projects
- Prepare integration mappings without exporting audience-level data
- Detect casing inconsistencies and normalize taxonomy

## Related Workflows

- **[Download Entire Audience Workflow](../download-entire-audience/SKILL.md)** - Source retrieval workflow used for channel pagination

## Best Practices

1. Normalize early in extraction to prevent duplicate variants.
2. Keep exclusion rules explicit and testable (`named_user_id` values excluded).
3. Stream process channels and discard raw rows immediately.
4. Treat JSON output as generated metadata and re-create rather than manually editing.
5. Re-run periodically to detect taxonomy drift.

## Additional Resources

- [Channel Listing Skill](../../../skills/api/channel-listing/SKILL.md)
- [Download Entire Audience Workflow](../download-entire-audience/SKILL.md)
- [Airship Channel Listing API](https://docs.airship.com/developer/rest-api/ua/operations/channels/#channellisting)
