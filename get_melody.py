import re
import sys  # Added import for sys.stderr

def note_to_midi(note_str):

    if not note_str or note_str.lower() == 'r': # Handle rests or empty strings
        return None

    base_notes = {'c': 0, 'd': 2, 'e': 4, 'f': 5, 'g': 7, 'a': 9, 'b': 11}
    reference_midi = 60 # Base MIDI note for 'c' in \fixed c (Middle C)

    # Use regex to handle pitch, accidentals, and octave marks more robustly
    match = re.match(r"([a-g])(is|isis|es|eses)?(['\,]*)", note_str.lower())
    if not match:
         # Basic rest check or unknown format
        if note_str.lower().startswith('r'):
            return None
        raise ValueError(f"Could not parse note: {note_str}")

    pitch_class_str, accidental, octave_marks = match.groups()

    if pitch_class_str not in base_notes:
         # This shouldn't happen with the regex, but belt-and-suspenders
        raise ValueError(f"Unknown base note: {pitch_class_str} in {note_str}")

    midi_val = base_notes[pitch_class_str]

    # Handle accidentals
    if accidental == "is":
        midi_val += 1
    elif accidental == "es":
        midi_val -= 1
    elif accidental == "isis":
        midi_val += 2
    elif accidental == "eses":
        midi_val -= 2

    # Handle octave marks
    octave_shift = (octave_marks.count("'") - octave_marks.count(",")) if octave_marks else 0
    midi_val += reference_midi + (octave_shift * 12)

    return midi_val


# --- Step 2: Melody Extraction Function ---
# (Keep extract_melodies_from_ly as it is)
def extract_melodies_from_ly(lilypond_content):
    """
    Extracts note sequences from named staves within a LilyPond file content.
    Looks for '\new Staff = "StaffName" << ... \fixed c { NOTES } ... >>' structure.
    Returns a dictionary mapping staff names to lists of MIDI note numbers.
    """
    melodies = {}
    # Regex to find staves and their notes within \fixed c {}
    pattern = re.compile(
          r'\\new\s+Staff\s*=\s*"(?P<staffname>[^"]+)"\s*<<.*?\\fixed\s+c[^{]*{(?P<notes>.*?)}.*?>>',
          re.DOTALL | re.IGNORECASE
      )

    for match in pattern.finditer(lilypond_content):
        staff_name = match.group("staffname")
        notes_str = match.group("notes")

        # Clean up the notes string: remove comments, bar lines, extra whitespace
        notes_str = re.sub(r'%.*?\n', '', notes_str) # Remove full-line comments
        notes_str = re.sub(r'%.*', '', notes_str)    # Remove end-of-line comments
        notes_str = notes_str.replace('|', ' ')     # Replace bar lines with spaces
        notes_str = re.sub(r'\s+', ' ', notes_str).strip() # Normalize whitespace

        # Split into individual note elements (pitch + duration, rest, etc.)
        note_tokens = [token for token in notes_str.split(' ') if token]

        midi_notes = []
        for token in note_tokens:
            # Extract just the pitch part using regex (more robust)
            # This tries to find the pitch at the beginning of the token
            pitch_match = re.match(r"([a-g](?:is|isis|es|eses)?['\,]*)", token)
            if pitch_match:
                pitch_str = pitch_match.group(1)
                try:
                    midi_val = note_to_midi(pitch_str)
                    midi_notes.append(midi_val) # midi_val could be None if note_to_midi handles 'r' inside
                except ValueError as e:
                    print(f"Warning: Skipping unparseable note token '{token}': {e}", file=sys.stderr)
                    midi_notes.append(None) # Append None for unparseable tokens to keep alignment
            elif token.lower().startswith('r'): # Explicit rest
                 midi_notes.append(None)

        melodies[staff_name] = midi_notes
    return melodies # Return in a dic of midi numbers eg:{'Counterpoint': [79, 83, 81, 83, 72, 76, 84, 83, 79, 77, 79], 'CantusFirmus': [60, 62, 65, 64, 65, 67, 69, 67, 64, 62, 60]}

