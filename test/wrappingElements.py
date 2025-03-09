import re

def change_large_paths_to_white(svg_file):
    """
    Reads an SVG file, identifies paths with values greater than 450 (excluding coordinate pairs),
    and changes their stroke and fill color to white (#ffffff).
    :param svg_file: Path to the modified SVG file (modified_image.svg)
    """
    try:
        with open(svg_file, "r", encoding="utf-8") as file:
            svg_text = file.read()
        
        # Function to check if a path contains a value greater than 450 (excluding coordinates)
        def modify_large_paths(match):
            path_tag = match.group(0)
            d_attr = match.group(1)
            
            # Extract numeric values from the d attribute
            values = [float(num) for num in re.findall(r'[-+]?[0-9]*\.?[0-9]+', d_attr)]
            
            # Identify if any non-coordinate number is greater than 450
            if any(v > 450 for v in values if v not in [300, 450]):
                path_tag = re.sub(r'stroke:[#0-9a-fA-F]+', 'stroke:#ffffff', path_tag)
                path_tag = re.sub(r'fill:[#0-9a-fA-F]+', 'fill:#ffffff', path_tag)
            
            return path_tag
        
        # Modify paths where numerical values exceed 450 but not standard ones like 300 and 450
        modified_svg_text = re.sub(r'(<path[^>]+d="([^"]+)")', modify_large_paths, svg_text)
        
        # Save the modified SVG
        output_svg_path = svg_file.replace("modified_image", "checked_image")
        with open(output_svg_path, "w", encoding="utf-8") as file:
            file.write(modified_svg_text)
        
        print(f"Checked and modified SVG saved to {output_svg_path}")
    except Exception as e:
        print(f"Error processing SVG: {e}")

# Example usage
svg_path = "modified_image.svg"  # The input SVG file
change_large_paths_to_white(svg_path)