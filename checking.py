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

