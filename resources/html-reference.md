# Message Center HTML Reference

This document describes the HTML tags and styling supported in Airship Message Center messages.

## Supported HTML Tags

Message Center messages support a subset of HTML for rich content rendering:

### Text Formatting
| Tag | Description | Example |
|-----|-------------|---------|
| `<p>` | Paragraph | `<p>Your message text here.</p>` |
| `<br>` | Line break | `First line<br>Second line` |
| `<strong>`, `<b>` | Bold text | `<strong>Important</strong>` |
| `<em>`, `<i>` | Italic text | `<em>Emphasized</em>` |
| `<u>` | Underlined text | `<u>Underlined</u>` |

### Headings
| Tag | Description |
|-----|-------------|
| `<h1>` - `<h6>` | Heading levels 1-6 |

### Links
| Tag | Description | Example |
|-----|-------------|---------|
| `<a href="">` | Hyperlink | `<a href="https://example.com">Click here</a>` |

### Lists
| Tag | Description |
|-----|-------------|
| `<ul>` | Unordered (bulleted) list |
| `<ol>` | Ordered (numbered) list |
| `<li>` | List item |

### Structure
| Tag | Description |
|-----|-------------|
| `<div>` | Block container |
| `<span>` | Inline container |

### Images
| Tag | Description | Example |
|-----|-------------|---------|
| `<img>` | Image (HTTPS required) | `<img src="https://example.com/image.png" alt="Description">` |

## Best Practices

1. **Keep content simple and readable**
   - Message center is typically viewed on mobile devices
   - Avoid overly complex layouts

2. **Test on both iOS and Android**
   - Rendering may vary slightly between platforms
   - Always preview before sending to production

3. **Use relative sizing**
   - Avoid fixed pixel widths
   - Let content flow naturally for different screen sizes

4. **Include alt text for images**
   - Improves accessibility
   - Shows fallback if image fails to load

5. **Use inline styles sparingly**
   - Only basic inline CSS is supported
   - Complex styles may not render correctly

## Example

```html
<h1>Welcome to Our Service!</h1>
<p>Thank you for signing up. Here's what you can do next:</p>
<ul>
  <li><strong>Complete your profile</strong> - Add your preferences</li>
  <li><strong>Explore features</strong> - See what's available</li>
  <li><strong>Get support</strong> - Contact us anytime</li>
</ul>
<p>
  <a href="https://example.com/get-started">Get Started Now</a>
</p>
<p><em>This message will expire in 7 days.</em></p>
```

## Limitations

- **No JavaScript** - Scripts are not executed in message center
- **No external stylesheets** - Only inline styles are supported
- **No iframes** - Embedded frames are not rendered
- **HTTPS required for images** - HTTP image URLs will not load
- **Limited CSS support** - Only basic inline styles work reliably
- **No form elements** - Input fields, buttons (other than links) not supported

## Styling with Inline CSS

Limited inline CSS is supported:

```html
<p style="color: #333; font-size: 16px;">Styled text</p>
<div style="padding: 10px; background-color: #f5f5f5;">Highlighted section</div>
```

**Commonly supported properties:**
- `color`, `background-color`
- `font-size`, `font-weight`, `font-style`
- `text-align`, `text-decoration`
- `padding`, `margin`
- `border`, `border-radius`

**Note:** Complex CSS (flexbox, grid, animations) is not supported.

---

*For the latest supported features, test messages in your development environment before production deployment.*
