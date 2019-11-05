from itertools import groupby
from pathlib import Path

import attr
import lingpy
from clldutils.misc import slug
from pylexibank import Concept
from pylexibank.providers import qlc
from pylexibank.util import progressbar


@attr.s
class HConcept(Concept):
    Spanish = attr.ib(default=None)
    Gloss_in_digital_source = attr.ib(default=None)


class Dataset(qlc.QLC):
    dir = Path(__file__).parent
    id = "hubercolumbian"
    DSETS = ["huber1992.csv"]
    concept_class = HConcept

    def cmd_makecldf(self, args):
        # column "counterpart_doculect" gives us the proper names of the doculects
        wl = lingpy.Wordlist((self.raw_dir / self.DSETS[0]).as_posix(), col="counterpart_doculect")
        args.writer.add_sources()

        # get the language identifiers stored in wl._meta['doculect'] parsed from input file
        lids = {}
        for line in wl._meta["doculect"]:
            rest = line.split(", ")
            name = rest.pop(0)
            lids[name] = rest.pop(0)

        concept_lookup = {}

        for concept in self.conceptlists[0].concepts.values():
            concept_id = "%s_%s" % (concept.number, slug(concept.english))

            args.writer.add_concept(
                ID=concept_id,
                Name=concept.english,
                Concepticon_ID=concept.concepticon_id,
                Concepticon_Gloss=concept.concepticon_gloss,
                Gloss_in_digital_source=concept.attributes["gloss_in_digital_source"],
                Spanish=concept.attributes["spanish"],
            )

            concept_lookup[concept.attributes["gloss_in_digital_source"]] = concept_id

        def grouped_rows(wl):
            rows = [
                (
                    wl[k, "counterpart_doculect"],
                    wl[k, "concept"],
                    wl[k, "counterpart"],
                    wl[k, "qlcid"],
                )
                for k in wl
                if wl[k, "counterpart_doculect"] not in ["English", "Español"]
            ]
            return groupby(sorted(rows), key=lambda r: (r[0], r[1]))

        for (language, concept), rows in progressbar(grouped_rows(wl)):
            iso = lids[language]

            args.writer.add_language(
                ID=slug(language, lowercase=False),
                Name=language,
                ISO639P3code=iso,
                Glottocode=self.glottolog.glottocode_by_iso.get(iso, ""),
            )

            for i, (l, c, form, id_) in enumerate(rows):
                args.writer.add_form(
                    Language_ID=slug(language, lowercase=False),
                    Parameter_ID=concept_lookup[concept],
                    Value=form,
                    Form=form,
                    Source=["Huber1992"],
                    Local_ID=id_,
                )
