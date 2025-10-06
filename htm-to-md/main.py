# earlan@ttc0815.com

import os
from html_to_markdown import convert_to_markdown

OUTPUT_DIR = os.path.join("..", "b")


def htm_to_markdown(file_path):
    """Read an HTML file, convert to markdown and write to OUTPUT_DIR.

    Uses os.path functions so it works on Windows and POSIX paths. Handles
    both .htm and .html extensions.
    """
    try:
        # Try UTF-8 first, fall back to Windows-1252, then Latin-1
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='windows-1252') as f:
                    file_content = f.read()
            except UnicodeDecodeError:
                with open(file_path, 'r', encoding='latin-1') as f:
                    file_content = f.read()

        # convert
        markdown = convert_to_markdown(file_content)

        # build output path robustly
        filename = os.path.splitext(os.path.basename(file_path))[0]
        out_path = os.path.join(OUTPUT_DIR, filename + ".md")

        # ensure output dir exists
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(markdown)

        print(f"Converted '{file_path}' -> '{out_path}'")

    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

    

def main():
    # walk input directory and convert any .htm files
    input_dir = os.path.join("..", "a")
    for dirpath, _, files in os.walk(input_dir):
        for fname in files:
            full_path = os.path.join(dirpath, fname)
            _, extension = os.path.splitext(full_path)
            # Only process .htm files (not .html)
            if extension.lower() == ".htm" or extension.lower() == ".html":
                htm_to_markdown(full_path)

    # Copy all folders from a to b (override if existing)
    import shutil
    for item in os.listdir(input_dir):
        src_path = os.path.join(input_dir, item)
        if os.path.isdir(src_path):
            dst_path = os.path.join(OUTPUT_DIR, item)
            if os.path.exists(dst_path):
                shutil.rmtree(dst_path)  # Remove existing folder
            shutil.copytree(src_path, dst_path)
            print(f"Copied folder '{src_path}' -> '{dst_path}'")


if __name__ == "__main__":
    main()
