import re
import sys
import os
from dotenv import load_dotenv
from openai import OpenAI
EXAMPLE_COUNTERPOINT = [79, 83, 81, 83, 72, 76, 84, 83, 79, 77, 79]
EXAMPLE_CANTUS_FIRMUS = [60, 62, 65, 64, 65, 67, 69, 67, 64, 62, 60]
load_dotenv()


def is_same_melody(midi_dict, example_counterpoint=EXAMPLE_COUNTERPOINT):
    """
    Check if the generated melody is too similar to the example.
    Returns True if more than 70% of notes are the same.
    """
    if not isinstance(midi_dict, dict) or 'Counterpoint' not in midi_dict:
        return False
        
    counterpoint_midi = midi_dict['Counterpoint']
    
    # If lengths are different, it's definitely a different melody
    if len(counterpoint_midi) != len(example_counterpoint):
        return False
    
    # Check if more than 70% of notes are the same
    same_notes = sum(1 for a, b in zip(counterpoint_midi, example_counterpoint) if a == b)
    similarity_percentage = same_notes / len(example_counterpoint) * 100
    
    return similarity_percentage > 80


def extract_midi_from_response(response_text):
    """
    Extract MIDI dictionary from LLM response using regex.
    Returns a dictionary with 'Counterpoint' and 'CantusFirmus' keys.
    """
    midi_format_pattern = r"\{\s*'Counterpoint'\s*:\s*\[(\d+(?:\s*,\s*\d+)*)\]\s*,\s*'CantusFirmus'\s*:\s*\[(\d+(?:\s*,\s*\d+)*)\]\s*\}"
    midi_match = re.search(midi_format_pattern, response_text)
    
    if not midi_match:
        return None
    
    # Extract the MIDI values from the regex match
    counterpoint_str = midi_match.group(1)
    cantus_firmus_str = midi_match.group(2)
    
    # Convert string representations to actual lists of integers
    counterpoint_midi = [int(x.strip()) for x in counterpoint_str.split(',')]
    cantus_firmus_midi = [int(x.strip()) for x in cantus_firmus_str.split(',')]
    
    return {
        'Counterpoint': counterpoint_midi,
        'CantusFirmus': cantus_firmus_midi
    }


def create_fallback_midi():
    """
    Create a fallback MIDI dictionary when LLM fails to return proper format.
    Returns a dictionary with slightly modified counterpoint from the example.
    """
    # Create a slightly different counterpoint from the example
    modified_counterpoint = [note + (1 if i % 2 == 0 else -1) 
                            for i, note in enumerate(EXAMPLE_COUNTERPOINT)]
    
    return {
        'Counterpoint': modified_counterpoint,
        'CantusFirmus': EXAMPLE_CANTUS_FIRMUS
    }


def send_to_llm(conterpoint, comments='None', max_attempts=3):
    api_key = os.getenv("OPEN_KEY")
    if not api_key:
        raise ValueError("API key not found in .env file")
    
    # Initialize OpenAI client with the provided API base URL
    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )
    
    # Base system prompt with specific instructions
    system_prompt = (
        "You are an expert music composer specializing in counterpoint. "
        "You must follow these strict counterpoint rules:\n"
        "1. Avoid parallel motives (when both voices move in the same direction for 3+ consecutive notes)\n"
        "2. Avoid parallel perfect intervals (unison, fifth, octave)\n"
        "3. Maintain proper voice spacing\n"
        "4. Avoid dissonant leaps\n\n"
        "When given feedback about rule violations, you MUST create a DIFFERENT melody that fixes these issues.\n"
        "Return only valid midi notation in the EXACT same format as the example: "
        "{'Counterpoint': [79, 83, 81, 83, 72, 76, 84, 83, 79, 77, 79], "
        "'CantusFirmus': [60, 62, 65, 64, 65, 67, 69, 67, 64, 62, 60]}"
    )
    
    # Use iteration instead of recursion for retries
    attempts_remaining = max_attempts
    
    while attempts_remaining > 0:
        try:
            completion = client.chat.completions.create(
                model="deepseek/deepseek-chat:free",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "Complete the following first species counterpoint example. \n"
                        + conterpoint + "\n Please fix the problem: " + comments},
                ]
            )
            
            # Check if completion and choices exist before accessing
            if completion and hasattr(completion, 'choices') and completion.choices:
                llm_response = completion.choices[0].message.content
                print(f"Attempt {max_attempts - attempts_remaining + 1}/{max_attempts} - LLM Response:", llm_response)
                
                midi_melodies = extract_midi_from_response(llm_response)
                if midi_melodies:
                    return midi_melodies
            else:
                print(f"Attempt {max_attempts - attempts_remaining + 1}/{max_attempts} - API returned empty or invalid response")
                
        except Exception as e:
            print(f"Attempt {max_attempts - attempts_remaining + 1}/{max_attempts} - Error: {str(e)}")
        
        # Enhance the prompt for retry
        system_prompt += ("\n\nIMPORTANT: Your previous response was not in the correct format.\n"
                         "You MUST return a dictionary with 'Counterpoint' and 'CantusFirmus' "
                         "keys containing MIDI note arrays.\n")
        
        attempts_remaining -= 1
        if attempts_remaining > 0:
            print(f"LLM returned invalid format. Trying again (attempt {max_attempts - attempts_remaining + 1}/{max_attempts})...")
    
    # All attempts failed, return fallback MIDI
    print("LLM failed to return valid format after multiple attempts. Returning fallback MIDI.")
    return create_fallback_midi()


# For testing the module directly
if __name__ == "__main__":


    example = """
    \version "2.24.4"
    \score {
      \new StaffGroup <<
        \new Staff = "Counterpoint" << \clef treble \key c \major \time 4/4 \fixed c' { g1 | a1 | g1 | a1 | e1 | g1 | c'1 | b1 | g1 | f1 | g1 } >>
        \new Staff = "CantusFirmus" << \clef bass \key c \major \time 4/4 \fixed c { c1 | d1 | f1 | e1 | f1 | g1 | a1 | g1 | e1 | d1 | c1 } >>
      >>
      \layout { }
    }
    """
    
    # Test the send_to_llm function
    result = send_to_llm(example, "There are parallel motives in measures 1-3")
    print("Final result:")
    print(result)