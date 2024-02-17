import os
import sys
urgencyTrustSpelling_path = os.path.join(os.path.dirname(__file__), '../..', 'UrgencyTrustSpelling')
sys.path.append(urgencyTrustSpelling_path)
from urgencyTrustSpelling import cues_testing

def main():
    phishing_count = 0
    legitimate_count = 0
    test_count = 0
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_file_path = os.path.join(current_dir, 'evaluationCuesTuning.txt')
    output_file_path = os.path.join(current_dir, 'resultsCuesTuning.txt')
    # Empty the file
    with open(output_file_path, 'w') as outfile:
        outfile.write("")
    # Read the messages file
    with open(input_file_path, 'r') as file:
        messages = file.readlines()
    for message in messages:
        # Remove the whitespace
        message = message.strip()
        result = cues_testing(message, 320)
        test_count += 1
        if result == 'P' and test_count < 26:
            phishing_count += 1
        elif result == 'L' and test_count > 25:
            legitimate_count += 1
        with open(output_file_path, 'a') as outfile:
            outfile.write(f"{result}\n")
    with open(output_file_path, 'a') as outfile:
        outfile.write(f"\nPhishing accuracy: {phishing_count / 25 * 100}%\n")
        outfile.write(f"Legitimate accuracy: {legitimate_count / 25 * 100}%\n")
        outfile.write(f"Overall accuracy: {(legitimate_count + phishing_count) / 25 * 100 / 2}%")

if __name__ == "__main__":
    main()