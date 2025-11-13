"""
Async conversion example
"""

import asyncio
from conversiontools import ConversionToolsClient


async def main():
    # Initialize client
    client = ConversionToolsClient({
        'api_token': 'your-api-token'
    })

    # Convert XML to Excel (async)
    print("Converting XML to Excel (async)...")
    await client.convert_async(
        'convert.xml_to_excel',
        'test.xml',
        'result.xlsx'
    )
    print("Conversion complete! Result saved to result.xlsx")

    # Advanced: Manual control with async
    print("\nManual control example...")

    # Upload file
    file_id = await client.files.upload_async('data.json')
    print(f"File uploaded: {file_id}")

    # Create task
    task = await client.create_task_async(
        'convert.json_to_excel',
        {'file_id': file_id}
    )
    print(f"Task created: {task.id}")

    # Wait for completion
    await task.wait_async()
    print(f"Task completed with status: {task.status}")

    # Download result
    output_path = await task.download_to_async('result.xlsx')
    print(f"Result downloaded to: {output_path}")


if __name__ == '__main__':
    asyncio.run(main())
