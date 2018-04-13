# coding=utf-8
from __future__ import unicode_literals, print_function
from itertools import groupby

import attr
import lingpy
from pycldf.sources import Source
from clldutils.path import Path

from pylexibank.dataset import Metadata, Concept
from pylexibank.providers import qlc


@attr.s
class HConcept(Concept):
    Spanish_gloss = attr.ib(default=None)


class Dataset(qlc.QLC):
    dir = Path(__file__).parent
    DSETS = ['huber1992.csv']
    concept_class = HConcept

    def cmd_install(self, **kw):
        # column "counterpart_doculect" gives us the proper names of the doculects
        wl = lingpy.Wordlist(self.raw.posix(self.DSETS[0]), col="counterpart_doculect")

        # get the language identifiers stored in wl._meta['doculect'] parsed from input
        # file
        lids = {}
        for line in wl._meta['doculect']:
            rest = line.split(', ')
            name = rest.pop(0)
            lids[name] = rest.pop(0)

        concepts = {
            c.attributes['spanish'] + '_' + c.english:
            (c.concepticon_id, c.english, c.attributes['spanish'])
            for c in self.conceptlist.concepts.values()}

        src = Source.from_bibtex("""
@book{Huber1992,
    author={Huber, Randall Q. and Reed, Robert B.},
    title={Comparative vocabulary. Selected words in indigenous languages of Columbia.},
    address={Santafé de Bogotá},
    publisher={Instituto lingüístico de Veterano}
}""")

        def grouped_rows(wl):
            rows = [
                (wl[k, 'counterpart_doculect'], wl[k, 'concept'], wl[k, 'counterpart'], wl[k, 'qlcid'])
                for k in wl if wl[k, 'counterpart_doculect'] not in ['English', 'Español']]
            return groupby(sorted(rows), key=lambda r: (r[0], r[1]))

        with self.cldf as ds:
            ds.add_sources(src)
            for (language, concept), rows in grouped_rows(wl):
                iso = lids[language]
                cid, ceng, cspa = concepts[concept.lower()]

                ds.add_language(
                    ID=language,
                    name=language,
                    iso=iso,
                    glottocode=self.glottolog.glottocode_by_iso.get(iso, ''))
                ds.add_concept(ID=concept, gloss=ceng, conceptset=cid, Spanish_gloss=cspa)

                for i, (l, c, form, id_) in enumerate(rows):
                    ds.add_lexemes(
                        Language_ID=language,
                        Parameter_ID=concept,
                        Value=form,
                        Source=[src.id],
                        Local_ID=id_)
