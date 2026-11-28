"""The user documents describe SDEM 0.22's core as it is (BX-17, SDEM 0.22.1): the metamodel guide's figures are the metamodel's own —
counted here from it — and no document says that SDEM itself ships BIAN, its catalogue or the banking examples (they are sdem-bian's,
BX-15, R-D6). Fails on a stale figure or a stale sentence, so the next change to the core cannot leave the guides behind."""
import re, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
GUIDE = ROOT / 'docs' / 'sdem-metamodel-guide.md'
CORE_EXAMPLE = ROOT / 'examples' / '0.20' / 'library-holds'   # a core design: the metamodel in 0.20's form, BIAN off


def user_documents():
    """What people and agents read: the README, the documents at the top of docs/, the agents' instructions and skills — not the
    design specs, evidence or history, which record what was true when they were written."""
    yield ROOT / 'README.md'
    yield ROOT / 'LICENSES.md'
    yield ROOT / 'THIRD_PARTY.md'
    yield from sorted((ROOT / 'docs').glob('*.md'))
    yield ROOT / 'templates' / 'agents' / 'AGENTS.md'
    for d in ('.github', '.claude', '.agents'):
        yield from sorted((ROOT / d / 'skills').glob('*/SKILL.md'))


STALE = [   # sentences true before SDEM 0.22, not since
    (r'(?i)\bBIAN\b[^.|\n]{0,80}\bships with SDEM\b', 'BIAN ships with sdem-bian, not SDEM'),
    (r'(?i)\bships with SDEM\b[^.|\n]{0,60}\bBIAN\b', 'BIAN ships with sdem-bian, not SDEM'),
    (r'(?i)\bPayments? example (that )?ships with SDEM', 'the Payments example ships with sdem-bian'),
    (r'(?i)\binside (the installed )?SDEM\b[^.|\n]{0,40}\bBIAN|\bBIAN\b[^.|\n]{0,60}\bare inside SDEM', 'BIAN is not inside SDEM'),
    (r'`bian/(base-|LICENSE)', "SDEM has no bian/ folder (the catalogue is sdem-bian's) — an organisation's own bian/ folder holds its pack, not these"),
    (r'(?i)\bonly through (the )?BIAN\b', 'in the core, business connects to applications directly'),
]


class NoStaleSentences(unittest.TestCase):
    def test_no_user_document_says_sdem_ships_bian(self):
        found = []
        for f in user_documents():
            for n, line in enumerate(f.read_text(encoding='utf-8').splitlines(), 1):
                found += [f'{f.relative_to(ROOT)}:{n}: {why}' for rx, why in STALE if re.search(rx, line)]
        self.assertEqual(found, [])


class GuideFiguresAreTheMetamodels(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from sdem import profile
        from sdem.model_health import integrity
        from sdem.validate import load_registry
        from sdem.rules_engine import _rules
        with profile.kept():
            cls.core = integrity(CORE_EXAMPLE)['core']
            profile.activate_from(CORE_EXAMPLE)
            cls.between = len(load_registry()['relationships'])
            cls.rules = len(_rules())
        cls.text = GUIDE.read_text(encoding='utf-8')

    def figure(self, label):
        m = re.search(label + r'</b><br/>(\d+)', self.text)
        self.assertIsNotNone(m, f'the guide has no "{label}" figure'); return int(m.group(1))

    def test_the_diagram(self):
        kinds = sum(l['types'] for l in self.core['layers'])
        self.assertEqual(self.figure('Kinds of thing'), kinds)
        self.assertEqual(self.figure('Links inside a layer'), self.core['frozen']['within_layer_rules'])
        self.assertEqual(self.figure('Connections between layers'), self.between)
        self.assertEqual(self.figure('Rules for finding connections'), self.rules)

    def test_the_layers(self):
        for l in self.core['layers']:   # e.g. | **A2 · Data** (3) |
            name = l['name'].split(' ', 1)[1]
            m = re.search(rf'\*\*{l["code"]} · {name}\*\* \((\d+)\)', self.text)
            self.assertIsNotNone(m, f'the guide has no row for {l["name"]}'); self.assertEqual(int(m.group(1)), l['types'], l['name'])

    def test_the_connections_count(self):
        self.assertIn(f'Only these {self.between} are allowed', self.text)


if __name__ == '__main__':
    unittest.main()
