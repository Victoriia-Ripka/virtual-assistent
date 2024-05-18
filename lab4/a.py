import spacy
from spacy.matcher import Matcher

# Example text
text = "I'm interested in the Mazda CX-30, the Volvo S90, and the Ford Mustang."

# Load English model
nlp = spacy.load("en_core_web_sm")

# Define car model patterns
car_model_patterns = [
    {"LOWER": {"REGEX": "(mazda|volvo|ford)"}},  # Brands
    {"IS_DIGIT": True},  # Numbers
    {"LOWER": {"IN": ["cx", "s"]}},  # Model types
    {"LOWER": {"IN": ["-", " ", ""]}},  # Separators
    {"LOWER": {"IN": ["x", ""]}},  # Model type suffixes
]

# Initialize Matcher with car model patterns
matcher = Matcher(nlp.vocab)
matcher.add("CAR_MODEL", [car_model_patterns])

# Process the text
doc = nlp(text)

# Print out tokens
print("Tokens:")
for token in doc:
    print(token.text, token.pos_, token.tag_)

# Extract car models using the Matcher
car_models = []
for match_id, start, end in matcher(doc):
    car_model = doc[start:end].text.replace(" ", "").replace("-", "").replace("x", "X")
    car_models.append(car_model)

# Output car models
print("\nCar models found:", car_models)
