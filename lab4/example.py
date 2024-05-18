import requests
from spacy.lang.en import English
from spacy.language import Language
from spacy.matcher import PhraseMatcher
from spacy.tokens import Doc, Span, Token

@Language.factory("rest_countries")
class RESTCountriesComponent:
    def __init__(self, nlp, name, label="GPE"):
        r = requests.get("https://restcountries.com/v2/all")
        r.raise_for_status()  # make sure requests raises an error if it fails
        countries = r.json()
        # Convert API response to dict keyed by country name for easy lookup
        self.countries = {c["name"]: c for c in countries}
        self.label = label
        # Set up the PhraseMatcher with Doc patterns for each country name
        self.matcher = PhraseMatcher(nlp.vocab)
        self.matcher.add("COUNTRIES", [nlp.make_doc(c) for c in self.countries.keys()])
        # Register attributes on the Span. We'll be overwriting this based on
        # the matches, so we're only setting a default value, not a getter.
        Span.set_extension("is_country", default=None)
        Span.set_extension("country_capital", default=None)
        Span.set_extension("country_latlng", default=None)
        Span.set_extension("country_flag", default=None)
        # Register attribute on Doc via a getter that checks if the Doc
        # contains a country entity
        Doc.set_extension("has_country", getter=self.has_country)

    def __call__(self, doc):
        spans = []  # keep the spans for later so we can merge them afterwards
        for _, start, end in self.matcher(doc):
            # Generate Span representing the entity & set label
            entity = Span(doc, start, end, label=self.label)
            # Set custom attributes on entity. Can be extended with other data
            # returned by the API, like currencies, country code, calling code etc.
            entity._.set("is_country", True)
            entity._.set("country_capital", self.countries[entity.text]["capital"])
            entity._.set("country_latlng", self.countries[entity.text]["latlng"])
            entity._.set("country_flag", self.countries[entity.text]["flag"])
            spans.append(entity)
        # Overwrite doc.ents and add entity – be careful not to replace!
        doc.ents = list(doc.ents) + spans
        return doc  # don't forget to return the Doc!

    def has_country(self, doc):
        """Getter for Doc attributes. Since the getter is only called
        when we access the attribute, we can refer to the Span's 'is_country'
        attribute here, which is already set in the processing step."""
        return any([entity._.get("is_country") for entity in doc.ents])

nlp = English()
nlp.add_pipe("rest_countries", config={"label": "GPE"})
doc = nlp("Some text about Colombia and the Czech Republic")
print("Pipeline", nlp.pipe_names)  # pipeline contains component name
print("Doc has countries", doc._.has_country)  # Doc contains countries
for ent in doc.ents:
    if ent._.is_country:
        print(ent.text, ent.label_, ent._.country_capital, ent._.country_latlng, ent._.country_flag)