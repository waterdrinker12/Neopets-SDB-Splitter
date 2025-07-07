import os
import re

def extract_page_number(file_path):
    """
    Extracts the page number from an HTML file.
    Looks for <option ... selected>NUMBER</option>, regardless of attribute order or quote type.
    Returns the integer page number or None if not found.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        # Regex explanation:
        # - <option ... selected ...>NUMBER</option>
        # - Allows any attributes before/after selected, with any quotes
        # - Captures the number inside the option tag (page number)
        match = re.search(
            r'<option\b[^>]*\bselected\b[^>]*>(\d+)</option>',
            content, re.IGNORECASE
        )
        if match:
            return int(match.group(1))
    return None

def convert_quantity_quotes(content):
    """
    Replaces data-total_count="123" with data-total_count='123'
    for Jellyneo compatibility.
    """
    return re.sub(r'data-total_count="(\d+)"', r"data-total_count='\1'", content)

def extract_valid_rows(content):
    """
    Extracts all <tr> rows that contain back_to_inv[...] inputs.
    Only returns the inner HTML that Jellyneo's checker needs.
    """
    # Fix quotes first
    content = convert_quantity_quotes(content)

    # Find all matching <tr>...</tr> blocks that contain the necessary input
    rows = re.findall(r"<tr.*?>.*?back_to_inv\[\d+\].*?</tr>", content, re.DOTALL | re.IGNORECASE)

    if not rows:
        return None

    # Wrap it in minimal HTML shell with required comment and table
    trimmed_html = (
        "<html>\n"
        "<head><title>Safety Deposit Box</title></head>\n"
        "<body>\n"
        "<!-- free safety deposit box! -->\n"
        "<table>\n"
        + "\n".join(rows) +
        "\n</table>\n</body>\n</html>"
    )
    return trimmed_html

def combine_html_files_in_chunks(folder_path, output_folder, chunk_size=25):
    os.makedirs(output_folder, exist_ok=True)

    html_files = sorted(f for f in os.listdir(folder_path) if f.lower().endswith('.html'))
    if not html_files:
        print("❌ No .html files found in folder.")
        return

    page_map = {}

    for file_name in html_files:
        path = os.path.join(folder_path, file_name)
        page_num = extract_page_number(path)
        if page_num is None:
            print(f"⚠️ Could not find page number in {file_name}")
            continue
        if page_num in page_map:
            print(f"⚠️ Duplicate page number {page_num} found in {file_name} (already mapped to {page_map[page_num]}). Ignoring this file.")
            continue
        page_map[page_num] = file_name

    if not page_map:
        print("❌ No valid HTML files with page numbers found.")
        return

    all_found_pages = sorted(page_map.keys())
    first_page = all_found_pages[0]
    last_page = all_found_pages[-1]
    expected_pages = set(range(first_page, last_page + 1))
    missing_pages = sorted(expected_pages - set(all_found_pages))

    if missing_pages:
        print("❌ Missing pages detected. Aborting chunk export.")
        print("Missing pages:", missing_pages)
        return

    sorted_pages = sorted(page_map.items())
    total_pages = len(sorted_pages)
    num_chunks = (total_pages + chunk_size - 1) // chunk_size

    for chunk_index in range(num_chunks):
        start_idx = chunk_index * chunk_size
        end_idx = min(start_idx + chunk_size, total_pages)
        chunk_items = sorted_pages[start_idx:end_idx]
        combined_content = ""

        for page_num, file_name in chunk_items:
            file_path = os.path.join(folder_path, file_name)
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_content = f.read()
                trimmed = extract_valid_rows(raw_content)
                if trimmed:
                    combined_content += trimmed + "\n\n"

        chunk_start_page = chunk_items[0][0]
        chunk_end_page = chunk_items[-1][0]
        output_name = f"combined_chunk_{chunk_index + 1}.txt"
        output_path = os.path.join(output_folder, output_name)

        if combined_content.strip():
            with open(output_path, 'w', encoding='utf-8') as out:
                out.write(combined_content)
            print(f"✅ Pages {chunk_start_page}–{chunk_end_page} saved as {output_name}")
        else:
            print(f"⚠️ Chunk {chunk_index + 1} (Pages {chunk_start_page}–{chunk_end_page}) had no valid content. Skipped.")

if __name__ == "__main__":
    current_dir = os.getcwd()
    combine_html_files_in_chunks(current_dir, current_dir)
