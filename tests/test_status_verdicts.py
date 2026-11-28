"""CPL-21: sdem status gives each of SDEM's verdicts apart — integrity, conformance, completeness, maturity, security, approval — one
question each, none implying another; approval rests on the others. On SDEM's own core example (no sdem-bian needed), and on the
complete Payment design (sdem-bian's)."""
import io, contextlib, json, shutil, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / 'tests'))
from needs import bian as _needs_bian, EXAMPLES  # noqa: E402

IDS = ['integrity', 'conformance', 'completeness', 'maturity', 'security', 'approval']


def status(ws):
    from sdem import cli
    out = io.StringIO()
    with contextlib.redirect_stdout(out): cli.main(['status', '--workspace', str(ws), '--json'])
    return json.loads(out.getvalue())


class Verdicts(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, self.tmp, True)

    def test_each_verdict_apart_and_approval_rests_on_the_checks(self):
        ws = self.tmp / 'library'; shutil.copytree(ROOT / 'examples' / '0.20' / 'library-holds', ws)
        s = status(ws); v = {x['id']: x for x in s['verdicts']}
        self.assertEqual([x['id'] for x in s['verdicts']], IDS)
        for x in s['verdicts']: self.assertTrue(x['question'].endswith('?') and x['says'], x)
        self.assertIs(v['conformance']['ok'], True)   # it passes the metamodel …
        self.assertIs(v['integrity']['ok'], False)    # … yet not every record reaches every layer (MID-05): a different question
        self.assertIsNone(v['security']['ok'])        # no security architecture: not asked, not failed
        self.assertIs(v['approval']['ok'], False); self.assertIn('integrity', v['approval']['says'])   # so not ready to approve

    def test_the_report_shows_them(self):
        from sdem.status import render
        ws = self.tmp / 'library'; shutil.copytree(ROOT / 'examples' / '0.20' / 'library-holds', ws)
        text = render(status(ws))
        self.assertIn('Verdicts — each answers its own question', text)
        for name in ('Integrity', 'Conformance', 'Completeness', 'Maturity', 'Security', 'Approval'): self.assertIn(name, text)


@_needs_bian
class PaymentVerdicts(unittest.TestCase):   # complete and well-formed, yet not ready: the review's own case
    def test_complete_is_not_ready(self):
        tmp = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, tmp, True)
        ws = tmp / 'pay'; shutil.copytree(EXAMPLES / '0.20' / 'payment-initiation-v4' / 'sdem', ws, ignore=shutil.ignore_patterns('graph'))
        v = {x['id']: x for x in status(ws)['verdicts']}
        self.assertIs(v['conformance']['ok'], True)
        self.assertIs(v['approval']['ok'], v['maturity']['ok'] is True and v['security']['ok'] is not False and v['integrity']['ok'] is True and v['completeness']['ok'] is not False
                      and not status(ws)['blocking'] and not status(ws)['unresolved'])


if __name__ == '__main__':
    unittest.main()
