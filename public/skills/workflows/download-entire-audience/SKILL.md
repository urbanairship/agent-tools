---
name: download-entire-audience
description: Download an entire audience by leveraging parallel pagination across UUID prefixes. Uses 16 parallel threads, each handling channels starting with a different hex digit (0-9, a-f). Use when you need to export all channels, perform bulk operations, or synchronize channel data.
---

# Download Entire Audience Workflow

This workflow downloads an entire audience from Airship by leveraging the sorted ordering of channel IDs (UUIDs) to enable efficient parallel pagination. Instead of paginating sequentially through all channels, this workflow uses 16 parallel threads, each handling channels that start with a different hexadecimal digit (0-9, a-f).

## Prerequisites

- Airship account with API access
- Ability to make parallel API requests (16 concurrent requests)
- Understanding of UUID format and hexadecimal characters

## Skills Required

- **[Channel Listing](../../../skills/api/channel-listing/SKILL.md)** - List channels with pagination support

## Strategy Overview

Channel IDs in Airship are UUIDs (e.g., `9c36e8c7-5a73-47c0-9716-99fd3d4197d5`), which are returned in sorted order by the channel listing API. UUIDs use hexadecimal characters (0-9, a-f), providing 16 possible starting characters.

**Key Insight**: Since UUIDs are evenly distributed across the ASCII-bet (alphabetical including numbers), we can split the pagination work across 16 threads, each handling channels starting with one hex digit. Each thread paginates until it encounters a channel ID starting with the next hex digit, at which point it stops.

**Benefits**:
- **Parallelization**: 16x faster than sequential pagination
- **Efficient**: Each thread only processes ~1/16th of the total channels
- **Complete**: No channels are missed or duplicated
- **Scalable**: Works regardless of audience size

## Step 1: Initialize 16 Threads

Create 16 parallel threads, each assigned to one hexadecimal digit:

**Hex Digits**: `0`, `1`, `2`, `3`, `4`, `5`, `6`, `7`, `8`, `9`, `a`, `b`, `c`, `d`, `e`, `f`

For each thread, construct a starting UUID that begins with that hex digit. The simplest approach is to use the minimum UUID for that prefix:

```json
Thread 0:  "00000000-0000-0000-0000-000000000000"
Thread 1:  "10000000-0000-0000-0000-000000000000"
Thread 2:  "20000000-0000-0000-0000-000000000000"
Thread 3:  "30000000-0000-0000-0000-000000000000"
Thread 4:  "40000000-0000-0000-0000-000000000000"
Thread 5:  "50000000-0000-0000-0000-000000000000"
Thread 6:  "60000000-0000-0000-0000-000000000000"
Thread 7:  "70000000-0000-0000-0000-000000000000"
Thread 8:  "80000000-0000-0000-0000-000000000000"
Thread 9:  "90000000-0000-0000-0000-000000000000"
Thread a:  "a0000000-0000-0000-0000-000000000000"
Thread b:  "b0000000-0000-0000-0000-000000000000"
Thread c:  "c0000000-0000-0000-0000-000000000000"
Thread d:  "d0000000-0000-0000-0000-000000000000"
Thread e:  "e0000000-0000-0000-0000-000000000000"
Thread f:  "f0000000-0000-0000-0000-000000000000"
```

**Note**: These are theoretical starting points. In practice, you may not have channels starting with these exact UUIDs. The API will return the first channel that is greater than or equal to your `start` parameter.

## Step 2: Paginate Each Thread

For each thread, make paginated requests to the channel listing API:

```json
GET /api/channels?limit=1000&start={thread_start_uuid}
Authorization: Bearer <token>
Accept: application/vnd.urbanairship+json; version=3
```

**Response**:
```json
{
  "ok": true,
  "channels": [
    {
      "channel_id": "9c36e8c7-5a73-47c0-9716-99fd3d4197d5",
      "device_type": "ios",
      "installed": true,
      "opt_in": true,
      "push_address": "FE66489F304DC75B8D6E8200DFF8A456E8DAEACEC428B427E9518741C92C6660",
      "created": "2020-08-08T20:41:06",
      "last_registration": "2020-10-07T21:28:35",
      "named_user_id": "some_id_that_maps_to_your_systems",
      "tags": ["tag1", "tag2"],
      "tag_groups": {
        "tag_group_1": ["tag1", "tag2"]
      }
    }
  ],
  "next_page": "https://go.urbanairship.com/api/channels?limit=1000&start=535ec31e-4b07-4b26-bead-a1c0e94e133c"
}
```

## Step 3: Check for Thread Completion

For each thread, continue paginating using the `next_page` URL or extracting the `start` parameter from the `next_page` URL. After processing each page:

1. **Check the first character** of each channel ID in the response
2. **If any channel ID starts with the next hex digit**, the thread has reached its boundary
3. **Stop the thread** when you encounter a channel ID starting with the next hex digit

