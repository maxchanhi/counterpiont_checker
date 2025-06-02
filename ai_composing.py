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
result, midi_melodies = send_to_llm(conterpoint, use_checking=False)
print("Initial melody generated:", midi_melodies)

# Check if the initial generation was successful
if midi_melodies is None or "Error:" in result:
    print(f"Failed to generate initial melody: {result}")
    exit(1)

raw_midi_melodies = midi_melodies.copy()
midi_to_lilypond(raw_midi_melodies, raw_output_file_name, generate_pdf=True, llm_name=MODEL, composition_detail=result)

# Try to improve with checking
checked_result, new_midi_melodies = send_to_llm(conterpoint=midi_melodies, use_checking=True)

# Use the improved version if successful, otherwise fall back to original
if new_midi_melodies is not None and "Error:" not in checked_result:
    final_melodies = new_midi_melodies
    final_result = checked_result
    print("Using improved melody with checking")
else:
    final_melodies = midi_melodies
    final_result = result
    print(f"Using original melody due to checking failure: {checked_result}")

midi_to_lilypond(final_melodies, lilypond_file_name, generate_pdf=True, llm_name=MODEL, composition_detail=final_result)

    
    