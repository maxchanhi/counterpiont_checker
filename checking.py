import sys # Added for sys.stderr, as other functions may use it.
def find_parallel_perfect_intervals(inputCounterpoint, inputCantusFirmus):

    findings_list = [] # Store just the range strings first
    if not inputCounterpoint or not inputCantusFirmus:
        print("Warning: One or both melodies are empty.", file=sys.stderr)
        return False # No findings possible

    if len(inputCounterpoint) != len(inputCantusFirmus):
        print(f"Warning: Melodies have different lengths ({len(inputCounterpoint)} vs {len(inputCantusFirmus)}). Checking up to shortest length.", file=sys.stderr)

    length = min(len(inputCounterpoint), len(inputCantusFirmus))
    perfect_interval_types = [0, 5, 7] # P1/P8=0, P4=5, P5=7

    for i in range(length - 1):
        m1_note_i, m2_note_i = inputCounterpoint[i], inputCantusFirmus[i]
        m1_note_i1, m2_note_i1 = inputCounterpoint[i+1], inputCantusFirmus[i+1]

        if None in [m1_note_i, m2_note_i, m1_note_i1, m2_note_i1]:
            continue

        interval_i = abs(m1_note_i - m2_note_i)
        interval_i1 = abs(m1_note_i1 - m2_note_i1)
        interval_type_i = interval_i % 12
        interval_type_i1 = interval_i1 % 12

        is_perfect_i = interval_type_i in perfect_interval_types
        is_perfect_i1 = interval_type_i1 in perfect_interval_types

        if is_perfect_i and is_perfect_i1 and (interval_type_i == interval_type_i1):
            dir1 = m1_note_i1 - m1_note_i
            dir2 = m2_note_i1 - m2_note_i

            if dir1 == 0 or dir2 == 0: continue # Skip oblique motion

            if (dir1 > 0 and dir2 > 0) or (dir1 < 0 and dir2 < 0):
                measure_start = i + 1
                measure_end = i + 2
                findings_list.append(f"{measure_start}-{measure_end}")

    if not findings_list:
        return False
    else:
        output_string = ""
        for item in findings_list:
            output_string += f"mm {{{item}}} find out parallel perfect interval\n"
        # Return True and the formatted string (remove trailing newline)
        return True, output_string.strip()


# --- Helper for Parallel Motives ---
def _get_direction(note1, note2):
    """ Helper function to determine melodic direction """
    if note1 is None or note2 is None: return None
    if note2 > note1: return 1
    elif note2 < note1: return -1
    else: return 0


# --- Step 4: Parallel Motive Detection (Modified Return) ---
def find_parallel_motives(inputCounterpoint, inputCantusFirmus, min_consecutive_moves=3):

    findings_list = [] # Store just the range strings first
    if not inputCounterpoint or not inputCantusFirmus:
        print("Warning: One or both melodies are empty.", file=sys.stderr)
        return False # No findings possible

    if len(inputCounterpoint) != len(inputCantusFirmus):
        print(f"Warning: Melodies have different lengths ({len(inputCounterpoint)} vs {len(inputCantusFirmus)}). Checking up to shortest length.", file=sys.stderr)

    required_notes = min_consecutive_moves + 1
    length = min(len(inputCounterpoint), len(inputCantusFirmus))

    if length < required_notes:
        return False # Not enough notes

    for i in range(length - min_consecutive_moves):
        is_parallel_sequence = True
        notes_in_sequence = []

        for j in range(min_consecutive_moves):
            idx1, idx2 = i + j, i + j + 1
            m1_note1, m2_note1 = inputCounterpoint[idx1], inputCantusFirmus[idx1]
            m1_note2, m2_note2 = inputCounterpoint[idx2], inputCantusFirmus[idx2]

            if j == 0: notes_in_sequence.extend([m1_note1, m2_note1])
            notes_in_sequence.extend([m1_note2, m2_note2])

            dir1 = _get_direction(m1_note1, m1_note2)
            dir2 = _get_direction(m2_note1, m2_note2)

            if dir1 is None or dir2 is None or dir1 == 0 or dir2 == 0 or dir1 != dir2:
                is_parallel_sequence = False
                break

        if None in notes_in_sequence:
            is_parallel_sequence = False

        if is_parallel_sequence:
            measure_start = i + 1
            measure_end = i + min_consecutive_moves + 1
            findings_list.append(f"{measure_start}-{measure_end}")
    
    # Add this missing return statement
    if not findings_list:
        return False
    else:
        output_string = ""
        for item in findings_list:
            output_string += f"mm {{{item}}} find out parallel motives\n"
        # Return True and the formatted string (remove trailing newline)
        return True, output_string.strip()

