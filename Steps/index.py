import os
import sys
import shutil
from colorama import init, Fore, Style
from Step1 import find_and_remove_duplicate_paths
from Step2 import modify_svg_stroke_and_fill
from Step3 import add_background_to_svg
from Step4 import apply_color_to_specific_paths
from Step5 import process_svg_file

# Initialize colorama
init()

def print_header(text):
    print(f"\n{Fore.CYAN}{'='*50}")
    print(f"{text:^50}")
    print(f"{'='*50}{Style.RESET_ALL}\n")

def print_step(number, description):
    print(f"{Fore.GREEN}Step {number}: {Fore.YELLOW}{description}{Style.RESET_ALL}")

def print_success(text):
    print(f"{Fore.GREEN}✓ {text}{Style.RESET_ALL}")

def print_error(text):
    print(f"{Fore.RED}✗ Error: {text}{Style.RESET_ALL}")

def print_info(text):
    print(f"{Fore.BLUE}ℹ {text}{Style.RESET_ALL}")

def run_all_steps():
    try:
        print_header("Starting SVG Processing Pipeline")

        # Step 1: Remove duplicates
        print_step(1, "Removing duplicate paths")
        input_svg = "a_file.svg"
        step1_output = "Step1.svg"
        
        if not os.path.exists(input_svg):
            print_error(f"Initial input file '{input_svg}' not found!")
            print_info(f"Current working directory: {os.getcwd()}")
            return
            
        find_and_remove_duplicate_paths(input_svg, step1_output)
        print_success(f"Step 1 completed: {step1_output} created")

        # Step 2: Modify stroke and fill
        print_step(2, "Modifying stroke and fill colors")
        step2_output = "Step2.svg"
        with open(step1_output, "r", encoding="utf-8") as file:
            svg_text = file.read()
        modified_svg = modify_svg_stroke_and_fill(svg_text)
        with open(step2_output, "w", encoding="utf-8") as file:
            file.write(modified_svg)
        print_success(f"Step 2 completed: {step2_output} created")

        # Step 3: Add background
        print_step(3, "Adding background")
        step3_output = "Step3.svg"
        background_color = "#202124"
        add_background_to_svg(step2_output, step3_output, background_color)
        print_success(f"Step 3 completed: {step3_output} created")

        # Step 4: Apply specific colors
        print_step(4, "Applying specific colors to paths")
        step4_output = "Step4.svg"
        apply_color_to_specific_paths(step3_output, step4_output)
        print_success(f"Step 4 completed: {step4_output} created")

        # Step 5: Find and update matching paths
        print_step(5, "Finding and updating matching paths")
        step5_output = "Step5.svg"
        process_svg_file(step4_output)
        print_success(f"Step 5 completed: {step5_output} created")

        # Cleanup intermediate files
        print_step("Cleanup", "Removing intermediate files")
        intermediate_files = [step1_output, step2_output, step3_output, step4_output]
        # for file in intermediate_files:
        #     if os.path.exists(file):
        #         os.remove(file)
        #         print_info(f"Removed intermediate file: {file}")

        print_success(f"Final output saved as: {step5_output}")

    except Exception as e:
        print_error(f"Pipeline error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run_all_steps()
