from __future__ import unicode_literals

from .util import WithTempDir
from .. import util


class Test(WithTempDir):
    def test_write_text_file(self):
        def lines_generator(n):
            for i in range(n):
                yield 'line%s' % i

        util.write_text_file('test', 'test')
        self.assertEqual(util.read_text_file('test'), 'test')

        util.write_text_file('test', ['line1', 'line2'])
        self.assertEqual(len(util.read_text_file('test', lines=True)), 2)

        util.write_text_file('test', lines_generator(5))
        self.assertEqual(len(util.read_text_file('test', lines=True)), 5)

    def test_TextFile(self):
        with util.TextFile('test') as fp:
            fp.writelines(['line1\n', 'line2\n'])
            fp.writeline(('a', 'b'))
            fp.writeline(['a', 'b'])
            fp.writeline('a', *['b', 'c'])
            fp.writeline('a', 'b', sep='---')
            fp.writeline('a')
        res = util.read_text_file('test', lines=True)
        self.assertEquals(len(res), 7)
        self.assertEquals(len([l for l in res if '---' in l]), 1)
        self.assertEquals(len([l for l in res if '\t' in l]), 3)