def check_voice_spacing_crossing_overlapping(inputCounterpoint, inputCantusFirmus):

    findings_list = []

    length = min(len(inputCounterpoint), len(inputCantusFirmus))
    if length == 0:
        return False # Nothing to check

    MAX_ALLOWED_INTERVAL = 16

    for i in range(length):
        upper_note_i = inputCounterpoint[i]
        lower_note_i = inputCantusFirmus[i]

        # Skip if either note at current position is a rest (None)
        if upper_note_i is None or lower_note_i is None:
            continue

        # 1. Check for vertical interval wider than an octave and a major third
        interval = abs(upper_note_i - lower_note_i)
        if interval > MAX_ALLOWED_INTERVAL:
            findings_list.append(
                f"mm {{{i+1}}} vertical interval too wide (actual: {interval} semitones, max allowed: {MAX_ALLOWED_INTERVAL})"
            )

        elif lower_note_i > upper_note_i:
            findings_list.append(
                f"mm {{{i+1}}} voice crossing (lower voice at {lower_note_i} is above upper voice at {upper_note_i})"
            )

        elif i > 0:
            upper_note_prev = inputCounterpoint[i-1]
            lower_note_prev = inputCantusFirmus[i-1]
            if upper_note_prev is not None and lower_note_i > upper_note_prev:
                findings_list.append(
                    f"mm {{{i+1}}} voice overlapping (lower voice at {lower_note_i} is above previous upper voice note at {upper_note_prev}, consider raise an octave or change a note in conterpoint)"
                )

            if lower_note_prev is not None and upper_note_i < lower_note_prev:
                 findings_list.append(
                    f"mm {{{i+1}}} voice overlapping (upper voice at {upper_note_i} is below previous lower voice note at {lower_note_prev}, consider lower an octave or change a note in conterpoint)"
                )

    if not findings_list:
        return False
    else:
        # Join findings into a single string, each on a new line
        output_string = "\n".join(findings_list)
        return True, output_string.strip()

def find_dissonant_leaps(inputCounterpoint):
    """
    Args:
        inputCounterpoint: List of MIDI note numbers for the melody.

    Returns:
        - False if no dissonant leaps are found.
        - Tuple (True, report_string) if found, where report_string lists occurrences.
    """
    findings_list = []
    if not inputCounterpoint or len(inputCounterpoint) < 2:
        # print(f"Warning: Melody '{melody_name}' is too short for dissonant leap check.", file=sys.stderr)
        return False
    problematic_leaps_info = {
        6: "Tritone (6s, e.g., Aug4/Dim5)", # C-F#, C-Gb
        10: "10s (e.g., m7/Aug6)",     # C-Bb, C-A#
        11: "11s (e.g., M7/Dim8)",     # C-B, C-Cb'
    }

    for i in range(len(inputCounterpoint) - 1):
        note1 = inputCounterpoint[i]
        note2 = inputCounterpoint[i+1]

        if note1 is None or note2 is None:
            continue # Skip if a rest is involved in the pair

        leap_size = abs(note1 - note2)

        if leap_size == 0: # Repeated note, not a leap
            continue

        # Define measure_start and measure_end for all cases
        measure_start = i + 1 # Note 1 is in measure i+1
        measure_end = i + 2   # Note 2 is in measure i+2

        if leap_size in problematic_leaps_info:
            interval_desc = problematic_leaps_info[leap_size]
            findings_list.append(
                f"mm {{{measure_start}-{measure_end}}} in Connterpoint: Dissonant melodic movement of {interval_desc}"
            )
        elif leap_size > 12: # General large leaps if not already specified
            findings_list.append(
                f"mm {{{measure_start}-{measure_end}}} in Connterpoint: Very large leap of {leap_size} semitones"
            )


    if not findings_list:
        return False
    else:
        return True, "\n".join(findings_list)


