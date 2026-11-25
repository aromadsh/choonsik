"""Mini Git regression tests. Run: python -m unittest -v test_main.py"""
import contextlib
import io
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from main import Commit, MiniGit, diff_lines, merge_sort, insertion_sort, parse_command, execute_command


class MiniGitTests(unittest.TestCase):
    def setUp(self):
        self.git = MiniGit()
        self.output = io.StringIO()

    def run_cmd(self, text):
        cmd, args = parse_command(text)
        with contextlib.redirect_stdout(self.output):
            if cmd:
                execute_command(self.git, cmd, args)
        return self.output.getvalue()

    def test_init_commit_index(self):
        self.run_cmd('init "Alice Smith"')
        self.run_cmd('commit "Initial commit"')
        a = self.git.branches['main']
        self.run_cmd('COMMIT "Add Login feature"')
        b = self.git.branches['main']
        self.assertNotEqual(a, b)
        self.assertEqual(self.git.commits[a].parents, ())
        self.assertEqual(self.git.commits[b].parents, (a,))
        self.assertIn(b, self.git.keyword_index['login'])
        self.assertIn(b, self.git.author_index['alice smith'])

    def test_branch_merge_topology(self):
        self.run_cmd('init Alice')
        self.run_cmd('commit root')
        root = self.git.branches['main']
        self.run_cmd('branch feature')
        self.run_cmd('switch feature')
        self.run_cmd('commit side')
        side = self.git.branches['feature']
        self.run_cmd('switch main')
        self.run_cmd('commit mainwork')
        main = self.git.branches['main']
        self.run_cmd('merge feature')
        merged = self.git.branches['main']
        self.assertEqual(self.git.commits[merged].parents, (main, side))
        order = [c.hash for c in self.git.topo()]
        for parent, child in ((root, side), (root, main), (main, merged), (side, merged)):
            self.assertLess(order.index(parent), order.index(child))
        self.run_cmd(f'ancestors {merged}')
        self.assertIn(f'Ancestors of {merged}: 3', self.output.getvalue())
        self.run_cmd(f'path {side} {main}')
        self.assertIn('Path:', self.output.getvalue())

    def test_search_and_reset(self):
        self.run_cmd('init Alice')
        self.run_cmd('commit "Add login feature"')
        self.run_cmd('commit "Add payment feature"')
        self.assertIn('Found 1 commit(s):', self.run_cmd('search login'))
        self.assertIn('Found 2 commit(s):', self.run_cmd('search "add feature"'))
        self.assertIn('Found 2 commit(s):', self.run_cmd('search --author=Alice'))
        self.run_cmd('init Bob')
        self.assertEqual(self.git.commits, {})
        self.assertEqual(self.git.keyword_index, {})

    def test_bad_inputs(self):
        self.assertIn('Invalid args', self.run_cmd('branch'))
        self.assertIn('Invalid args', self.run_cmd('log --sort-by=bad'))
        self.assertIn('Unknown command: XXX', self.run_cmd('xxx'))
        self.run_cmd('init Alice')
        self.assertIn('Unknown branch: nope', self.run_cmd('switch nope'))
        self.assertIn('Unknown commit: nope', self.run_cmd('path nope nope'))

    def test_path_lexicographic_tie(self):
        self.run_cmd('init Alice')
        stamp = datetime.now()
        self.git.commits = {
            'a': Commit('a', 'root', 'Alice', stamp, ()),
            'b': Commit('b', 'left', 'Alice', stamp, ('a',)),
            'c': Commit('c', 'right', 'Alice', stamp, ('a',)),
            'd': Commit('d', 'join', 'Alice', stamp, ('b', 'c')),
        }
        self.git.children = {'a': {'b', 'c'}, 'b': {'d'}, 'c': {'d'}, 'd': set()}
        self.assertIn('Path: a -> b -> d', self.run_cmd('path a d'))

    def test_sort_stability(self):
        data = [(2, 'a'), (1, 'b'), (2, 'c')]
        expected = [(1, 'b'), (2, 'a'), (2, 'c')]
        self.assertEqual(merge_sort(data, lambda x: x[0]), expected)
        self.assertEqual(insertion_sort(data, lambda x: x[0]), expected)

    def test_diff(self):
        with tempfile.TemporaryDirectory() as d:
            a, b = Path(d) / 'a.txt', Path(d) / 'b.txt'
            a.write_text('common\nold\n', encoding='utf-8')
            b.write_text('common\nnew\n', encoding='utf-8')
            self.assertEqual(diff_lines(a, b), ['  common', '- old', '+ new'])

    def test_parser_quotes(self):
        self.assertEqual(parse_command('CoMmIt "Add login feature"'), ('COMMIT', ['Add login feature']))

    def test_no_path_for_disjoint_roots(self):
        self.run_cmd('init Alice')
        self.run_cmd('commit root')
        a = self.git.branches['main']
        self.run_cmd('branch empty')
        self.git.branches['empty'] = None
        self.run_cmd('switch empty')
        self.run_cmd('commit anotherroot')
        b = self.git.branches['empty']
        self.assertIn('No path', self.run_cmd(f'path {a} {b}'))


if __name__ == '__main__':
    unittest.main()
