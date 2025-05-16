import sys # Added for sys.stderr, as other functions may use it.
from get_melody import extract_melodies_from_ly
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

def check_voice_spacing_crossing_overlapping(melody1, melody2):

    findings_list = []

    length = min(len(melody1), len(melody2))
    if length == 0:
        return False # Nothing to check

    # Define the maximum allowed interval (Octave + Major Third = 12 + 4 = 16 semitones)
    # "Wider than" this means interval > MAX_ALLOWED_INTERVAL.
    MAX_ALLOWED_INTERVAL = 16

    for i in range(length):
        upper_note_i = melody1[i]
        lower_note_i = melody2[i]

        # Skip if either note at current position is a rest (None)
        if upper_note_i is None or lower_note_i is None:
            continue

        # 1. Check for vertical interval wider than an octave and a major third
        interval = abs(upper_note_i - lower_note_i)
        if interval > MAX_ALLOWED_INTERVAL:
            findings_list.append(
                f"mm {{{i+1}}} vertical interval too wide (actual: {interval} semitones, max allowed: {MAX_ALLOWED_INTERVAL})"
            )

        # 2. Check for voice crossing
        # Assumes melody1 is upper voice, melody2 is lower voice.
        # Crossing occurs if lower voice is pitched higher than upper voice.
        if lower_note_i > upper_note_i:
            findings_list.append(
                f"mm {{{i+1}}} voice crossing (lower voice at {lower_note_i} is above upper voice at {upper_note_i})"
            )

        # 3. Check for voice overlapping (needs previous note, so start from i > 0)
        if i > 0:
            upper_note_prev = melody1[i-1]
            lower_note_prev = melody2[i-1]

            # Check current lower voice note against previous upper voice note
            # Ensure previous upper note was not a rest before comparing
            if upper_note_prev is not None and lower_note_i > upper_note_prev:
                findings_list.append(
                    f"mm {{{i+1}}} voice overlapping (lower voice at {lower_note_i} is above previous upper voice note at {upper_note_prev})"
                )

            # Check current upper voice note against previous lower voice note
            # Ensure previous lower note was not a rest before comparing
            if lower_note_prev is not None and upper_note_i < lower_note_prev:
                 findings_list.append(
                    f"mm {{{i+1}}} voice overlapping (upper voice at {upper_note_i} is below previous lower voice note at {lower_note_prev})"
                )

    if not findings_list:
        return False
    else:
        # Join findings into a single string, each on a new line
        output_string = "\n".join(findings_list)
        return True, output_string.strip()

score=r"""\version "2.24.4"
\header {
  title = "First Species Counterpoint Example"
  subtitle = "Counterpoint Above CF in C Major"
}

\score {
  <<
    \new Staff = "Counterpoint" <<
      \clef treble
      \key c \major
      \time 4/4
      \fixed c {
        g'1 | b'1 | a'1 | b'1 | c'1 | e'1 | c''1 | b'1 | g'1 | f'1 | g'1
      }
    >>
    \new Staff = "CantusFirmus" <<
      \clef bass
      \key c \major
      \time 4/4
      \fixed c {
        c1 | d1 | f1 | e1 | f1 | g1 | a1 | g1 | e1 | d1 | c1
      }
    >>
  >>
  \layout { }
}
"""

print(extract_melodies_from_ly(score))

score2=r"""\version "2.24.4"
\header {
  title = "First Species Counterpoint Example"
  subtitle = "Counterpoint Above CF in C Major"
}

\score {
  <<
    \new Staff = "Counterpoint" <<
      \clef treble
      \key c \major
      \time 4/4
      \fixed c' { 
        g1 | f'1 | e'1 | g'1 | a'1 | f'1 | e'1 | b1 | d'1 | b'1 | c'1
      }
    >>
    \new Staff = "CantusFirmus" <<
      \clef bass
      \key c \major
      \time 4/4
      \fixed c { 
        c1 | d1 | f1 | e1 | f1 | g1 | a1 | g1 | e1 | d1 | c1
      }
    >>
  >>
  \layout { }
}"""

print(extract_melodies_from_ly(score2))