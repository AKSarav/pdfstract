"""
Example demonstrating PDFStract library usage

This shows how to use PDFStract as a Python library in your own code,
without needing the CLI.
"""

import asyncio
from pathlib import Path
import os
from pdfstract import PDFStract, convert_pdf, list_available_libraries


def example_basic_conversion():
    """Example 1: Basic PDF conversion"""
    print("=" * 60)
    print("Example 1: Basic PDF Conversion")
    print("=" * 60)
    
    pdfstract = PDFStract()
    
    # List available libraries
    libs = pdfstract.list_available_libraries()
    print(f"Available libraries: {libs}\n")
    
    # Convert a PDF to markdown
    pdf_path = os.path.join(os.getcwd(), "tests/samples/sample1.pdf")
    if Path(pdf_path).exists():
        result = pdfstract.convert(pdf_path, library="marker")
        print(f"✓ Converted {pdf_path} with marker")
        print(f"Content preview (first 200 chars):\n{result[:200]}...\n")
    else:
        print(f"(Skipping - {pdf_path} not found)\n")


def example_quick_conversion():
    """Example 2: Quick one-liner conversion"""
    print("=" * 60)
    print("Example 2: Quick One-liner Conversion")
    print("=" * 60)
    
    pdf_path = os.path.join(os.getcwd(), "tests/samples/sample1.pdf")  # Replace with your PDF path
    if Path(pdf_path).exists():
        # Using the convenience function
        result = convert_pdf(pdf_path, library="pymupdf4llm")
        print(f"✓ Quick converted with one-liner")
        print(f"Content length: {len(result)} chars\n")
    else:
        print(f"(Skipping - {pdf_path} not found)\n")


def example_list_converters():
    """Example 3: List converter details"""
    print("=" * 60)
    print("Example 3: List Converter Details")
    print("=" * 60)
    
    pdfstract = PDFStract()
    all_libs = pdfstract.list_libraries()
    
    print("All converters:\n")
    for lib in all_libs:
        status = "✓ Available" if lib["available"] else "✗ Not available"
        print(f"  {lib['name']:20} {status}")
        if lib["error"]:
            print(f"    Error: {lib['error']}")
    print()


def example_batch_conversion():
    """Example 4: Batch conversion with parallelization"""
    print("=" * 60)
    print("Example 4: Batch Conversion")
    print("=" * 60)
    
    pdfstract = PDFStract()
    
    pdf_dir = os.path.join(os.getcwd(), "tests/samples")
    if Path(pdf_dir).exists():
        results = pdfstract.batch_convert(
            pdf_directory=pdf_dir,
            library="marker",
            output_format="markdown",
            parallel_workers=4
        )
        
        print(f"Batch conversion results:")
        print(f"  ✓ Success: {results['success']}")
        print(f"  ✗ Failed: {results['failed']}")
        print(f"  Total: {results['success'] + results['failed']}\n")
    else:
        print(f"(Skipping - {pdf_dir} directory not found)\n")


async def example_async_conversion():
    """Example 5: Async PDF conversion"""
    print("=" * 60)
    print("Example 5: Async Conversion")
    print("=" * 60)
    
    pdfstract = PDFStract()
    
    pdf_path = os.path.join(os.getcwd(), "tests/samples/sample1.pdf")
    if Path(pdf_path).exists():
        # Async conversion for non-blocking I/O
        result = await pdfstract.convert_async(
            pdf_path=pdf_path,
            library="docling",
            output_format="json"
        )
        
        print(f"✓ Async converted {pdf_path} to JSON")
        if isinstance(result, dict):
            print(f"  Result type: dict with keys {list(result.keys())}")
        else:
            print(f"  Result type: {type(result).__name__}")
        print()
    else:
        print(f"(Skipping - {pdf_path} not found)\n")


def example_get_converter_info():
    """Example 6: Get information about specific converter"""
    print("=" * 60)
    print("Example 6: Get Converter Info")
    print("=" * 60)
    
    pdfstract = PDFStract()
    
    # Get info about a specific converter
    info = pdfstract.get_converter_info("marker")
    if info:
        print(f"Converter: {info['name']}")
        print(f"  Available: {info['available']}")
        print(f"  Error: {info.get('error', 'None')}\n")
    else:
        print("Converter 'marker' not found\n")


def example_error_handling():
    """Example 7: Error handling"""
    print("=" * 60)
    print("Example 7: Error Handling")
    print("=" * 60)
    
    pdfstract = PDFStract()
    
    # Handling non-existent file
    try:
        result = pdfstract.convert("nonexistent.pdf", "marker")
    except FileNotFoundError as e:
        print(f"✓ Caught FileNotFoundError: {e}\n")
    
    # Handling unavailable library (use a PDF that doesn't need to exist in error case)
    try:
        # This will fail on converter availability before trying to open file
        result = pdfstract.convert("dummy.pdf", "nonexistent_library")
    except ValueError as e:
        print(f"✓ Caught ValueError: {str(e)[:70]}...\n")


def main():
    """Run all examples"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  PDFStract Library Usage Examples".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    # Run synchronous examples
    example_list_converters()
    example_basic_conversion()
    example_quick_conversion()
    example_get_converter_info()
    example_batch_conversion()
    example_error_handling()
    
    # Run async example
    asyncio.run(example_async_conversion())
    
    print("=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