def find_dissonant_interval(inputCounterpoint = [], inputCantusFirmus = []): #find vertical interval is it dissonnant, input as a list of midi number
    """
    Identifies dissonant vertical intervals between counterpoint and cantus firmus.
    
    Args:
        inputCounterpoint: List of MIDI note numbers for the counterpoint melody
        inputCantusFirmus: List of MIDI note numbers for the cantus firmus melody
        
    Returns:
        - False if no dissonant intervals are found
        - Tuple (True, report_string) if found, where report_string lists occurrences
    """
    findings_list = []
    
    if not inputCounterpoint or not inputCantusFirmus:
        print("Warning: One or both melodies are empty.", file=sys.stderr)
        return False  # No findings possible
    
    if len(inputCounterpoint) != len(inputCantusFirmus):
        print(f"Warning: Melodies have different lengths ({len(inputCounterpoint)} vs {len(inputCantusFirmus)}). Checking up to shortest length.", file=sys.stderr)
    
    length = min(len(inputCounterpoint), len(inputCantusFirmus))
    
    # Define dissonant intervals (semitones mod 12)
    dissonant_intervals = {
        1: "minor second",
        2: "major second", 
        6: "tritone",    
        10: "minor seventh",
        11: "major seventh"
    }
    
    for i in range(length):
        cp_note = inputCounterpoint[i]
        cf_note = inputCantusFirmus[i]
        
        if cp_note is None or cf_note is None:
            continue  # Skip if either note is a rest
        
        # Calculate interval
        interval = abs(cp_note - cf_note)
        interval_type = interval % 12  # Normalize to within an octave
        
        if interval_type in dissonant_intervals:
            measure = i + 1  # 1-indexed measure number
            interval_name = dissonant_intervals[interval_type]
            findings_list.append(
                f"mm {{{measure}}} dissonant vertical interval: {interval_name}"
            )
    
    if not findings_list:
        return False
    else:
        return True, "\n".join(findings_list)


def check_octave_unison_rules(inputCounterpoint=[], inputCantusFirmus=[]):
    """
    Checks that octave/unison vertical intervals are only allowed at the beginning and end,
    and that the last interval is either an octave or unison.
    
    Args:
        inputCounterpoint: List of MIDI note numbers for the counterpoint melody
        inputCantusFirmus: List of MIDI note numbers for the cantus firmus melody
        
    Returns:
        - False if no issues are found (all rules followed)
        - Tuple (True, report_string) if issues found, where report_string lists occurrences
    """
    findings_list = []
    
    if not inputCounterpoint or not inputCantusFirmus:
        print("Warning: One or both melodies are empty.", file=sys.stderr)
        return False  # No findings possible
    
    if len(inputCounterpoint) != len(inputCantusFirmus):
        print(f"Warning: Melodies have different lengths ({len(inputCounterpoint)} vs {len(inputCantusFirmus)}). Checking up to shortest length.", file=sys.stderr)
    
    length = min(len(inputCounterpoint), len(inputCantusFirmus))
    if length < 2:
        return False  # Not enough notes to check
    
    # Check middle intervals (not first or last)
    for i in range(1, length - 1):
        cp_note = inputCounterpoint[i]
        cf_note = inputCantusFirmus[i]
        
        if cp_note is None or cf_note is None:
            continue  # Skip if either note is a rest
        
        # Calculate interval and normalize to within an octave
        interval = abs(cp_note - cf_note)
        interval_type = interval % 12
        
        # Check if it's an octave (0) or unison (0)
        if interval_type == 0:
            measure = i + 1  # 1-indexed measure number
            findings_list.append(
                f"mm {{{measure}}} contains octave/unison vertical interval which is only allowed at beginning and end"
            )
    
    # Check last interval
    last_cp = inputCounterpoint[length - 1]
    last_cf = inputCantusFirmus[length - 1]
    
    if last_cp is not None and last_cf is not None:
        last_interval = abs(last_cp - last_cf)
        last_interval_type = last_interval % 12
        
        if last_interval_type != 0:  # Not octave or unison
            findings_list.append(
                f"mm {{{length}}} (final measure) does not end with octave or unison interval"
            )
    
    if not findings_list:
        return False  # No issues found
    else:
        return True, "\n".join(findings_list)