**Example for Thread 9 (handling channels starting with '9')**:
- Continue paginating while channel IDs start with '9'
- When you encounter a channel ID starting with 'a' (the next hex digit), stop this thread
- The 'a' channel will be handled by Thread a

**Boundary Logic**:
```python
# Pseudocode for thread boundary detection
current_thread_hex = '9'
next_thread_hex = 'a'

for channel in response['channels']:
    channel_id_first_char = channel['channel_id'][0].lower()
    
    if channel_id_first_char == next_thread_hex:
        # This channel belongs to the next thread
        # Stop processing this thread
        break
    
    # Process this channel (it belongs to current thread)
    process_channel(channel)
```

## Step 4: Handle Edge Cases

### Empty Ranges
Some hex digits may have no channels. If a thread's first request returns no channels or channels starting with the next hex digit, that thread completes immediately.

### Last Thread (Thread f)
Thread f handles channels starting with 'f'. Since 'f' is the last hex digit, this thread continues until there are no more pages (`next_page` is null or empty).

### Boundary Channels
When a thread encounters a channel starting with the next hex digit, that channel should be included in the current thread's results (it's the boundary marker), but the thread should stop after processing it.

## Step 5: Combine Results

Once all 16 threads complete:

1. **Merge results** from all threads into a single collection
2. **Sort if needed** (though results should already be sorted within each thread)
3. **Deduplicate** if necessary (though the parallel approach should prevent duplicates)
4. **Export or process** the complete audience data

## Example Implementation Pattern

```python
# Pseudocode for parallel pagination
import concurrent.futures
import requests

hex_digits = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']

def paginate_thread(hex_digit, next_hex_digit):
    """Paginate channels starting with hex_digit until reaching next_hex_digit"""
    all_channels = []
    start_uuid = f"{hex_digit}0000000-0000-0000-0000-000000000000"
    
    while True:
        response = requests.get(
            'https://go.urbanairship.com/api/channels',
            params={'limit': 1000, 'start': start_uuid},
            headers={'Authorization': 'Bearer <token>'}
        )
        data = response.json()
        
        for channel in data['channels']:
            channel_id_first_char = channel['channel_id'][0].lower()
            
            # Check if we've reached the next thread's boundary
            if channel_id_first_char == next_hex_digit:
                # Include this boundary channel, then stop
                all_channels.append(channel)
                return all_channels
            
            # Check if channel belongs to this thread
            if channel_id_first_char == hex_digit:
                all_channels.append(channel)
            else:
                # Unexpected: channel doesn't match thread prefix
                # This shouldn't happen with proper ordering
                continue
        
        # Check for next page
        if not data.get('next_page'):
            break
        
        # Extract start parameter from next_page URL
        start_uuid = extract_start_from_url(data['next_page'])
    
    return all_channels

# Execute all threads in parallel
with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
    futures = []
    for i, hex_digit in enumerate(hex_digits):
        next_hex_digit = hex_digits[i + 1] if i < 15 else None
        future = executor.submit(paginate_thread, hex_digit, next_hex_digit)
        futures.append(future)
    
    # Collect results
    all_results = []
    for future in concurrent.futures.as_completed(futures):
        all_results.extend(future.result())

# all_results now contains the entire audience
```

## Outcomes

- Complete audience downloaded efficiently using parallel pagination
- All channels retrieved without duplicates or gaps
- Significantly faster than sequential pagination (up to 16x speedup)
- Results ready for export, analysis, or bulk operations

## Use Cases

- **Data Export**: Export all channels for backup or migration
- **Bulk Operations**: Perform operations on entire audience
- **Data Synchronization**: Sync channel data with external systems
- **Analytics**: Analyze complete audience composition
- **Audit**: Verify channel counts and data integrity

## Performance Considerations

- **Rate Limiting**: Be aware of Airship API rate limits. Consider adding delays or using exponential backoff if needed
- **Memory**: For very large audiences, consider streaming results to disk rather than keeping all channels in memory
- **Thread Count**: 16 threads is optimal for hex digit distribution. Adjust based on your system capabilities and rate limits
- **Error Handling**: Implement retry logic for failed requests. Consider resuming from the last successful `start` UUID

## Related Workflows

- None currently

## Best Practices

1. **Monitor Progress**: Track progress across threads to identify any that are taking longer than expected
2. **Handle Failures**: If a thread fails, you can resume it from the last successful `start` UUID
3. **Validate Results**: After completion, verify the total count matches expected audience size
4. **Respect Rate Limits**: Implement appropriate delays or use rate limiting to avoid hitting API limits
5. **Logging**: Log thread progress and any boundary conditions encountered

## Additional Resources

- [Channel Listing Skill](../../../skills/api/channel-listing/SKILL.md) - Complete API documentation for channel listing
- [Channel Listing API Documentation](https://docs.airship.com/developer/rest-api/ua/operations/channels/#channellisting)
- [Pagination Best Practices](https://docs.airship.com/developer/rest-api/ua/operations/#pagination)
