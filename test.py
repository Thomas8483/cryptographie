import re

subject = "/C=FR/ST=PACA/L=TOULON/O=ISEN/OU=M1/CN=thomas2.com"
values = ["FR", "PACA", "TOULON", "ISEN", "M1", "thomas2.com"]

# Use regular expressions to extract the values from the subject string
matches = re.findall(r'/(\w+)=([\w.]+)', subject)

# Create a dictionary from the matches
dict_matches = dict(matches)

# Check if the values are in the dictionary
if all(value in dict_matches.values() for value in values):
    print("All values match")
else:
    print("Not all values match")
