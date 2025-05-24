from get_melody import *
from checking import *
from midi_lily import midi_to_lilypond
import os
import datetime # Import datetime

conterpoint = r"'CantusFirmus': [60, 62, 65, 64, 65, 67, 69, 67, 64, 62, 60]"

# Sanitize MODEL name for filename and get current date
safe_model_name = MODEL.replace('/', '_').replace(':', '_')
today_date = datetime.datetime.now().strftime("%Y-%m-%d")
output_base_filename = f"{safe_model_name}_{today_date}"
lilypond_file_name = f"{output_base_filename}.ly"
pdf_file_name = f"{output_base_filename}.pdf" # Construct PDF filename as well for print statements

# Initial melody generation
midi_melodies = send_to_llm(conterpoint)
print("Initial melody generated:", midi_melodies)

# Loop to check and refine the counterpoint
max_iterations = 5
for i in range(max_iterations):
    print(midi_melodies)
    parallel_intervals_result = find_parallel_perfect_intervals(midi_melodies['Counterpoint'], midi_melodies['CantusFirmus'])
    parallel_motives_result = find_parallel_motives(midi_melodies['Counterpoint'], midi_melodies['CantusFirmus'])
    voice_spacing_result = check_voice_spacing_crossing_overlapping(midi_melodies['Counterpoint'], midi_melodies['CantusFirmus'])
    dissonant_leaps_result = find_dissonant_leaps(midi_melodies['Counterpoint'])
    dissonant_inteval_result = find_dissonant_interval(midi_melodies['Counterpoint'], midi_melodies['CantusFirmus'])
    check_octave_inverval_resulte = check_octave_unison_rules(midi_melodies['Counterpoint'], midi_melodies['CantusFirmus'])
    # Collect all issues
    issues = []
    if parallel_intervals_result:
        issues.append(parallel_intervals_result[1])
    if parallel_motives_result:
        issues.append(parallel_motives_result[1])
    if voice_spacing_result:
        issues.append(voice_spacing_result[1])
    if dissonant_leaps_result:
        issues.append(dissonant_leaps_result[1])
    if dissonant_inteval_result:
        issues.append(dissonant_inteval_result[1])
    if check_octave_inverval_resulte:
        issues.append(check_octave_inverval_resulte[1])
    
    # If no issues found, generate PDF and exit loop
    if not issues:
        print(f"No counterpoint issues found after {i+1} iterations!")
        # Generate PDF directly
        midi_to_lilypond(midi_melodies, lilypond_file_name, generate_pdf=True)
        print(f"Final counterpoint saved as {pdf_file_name}")
        break
    
    # If this is the last iteration and we still have issues
    if i == max_iterations - 1:
        print("Could not find a perfect solution after 5 iterations.")
        print("Generating PDF with the best solution so far...")
        # Generate PDF with the best solution we have
        midi_to_lilypond(midi_melodies, lilypond_file_name, generate_pdf=True)
        print(f"Final counterpoint saved as {pdf_file_name}")
        break
    
    # Otherwise, report issues and regenerate
    print(f"Iteration {i+1}: Found {len(issues)} counterpoint issues:")
    for issue in issues:
        print(issue)
    
    # Regenerate the melody with feedback
    feedback = "\n".join(issues)
    # After this line:
    midi_melodies = send_to_llm(conterpoint, feedback)
    
    # Add this check to ensure we get a different melody:
    max_attempts = 3
    attempt = 0
    original_melody = midi_melodies['Counterpoint'].copy()
    
    while midi_melodies['Counterpoint'] == original_melody and attempt < max_attempts:
        print(f"LLM returned the same melody. Trying again (attempt {attempt+1}/{max_attempts})...")
        midi_melodies = send_to_llm(conterpoint, feedback + "\nIMPORTANT: You MUST create a COMPLETELY DIFFERENT melody.")
        attempt += 1
    
    if midi_melodies['Counterpoint'] == original_melody:
        print("Warning: LLM failed to generate a different melody after multiple attempts.")
    print("New melody generated:", midi_melodies)