"""
Test the SCA module.
"""
from __future__ import unicode_literals
from itertools import product

from six import text_type
from mock import patch, Mock

from lingpy import Alignments, MSA, PSA
import lingpy as lp
from lingpy.tests.util import test_data, WithTempDir
from lingpy.util import write_text_file, read_config_file
from lingpy.thirdparty.cogent.tree import TreeNode


class TestPSA(WithTempDir):
    def test_output(self):
        fpsa = self.tmp_path('test.psa')
        write_text_file(fpsa, 'HEADER\nline\n')
        psa = PSA(text_type(fpsa))
        fname = text_type(self.tmp_path('test'))
        psa.output(fileformat='psa', filename=fname)

        psq = self.tmp_path('test.psq')
        write_text_file(psq, '\n')
        PSA(text_type(psq))

        psa = PSA(test_data('harry_potter.psa'))
        fname = text_type(self.tmp_path('test'))
        psa.output(fileformat='psq', filename=fname)
        psa.align()
        psa.output(fileformat='psa', filename=fname)


class TestMSA(WithTempDir):
    def test_output(self):
        msa = MSA(test_data('harry.msa'))
        msa.ipa2cls()
        # well. it is a list, but the code apparently wants a dict ...
        msa.merge = {'a': 'x', 'b': 'x'}
        fname = text_type(self.tmp_path('test'))
        for fmt in 'msa psa msq html tex'.split():
            for s, u in product([True, False], [True, False]):
                msa.output(
                    timestamp=True,
                    fileformat=fmt,
                    filename=fname,
                    sorted_seqs=s,
                    unique_seqs=u)


class TestAlignments(WithTempDir):
    def setUp(self):
        WithTempDir.setUp(self)
        self.alm = Alignments(test_data('KSL2.qlc'), loans=False, _interactive=False)

    def test_init(self):
        log = Mock(deprecated=Mock())
        with patch('lingpy.align.sca.log', log):
            Alignments(test_data('KSL2.qlc'), cognates='cogid')
        assert log.deprecated.called

    def test_ipa2tokens(self):
        # iterate over the keys
        for key in self.alm:  # .get_list(language="Turkish",flat=True):
            ipa = self.alm[key, 'ipa']
            tokensA = self.alm[key, 'tokensa'].split(' ')
            tokensB = self.alm[key, 'tokensb'].split(' ')

            new_tokensA = lp.ipa2tokens(ipa, merge_vowels=True, merge_geminates=False)
            new_tokensB = lp.ipa2tokens(ipa, merge_vowels=False, merge_geminates=False)
            assert tokensA == new_tokensA
            assert tokensB == new_tokensB

    def test_align(self):
        # align all sequences using standard params
        self.alm.align()

        # iterate and align using the multiple function
        for key, value in self.alm.msa['cogid'].items():
            # first compare simple alignments
            msaA = lp.SCA(value)
            msaB = lp.Multiple(value['seqs'])
            msaB.prog_align()
            assert msaA == msaB

            # now compare with different flag
            msaA = lp.Multiple([self.alm[idx, 'tokensb'] for idx in value['ID']])
            msaB = lp.Multiple([''.join(s) for s in value['seqs']], merge_vowels=False)
            msaA.lib_align()
            msaB.lib_align()
            assert msaA == msaB

    def test_get_consensus(self):
        # align all sequences using standard params
        self.alm.align()

        tree = TreeNode(
            Name='root',
            Children=[TreeNode(Name=line.split('\t')[1]) for line in
                      read_config_file(test_data('KSL2.qlc'))])

        self.alm.get_consensus(consensus="consensus", tree=tree)
        self.alm.get_consensus(consensus="consensus", classes=True)
        self.alm.get_consensus(consensus="consensus")

        # check whether Turkish strings are identical
        self.assertEquals(
            self.alm.get_list(language="Turkish", entry="consensus", flat=True),
            [''.join(x) for x in self.alm.get_list(
                language="Turkish", entry="tokens", flat=True)])

    def test_get_consensus2(self):
        from lingpy.align.sca import get_consensus

        def get_msa():
            msa = MSA(test_data('harry.msa'))
            msa.prog_align()
            return msa

        get_consensus(get_msa())
        get_consensus(get_msa(), local='peaks')
        get_consensus(get_msa(), local='gaps')
        get_consensus(get_msa(), classes=True, mode='maximize')

    def test_output(self):
        self.alm.align()
        self.alm.output('qlc', filename=text_type(self.tmp_path('test')))
        self.alm.output('psa', filename=text_type(self.tmp_path('test')))
        self.alm.output('html', filename=text_type(self.tmp_path('test')))
