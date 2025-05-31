import checking
from get_melody import *
from checking import *
from midi_lily import midi_to_lilypond
import os
import datetime # Import datetime
from get_melody import send_to_llm, MODEL # Ensure MODEL is imported
from checking import *
import os
import datetime # Import datetime

conterpoint = r"'CantusFirmus': [60, 62, 65, 64, 65, 67, 69, 67, 64, 62, 60]"
# Sanitize MODEL name for filename and get current date
safe_model_name = MODEL.replace('/', '_').replace(':', '_')
today_date = datetime.datetime.now().strftime("%Y-%m-%d")
output_base_filename = f"{safe_model_name}_{today_date}"
lilypond_file_name = f"{output_base_filename}.ly"
raw_output_file_name = f"{output_base_filename}_RawOutput.ly"
pdf_file_name = f"{output_base_filename}.pdf" # Construct PDF filename as well for print statements

# Initial melody generation
midi_melodies = send_to_llm(conterpoint,use_checking=False)
print("Initial melody generated:", midi_melodies)
raw_midi_melodies = midi_melodies.copy()
midi_to_lilypond(raw_midi_melodies, raw_output_file_name, generate_pdf=True, llm_name=MODEL, composition_detail="Raw Output")

max_iterations = 1
for i in range(max_iterations):
    
    new_midi_melodies = send_to_llm(conterpoint=midi_melodies, use_checking=True)
    print("New melody generated:", new_midi_melodies)
    if new_midi_melodies:
        print("Correct counterpoint generated:", new_midi_melodies)
        midi_to_lilypond(new_midi_melodies, lilypond_file_name, generate_pdf=True, llm_name=MODEL, composition_detail="Successful Solution")
        break
    if i == max_iterations - 1:
        print("Could not find a perfect solution after 5 iterations.")
        print("Generating PDF with the best solution so far...")
        # Generate PDF with the best solution we have
        midi_to_lilypond(new_midi_melodies, lilypond_file_name, generate_pdf=True, llm_name=MODEL, composition_detail="Failed to Find Solution")
        print(f"Final counterpoint saved as {pdf_file_name}")
        break
    midi_melodies = new_midi_melodies
    new_midi_melodies=None


    
    
    