from hypothesis import given, strategies as st
from hypothesis import settings, Verbosity, Phase

default_fuzz_settings = settings(
    max_examples=100,
    verbosity=Verbosity.normal,
    phases=[Phase.generate, Phase.shrink],
    deadline=None,
)


class Strategies:
    integers = st.integers
    floats = st.floats
    text = st.text
    booleans = st.booleans
    uuids = st.uuids
    lists = st.lists
    dictionaries = st.dictionaries
    sampled_from = st.sampled_from

    @staticmethod
    def alphanumeric(min_size: int = 1, max_size: int = 30):
        """Generate alphanumeric string (A-Z, a-z, 0-9) safe for URL paths"""
        return st.text(
            alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd")),
            min_size=min_size,
            max_size=max_size,
        )

    @staticmethod
    def safe_text(min_size: int = 1, max_size: int = 50):
        """สร้างสตริงทั่วไปโดยตัด Control Characters ทิ้ง"""
        return st.text(
            alphabet=st.characters(blacklist_categories=("Cs", "Cc")),
            min_size=min_size,
            max_size=max_size,
        )


strategy = Strategies