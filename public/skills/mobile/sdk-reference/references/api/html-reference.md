# HTML Reference for Message Center

## Supported HTML Elements

### Text Elements
- `<h1>` to `<h6>` - Headings
- `<p>` - Paragraphs
- `<span>` - Inline text
- `<strong>`, `<b>` - Bold text
- `<em>`, `<i>` - Italic text
- `<u>` - Underlined text
- `<br>` - Line breaks

### Lists
- `<ul>`, `<ol>` - Unordered/ordered lists
- `<li>` - List items

### Links and Buttons
- `<a href="...">` - Links (support deep links)
- Deep link format: `app://path/to/screen`
- External links: `https://example.com`

### Layout
- `<div>` - Block containers
- `<section>` - Semantic sections
- `<header>`, `<footer>` - Semantic layout

### Media (Limited Support)
- `<img src="...">` - Images (use HTTPS URLs)
- Base64 encoded images supported

## Styling Guidelines

### Inline Styles Only
```html
<div style="color: #333; font-size: 16px;">
    Content here
</div>
```

### Common Style Patterns

#### Buttons
```html
<a href="app://action" 
   style="display: inline-block;
          padding: 12px 24px;
          background: #007AFF;
          color: white;
          text-decoration: none;
          border-radius: 8px;
          font-weight: 600;">
    Click Me
</a>
```

#### Cards
```html
<div style="background: white;
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            padding: 20px;
            margin: 10px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
    Card content
</div>
```

#### Gradients
```html
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;">
    Gradient background
</div>
```

## Platform Differences

### iOS
- Supports most HTML5 elements
- Better gradient support
- System fonts: -apple-system

### Android
- May have limited gradient support
- System fonts: Roboto
- Test complex layouts

## Best Practices
1. Keep HTML under 10KB
2. Optimize images (use CDN)
3. Test on both platforms
4. Use semantic HTML
5. Ensure accessibility
6. Avoid JavaScript (not supported)
7. No external stylesheets