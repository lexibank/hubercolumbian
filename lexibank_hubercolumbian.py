from itertools import groupby
from pathlib import Path

import attr
import lingpy
from clldutils.misc import slug
from pylexibank import Concept
from pylexibank.providers import qlc
from tqdm import tqdm


@attr.s
class HConcept(Concept):
    Spanish_Gloss = attr.ib(default=None)


class Dataset(qlc.QLC):
    dir = Path(__file__).parent
    id = "hubercolumbian"
    DSETS = ["huber1992.csv"]
    concept_class = HConcept

    def cmd_makecldf(self, args):
        # column "counterpart_doculect" gives us the proper names of the doculects
        wl = lingpy.Wordlist((self.raw_dir / self.DSETS[0]).as_posix(), col="counterpart_doculect")

        # get the language identifiers stored in wl._meta['doculect'] parsed from input
        # file
        lids = {}
        for line in wl._meta["doculect"]:
            rest = line.split(", ")
            name = rest.pop(0)
            lids[name] = rest.pop(0)

        concepts = {
            c.attributes["spanish"]
            + "_"
            + c.english: (c.concepticon_id, c.english, c.attributes["spanish"])
            for c in self.conceptlist.concepts.values()
        }

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

        args.writer.add_sources(*self.raw_dir.read_bib())

        for (language, concept), rows in tqdm(grouped_rows(wl), desc="cldfify", total=len(wl)):
            iso = lids[language]
            cid, ceng, cspa = concepts[concept.lower()]
            concept = slug(concept)

            args.writer.add_language(
                ID=slug(language),
                Name=language,
                ISO639P3code=iso,
                Glottocode=self.glottolog.glottocode_by_iso.get(iso, ""),
            )
            args.writer.add_concept(ID=concept, Name=ceng, Concepticon_ID=cid, Spanish_Gloss=cspa)

            for i, (l, c, form, id_) in enumerate(rows):
                args.writer.add_form(
                    Language_ID=slug(language),
                    Parameter_ID=concept,
                    Value=form,
                    Form=form,
                    Source=["Huber1992"],
                    Local_ID=id_,
                )
