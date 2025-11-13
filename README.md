# Conversion Tools Python Client (v2)

[![PyPI version](https://badge.fury.io/py/conversiontools.svg)](https://pypi.org/project/conversiontools/)
[![Python Version](https://img.shields.io/pypi/pyversions/conversiontools.svg)](https://pypi.org/project/conversiontools/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Modern Python library for converting files using the [Conversion Tools API](https://conversiontools.io). Convert between 100+ file formats including XML, JSON, Excel, PDF, CSV, images, audio, video, and more.

## ✨ What's New in v2

- 🎯 **Full Type Hints** - Complete type annotations with IDE support
- 🔄 **Async Support** - Both sync and async APIs using httpx
- 📊 **Progress Tracking** - Monitor upload, conversion, and download progress
- 🔄 **Smart Retry Logic** - Automatic retry with exponential backoff
- 🎨 **Better DX** - Cleaner API with improved error handling
- 🔌 **Webhook Support** - Async notifications for task completion
- 🧪 **Sandbox Mode** - Unlimited testing without consuming quota
- ⚡ **Modern Stack** - httpx, Python 3.8+, full type safety

## Installation

```bash
pip install conversiontools
```

Or with the latest version:

```bash
pip install --upgrade conversiontools
```

## Quick Start

### Synchronous API

```python
from conversiontools import ConversionToolsClient

# Initialize client
client = ConversionToolsClient({
    'api_token': 'your-api-token'  # Get from https://conversiontools.io/profile
})

# Convert XML to Excel
client.convert(
    'convert.xml_to_excel',
    'data.xml',
    'result.xlsx'
)
```

### Asynchronous API

```python
import asyncio
from conversiontools import ConversionToolsClient

async def main():
    client = ConversionToolsClient({
        'api_token': 'your-api-token'
    })

    # Convert XML to Excel (async)
    await client.convert_async(
        'convert.xml_to_excel',
        'data.xml',
        'result.xlsx'
    )

asyncio.run(main())
```

## Features

### 📁 100+ File Format Conversions

Convert between all major file formats:

- **Documents**: XML, JSON, Excel, PDF, CSV, Word, PowerPoint, Markdown
- **Images**: JPG, PNG, WebP, AVIF, HEIC, SVG, TIFF
- **eBooks**: ePUB, MOBI, AZW, AZW3, FB2
- **Audio**: MP3, WAV, FLAC
- **Video**: MP4, MOV, MKV, AVI
- **And more...**

### 🚀 Simple API

```python
# One-liner conversions
client.convert(
    'convert.json_to_excel',
    'data.json',
    'result.xlsx'
)

# With options
client.convert(
    'convert.xml_to_csv',
    'data.xml',
    'result.csv',
    options={
        'delimiter': 'comma',
        'quote': True
    }
)

# URL-based conversions
client.convert(
    'convert.website_to_pdf',
    {'url': 'https://example.com'},
    'website.pdf',
    options={
        'images': True,
        'javascript': True
    }
)

# File-like objects
with open('data.xml', 'rb') as f:
    client.convert(
        'convert.xml_to_excel',
        f,
        'result.xlsx'
    )
```

### 📊 Progress Tracking

```python
def upload_progress(progress):
    print(f"Upload: {progress['percent']}%")

def conversion_progress(progress):
    print(f"Converting: {progress['percent']}%")

def download_progress(progress):
    print(f"Download: {progress['percent']}%")

client = ConversionToolsClient({
    'api_token': 'your-token',
    'on_upload_progress': upload_progress,
    'on_conversion_progress': conversion_progress,
    'on_download_progress': download_progress
})

client.convert(
    'convert.pdf_to_excel',
    'large-file.pdf',
    'result.xlsx'
)
```

### 🎯 Type Hints Support

Full type safety with IDE support:

```python
from conversiontools import ConversionToolsClient, RateLimitError

client: ConversionToolsClient = ConversionToolsClient({
    'api_token': 'your-token'
})

# Type hints for all parameters
client.convert(
    conversion_type='convert.xml_to_csv',
    input='data.xml',
    output='result.csv',
    options={'delimiter': 'comma'}  # IDE suggests valid options
)
```

### 🔄 Advanced Control

For fine-grained control over the conversion process:

```python
# Step 1: Upload file
file_id = client.files.upload('data.xml')

# Step 2: Create task
task = client.create_task(
    conversion_type='convert.xml_to_excel',
    options={'file_id': file_id}
)

# Step 3: Wait for completion
def on_progress(status):
    print(f"Status: {status['status']}, Progress: {status['conversionProgress']}%")

task.wait({'on_progress': on_progress})

# Step 4: Download result
task.download_to('result.xlsx')
```

### Async Version

```python
# Async advanced control
file_id = await client.files.upload_async('data.xml')
task = await client.create_task_async(
    'convert.xml_to_excel',
    {'file_id': file_id}
)
await task.wait_async()
await task.download_to_async('result.xlsx')
```

### 🧪 Sandbox Mode

Test your integration without consuming quota:

```python
client.convert(
    'convert.json_to_excel',
    'test-data.json',
    'result.xlsx',
    options={'sandbox': True}  # ✨ Doesn't count against quota
)
```

### 🎨 Error Handling

Type-safe error handling:

```python
from conversiontools import (
    RateLimitError,
    ValidationError,
    ConversionError,
    FileNotFoundError
)

try:
    client.convert('convert.xml_to_excel', 'data.xml', 'result.xlsx')
except RateLimitError as e:
    print(f'Quota exceeded: {e.limits}')
    print('Upgrade at: https://conversiontools.io/api-pricing')
except ValidationError as e:
    print(f'Invalid input: {e.message}')
except ConversionError as e:
    print(f'Conversion failed: {e.message}')
except FileNotFoundError as e:
    print(f'File not found: {e.message}')
```

## API Reference

### ConversionToolsClient

#### Constructor

```python
ConversionToolsClient(config: dict)
```

**Config Options:**
- `api_token` (str, required) - API token from your profile
- `base_url` (str, optional) - API base URL (default: https://api.conversiontools.io/v1)
- `timeout` (float, optional) - Request timeout in ms (default: 300000 / 5 min)
- `retries` (int, optional) - Retry attempts (default: 3)
- `retry_delay` (float, optional) - Initial retry delay in ms (default: 1000)
- `polling_interval` (float, optional) - Status polling interval in ms (default: 5000)
- `max_polling_interval` (float, optional) - Max polling interval in ms (default: 30000)
- `webhook_url` (str, optional) - Webhook URL for task notifications
- `on_upload_progress` (callable, optional) - Upload progress callback
- `on_download_progress` (callable, optional) - Download progress callback
- `on_conversion_progress` (callable, optional) - Conversion progress callback

#### Methods

##### `convert(conversion_type, input, output=None, options=None, wait=True, callback_url=None, polling=None)`

Simple conversion method - handles upload, conversion, and download automatically.

##### `convert_async(...)` - Async version

##### `create_task(conversion_type, options, callback_url=None)`

Create a conversion task manually.

##### `create_task_async(...)` - Async version

##### `get_task(task_id)`

Get an existing task by ID.

##### `get_task_async(task_id)` - Async version

##### `get_rate_limits()`

Get rate limits from last API call.

```python
limits = client.get_rate_limits()
# {'daily': {'limit': 30, 'remaining': 25}, 'monthly': {'limit': 300, 'remaining': 275}}
```

##### `get_user()`

Get authenticated user information.

```python
user = client.get_user()
# {'email': 'user@example.com'}
```

##### `get_user_async()` - Async version

### Files API

Accessible via `client.files`:

```python
# Upload file
file_id = client.files.upload('file.xml')

# Get file info
info = client.files.get_info(file_id)

# Download file
client.files.download_to(file_id, 'output.xlsx')
file_bytes = client.files.download_bytes(file_id)

# Async versions
file_id = await client.files.upload_async('file.xml')
info = await client.files.get_info_async(file_id)
await client.files.download_to_async(file_id, 'output.xlsx')
```

### Tasks API

Accessible via `client.tasks`:

```python
# Create task
response = client.tasks.create({
    'type': 'convert.xml_to_excel',
    'options': {'file_id': 'xxx'}
})

# Get task status
status = client.tasks.get_status('task-id')

# List tasks
tasks = client.tasks.list(status='SUCCESS')

# Async versions
response = await client.tasks.create_async({...})
status = await client.tasks.get_status_async('task-id')
tasks = await client.tasks.list_async(status='SUCCESS')
```

### Task Model

```python
# Task properties
task.id              # Task ID
task.status          # 'PENDING' | 'RUNNING' | 'SUCCESS' | 'ERROR'
task.file_id         # Result file ID
task.error           # Error message (if failed)
task.conversion_progress  # Progress (0-100)

# Task methods
task.refresh()                # Refresh status
task.wait()                   # Wait for completion
task.download_to('output.xlsx')  # Download result
file_bytes = task.download_bytes()  # Get as bytes

# Async versions
await task.refresh_async()
await task.wait_async()
await task.download_to_async('output.xlsx')
```

## Common Conversion Types

Here are some frequently used conversion types:

### Document Conversions

```python
# XML to Excel
client.convert('convert.xml_to_excel', 'data.xml', 'result.xlsx')

# JSON to Excel
client.convert('convert.json_to_excel', 'data.json', 'result.xlsx')

# Excel to CSV
client.convert(
    'convert.excel_to_csv',
    'data.xlsx',
    'result.csv',
    options={'delimiter': 'comma'}
)

# PDF to Text
client.convert('convert.pdf_to_text', 'document.pdf', 'document.txt')

# Word to PDF
client.convert('convert.word_to_pdf', 'document.docx', 'document.pdf')
```

### Image Conversions

```python
# PDF to JPG
client.convert(
    'convert.pdf_to_jpg',
    'document.pdf',
    'image.jpg',
    options={
        'image_resolution': '300',
        'jpeg_quality': 90
    }
)

# PNG to WebP
client.convert(
    'convert.png_to_webp',
    'image.png',
    'image.webp',
    options={'webp_quality': 85}
)
```

### Website Conversions

```python
# Website to PDF
client.convert(
    'convert.website_to_pdf',
    {'url': 'https://example.com'},
    'website.pdf',
    options={
        'images': True,
        'javascript': True,
        'orientation': 'Portrait'
    }
)

# Website to JPG
client.convert(
    'convert.website_to_png',
    {'url': 'https://example.com'},
    'screenshot.png'
)
```

### OCR (Text Recognition)

```python
# OCR PDF to Text
client.convert(
    'convert.ocr_pdf_to_text',
    'scanned.pdf',
    'text.txt',
    options={'language_ocr': 'eng'}  # or 'eng+fra' for multiple languages
)
```

For a complete list of conversion types, see the [API Documentation](https://conversiontools.io/api-documentation).

## Migrating from v1.0.0 to v2.0.0

Python v2.0.0 introduces breaking changes for better API design, type safety, and async support. This guide will help you migrate your existing v1.0.0 code.

### What's New in v2.0.0

- ✅ **Full Type Hints** - Complete type annotations for better IDE support
- ✅ **Async Support** - Both sync and async APIs
- ✅ **Better Error Handling** - Specific error classes instead of generic exceptions
- ✅ **Retry Logic** - Automatic retry with exponential backoff
- ✅ **Progress Tracking** - Monitor upload, download, and conversion progress
- ✅ **Improved API** - More consistent method signatures
- ✅ **Modern Dependencies** - Uses `httpx` instead of `requests`

### Breaking Changes

#### 1. Class Name Changed

```python
# v1.0.0
from conversiontools import ConversionClient

# v2.0.0
from conversiontools import ConversionToolsClient
```

#### 2. Client Initialization

```python
# v1.0.0
client = ConversionClient('your-token')

# v2.0.0
client = ConversionToolsClient({
    'api_token': 'your-token'
})
```

The v2 constructor now accepts a configuration dictionary, allowing you to set additional options:

```python
# v2.0.0 with additional options
client = ConversionToolsClient({
    'api_token': 'your-token',
    'timeout': 300000,
    'retries': 3,
    'polling_interval': 5000
})
```

#### 3. convert() Method Signature

```python
# v1.0.0
client.convert(
    'convert.xml_to_csv',
    'input.xml',
    'output.csv',
    {'delimiter': 'tabulation'}  # Options as 4th positional argument
)

# v2.0.0
client.convert(
    'convert.xml_to_csv',
    'input.xml',
    'output.csv',
    options={'delimiter': 'tabulation'}  # Options as keyword argument
)
```

#### 4. Error Handling

```python
# v1.0.0
try:
    client.convert(...)
except Exception as e:
    print(f"Error: {e}")

# v2.0.0
from conversiontools import (
    ConversionToolsError,
    RateLimitError,
    ValidationError,
    ConversionError
)

try:
    client.convert(...)
except RateLimitError as e:
    print(f"Quota exceeded: {e.limits}")
except ValidationError as e:
    print(f"Invalid input: {e.message}")
except ConversionError as e:
    print(f"Conversion failed: {e.message}")
except ConversionToolsError as e:
    print(f"API error: {e.message}")
```

### Migration Examples

#### Basic Conversion

```python
# v1.0.0
from conversiontools import ConversionClient

client = ConversionClient('your-token')
client.convert('convert.xml_to_csv', 'test.xml', 'test.csv', {'delimiter': 'tabulation'})
```

```python
# v2.0.0
from conversiontools import ConversionToolsClient

client = ConversionToolsClient({'api_token': 'your-token'})
client.convert('convert.xml_to_csv', 'test.xml', 'test.csv', options={'delimiter': 'tabulation'})
```

#### With Progress Tracking (New in v2.0.0)

```python
# v2.0.0 only
from conversiontools import ConversionToolsClient

def on_progress(progress):
    print(f"Progress: {progress['percent']}%")

client = ConversionToolsClient({
    'api_token': 'your-token',
    'on_conversion_progress': on_progress
})

client.convert('convert.xml_to_csv', 'test.xml', 'test.csv')
```

#### Async Support (New in v2.0.0)

```python
# v2.0.0 only
import asyncio
from conversiontools import ConversionToolsClient

async def main():
    client = ConversionToolsClient({'api_token': 'your-token'})

    await client.convert_async(
        'convert.xml_to_csv',
        'test.xml',
        'test.csv',
        options={'delimiter': 'tabulation'}
    )

asyncio.run(main())
```

### Quick Migration Checklist

- [ ] Change `ConversionClient` to `ConversionToolsClient`
- [ ] Update initialization: `ConversionClient(token)` → `ConversionToolsClient({'api_token': token})`
- [ ] Add `options=` keyword to `convert()` calls
- [ ] Update exception handling to use specific error classes
- [ ] Consider adding progress callbacks
- [ ] Consider using async methods for better performance

### Should You Upgrade?

**Upgrade to v2.0.0 if you want:**
- Type hints and better IDE autocomplete
- Async/await support
- Better error handling
- Progress tracking
- Retry logic

**Stay on v1.0.0 if:**
- You have a large codebase and can't migrate immediately
- You don't need the new features
- Your code is stable and working

**Note:** v1.0.0 will continue to work but won't receive new features. Security and critical bug fixes may still be backported.

## Examples

See the [`examples/`](./examples) directory for more examples:

- [Simple conversion](./examples/simple_conversion.py)
- [With progress tracking](./examples/with_progress.py)
- [Advanced manual control](./examples/advanced_control.py)
- [Sandbox testing](./examples/sandbox_testing.py)
- [URL-based conversions](./examples/url_conversion.py)
- [Async usage](./examples/async_example.py)

## Requirements

- Python 3.8 or higher
- API token from [Conversion Tools](https://conversiontools.io/profile)

## License

[MIT](./LICENSE)

## Support

- 📚 [API Documentation](https://conversiontools.io/api-documentation)
- 🐛 [Report Issues](https://github.com/conversiontools/conversiontools-python/issues)
- 💬 [Contact Support](https://conversiontools.io/contact)
- 🌐 [Website](https://conversiontools.io)

---

**Made with ❤️ by [Conversion Tools](https://conversiontools.io)**
