# test_pairs.py (temporary — delete after)
from app.services.pair_generator import generate_pairs, get_pair_count

# Simulated normalized drug data
drugs = [
    {"input_name": "Warfarin",     "normalized_name": "Warfarin",
     "rxcui": "11289"},
    {"input_name": "Aspirin",      "normalized_name": "Aspirin",
     "rxcui": "1191"},
    {"input_name": "Metformin",    "normalized_name": "Metformin",
     "rxcui": "6809"},
    {"input_name": "Lisinopril",   "normalized_name": "Lisinopril",
     "rxcui": "29046"},
]

pairs = generate_pairs(drugs)

print(f"Drugs: {len(drugs)}")
print(f"Expected pairs: {get_pair_count(len(drugs))}")
print(f"Generated pairs: {len(pairs)}\n")

for i, (a, b) in enumerate(pairs, 1):
    print(f"Pair {i}: {a['normalized_name']} + {b['normalized_name']}")