def check_key_adherence(inputCounterpoint=[], key_root=60, is_minor=False):
    """
    Checks if all notes in the counterpoint melody adhere to the specified key.
    For minor keys, considers natural minor and melodic minor (raised 6th and 7th ONLY when ascending).
    
    Args:
        inputCounterpoint: List of MIDI note numbers for the counterpoint melody
        key_root: MIDI note number of the key root (e.g., 60 for C)
        is_minor: Boolean indicating if the key is minor (True) or major (False)
        
    Returns:
        - False if all notes adhere to the key
        - Tuple (True, report_string) if issues found, where report_string lists occurrences
    """
    findings_list = []
    
    if not inputCounterpoint:
        print("Warning: Counterpoint melody is empty.", file=sys.stderr)
        return False
    
    major_scale = [0, 2, 4, 5, 7, 9, 11]
    natural_minor_scale = [0, 2, 3, 5, 7, 8, 10]
    melodic_minor_ascending_scale = [0, 2, 3, 5, 7, 9, 11] # Raised 6th and 7th
    
    note_names = ["C", "C#/Db", "D", "D#/Eb", "E", "F", "F#/Gb", "G", "G#/Ab", "A", "A#/Bb", "B"]
    key_name = note_names[key_root % 12]
    key_name += " minor" if is_minor else " major"
    
    for i in range(len(inputCounterpoint)):
        note = inputCounterpoint[i]
        if note is None:
            continue
        scale_degree = (note - key_root) % 12
        note_name = note_names[note % 12]
        if is_minor:
            # Default to natural minor
            current_scale_to_check = natural_minor_scale
            # If this note is approached by an ascending step, use melodic minor
            if i > 0 and inputCounterpoint[i-1] is not None and note > inputCounterpoint[i-1]:
                current_scale_to_check = melodic_minor_ascending_scale
            if scale_degree not in current_scale_to_check:
                findings_list.append(
                    f"mm {{{i+1}}} note {note_name} (MIDI {note}) is not in {key_name} scale (used {'melodic ascending' if current_scale_to_check == melodic_minor_ascending_scale else 'natural minor'})"
                )
        else:  # Major key
            if scale_degree not in major_scale:
                findings_list.append(
                    f"mm {{{i+1}}} note {note_name} (MIDI {note}) is not in {key_name} scale"
                )
    
    if not findings_list:
        return False
    else:
        return True, "\n".join(findings_list)

        import collections
