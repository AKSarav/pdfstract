#!/usr/bin/env python3
"""
PDFStract CLI - Command-line interface for PDF extraction and conversion
Provides: single conversions, multi-library comparisons, batch processing
"""

import click
import json
import os
import asyncio
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import csv
import sys

from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.panel import Panel
from rich.syntax import Syntax

from services.cli_factory import CLILazyFactory
from services.base import OutputFormat
from services.logger import logger
from services.chunker_factory import get_chunker_factory

# Import version for --version option (reads from api module which reads from pyproject.toml)
try:
    from api import __version__
except ImportError:
    __version__ = "1.1.0"  # Fallback version

# Rich console for beautiful output
console = Console()

# Factory (lazy initialized - uses lightweight CLILazyFactory)
_factory = None

def get_factory():
    """Get factory instance (lazy initialization to speed up CLI startup)"""
    global _factory
    if _factory is None:
        _factory = CLILazyFactory()
    return _factory


class PDFStractCLI:
    """Main CLI class handling all operations"""
    
    def __init__(self, lazy=True):
        self.console = console
        self._lazy = lazy
        self._factory = None
    
    @property
    def factory(self):
        """Get factory with lazy loading"""
        if self._factory is None:
            if not self._lazy:
                # Eager load for help/libs commands
                self._factory = get_factory()
            else:
                # For action commands, factory is initialized on first use
                self._factory = get_factory()
        return self._factory
    
    def print_banner(self):
        """Print CLI banner"""
        banner = f"""
[bold cyan]╔════════════════════════════════════════╗[/bold cyan]
[bold cyan]║         PDFStract CLI v{__version__:<16}║[/bold cyan]
[bold cyan]║    PDF Extraction & Chunking Layer     ║[/bold cyan]
[bold cyan]╚════════════════════════════════════════╝[/bold cyan]
        """
        self.console.print(banner)
    
    def print_success(self, msg: str):
        """Print success message"""
        self.console.print(f"[bold green]✓[/bold green] {msg}")
    
    def print_error(self, msg: str):
        """Print error message"""
        self.console.print(f"[bold red]✗[/bold red] {msg}")
    
    def print_warning(self, msg: str):
        """Print warning message"""
        self.console.print(f"[bold yellow]⚠[/bold yellow] {msg}")
    
    def print_info(self, msg: str):
        """Print info message"""
        self.console.print(f"[bold blue]ℹ[/bold blue] {msg}")
    
    def get_available_libraries(self) -> Dict:
        """Get all available libraries and their status"""
        return self.factory.list_all_converters()
    
    def get_available_formats(self) -> List[str]:
        """Get available output formats"""
        return [f.value for f in OutputFormat]


# Create CLI instance with lazy loading (don't load libraries until needed)
cli_app = PDFStractCLI(lazy=True)


def print_version(ctx, param, value):
    """Callback to print version and exit"""
    if value:
        console.print(f"pdfstract, version {__version__}")
        ctx.exit()


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option('--version', is_flag=True, callback=print_version, expose_value=False, is_eager=True, help="Show the version and exit.")
def pdfstract():
    """PDFStract - Unified PDF Extraction CLI Tool
    
    The Extraction and Chunking Layer in Your RAG Pipeline
    """
    pass


@pdfstract.command()
def libs():
    """List all available extraction libraries and their status"""
    cli_app.print_banner()
    
    # Initialize factory ONLY when listing libraries
    libraries = get_factory().list_all_converters()
    
    table = Table(title="Available PDF Extraction Libraries", show_lines=True)
    table.add_column("Library", style="cyan", no_wrap=True)
    table.add_column("Status", style="green")
    table.add_column("Download", style="blue")
    table.add_column("Notes", style="yellow")
    
    for lib in libraries:
        status = "[bold green]✓ Available[/bold green]" if lib["available"] else "[bold red]✗ Unavailable[/bold red]"
        
        # Show download status
        download_status = lib.get("download_status", "not_required")
        if download_status == "ready":
            download_col = "[bold green]✓ Ready[/bold green]"
        elif download_status == "downloading":
            download_col = "[bold yellow]⏳ Downloading...[/bold yellow]"
        elif download_status == "not_started" and lib.get("requires_download"):
            download_col = "[dim]⬇ Not downloaded[/dim]"
        elif download_status == "failed":
            download_col = "[bold red]✗ Failed[/bold red]"
        else:
            download_col = "[dim]N/A[/dim]"
        
        notes = lib.get("error", "") or ""
        if lib.get("download_error"):
            notes = lib["download_error"]
        
        table.add_row(lib["name"], status, download_col, notes if not lib["available"] else "")
    
    console.print(table)
    console.print()
    console.print("[dim]Use 'pdfstract download <library>' to download models on demand[/dim]")
    console.print("[dim]Use 'pdfstract convert --help' to get started with conversions[/dim]")


