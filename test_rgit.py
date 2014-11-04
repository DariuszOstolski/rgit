#!/usr/bin/env python
import unittest
import rgit


class TestStatusParser(unittest.TestCase):
    deleted = """## master...origin/master
D  COPYING.llvm
 D COPYING.unrar
"""
    renamed = """## master...origin/master
R  COPYING.unrar -> COPYING.unra"""

    untracked = """## master...origin/master
?? COPYING.unra"""

    new_file = """## master...origin/master
A  blabla.file
AM blabla1.file"""

    modified = """## master...origin/master
M  COPYING
 M COPYING.lzma
"""
    branch = """## master...origin/master [ahead 1, behind 2]"""
    branch_detached = """## HEAD (no branch)"""
    branch_simple = """## dev"""

    def setUp(self):
        pass

    def test_parse_deleted(self):
        parser = rgit.StatusParser()
        result = parser.parse(TestStatusParser.deleted)
        self.assertEquals(1, len(result.deleted))
        self.assertEquals(1, len(result.deleted_work_tree))
        self.assertEquals("COPYIMG.llvm", result.deleted[0])
        self.assertEquals("COPYIMG.unrar", result.deleted_work_tree[0])

    def test_parse_renamed(self):
        parser = rgit.StatusParser()
        result = parser.parse(TestStatusParser.renamed)
        self.assertEquals(1, len(result.renamed))
        self.assertEquals("COPYING.unrar", result.renamed[0].path_from)
        self.assertEquals("COPYING.unra", result.renamed[0].path_to)

    def test_parse_untracked(self):
        parser = rgit.StatusParser()
        result = parser.parse(TestStatusParser.untracked)
        self.assertEquals(1, len(result.untracked))
        self.assertEquals("COPYING.unra", result.untracked[0])

    def test_parse_new_file(self):
        parser = rgit.StatusParser()
        result = parser.parse(TestStatusParser.new_file)
        self.assertEquals(2, len(result.new_files))
        self.assertEquals(1, len(result.modified))
        self.assertEquals("blabla.file", result.new_files[0])
        self.assertEquals("blabla1.file", result.new_files[0])
        self.assertEquals("blabla1.file", result.modified[0])

    def test_parse_modified(self):
        parser = rgit.StatusParser()
        result = parser.parse(TestStatusParser.modified)
        self.assertEquals(1, len(result.modified))
        self.assertEquals(1, len(result.modified_work_tree))
        self.assertEquals("COPYING", result.modified[0])
        self.assertEquals("COPYING.lzma", result.modified_work_tree[0])

    def test_parse_branch(self):
        parser = rgit.StatusParser()

        result = parser.parse(TestStatusParser.branch)
        self.assertEquals("master", result.branch)
        self.assertEquals("origin/master", result.branch_remote)
        self.assertEquals(1, result.ahead)
        self.assertEquals(2, result.behind)

        result = parser.parse(TestStatusParser.branch_detached)
        self.assertEquals("detached", result.branch)
        self.assertEquals(None, result.branch_remote)
        self.assertEquals(0, result.ahead)
        self.assertEquals(0, result.behind)

        result = parser.parse(TestStatusParser.branch_simple)
        self.assertEquals("dev", result.branch)
        self.assertEquals(None, result.branch_remote)
        self.assertEquals(0, result.ahead)
        self.assertEquals(0, result.behind)

if __name__ == '__main__':
    unittest.main()