import math # Using math.floor for clarity, though int() truncates (like floor for positive numbers)
import collections
def analyze_melody_characteristics(inputMelody):
    """
    Analyzes a melody for specific characteristics:
    1. Note Variety: No single note (MIDI pitch) occupies more than 30% of the melody's
       actual notes (rests are excluded from this count).
    2. Apex Location: There is a single occurrence of the melody's highest note (apex)
       within the window spanning from the 50% position to the 90% position
       of the melody's total length (inclusive, 0-indexed).

    Args:
        inputMelody: List of MIDI note numbers for the melody.
                     `None` values represent rests.

    Returns:
        - False if all conditions are met.
        - Tuple (True, report_string) if one or more conditions are not met,
          where report_string lists all identified issues.
    """
    findings_list = []

    if not inputMelody:
        findings_list.append("Melody is empty. Compose a melody first with notes.")
        return True, "\n".join(findings_list)  # Return early if melody is empty

    actual_notes = [note for note in inputMelody if note is not None]


    num_actual_notes = len(actual_notes)
    note_counts = collections.Counter(actual_notes)
    for note_pitch, count in note_counts.items():
        percentage = (count / num_actual_notes) * 100
        if percentage > 30:
            # Find 1-based positions for reporting
            positions_of_note = [i + 1 for i, n in enumerate(inputMelody) if n == note_pitch]
            findings_list.append(
                f"Note Variety: Pitch {note_pitch} occurs too frequently, "
                f"occupying {percentage:.1f}% of the {num_actual_notes} actual notes "
                f"(at melody positions: {positions_of_note}). Maximum allowed is 30%."
            )

    # --- 2. Single Apex in 50%-90% Window Check ---
    melody_total_length = len(inputMelody) # Total items, including rests


    overall_highest_note = max(actual_notes)

    # Find all 0-based indices where the overall_highest_note occurs in the original melody
    indices_of_overall_highest = [i for i, note in enumerate(inputMelody) if note == overall_highest_note]

    # Define the 0-based index window [50% mark, 90% mark] inclusive for positions.
    # Example: melody_total_length = 10 (indices 0-9)
    # window_start_idx = floor(10 * 0.5) = 5
    # window_end_idx   = floor(10 * 0.9) = 9
    # This means the window covers indices 5, 6, 7, 8, 9.
    
    # For L=1 (index 0): start=floor(0.5)=0, end=floor(0.9)=0. Window: index 0.
    # For L=2 (indices 0,1): start=floor(1.0)=1, end=floor(1.8)=1. Window: index 1.
    # This interpretation seems consistent with "position of".
    window_start_idx = math.floor(melody_total_length * 0.5)
    window_end_idx = math.floor(melody_total_length * 0.9)
    
    # Ensure the window is sensible (e.g., for L=1, start=0, end=0 is fine).
    # If melody_total_length is 0, this block is skipped by 'if not actual_notes'
    # or 'if not inputMelody'.

    occurrences_of_highest_in_window = 0
    positions_in_window_report = [] # 1-based for reporting

    for idx in indices_of_overall_highest:
        if window_start_idx <= idx <= window_end_idx:
            occurrences_of_highest_in_window += 1
            positions_in_window_report.append(idx + 1)
    
    # Prepare 1-based indices for reporting the window
    report_window_start = window_start_idx + 1
    report_window_end = window_end_idx + 1
    if melody_total_length == 0 : # Should not happen here due to prior checks.
            report_window_start = 0
            report_window_end = 0


    if occurrences_of_highest_in_window == 0:
        all_occurrences_report = [i+1 for i in indices_of_overall_highest]
        findings_list.append(
            f"Apex: The highest note ({overall_highest_note}, found at melody positions {all_occurrences_report}) "
            f"does not occur within the 50%-90% target window "
            f"(melody positions {report_window_start}-{report_window_end} of {melody_total_length} total items)."
        )
    elif occurrences_of_highest_in_window > 1:
        findings_list.append(
            f"Apex: The highest note ({overall_highest_note}) occurs multiple times "
            f"({occurrences_of_highest_in_window} times at melody positions {positions_in_window_report}) "
            f"within the 50%-90% target window "
            f"(melody positions {report_window_start}-{report_window_end}). Expected a single occurrence here."
        )
    # If occurrences_of_highest_in_window == 1, this condition is met.

    if not findings_list:
        return False
    else:
        return True, "\n".join(findings_list)

