This project leverages large language models (LLMs) to create musical compositions following counterpoint rules, then validates them against classical music theory principles.

## Features
- Generate musical counterpoint melodies using various AI models (OpenAI, DeepSeek, Google Gemini)
- Convert between MIDI and LilyPond formats for musical notation
- Analyze melodies for adherence to counterpoint rules
- Provide feedback on musical characteristics
- Robust error handling for API interactions
- Export results as MIDI, LilyPond (.ly), and PDF files

## Counterpoint Rule Validation
- Parallel Perfect Intervals Detection : Identifies consecutive perfect intervals (unisons, octaves, fourths, fifths) moving in the same direction, which are generally avoided in good counterpoint.
- Parallel Motives Analysis : Detects when both voices move in parallel motion for three or more consecutive notes.
- Voice Spacing and Crossing : Ensures proper vertical spacing between voices (not exceeding an octave and a major third) and prevents voice crossing or overlapping.
- Dissonant Leaps : Identifies problematic melodic movements such as tritones, sevenths, and other dissonant intervals that should be handled with care in counterpoint.
- Repeated Notes : Flags consecutive repetitions of the same pitch, which can diminish melodic interest.
- Dissonant Vertical Intervals : Detects harmonically dissonant intervals between the counterpoint and cantus firmus, including seconds, sevenths, and tritones.
- Octave/Unison Rules : Enforces the convention that octaves and unisons should only appear at the beginning and end of a composition.
- Key Adherence : Verifies that all notes in the melody adhere to the specified key, with special handling for melodic minor scales (raised 6th and 7th degrees when ascending).
## Melodic Characteristics Analysis
- Note Variety : Ensures no single pitch dominates the melody (no more than 40% of the total notes).
- Apex Placement : Validates that the highest note (apex) of the melody appears only once and is properly positioned within the 50-90% window of the composition's length.
