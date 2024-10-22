import os
import subprocess
import colorsys
import re

def extract_label_from_filename(filename, cleaned_external_files):
    base_name = os.path.basename(filename)
    parts = base_name.split('-')
    
    if len(parts) >= 5:
        author = parts[3]
        data = parts[4].split('.')[0]  # Exclude file extension
        year = parts[4].split('.')[1]

        weight = "w1" if filename in cleaned_external_files else "w0"
        return f"{author}-{data} ({year}) {weight}"
    return base_name   # Return filename if pattern is unexpected

def extract_year_from_filename(filename):
    match = re.search(r'\.(\d{4})$', filename)  # Looks for a 4-digit year at the end of the filename
    if match:
        return int(match.group(1))
    return None

def rgb_to_hex(r, g, b):
    return f'#{r:02X}{g:02X}{b:02X}' 

def hsl_to_rgb(h, s, l):
    """Convert HSL color to RGB."""
    rgb_float = colorsys.hls_to_rgb(h, l, s)
    return tuple(int(255 * x) for x in rgb_float)  # Convert float [0, 1] to int [0, 255]

def generate_combined_gnuplot_script(cleaned_output_files, cleaned_external_files, cleaned_all_external_files, plot_file):

    gnuplot_script = f"""
set terminal pngcairo enhanced font 'Arial,10' size 800,600
set output '{plot_file}'
set title 'Cross Section Plot'
set xlabel 'Energy (MeV)'
set ylabel 'Cross Section (mb)'
set grid
set xrange [0:40]

plot """
    # Add TALYS-generated data files
    for i, cleaned_output_file in enumerate(cleaned_output_files):
        label = f"Input {round(1 + i , 5)}" 
        if i == 0:
            gnuplot_script += f"'{cleaned_output_file}' using 1:2 title '{label}' with lines"
        else:
            gnuplot_script += f", '{cleaned_output_file}' using 1:2 title '{label}' with lines"

    # Add external data files
    for index, cleaned_all_external_file in enumerate(cleaned_all_external_files):
        ext_label = extract_label_from_filename(cleaned_all_external_file, cleaned_external_files)  
        point_type = index + 7  

        hue = index / len(cleaned_all_external_files)  
        saturation = 1  
        lightness = 0.5

        r, g, b = hsl_to_rgb(hue, saturation, lightness)

        color = rgb_to_hex(r, g, b) 
        gnuplot_script += f", '{cleaned_all_external_file}' using 1:3:4 with errorbars title '{ext_label}' pt {point_type} lc rgb '{color}'"
    
    return gnuplot_script

def run_gnuplot(gnuplot_script_content, script_file):

    with open(script_file, 'w') as f:
        f.write(gnuplot_script_content)

    result = subprocess.run(["gnuplot", script_file], capture_output=True, text=True)

    if result.returncode != 0:
        print("Gnuplot Error:", result.stderr)
    else:
        print("Gnuplot Output:", result.stdout)