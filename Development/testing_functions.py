from logic import AbbreviationCollection

def testing_manual_inputs():
    # Sample abbreviations for testing
    abb1_en = AbbreviationCollection.an_abbreviation("english", long="Telephone", short="Phone", compact="Tel")
    abb2_en = AbbreviationCollection.an_abbreviation("english", long="Computer", short="Comp", compact="C")
    abb3_en = AbbreviationCollection.an_abbreviation("english", long="Television", short="TV", compact="T")
    abb4_en = AbbreviationCollection.an_abbreviation("english", long="Telecom", short="Telco", compact=None)
    abb5_en = AbbreviationCollection.an_abbreviation("english", long="Smartphone", short="Phone", compact="Smart")
    abb6_en = AbbreviationCollection.an_abbreviation("english", long="Refrigerator", short="Fridge", compact="Fr")
    abb7_en = AbbreviationCollection.an_abbreviation("english", long="Microwave Oven", short="Microwave", compact="M.O.")
    abb8_en = AbbreviationCollection.an_abbreviation("english", long="Washing Machine", short="Washer", compact="W.M.")
    abb9_en = AbbreviationCollection.an_abbreviation("english", long="Air Conditioner", short="A.C.", compact="AC")
    abb10_en = AbbreviationCollection.an_abbreviation("english", long="Laptop Computer", short="Laptop", compact="L.C.")

    abb1_da = AbbreviationCollection.an_abbreviation("danish", long="Telefon", short="Tlf", compact="Tel")
    abb2_da = AbbreviationCollection.an_abbreviation("danish", long="Computer", short="Comp", compact="C")
    abb3_da = AbbreviationCollection.an_abbreviation("danish", long="Fernseher", short="TV", compact="T")
    abb4_da = AbbreviationCollection.an_abbreviation("danish", long="Telekommunikation", short="Telco", compact=None)
    abb5_da = AbbreviationCollection.an_abbreviation("danish", long="Smartphone", short="Mobil", compact="Smart")
    abb6_da = AbbreviationCollection.an_abbreviation("danish", long="Køleskab", short="Fridge", compact="Fr")
    abb7_da = AbbreviationCollection.an_abbreviation("danish", long="Mikrobølgeovn", short="Mikro", compact="M.O.")
    abb8_da = AbbreviationCollection.an_abbreviation("danish", long="Vaskemaskine", short="Vasker", compact="V.M.")
    abb9_da = AbbreviationCollection.an_abbreviation("danish", long="Luftkonditionering", short="A.C.", compact="AC")
    abb10_da = AbbreviationCollection.an_abbreviation("danish", long="Bærbar Computer", short="Bærbar", compact="B.C.")

    # Create abbreviation instances with priorities for testing
    abbrev1_en = AbbreviationCollection.abbreviation(abb1_en, abb2_en, abb3_en, abb4_en, priority=1)
    abbrev2_en = AbbreviationCollection.abbreviation(abb5_en, abb6_en, abb7_en, abb8_en, priority=2)
    abbrev3_en = AbbreviationCollection.abbreviation(abb9_en, abb10_en, priority=3)

    abbrev1_da = AbbreviationCollection.abbreviation(abb1_da, abb2_da, abb3_da, abb4_da, priority=1)
    abbrev2_da = AbbreviationCollection.abbreviation(abb5_da, abb6_da, abb7_da, abb8_da, priority=2)
    abbrev3_da = AbbreviationCollection.abbreviation(abb9_da, abb10_da, priority=3)

    # Create the abbreviation collection and add instances
    abbr_collection = AbbreviationCollection()
    abbr_collection.add_abbreviation(abbrev1_en)
    abbr_collection.add_abbreviation(abbrev2_en)
    abbr_collection.add_abbreviation(abbrev3_en)

    abbr_collection.add_abbreviation(abbrev1_da)
    abbr_collection.add_abbreviation(abbrev2_da)
    abbr_collection.add_abbreviation(abbrev3_da)