def find_parallel_perfect_intervals(melody1, melody2):
    """
    Finds parallel perfect intervals (P1, P4, P5, P8) between two MIDI note lists.
    Returns:
        - False if no parallel perfect intervals are found.
        - Tuple (True, report_string) if found, where report_string lists
          each occurrence formatted as "mm {x-y} find out parallel perfect interval\n".
    """
    findings_list = [] # Store just the range strings first
    if not melody1 or not melody2:
        print("Warning: One or both melodies are empty.", file=sys.stderr)
        return False # No findings possible

    if len(melody1) != len(melody2):
        print(f"Warning: Melodies have different lengths ({len(melody1)} vs {len(melody2)}). Checking up to shortest length.", file=sys.stderr)

    length = min(len(melody1), len(melody2))
    perfect_interval_types = [0, 5, 7] # P1/P8=0, P4=5, P5=7

    for i in range(length - 1):
        m1_note_i, m2_note_i = melody1[i], melody2[i]
        m1_note_i1, m2_note_i1 = melody1[i+1], melody2[i+1]

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

    # --- Format the return value ---
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
def find_parallel_motives(melody1, melody2, min_consecutive_moves=3):

    findings_list = [] # Store just the range strings first
    if not melody1 or not melody2:
        print("Warning: One or both melodies are empty.", file=sys.stderr)
        return False # No findings possible

    if len(melody1) != len(melody2):
        print(f"Warning: Melodies have different lengths ({len(melody1)} vs {len(melody2)}). Checking up to shortest length.", file=sys.stderr)

    required_notes = min_consecutive_moves + 1
    length = min(len(melody1), len(melody2))

    if length < required_notes:
        return False # Not enough notes

    for i in range(length - min_consecutive_moves):
        is_parallel_sequence = True
        notes_in_sequence = []

        for j in range(min_consecutive_moves):
            idx1, idx2 = i + j, i + j + 1
            m1_note1, m2_note1 = melody1[idx1], melody2[idx1]
            m1_note2, m2_note2 = melody1[idx2], melody2[idx2]

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