#!/usr/bin/env python3
"""
Serve script for Zola-based site with full build pipeline and live reload.
"""

import subprocess
import sys
import time
from pathlib import Path


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command, printing it first."""
    print(f"  $ {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout.strip())
    if result.returncode != 0 and result.stderr:
        print(result.stderr.strip(), file=sys.stderr)
    if check and result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")
    return result


def build():
    """Full build pipeline matching release.py."""
    print("\n=== Building site ===")
    
    # Clean build
    run(["rm", "-rf", "docs"])
    run(["zola", "build"])
    
    # Copy static assets
    run(["cp", "-r", "static/documents", "docs/"])
    if Path("static/images").exists():
        run(["cp", "-r", "static/images", "docs/"])
    
    # Post-processing
    run(["python3", "scripts/fix_links.py"])
    run(["python3", "scripts/generate_search_index.py"])
    run(["python3", "scripts/generate_taxonomy_index.py"])
    
    # Verify
    if not Path("docs/index.html").exists():
        raise RuntimeError("Build failed: docs/index.html not found")
    
    print("=== Build complete ===\n")


def main():
    # Initial build
    try:
        build()
    except Exception as e:
        print(f"Build failed: {e}", file=sys.stderr)
        sys.exit(1)

    # Try to use livereload for live reload
    try:
        from livereload import Server
    except ImportError:
        print("Installing livereload...")
        run([sys.executable, "-m", "pip", "install", "livereload"])
        from livereload import Server

    server = Server()
    
    # Watch for changes and rebuild
    def rebuild():
        try:
            build()
        except Exception as e:
            print(f"Rebuild failed: {e}", file=sys.stderr)

    server.watch("content/", rebuild)
    server.watch("templates/", rebuild)
    server.watch("sass/", rebuild)
    server.watch("static/", rebuild)
    server.watch("scripts/", rebuild)
    server.watch("config.toml", rebuild)
    
    print("Serving at http://127.0.0.1:1111")
    print("Press Ctrl+C to stop\n")
    
    try:
        # Create base_url path for CSS/asset links to work
        base_path = Path("docs/a_careful_examination")
        base_path.mkdir(parents=True, exist_ok=True)
        
        # Symlink all docs contents into base_url subdirectory
        for item in Path("docs").iterdir():
            target = base_path / item.name
            if target.exists() or target.is_symlink():
                target.unlink()
            target.symlink_to(item.absolute())
        
        server.serve(root="docs", port=1111, host="127.0.0.1")
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        # Cleanup symlink
        import shutil
        if base_path.exists():
            shutil.rmtree(base_path)


if __name__ == "__main__":
    main()