# HTML to Markdown converter
# Handles the specific HTML structure from The Building Coder blog

from html.parser import HTMLParser
import re


class HTMLToMarkdownConverter(HTMLParser):
    """Convert HTML to Markdown, preserving code blocks and structure."""
    
    def __init__(self):
        super().__init__()
        self.markdown = []
        self.current_tag = None
        self.list_level = 0
        self.in_pre = False
        self.in_code = False
        self.pre_content = []
        self.tag_stack = []
        
    def handle_starttag(self, tag, attrs):
        self.tag_stack.append(tag)
        
        if tag == 'h1':
            self.current_tag = 'h1'
        elif tag == 'h2':
            self.current_tag = 'h2'
        elif tag == 'h3':
            self.current_tag = 'h3'
        elif tag == 'h4':
            self.current_tag = 'h4'
        elif tag == 'h5':
            self.current_tag = 'h5'
        elif tag == 'h6':
            self.current_tag = 'h6'
        elif tag == 'p':
            self.current_tag = 'p'
        elif tag == 'pre':
            self.in_pre = True
            self.pre_content = []
            # Check if it has class="code"
            attrs_dict = dict(attrs)
            if attrs_dict.get('class') == 'code':
                self.current_tag = 'pre_code'
            else:
                self.current_tag = 'pre'
        elif tag == 'code' and not self.in_pre:
            self.in_code = True
            self.markdown.append('`')
        elif tag == 'ul':
            self.list_level += 1
            self.current_tag = 'ul'
        elif tag == 'ol':
            self.list_level += 1
            self.current_tag = 'ol'
        elif tag == 'li':
            self.current_tag = 'li'
        elif tag == 'a':
            attrs_dict = dict(attrs)
            href = attrs_dict.get('href', '')
            self.current_tag = ('a', href)
        elif tag == 'strong' or tag == 'b':
            self.markdown.append('**')
        elif tag == 'em' or tag == 'i':
            self.markdown.append('*')
        elif tag == 'br':
            self.markdown.append('  \n')
        elif tag == 'img':
            attrs_dict = dict(attrs)
            src = attrs_dict.get('src', '')
            alt = attrs_dict.get('alt', '')
            self.markdown.append(f'![{alt}]({src})')
        elif tag == 'hr':
            self.markdown.append('\n---\n\n')
        # Ignore style tags and their content
        elif tag == 'style':
            self.current_tag = 'style'
            
    def handle_endtag(self, tag):
        if self.tag_stack and self.tag_stack[-1] == tag:
            self.tag_stack.pop()
            
        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            self.markdown.append('\n\n')
            self.current_tag = None
        elif tag == 'p':
            self.markdown.append('\n\n')
            self.current_tag = None
        elif tag == 'pre':
            if self.in_pre:
                # Join pre content and add as code block
                content = ''.join(self.pre_content)
                # Clean up HTML entities and spans in code
                content = self.clean_code_content(content)
                self.markdown.append(f'```\n{content}\n```\n\n')
                self.in_pre = False
                self.pre_content = []
            self.current_tag = None
        elif tag == 'code' and not self.in_pre:
            self.markdown.append('`')
            self.in_code = False
        elif tag == 'ul' or tag == 'ol':
            self.list_level -= 1
            self.markdown.append('\n')
            self.current_tag = None
        elif tag == 'li':
            self.markdown.append('\n')
            self.current_tag = None
        elif tag == 'a':
            if isinstance(self.current_tag, tuple) and self.current_tag[0] == 'a':
                href = self.current_tag[1]
                # The link text is already added, now add the URL
                # We need to wrap what was just added
                # This is tricky - we'll handle it in handle_data
            self.current_tag = None
        elif tag in ['strong', 'b']:
            self.markdown.append('**')
        elif tag in ['em', 'i']:
            self.markdown.append('*')
        elif tag == 'style':
            self.current_tag = None
            
    def handle_data(self, data):
        # Skip content in style tags
        if self.current_tag == 'style':
            return
            
        if self.in_pre:
            self.pre_content.append(data)
        elif self.current_tag == 'h1':
            self.markdown.append(f'# {data.strip()}')
        elif self.current_tag == 'h2':
            self.markdown.append(f'## {data.strip()}')
        elif self.current_tag == 'h3':
            self.markdown.append(f'### {data.strip()}')
        elif self.current_tag == 'h4':
            self.markdown.append(f'#### {data.strip()}')
        elif self.current_tag == 'h5':
            self.markdown.append(f'##### {data.strip()}')
        elif self.current_tag == 'h6':
            self.markdown.append(f'###### {data.strip()}')
        elif self.current_tag == 'li':
            indent = '  ' * (self.list_level - 1)
            self.markdown.append(f'{indent}- {data.strip()}')
        elif isinstance(self.current_tag, tuple) and self.current_tag[0] == 'a':
            # Store link text and we'll add the URL on endtag
            href = self.current_tag[1]
            self.markdown.append(f'[{data}]({href})')
            self.current_tag = None  # Reset to avoid double processing
        else:
            # Regular text
            if data.strip():
                self.markdown.append(data)
            elif data:  # Preserve spaces
                # Only add space if we have content before it
                if self.markdown and not self.markdown[-1].endswith('\n'):
                    self.markdown.append(' ')
                    
    def clean_code_content(self, content):
        """Clean HTML entities and tags from code content."""
        # Remove span tags but keep content
        content = re.sub(r'<span[^>]*>', '', content)
        content = re.sub(r'</span>', '', content)
        
        # Convert HTML entities
        content = content.replace('&nbsp;', ' ')
        content = content.replace('&lt;', '<')
        content = content.replace('&gt;', '>')
        content = content.replace('&amp;', '&')
        content = content.replace('&quot;', '"')
        content = content.replace('&#39;', "'")
        
        return content
    
    def get_markdown(self):
        """Return the final markdown string."""
        result = ''.join(self.markdown)
        # Clean up multiple newlines
        result = re.sub(r'\n{3,}', '\n\n', result)
        return result.strip()


def convert_to_markdown(html_content):
    """
    Convert HTML content to Markdown.
    
    Args:
        html_content: String containing HTML
        
    Returns:
        String containing Markdown
    """
    # Remove DOCTYPE and html/body tags if present
    html_content = re.sub(r'<!DOCTYPE[^>]*>', '', html_content, flags=re.IGNORECASE)
    html_content = re.sub(r'<html[^>]*>', '', html_content, flags=re.IGNORECASE)
    html_content = re.sub(r'</html>', '', html_content, flags=re.IGNORECASE)
    html_content = re.sub(r'<body[^>]*>', '', html_content, flags=re.IGNORECASE)
    html_content = re.sub(r'</body>', '', html_content, flags=re.IGNORECASE)
    html_content = re.sub(r'<head[^>]*>.*?</head>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    
    converter = HTMLToMarkdownConverter()
    converter.feed(html_content)
    return converter.get_markdown()
