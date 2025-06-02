import re
import sys
import os
from dotenv import load_dotenv
from openai import OpenAI
# Import checking functions
from checking import (
    find_parallel_perfect_intervals,
    find_parallel_motives,
    check_voice_spacing_crossing_overlapping,
    find_dissonant_leaps,
    check_repeated_notes,
    find_dissonant_interval,
    check_octave_unison_rules,
    check_key_adherence,
    analyze_melody_characteristics # Ensure it's imported
)

EXAMPLE_COUNTERPOINT = [79, 83, 81, 83, 72, 76, 84, 83, 79, 77, 79]
EXAMPLE_CANTUS_FIRMUS = [60, 62, 65, 64, 65, 67, 69, 67, 64, 62, 60]
load_dotenv()
MODEL = "deepseek/deepseek-r1-0528"
BASE_URL ="https://openrouter.ai/api/v1"# "https://api.x.ai/v1"##"https://api.siliconflow.cn/v1"#"https://api.siliconflow.cn/v1"##" #"Pro/deepseek-ai/DeepSeek-R1"
api_key = os.getenv("OPEN_API")
if not api_key:
    raise ValueError("API key not found in .env file")
def is_same_melody(midi_dict, example_counterpoint=EXAMPLE_COUNTERPOINT):
    """
    Check if the generated melody is too similar to the example.
    """
    if not isinstance(midi_dict, dict) or 'Counterpoint' not in midi_dict:
        return False
        
    counterpoint_midi = midi_dict['Counterpoint']
    
    # If lengths are different, it's definitely a different melody
    if len(counterpoint_midi) != len(example_counterpoint):
        return False
    
    same_notes = sum(1 for a, b in zip(counterpoint_midi, example_counterpoint) if a == b)
    similarity_percentage = same_notes / len(example_counterpoint) * 100
    
    return similarity_percentage > 80