if __name__ == '__main__':
    # Test cases
    print("--- Test Cases ---")

    # Case 1: All good
    melody1 = [60, 62, 64, 65, 67, 72, 70, 69, 65, 62] # L=10. Apex 72 at index 5 (pos 6).
    # Actual notes: 10. No note > 30%.
    # Apex: Highest 72. Occurs at index 5.
    # Window: L=10. start_idx = floor(5)=5. end_idx = floor(9)=9. Window indices [5,6,7,8,9].
    # Index 5 is in window. Single occurrence.
    print(f"Melody 1: {melody1}")
    result1 = analyze_melody_characteristics(melody1)
    print(f"Result: {result1}\n") # Expected: False

    # Case 2: Note variety issue
    melody2 = [60, 60, 60, 60, 60, 72, 65, 65, 65, 65] # L=10. 60 is 50%, 65 is 40%. Apex 72 at index 5.
    # Actual notes: 10. 60 (50%), 65 (40%)
    # Apex: Highest 72. Occurs at index 5. Window [5-9]. OK.
    print(f"Melody 2: {melody2}")
    result2 = analyze_melody_characteristics(melody2)
    print(f"Result: {result2}\n") # Expected: (True, "Note Variety: Pitch 60...\nNote Variety: Pitch 65...")

    # Case 3: Apex not in window
    melody3 = [72, 60, 62, 64, 65, 67, 70, 69, 65, 62] # L=10. Apex 72 at index 0.
    # Actual notes: 10. Variety OK.
    # Apex: Highest 72. Occurs at index 0. Window [5-9]. Not in window.
    print(f"Melody 3: {melody3}")
    result3 = analyze_melody_characteristics(melody3)
    print(f"Result: {result3}\n") # Expected: (True, "Apex: The highest note (72)...does not occur...")

    # Case 4: Multiple apexes in window
    melody4 = [60, 62, 64, 65, 67, 72, 70, 72, 65, 72] # L=10. Apex 72 at indices 5, 7, 9.
    # Actual notes: 10. Variety OK.
    # Apex: Highest 72. Occurs at 5,7,9. Window [5-9]. All 3 in window.
    print(f"Melody 4: {melody4}")
    result4 = analyze_melody_characteristics(melody4)
    print(f"Result: {result4}\n") # Expected: (True, "Apex: The highest note (72)...occurs multiple times...")

    # Case 5: Apex outside window, another occurrence of highest note also outside.
    melody5 = [72, 60, 62, 64, 65, 67, 70, 69, 65, 72] # L=10. Apex 72 at indices 0, 9.
    # Actual notes: 10. Variety OK.
    # Apex: Highest 72. Occurs at 0, 9. Window [5-9]. Index 9 is in window. Single occurrence IN window.
    print(f"Melody 5: {melody5}")
    result5 = analyze_melody_characteristics(melody5)
    print(f"Result: {result5}\n") # Expected: False

    # Case 6: Short melody - passes apex, fails variety
    melody6 = [60] # L=1.
    # Actual notes: 1. Variety: 60 is 100%. Fails.
    # Apex: Highest 60. Occurs at index 0. Window: L=1. start=floor(0.5)=0, end=floor(0.9)=0. Window [0]. OK.
    print(f"Melody 6: {melody6}")
    result6 = analyze_melody_characteristics(melody6)
    print(f"Result: {result6}\n") # Expected: (True, "Note Variety: Pitch 60...")

    # Case 7: Short melody - passes both (e.g. two different notes)
    melody7 = [60, 70] # L=2
    # Actual notes: 2. Variety: 60 (50%), 70 (50%). Fails.
    # Apex: Highest 70. Occurs at index 1. Window: L=2. start=floor(1)=1, end=floor(1.8)=1. Window [1]. OK.
    print(f"Melody 7: {melody7}")
    result7 = analyze_melody_characteristics(melody7)
    print(f"Result: {result7}\n") # Expected: (True, "Note Variety: Pitch 60...\nNote Variety: Pitch 70...")
    
    melody7b = [60,70,65] # L=3
    # Actual notes: 3. Variety: Each 33.33%. Fails for all.
    # Apex: Highest 70. Index 1. Window: L=3. start=floor(1.5)=1, end=floor(2.7)=2. Window [1,2]. OK.
    print(f"Melody 7b: {melody7b}")
    result7b = analyze_melody_characteristics(melody7b)
    print(f"Result: {result7b}\n") # Expected: (True, "Note Variety: Pitch 60...\nNote Variety: Pitch 70...\nNote Variety: Pitch 65...")

    # Case 8: Melody with rests
    melody8 = [60, None, 62, None, 72, 65] # L=6. Actual notes = [60,62,72,65] (len 4)
    # Variety: Each note 1/4 = 25%. OK.
    # Apex: Highest 72 at original index 4.
    # Window: L=6. start=floor(3)=3, end=floor(5.4)=5. Window indices [3,4,5].
    # Index 4 (for note 72) is in window. Single occurrence. OK.
    print(f"Melody 8: {melody8}")
    result8 = analyze_melody_characteristics(melody8)
    print(f"Result: {result8}\n") # Expected: False

    # Case 9: Empty melody
    melody9 = []
    print(f"Melody 9: {melody9}")
    result9 = analyze_melody_characteristics(melody9)
    print(f"Result: {result9}\n") # Expected: False

    # Case 10: Melody with only rests
    melody10 = [None, None, None]
    print(f"Melody 10: {melody10}")
    result10 = analyze_melody_characteristics(melody10)
    print(f"Result: {result10}\n") # Expected: (True, "Apex: Melody contains no actual notes...")

    # Case 11: Multiple apexes, one in window, one outside
    melody11 = [72, 60, 62, 64, 65, 72, 70, 69, 65, 62] # L=10. Apex 72 at indices 0, 5.
    # Variety OK.
    # Apex: Highest 72. Occurs at index 0 and 5. Window [5-9]. Index 5 is in window. Single occurrence in window. OK.
    print(f"Melody 11: {melody11}")
    result11 = analyze_melody_characteristics(melody11)
    print(f"Result: {result11}\n") # Expected: False