@pdfstract.command()
@click.argument('library_name')
@click.option('--all', '-a', 'download_all', is_flag=True, help='Download models for all available libraries')
def download(library_name: str, download_all: bool):
    """Download models for a specific library on demand
    
    This command downloads the required ML models for libraries like marker, docling, etc.
    Models are cached locally and only need to be downloaded once.
    
    Examples:
        pdfstract download marker
        pdfstract download docling
        pdfstract download --all
    """
    cli_app.print_banner()
    
    factory = get_factory()
    
    if download_all or library_name == 'all':
        # Download all libraries that require downloads
        libraries = factory.list_all_converters()
        to_download = [lib["name"] for lib in libraries if lib.get("requires_download") and lib["available"]]
        
        if not to_download:
            cli_app.print_warning("No libraries require model downloads")
            return
        
        cli_app.print_info(f"Downloading models for {len(to_download)} libraries: {', '.join(to_download)}")
        
        for lib_name in to_download:
            cli_app.print_info(f"Downloading {lib_name}...")
            try:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console
                ) as progress:
                    task = progress.add_task(f"Downloading {lib_name} models...", total=None)
                    result = asyncio.run(factory.prepare_converter(lib_name))
                    progress.stop()
                
                if result["success"]:
                    cli_app.print_success(f"{lib_name}: {result.get('message', 'Downloaded successfully')}")
                else:
                    cli_app.print_error(f"{lib_name}: {result.get('error', 'Download failed')}")
            except Exception as e:
                cli_app.print_error(f"{lib_name}: {str(e)}")
        
        return
    
    # Download single library
    status = factory.get_converter_status(library_name)
    if not status:
        cli_app.print_error(f"Library '{library_name}' not found")
        cli_app.print_info(f"Available libraries: {', '.join(factory.list_available_converters())}")
        sys.exit(1)
    
    if not status.get("available"):
        cli_app.print_error(f"Library '{library_name}' is not installed. Install the Python package first.")
        sys.exit(1)
    
    if not status.get("requires_download"):
        cli_app.print_info(f"Library '{library_name}' does not require model downloads")
        return
    
    if status.get("download_status") == "ready":
        cli_app.print_success(f"Library '{library_name}' models are already downloaded")
        return
    
    cli_app.print_info(f"Downloading models for {library_name}...")
    cli_app.print_info("This may take several minutes depending on your internet connection")
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"Downloading {library_name} models...", total=None)
            result = asyncio.run(factory.prepare_converter(library_name))
            progress.stop()
        
        if result["success"]:
            cli_app.print_success(result.get("message", f"Models for {library_name} downloaded successfully"))
        else:
            cli_app.print_error(result.get("error", "Download failed"))
            sys.exit(1)
            
    except KeyboardInterrupt:
        cli_app.print_warning("Download interrupted")
        sys.exit(1)
    except Exception as e:
        cli_app.print_error(f"Download failed: {str(e)}")
        logger.exception("Full error traceback:")
        sys.exit(1)