def extract_midi_from_response(response_text):
    """
    Extract MIDI dictionary from LLM response using regex.
    Returns a dictionary with 'Counterpoint' and 'CantusFirmus' keys.
    """
    import json
    import re # Ensure re is imported
    
    # First, try to extract JSON from markdown code blocks
    code_block_pattern = r'```(?:json)?\s*({[^`]+})\s*```'
    code_block_match = re.search(code_block_pattern, response_text, re.DOTALL)
    
    if code_block_match:
        json_str = code_block_match.group(1)
        try:
            midi_dict_raw = json.loads(json_str)
            
            # Normalize keys: check for lowercase and capitalize if necessary
            counterpoint_key = None
            cantus_firmus_key = None

            for k in midi_dict_raw.keys():
                if k.lower() == 'counterpoint':
                    counterpoint_key = k
                elif k.lower() == 'cantusfirmus': # Checking for 'cantusfirmus' as well
                    cantus_firmus_key = k
                elif k.lower() == 'cantus_firmus': # Checking for 'cantus_firmus' with underscore
                    cantus_firmus_key = k
            
            if counterpoint_key and cantus_firmus_key:
                print("Extracted from code block:", {
                    'Counterpoint': midi_dict_raw[counterpoint_key],
                    'CantusFirmus': midi_dict_raw[cantus_firmus_key]
                })
                return {
                    'Counterpoint': midi_dict_raw[counterpoint_key],
                    'CantusFirmus': midi_dict_raw[cantus_firmus_key]
                }
        except (json.JSONDecodeError, ValueError) as e:
            print(f"JSON parsing from code block failed: {e}. Trying other methods.")
    
    # Try to parse as JSON directly and handle different key casings
    try:
        # Look for JSON object pattern (fixed regex)
        match = re.search(r'{[^{}]*}', response_text, re.DOTALL)
        if match:
            json_str = match.group(0)
            midi_dict_raw = json.loads(json_str)
            
            # Normalize keys: check for lowercase and capitalize if necessary
            counterpoint_key = None
            cantus_firmus_key = None

            for k in midi_dict_raw.keys():
                if k.lower() == 'counterpoint':
                    counterpoint_key = k
                elif k.lower() == 'cantusfirmus': # Checking for 'cantusfirmus' as well
                    cantus_firmus_key = k
                elif k.lower() == 'cantus_firmus': # Checking for 'cantus_firmus' with underscore
                    cantus_firmus_key = k
            
            if counterpoint_key and cantus_firmus_key:
                return {
                    'Counterpoint': midi_dict_raw[counterpoint_key],
                    'CantusFirmus': midi_dict_raw[cantus_firmus_key]
                }
    except (json.JSONDecodeError, ValueError) as e:
        print(f"JSON parsing failed: {e}. Falling back to regex.")
        pass
    
    # Fallback to regex patterns, making key matching case-insensitive
    # Pattern for 'Counterpoint' or 'counterpoint'
    cp_pattern = r"['\"](?:Counterpoint|counterpoint)['\"]\s*:\s*\[([\d\s,]*)\]"
    # Pattern for 'CantusFirmus', 'cantusfirmus', or 'cantus_firmus'
    cf_pattern = r"['\"](?:CantusFirmus|cantusfirmus|Cantus_Firmus|cantus_firmus)['\"]\s*:\s*\[([\d\s,]*)\]"

    cp_match = re.search(cp_pattern, response_text, re.IGNORECASE)
    cf_match = re.search(cf_pattern, response_text, re.IGNORECASE)
    
    if cp_match and cf_match:
        counterpoint_str = cp_match.group(1)
        cantus_firmus_str = cf_match.group(1)
        
        counterpoint_midi = [int(x.strip()) for x in counterpoint_str.split(',') if x.strip().isdigit()]
        cantus_firmus_midi = [int(x.strip()) for x in cantus_firmus_str.split(',') if x.strip().isdigit()]
        
        if counterpoint_midi and cantus_firmus_midi: # Ensure lists are not empty
            print("Extracted json:",{
                'Counterpoint': counterpoint_midi,
                'CantusFirmus': cantus_firmus_midi
            })
            return {
                'Counterpoint': counterpoint_midi,
                'CantusFirmus': cantus_firmus_midi
            }
    
    print("Failed to extract MIDI data from response.")
    return None



