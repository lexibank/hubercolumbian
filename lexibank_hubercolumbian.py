from pathlib import Path

import attr
import lingpy
from clldutils.misc import slug
from pylexibank import Concept, Language
from pylexibank.providers import qlc
from pylexibank.util import progressbar


@attr.s
class CustomConcept(Concept):
    Spanish = attr.ib(default=None)
    Gloss_in_digital_source = attr.ib(default=None)


@attr.s
class CustomLanguage(Language):
    Longitude = attr.ib(default=None)
    Latitude = attr.ib(default=None)
    Name_in_Source = attr.ib(default=None)


class Dataset(qlc.QLC):
    dir = Path(__file__).parent
    id = "hubercolumbian"
    DSETS = ["huber1992.csv"]
    concept_class = CustomConcept
    language_class = CustomLanguage

    def cmd_makecldf(self, args):
        # column "counterpart_doculect" gives us the proper names of the doculects
        wl = lingpy.Wordlist((self.raw_dir / self.DSETS[0]).as_posix(), col="counterpart_doculect")
        args.writer.add_sources()

        # get the language identifiers stored in wl._meta['doculect'] parsed from input file
        language_lookup = args.writer.add_languages(lookup_factory="Name_in_Source")

        concept_lookup = args.writer.add_concepts(
            id_factory=lambda x: x.id.split("-")[-1] + "_" + slug(x.english),
            lookup_factory="LEXIBANK_GLOSS",
        )

        rows = [
            (doculect, concept, value, qlcid)
            for (idx, doculect, concept, value, qlcid) in wl.iter_rows(
                "counterpart_doculect", "concept", "counterpart", "qlcid"
            )
            if doculect not in ["English", "Español"]
        ]

        for doculect, concept, value, qlcid in progressbar(rows):
            args.writer.add_form(
                Language_ID=language_lookup[doculect],
                Parameter_ID=concept_lookup[concept],
                Value=value,
                Form=value,
                Source=["Huber1992"],
                Local_ID=qlcid,
            )