@pdfstract.command()
@click.argument('input_file', type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option('--library', '-l', required=True, help='Extraction library to use')
@click.option('--format', '-f', type=click.Choice(['markdown', 'json', 'text']), 
              default='markdown', help='Output format')
@click.option('--output', '-o', type=click.Path(), help='Output file path (optional, auto-generates if not specified)')
def convert(input_file: Path, library: str, format: str, output: Optional[str]):
    """Convert a single PDF file
    
    Without --output: Creates file with same name as input PDF (e.g., sample.pdf → sample.md)
    
    Examples:
        pdfstract convert sample.pdf --library unstructured
        pdfstract convert sample.pdf --library unstructured --format markdown --output result.md
    """
    cli_app.print_banner()
    
    # Validate inputs
    if not input_file.exists():
        cli_app.print_error(f"File not found: {input_file}")
        sys.exit(1)
    
    if not input_file.suffix.lower() == '.pdf':
        cli_app.print_error("Only PDF files are supported")
        sys.exit(1)
    
    # Get converter (lazy load factory only when needed)
    converter = get_factory().get_converter(library)
    if not converter:
        available = [lib["name"] for lib in cli_app.get_available_libraries() if lib["available"]]
        cli_app.print_error(f"Library '{library}' not available")
        cli_app.print_info(f"Available: {', '.join(available)}")
        sys.exit(1)
    
    cli_app.print_info(f"Converting: {input_file.name}")
    cli_app.print_info(f"Library: {library} | Format: {format}")
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Converting...", total=None)
            
            # Run conversion
            output_format = OutputFormat(format)
            result = get_factory().convert(
                converter_name=library,
                file_path=str(input_file),
                output_format=output_format
            )
            
            progress.stop()
        
        cli_app.print_success(f"Conversion completed successfully")
        
        # Handle output
        if output:
            output_path = Path(output)
        else:
            # Auto-generate output filename if not specified
            ext = 'json' if format == 'json' else 'md' if format == 'markdown' else 'txt'
            output_path = Path(input_file.stem + '.' + ext)
        
        # Save to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if format == 'json' and isinstance(result, dict):
            with open(output_path, 'w') as f:
                json.dump(result, f, indent=2)
        else:
            with open(output_path, 'w') as f:
                f.write(str(result))
        
        cli_app.print_success(f"Output saved to: {output_path.absolute()}")
        
    except Exception as e:
        cli_app.print_error(f"Conversion failed: {str(e)}")
        logger.exception("Full error traceback:")
        sys.exit(1)


@pdfstract.command()
@click.argument('input_file', type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option('--libraries', '-l', multiple=True, required=True, 
              help='Libraries to compare (can specify multiple times)')
@click.option('--format', '-f', type=click.Choice(['markdown', 'json', 'text']), 
              default='markdown', help='Output format')
@click.option('--output', '-o', type=click.Path(), required=True,
              help='Output directory for results')
def compare(input_file: Path, libraries: tuple, format: str, output: str):
    """Compare multiple extraction libraries on a single PDF
    
    Example: pdfstract compare sample.pdf -l unstructured -l marker -l docling --format markdown --output ./results
    """
    cli_app.print_banner()
    
    if not input_file.exists():
        cli_app.print_error(f"File not found: {input_file}")
        sys.exit(1)
    
    if not input_file.suffix.lower() == '.pdf':
        cli_app.print_error("Only PDF files are supported")
        sys.exit(1)
    
    if not libraries or len(libraries) < 2:
        cli_app.print_error("Please specify at least 2 libraries to compare")
        sys.exit(1)
    
    if len(libraries) > 5:
        cli_app.print_warning(f"Limiting to 5 libraries (you specified {len(libraries)})")
        libraries = libraries[:5]
    
    # Validate libraries
    available_libs = get_factory().list_available_converters()
    for lib in libraries:
        if lib not in available_libs:
            cli_app.print_error(f"Library '{lib}' not available")
            sys.exit(1)
    
    output_dir = Path(output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    cli_app.print_info(f"Comparing {len(libraries)} libraries on: {input_file.name}")
    cli_app.print_info(f"Libraries: {', '.join(libraries)}")
    cli_app.print_info(f"Format: {format}")
    
    results = {}
    output_format = OutputFormat(format)
    
    with Progress(
        SpinnerColumn(),
        BarColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Converting...", total=len(libraries))
        
        for lib in libraries:
            progress.update(task, description=f"Processing {lib}...")
            
            try:
                result = get_factory().convert(
                    converter_name=lib,
                    file_path=str(input_file),
                    output_format=output_format
                )
                
                # Save result
                ext = 'json' if format == 'json' else 'md' if format == 'markdown' else 'txt'
                result_file = output_dir / f"{lib}_result.{ext}"
                
                if format == 'json' and isinstance(result, dict):
                    with open(result_file, 'w') as f:
                        json.dump(result, f, indent=2)
                else:
                    with open(result_file, 'w') as f:
                        f.write(str(result))
                
                results[lib] = {
                    "status": "success",
                    "file": str(result_file),
                    "size_bytes": result_file.stat().st_size
                }
                
            except Exception as e:
                results[lib] = {
                    "status": "failed",
                    "error": str(e)
                }
            
            progress.advance(task)
    
    # Save comparison summary
    summary_file = output_dir / "comparison_summary.json"
    summary = {
        "input_file": input_file.name,
        "format": format,
        "timestamp": datetime.now().isoformat(),
        "libraries": libraries,
        "results": results
    }
    
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    # Print results
    table = Table(title="Comparison Results", show_lines=True)
    table.add_column("Library", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Output Size", style="yellow")
    table.add_column("Details", style="dim")
    
    for lib, result in results.items():
        status_text = "[bold green]✓ Success[/bold green]" if result["status"] == "success" else "[bold red]✗ Failed[/bold red]"
        size_text = f"{result.get('size_bytes', 0) / 1024:.1f} KB" if result["status"] == "success" else "N/A"
        details = result.get("error", "")
        table.add_row(lib, status_text, size_text, details)
    
    console.print(table)
    cli_app.print_success(f"Comparison complete! Results saved to: {output_dir.absolute()}")
    cli_app.print_info(f"Summary: {summary_file}")


@pdfstract.command()
@click.argument('input_dir', type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option('--library', '-l', required=True, help='Extraction library to use')
@click.option('--format', '-f', type=click.Choice(['markdown', 'json', 'text']), 
              default='markdown', help='Output format')
@click.option('--output', '-o', type=click.Path(), required=True,
              help='Output directory for converted files')
@click.option('--parallel', '-p', type=int, default=2, 
              help='Number of parallel workers')
@click.option('--pattern', type=str, default='*.pdf',
              help='File pattern to match (e.g., "*.pdf" or "invoice_*.pdf")')
@click.option('--skip-errors', is_flag=True, help='Skip PDFs that fail conversion')
def batch(input_dir: Path, library: str, format: str, output: str, parallel: int, pattern: str, skip_errors: bool):
    """Batch convert all PDFs in a directory
    
    Example: pdfstract batch ./pdfs --library unstructured --format markdown --output ./converted --parallel 4
    """
    cli_app.print_banner()
    
    if not input_dir.is_dir():
        cli_app.print_error(f"Directory not found: {input_dir}")
        sys.exit(1)
    
    # Find PDFs
    pdf_files = sorted(input_dir.glob(pattern))
    pdf_files = [f for f in pdf_files if f.suffix.lower() == '.pdf']
    
    if not pdf_files:
        cli_app.print_warning(f"No PDF files found matching pattern '{pattern}'")
        sys.exit(0)
    
    cli_app.print_info(f"Found {len(pdf_files)} PDF files to convert")
    cli_app.print_info(f"Library: {library} | Format: {format} | Workers: {parallel}")
    
    # Validate library
    converter = cli_app.factory.get_converter(library)
    if not converter:
        available = [lib["name"] for lib in cli_app.get_available_libraries() if lib["available"]]
        cli_app.print_error(f"Library '{library}' not available")
        cli_app.print_info(f"Available: {', '.join(available)}")
        sys.exit(1)
    
    output_dir = Path(output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Track results
    results = {
        "success": 0,
        "failed": 0,
        "skipped": 0,
        "files": {}
    }
    
    output_format = OutputFormat(format)
    
    def convert_single_pdf(pdf_file: Path) -> tuple:
        """Convert a single PDF - for parallel execution"""
        try:
            result = get_factory().convert(
                converter_name=library,
                file_path=str(pdf_file),
                output_format=output_format
            )
            
            # Save result
            ext = 'json' if format == 'json' else 'md' if format == 'markdown' else 'txt'
            output_file = output_dir / f"{pdf_file.stem}.{ext}"
            
            if format == 'json' and isinstance(result, dict):
                with open(output_file, 'w') as f:
                    json.dump(result, f, indent=2)
            else:
                with open(output_file, 'w') as f:
                    f.write(str(result))
            
            return (pdf_file.name, "success", None, output_file.stat().st_size)
        
        except Exception as e:
            error_msg = str(e)
            if skip_errors:
                return (pdf_file.name, "skipped", error_msg, 0)
            else:
                return (pdf_file.name, "failed", error_msg, 0)
    
    # Run parallel conversion
    with Progress(
        SpinnerColumn(),
        BarColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Converting...", total=len(pdf_files))
        
        with ThreadPoolExecutor(max_workers=parallel) as executor:
            futures = [executor.submit(convert_single_pdf, pdf) for pdf in pdf_files]
            
            for future in futures:
                filename, status, error, size = future.result()
                results["files"][filename] = {
                    "status": status,
                    "error": error,
                    "size_bytes": size
                }
                
                if status == "success":
                    results["success"] += 1
                elif status == "failed":
                    results["failed"] += 1
                else:
                    results["skipped"] += 1
                
                progress.advance(task)
    
    # Save batch report
    report_file = output_dir / "batch_report.json"
    report = {
        "input_directory": str(input_dir.absolute()),
        "output_directory": str(output_dir.absolute()),
        "library": library,
        "format": format,
        "timestamp": datetime.now().isoformat(),
        "total_files": len(pdf_files),
        "statistics": {
            "success": results["success"],
            "failed": results["failed"],
            "skipped": results["skipped"]
        },
        "files": results["files"]
    }
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary table
    table = Table(title="Batch Conversion Summary", show_lines=True)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="yellow")
    
    table.add_row("Total Files", str(len(pdf_files)))
    table.add_row("[bold green]✓ Successful[/bold green]", f"[bold green]{results['success']}[/bold green]")
    table.add_row("[bold red]✗ Failed[/bold red]", f"[bold red]{results['failed']}[/bold red]")
    table.add_row("[bold yellow]⊝ Skipped[/bold yellow]", f"[bold yellow]{results['skipped']}[/bold yellow]")
    table.add_row("Success Rate", f"{(results['success'] / len(pdf_files) * 100):.1f}%")
    
    console.print(table)
    cli_app.print_success(f"Batch conversion complete!")
    cli_app.print_info(f"Output directory: {output_dir.absolute()}")
    cli_app.print_info(f"Report: {report_file}")
    
    # Exit with error if there were failures and not skipping
    if results["failed"] > 0 and not skip_errors:
        sys.exit(1)


@pdfstract.command()
@click.argument('input_dir', type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option('--libraries', '-l', multiple=True, required=True,
              help='Libraries to compare (can specify multiple times)')
@click.option('--format', '-f', type=click.Choice(['markdown', 'json', 'text']),
              default='markdown', help='Output format')
@click.option('--output', '-o', type=click.Path(), required=True,
              help='Output directory for results')
@click.option('--max-files', type=int, default=None,
              help='Limit number of files to process')
def batch_compare(input_dir: Path, libraries: tuple, format: str, output: str, max_files: Optional[int]):
    """Compare multiple libraries on all PDFs in a directory
    
    Generates comparative analysis of extraction quality across multiple libraries.
    
    Example: pdfstract batch-compare ./pdfs -l unstructured -l marker -l docling --output ./comparison
    """
    cli_app.print_banner()
    
    # Find PDFs
    pdf_files = sorted(input_dir.glob("*.pdf"))
    
    if not pdf_files:
        cli_app.print_warning(f"No PDF files found in {input_dir}")
        sys.exit(0)
    
    if max_files:
        pdf_files = pdf_files[:max_files]
        cli_app.print_info(f"Processing first {max_files} files")
    
    cli_app.print_info(f"Found {len(pdf_files)} PDF files")
    cli_app.print_info(f"Libraries: {', '.join(libraries)}")
    
    # Validate libraries
    available_libs = get_factory().list_available_converters()
    for lib in libraries:
        if lib not in available_libs:
            cli_app.print_error(f"Library '{lib}' not available")
            sys.exit(1)
    
    output_dir = Path(output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_format = OutputFormat(format)
    comparison_results = {}
    
    with Progress(
        SpinnerColumn(),
        BarColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        file_task = progress.add_task("Processing files...", total=len(pdf_files))
        
        for pdf_file in pdf_files:
            progress.update(file_task, description=f"Processing {pdf_file.name}...")
            file_results = {}
            
            for lib in libraries:
                try:
                    result = get_factory().convert(
                        converter_name=lib,
                        file_path=str(pdf_file),
                        output_format=output_format
                    )
                    
                    file_results[lib] = {
                        "status": "success",
                        "size_bytes": len(str(result).encode())
                    }
                
                except Exception as e:
                    file_results[lib] = {
                        "status": "failed",
                        "error": str(e)
                    }
            
            comparison_results[pdf_file.name] = file_results
            progress.advance(file_task)
    
    # Save comparison report
    report_file = output_dir / "batch_comparison_report.json"
    report = {
        "input_directory": str(input_dir.absolute()),
        "libraries": list(libraries),
        "format": format,
        "timestamp": datetime.now().isoformat(),
        "total_files": len(pdf_files),
        "results": comparison_results
    }
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    cli_app.print_success(f"Batch comparison complete!")
    cli_app.print_info(f"Report: {report_file}")
    
    # Calculate success rates
    table = Table(title="Batch Comparison Summary", show_lines=True)
    table.add_column("Library", style="cyan")
    table.add_column("Success Rate", style="green")
    table.add_column("Avg Size (KB)", style="yellow")
    
    for lib in libraries:
        successes = sum(
            1 for file_results in comparison_results.values()
            if file_results.get(lib, {}).get("status") == "success"
        )
        success_rate = (successes / len(pdf_files) * 100) if pdf_files else 0
        
        avg_size = 0
        if successes > 0:
            total_size = sum(
                file_results.get(lib, {}).get("size_bytes", 0)
                for file_results in comparison_results.values()
                if file_results.get(lib, {}).get("status") == "success"
            )
            avg_size = total_size / successes / 1024
        
        table.add_row(lib, f"{success_rate:.1f}%", f"{avg_size:.1f}")
    
    console.print(table)


# ============================================================================
# CHUNKING COMMANDS
# ============================================================================

@pdfstract.command()
def chunkers():
    """List all available text chunkers and their parameters"""
    cli_app.print_banner()
    
    factory = get_chunker_factory()
    all_chunkers = factory.list_all_chunkers()
    
    table = Table(title="Available Text Chunkers", show_lines=True)
    table.add_column("Chunker", style="cyan", no_wrap=True)
    table.add_column("Status", style="green")
    table.add_column("Description", style="yellow")
    
    for chunker_info in all_chunkers:
        status = "[bold green]✓ Available[/bold green]" if chunker_info["available"] else "[bold red]✗ Unavailable[/bold red]"
        description = chunker_info.get("description", "")
        table.add_row(chunker_info["name"], status, description)
    
    console.print(table)
    console.print()
    
    # Show parameter details for available chunkers
    available = [c for c in all_chunkers if c["available"]]
    if available:
        console.print("[bold]Chunker Parameters:[/bold]")
        for chunker_info in available:
            console.print(f"\n[cyan]{chunker_info['name']}[/cyan]:")
            for param_name, param_spec in chunker_info.get("parameters", {}).items():
                param_type = param_spec.get("type", "any")
                default = param_spec.get("default", "N/A")
                desc = param_spec.get("description", "")
                console.print(f"  --{param_name}: {param_type} (default: {default})")
                if desc:
                    console.print(f"    [dim]{desc}[/dim]")
    
    console.print()
    console.print("[dim]Use 'pdfstract chunk --help' to chunk text files[/dim]")


@pdfstract.command()
@click.argument('input_file', type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option('--chunker', '-c', required=True, help='Chunker to use (token, sentence, recursive, table)')
@click.option('--chunk-size', type=int, default=2048, help='Maximum tokens/units per chunk')
@click.option('--chunk-overlap', type=int, default=0, help='Overlapping tokens between chunks')
@click.option('--output', '-o', type=click.Path(), help='Output file path for chunked JSON')
@click.option('--params', type=str, default='{}', help='Additional chunker parameters as JSON string')
def chunk(input_file: Path, chunker: str, chunk_size: int, chunk_overlap: int, output: Optional[str], params: str):
    """Chunk a text or markdown file into smaller pieces
    
    Reads a text/markdown file and splits it into chunks using the specified chunker.
    Output is saved as JSON with chunk metadata.
    
    Examples:
        pdfstract chunk document.md --chunker token --chunk-size 1024
        pdfstract chunk document.md --chunker sentence --chunk-size 2048 --output chunks.json
        pdfstract chunk document.txt --chunker recursive --params '{"recipe": "markdown"}'
    """
    cli_app.print_banner()
    
    # Validate input
    if not input_file.exists():
        cli_app.print_error(f"File not found: {input_file}")
        sys.exit(1)
    
    # Read input file
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        cli_app.print_error(f"Failed to read file: {str(e)}")
        sys.exit(1)
    
    if not text.strip():
        cli_app.print_error("Input file is empty")
        sys.exit(1)
    
    # Parse additional params
    try:
        extra_params = json.loads(params) if params else {}
    except json.JSONDecodeError:
        cli_app.print_error("Invalid params JSON format")
        sys.exit(1)
    
    # Merge params
    chunker_params = {
        "chunk_size": chunk_size,
        "chunk_overlap": chunk_overlap,
        **extra_params
    }
    
    cli_app.print_info(f"Chunking: {input_file.name}")
    cli_app.print_info(f"Chunker: {chunker} | Size: {chunk_size} | Overlap: {chunk_overlap}")
    
    try:
        factory = get_chunker_factory()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Chunking...", total=None)
            
            # Run chunking (synchronously for CLI)
            result = asyncio.run(
                factory.chunk_with_result(chunker, text, **chunker_params)
            )
            
            progress.stop()
        
        cli_app.print_success(f"Chunking completed: {result.total_chunks} chunks created")
        
        # Handle output
        if output:
            output_path = Path(output)
        else:
            output_path = Path(input_file.stem + '_chunks.json')
        
        # Save to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
        
        cli_app.print_success(f"Output saved to: {output_path.absolute()}")
        
        # Print summary table
        table = Table(title="Chunking Summary", show_lines=True)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="yellow")
        
        table.add_row("Total Chunks", str(result.total_chunks))
        table.add_row("Total Tokens", str(result.total_tokens))
        table.add_row("Original Length", f"{result.original_length:,} chars")
        table.add_row("Avg Chunk Size", f"{result.original_length // max(result.total_chunks, 1):,} chars")
        
        console.print(table)
        
    except ValueError as e:
        cli_app.print_error(f"Chunking failed: {str(e)}")
        sys.exit(1)
    except Exception as e:
        cli_app.print_error(f"Chunking failed: {str(e)}")
        logger.exception("Full error traceback:")
        sys.exit(1)


@pdfstract.command('convert-chunk')
@click.argument('input_file', type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option('--library', '-l', required=True, help='Extraction library to use')
@click.option('--chunker', '-c', required=True, help='Chunker to use after conversion')
@click.option('--format', '-f', type=click.Choice(['markdown', 'text']), default='markdown',
              help='Intermediate output format (before chunking)')
@click.option('--chunk-size', type=int, default=2048, help='Maximum tokens per chunk')
@click.option('--chunk-overlap', type=int, default=0, help='Overlapping tokens between chunks')
@click.option('--output', '-o', type=click.Path(), help='Output file path for chunked JSON')
@click.option('--save-converted', is_flag=True, help='Also save the intermediate converted text')
@click.option('--params', type=str, default='{}', help='Additional chunker parameters as JSON')
def convert_chunk(
    input_file: Path,
    library: str,
    chunker: str,
    format: str,
    chunk_size: int,
    chunk_overlap: int,
    output: Optional[str],
    save_converted: bool,
    params: str
):
    """Convert a PDF and chunk the result in one step
    
    Combines PDF conversion with text chunking for RAG/embedding workflows.
    
    Examples:
        pdfstract convert-chunk document.pdf --library marker --chunker token
        pdfstract convert-chunk document.pdf -l docling -c sentence --chunk-size 1024 --output chunks.json
        pdfstract convert-chunk doc.pdf -l marker -c recursive --save-converted
    """
    cli_app.print_banner()
    
    # Validate inputs
    if not input_file.exists():
        cli_app.print_error(f"File not found: {input_file}")
        sys.exit(1)
    
    if not input_file.suffix.lower() == '.pdf':
        cli_app.print_error("Only PDF files are supported")
        sys.exit(1)
    
    # Validate library
    converter = get_factory().get_converter(library)
    if not converter:
        available = [lib["name"] for lib in cli_app.get_available_libraries() if lib["available"]]
        cli_app.print_error(f"Library '{library}' not available")
        cli_app.print_info(f"Available: {', '.join(available)}")
        sys.exit(1)
    
    # Parse additional params
    try:
        extra_params = json.loads(params) if params else {}
    except json.JSONDecodeError:
        cli_app.print_error("Invalid params JSON format")
        sys.exit(1)
    
    chunker_params = {
        "chunk_size": chunk_size,
        "chunk_overlap": chunk_overlap,
        **extra_params
    }
    
    cli_app.print_info(f"Processing: {input_file.name}")
    cli_app.print_info(f"Convert: {library} → {format} | Chunk: {chunker}")
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            # Step 1: Convert PDF
            progress.add_task("Converting PDF...", total=None)
            
            output_format = OutputFormat(format)
            converted_text = get_factory().convert(
                converter_name=library,
                file_path=str(input_file),
                output_format=output_format
            )
            
            progress.stop()
            cli_app.print_success(f"Conversion complete: {len(converted_text):,} characters")
        
        # Optionally save converted text
        if save_converted:
            ext = 'md' if format == 'markdown' else 'txt'
            converted_file = Path(input_file.stem + f'_converted.{ext}')
            with open(converted_file, 'w', encoding='utf-8') as f:
                f.write(converted_text)
            cli_app.print_info(f"Converted text saved to: {converted_file}")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            # Step 2: Chunk the converted text
            progress.add_task("Chunking text...", total=None)
            
            factory = get_chunker_factory()
            result = asyncio.run(
                factory.chunk_with_result(chunker, converted_text, **chunker_params)
            )
            
            progress.stop()
        
        cli_app.print_success(f"Chunking complete: {result.total_chunks} chunks")
        
        # Handle output
        if output:
            output_path = Path(output)
        else:
            output_path = Path(input_file.stem + '_chunks.json')
        
        # Prepare output data
        output_data = {
            "source_file": str(input_file.name),
            "conversion": {
                "library": library,
                "format": format,
                "text_length": len(converted_text)
            },
            "chunking": result.to_dict()
        }
        
        # Save to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        cli_app.print_success(f"Output saved to: {output_path.absolute()}")
        
        # Print summary
        table = Table(title="Convert & Chunk Summary", show_lines=True)
        table.add_column("Step", style="cyan")
        table.add_column("Details", style="yellow")
        
        table.add_row("Conversion", f"{library} → {len(converted_text):,} chars")
        table.add_row("Chunking", f"{chunker} → {result.total_chunks} chunks")
        table.add_row("Total Tokens", str(result.total_tokens))
        table.add_row("Avg Chunk Size", f"{len(converted_text) // max(result.total_chunks, 1):,} chars")
        
        console.print(table)
        
    except ValueError as e:
        cli_app.print_error(f"Operation failed: {str(e)}")
        sys.exit(1)
    except Exception as e:
        cli_app.print_error(f"Operation failed: {str(e)}")
        logger.exception("Full error traceback:")
        sys.exit(1)


def main():
    """Main entry point for the CLI"""
    pdfstract(standalone_mode=False)


if __name__ == '__main__':
    main()