def send_to_llm(conterpoint, initial_comments="", max_attempts=5, use_checking=True):
    """
    Send the counterpoint to the LLM and return the generated MIDI.
    Optionally uses checking.py to refine the output.
    """
    
    client = OpenAI(
        api_key=api_key,
        base_url=BASE_URL
    )
    
    system_prompt_base = (
        "You are an expert music composer specializing in counterpoint. "
        "You must follow these strict counterpoint rules:\n"
        "1. Avoid parallel motives (when both voices move in the same direction for 3+ consecutive notes)\n"
        "2. Avoid parallel perfect intervals (unison, fifth, octave)\n"
        "3. Maintain proper voice spacing (avoid crossing, overlapping, and intervals > octave + M3)\n"
        "4. Avoid dissonant leaps (tritones, sevenths, ninths, etc.) in melodies\n"
        "5. Avoid repeated notes consecutively in the counterpoint.\n"
        "6. Vertical intervals should generally be consonant (P1, m3, M3, P4, P5, m6, M6, P8). P4 is dissonant against the bass but can be used carefully.\n"
        "7. Octaves/Unisons are only allowed at the beginning and end of the piece for vertical intervals.\n"
        "8. Adhere to the specified key (e.g., C Major) and avoid notes outside the key unless modally appropriate or for specific expressive reasons that are resolved.\n\n"
        "When given feedback about rule violations, you MUST create a DIFFERENT melody that fixes these issues.\n"
        "Return only valid midi notation in the EXACT same format as the example in json format: "
        "{'Counterpoint': [79, 83, 81, 83, 72, 76, 84, 83, 79, 77, 79], "
        "'CantusFirmus': [60, 62, 65, 64, 65, 67, 69, 67, 64, 62, 60]}"
    )

    current_comments = initial_comments
    attempts_remaining = max_attempts

    while attempts_remaining > 0:
        llm_response = None # Initialize llm_response here for each attempt
        system_prompt = system_prompt_base
        user_content = f"Complete the following first species counterpoint example. \n{conterpoint}"
        user_content += f"\nPlease fix the following problems based on the previous attempt: {current_comments}"

        print(f"Sending with comments: {current_comments}")
        try:
            completion = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                ],
                temperature=0.8 
            )
            
            llm_response = completion.choices[0].message.content
            print(f"LLM Response content: {llm_response}")
            
        except Exception as e:
            print(f"Error calling LLM API: {e}")
            if attempts_remaining < max_attempts - 1:
                print(f"Retrying... (attempt {attempts_remaining + 1}/{max_attempts})")
                continue
            else:
                print("Max attempts reached. Returning fallback result.")
                # Return a proper tuple instead of None
                if use_checking:
                    return "Error: API failed after max attempts", conterpoint if conterpoint else None
                else:
                    return "Error: API failed after max attempts", None
        
        midi_melodies = extract_midi_from_response(llm_response)
        print(use_checking, midi_melodies)
        if use_checking and midi_melodies:
            print("Checking generated MIDI...")
            cp = midi_melodies.get('Counterpoint', [])
            cf = midi_melodies.get('CantusFirmus', [])
            all_feedback = []

            # Run all checks from checking.py
            checks = [
                (find_parallel_perfect_intervals, (cp, cf)),
                (find_parallel_motives, (cp, cf)),
                (check_voice_spacing_crossing_overlapping, (cp, cf)),
                (find_dissonant_leaps, (cp,)),
                (check_repeated_notes, (cp,)),
                (find_dissonant_interval, (cp, cf)),
                (check_octave_unison_rules, (cp, cf)),
                (check_key_adherence, (cp,60)),
                (analyze_melody_characteristics, (cp,)),
            ]

            for func, args in checks:
                result = func(*args)
                if isinstance(result, tuple) and result[0]: # Check returned True and a message
                    all_feedback.append(result[1])
            if all_feedback:
                current_comments = "\n".join(all_feedback)
                attempts_remaining -= 1
                if attempts_remaining == 0:
                    print("Max attempts reached after checking. Returning last valid MIDI or fallback.")
                    return "Failed Output", midi_melodies # Return the last problematic one if all retries used
                system_prompt_base += ("\n\nIMPORTANT: Your previous response had rule violations. "
                                        "Please address the feedback.")
                continue # Go to next iteration of the while loop to resend with comments
            else:
                print("No issues found by checking.py or all issues resolved.")
                return "Successful Output",midi_melodies # Good MIDI found
        elif use_checking == False and midi_melodies:  # Add this condition to return midi_melodies when use_checking is False
            return "Raw Output",midi_melodies
      
        system_prompt_base += ("\n\nIMPORTANT: Your previous response was not in the correct format or had issues."
                               "You MUST return a dictionary with 'Counterpoint' and 'CantusFirmus' "
                               "keys containing MIDI note arrays, and adhere to counterpoint rules.")
        
        attempts_remaining -= 1
        if llm_response is not None:
            print(f"Current llm_response before next attempt or fallback: {llm_response}")
        else:
            print("llm_response was not assigned in this attempt.")
    
        if attempts_remaining > 0:
            print(f"LLM returned invalid format or issues found. Trying again (attempt {max_attempts - attempts_remaining + 1}/{max_attempts})...")
    
    
if __name__ == "__main__":
    testcounterpoint = {'Counterpoint': 
                        [60, 62, 65, 64, 65, 67, 69, 67, 64, 62, 60],
                        'CantusFirmus':
                         [60, 62, 65, 64, 65, 67, 69, 67, 64, 62, 60]}
    result= send_to_llm(conterpoint=testcounterpoint,use_checking=True)
    print("test result: ",result)
