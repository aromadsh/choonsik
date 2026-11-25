"""Educational in-memory Mini Git. Python 3.10+, standard library only."""
import shlex
import hashlib
import time
from collections import deque
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class Commit:
    """Immutable commit metadata and its parent hashes."""
    hash: str
    message: str
    author: str
    timestamp: datetime
    parents: tuple


def merge_sort(items, key=lambda x: x):
    """Stable merge sort; O(n log n) average/worst, O(n) extra space."""
    items = list(items)
    if len(items) < 2:
        return items
    mid = len(items) // 2
    left = merge_sort(items[:mid], key)
    right = merge_sort(items[mid:], key)
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    result.extend(left[i:]); result.extend(right[j:])
    return result


def insertion_sort(items, key=lambda x: x):
    """Stable insertion sort; O(n²) average/worst, O(n) best."""
    items = list(items)
    for i in range(1, len(items)):
        value = items[i]
        j = i - 1
        while j >= 0 and key(items[j]) > key(value):
            items[j + 1] = items[j]
            j -= 1
        items[j + 1] = value
    return items


def diff_lines(before, after):
    """LCS line comparison: '  ' shared, '- ' deleted, '+ ' inserted."""
    a = Path(before).read_text(encoding='utf-8').splitlines()
    b = Path(after).read_text(encoding='utf-8').splitlines()
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n - 1, -1, -1):
        for j in range(m - 1, -1, -1):
            dp[i][j] = 1 + dp[i + 1][j + 1] if a[i] == b[j] else max(dp[i + 1][j], dp[i][j + 1])
    i = j = 0
    result = []
    while i < n and j < m:
        if a[i] == b[j]:
            result.append('  ' + a[i]); i += 1; j += 1
        elif dp[i + 1][j] >= dp[i][j + 1]:
            result.append('- ' + a[i]); i += 1
        else:
            result.append('+ ' + b[j]); j += 1
    while i < n:
        result.append('- ' + a[i]); i += 1
    while j < m:
        result.append('+ ' + b[j]); j += 1
    return result


class MiniGit:
    """Commit DAG, branch pointers, reverse edges and inverted indexes."""
    def __init__(self):
        self.initialized = False
        self.user = None
        self.commits = {}
        self.branches = {}
        self.current_branch = None
        self.keyword_index = {}
        self.author_index = {}
        self.children = {}
        self.counter = 0

    def init(self, user):
        """Start a fresh session repository with an empty main branch."""
        self.initialized = True
        self.user = user
        self.commits = {}
        self.branches = {'main': None}
        self.current_branch = 'main'
        self.keyword_index = {}
        self.author_index = {}
        self.children = {}
        self.counter = 0
        print('Initialized repository.')
        print('Current branch: main')
        print(f'Current user: {user}')

    def ready(self):
        if not self.initialized:
            print('Repository not initialized.')
            return False
        return True

    def add_commit(self, message, parents):
        """Make unique session hash; update DAG, branch and posting lists."""
        while True:
            self.counter += 1
            h = hashlib.sha256(f'mini-git:{self.counter}'.encode()).hexdigest()[:12]
            if h not in self.commits:
                break
        c = Commit(h, message, self.user, datetime.now(), tuple(parents))
        self.commits[h] = c
        self.children[h] = set()
        for parent in parents:
            self.children[parent].add(h)
        for word in set(token.lower() for token in message.split()):
            self.keyword_index.setdefault(word, set()).add(h)
        self.author_index.setdefault(self.user.lower(), set()).add(h)
        self.branches[self.current_branch] = h
        return c

    def commit(self, message):
        if not self.ready(): return
        head = self.branches[self.current_branch]
        c = self.add_commit(message, () if head is None else (head,))
        print(f'[{self.current_branch} {c.hash}] {message}')

    def branch(self, name):
        if not self.ready(): return
        if name in self.branches:
            print(f'Branch already exists: {name}')
            return
        self.branches[name] = self.branches[self.current_branch]
        print(f'Created branch: {name}')

    def switch(self, name):
        if not self.ready(): return
        if name not in self.branches:
            print(f'Unknown branch: {name}')
            return
        self.current_branch = name
        print(f'Switched to branch: {name}')

    def topo(self):
        """Kahn traversal: always output parents before children."""
        degree = {h: len(c.parents) for h, c in self.commits.items()}
        queue = merge_sort((h for h, n in degree.items() if n == 0))
        result = []
        while queue:
            h = queue.pop(0)
            result.append(self.commits[h])
            for child in merge_sort(self.children[h]):
                degree[child] -= 1
                if degree[child] == 0:
                    i = 0
                    while i < len(queue) and queue[i] < child: i += 1
                    queue.insert(i, child)
        if len(result) != len(self.commits):
            raise RuntimeError('Cycle detected')
        return result

    def log(self, sort_by=None):
        if not self.ready(): return
        if sort_by is None:
            values = self.topo()
        elif sort_by == 'date':
            values = merge_sort(self.commits.values(), lambda c: (c.timestamp, c.hash))
        elif sort_by == 'author':
            values = merge_sort(self.commits.values(), lambda c: (c.author.lower(), c.hash))
        else:
            print('Invalid args'); return
        if not values:
            print('No commits.'); return
        for c in values:
            tags = merge_sort((n for n, h in self.branches.items() if h == c.hash))
            label = ' [' + ', '.join(tags) + ']' if tags else ''
            print(f'commit {c.hash} ({c.author}, {c.timestamp:%Y-%m-%d %H:%M:%S}){label}')
            print(c.message)

    def neighbors(self, h):
        """Parent and child edges as an undirected set."""
        return merge_sort(set(self.commits[h].parents) | self.children[h])

    def path(self, start, end):
        """BFS, sorted neighbors ensure lexicographically smallest shortest path."""
        if not self.ready(): return
        for h in (start, end):
            if h not in self.commits:
                print(f'Unknown commit: {h}'); return
        queue = deque([start])
        previous = {start: None}
        while queue:
            h = queue.popleft()
            if h == end: break
            for nxt in self.neighbors(h):
                if nxt not in previous:
                    previous[nxt] = h
                    queue.append(nxt)
        if end not in previous:
            print('No path'); return
        route = []
        h = end
        while h is not None:
            route.append(h)
            h = previous[h]
        route.reverse()
        print('Path: ' + ' -> '.join(route))

    def ancestors(self, h):
        """DFS over parent references; each ancestor visited once."""
        if not self.ready(): return
        if h not in self.commits:
            print(f'Unknown commit: {h}'); return
        seen = set()
        stack = list(self.commits[h].parents)
        while stack:
            node = stack.pop()
            if node in seen: continue
            seen.add(node)
            stack.extend(self.commits[node].parents)
        print(f'Ancestors of {h}: {len(seen)}')
        for node in merge_sort(seen):
            print(f'- {node}: {self.commits[node].message}')

    def search(self, query, author=False):
        """Index-only keyword and author lookup; multiword keywords use AND."""
        if not self.ready(): return
        if author:
            candidates = self.author_index.get(query.lower(), set())
        else:
            words = query.lower().split()
            candidates = set(self.keyword_index.get(words[0], set())) if words else set()
            for word in words[1:]:
                candidates.intersection_update(self.keyword_index.get(word, set()))
        matches = merge_sort((self.commits[h] for h in candidates), lambda c: (c.timestamp, c.hash))
        print(f'Found {len(matches)} commit(s):')
        for c in matches:
            print(f'- {c.hash} ({c.author}): {c.message}')

    def merge(self, name):
        """Bonus: metadata-only 2-parent merge; no file conflict resolution."""
        if not self.ready(): return
        if name not in self.branches:
            print(f'Unknown branch: {name}'); return
        if name == self.current_branch:
            print('Cannot merge a branch into itself.'); return
        a = self.branches[self.current_branch]
        b = self.branches[name]
        if a is None or b is None:
            print('Cannot merge an empty branch.'); return
        if a == b:
            print('Already up to date.'); return
        seen, stack = set(), [a]
        while stack:
            h = stack.pop()
            if h in seen: continue
            seen.add(h)
            stack.extend(self.commits[h].parents)
        if b in seen:
            print('Already up to date.'); return
        message = f"Merge branch '{name}' into {self.current_branch}"
        c = self.add_commit(message, (a, b))
        print(f'[{self.current_branch} {c.hash}] {message}')


def benchmark():
    """Bonus: runtime comparison on deterministic reverse-order input."""
    print('N | Merge(ms) | Insertion(ms) | Equal')
    for n in (100, 500, 1000, 2000):
        data = list(range(n, 0, -1))
        start = time.perf_counter()
        a = merge_sort(data)
        merge_ms = (time.perf_counter() - start) * 1000
        start = time.perf_counter()
        b = insertion_sort(data)
        insert_ms = (time.perf_counter() - start) * 1000
        print(f'{n} | {merge_ms:.3f} | {insert_ms:.3f} | {a == b}')


COMMANDS = {'INIT', 'BRANCH', 'SWITCH', 'COMMIT', 'LOG', 'PATH', 'ANCESTORS', 'SEARCH', 'DIFF', 'MERGE', 'BENCHMARK', 'HELP'}


def parse_command(line):
    """Use shlex for quoted args; case-insensitive command verbs."""
    try:
        parts = shlex.split(line)
    except ValueError:
        print('Invalid args')
        return None, None
    return (parts[0].upper(), parts[1:]) if parts else (None, None)


def execute_command(git, command, args):
    """Validate arguments and dispatch all mandatory/bonus commands."""
    if command not in COMMANDS:
        print(f'Unknown command: {command}'); return
    if command in {'INIT', 'BRANCH', 'SWITCH', 'COMMIT', 'ANCESTORS', 'MERGE'}:
        if len(args) != 1 or not args[0].strip():
            print('Invalid args'); return
    elif command in {'PATH', 'DIFF'}:
        if len(args) != 2 or not all(args):
            print('Invalid args'); return
    elif command == 'LOG':
        if len(args) > 1 or (args and args[0].lower() not in {'--sort-by=date', '--sort-by=author'}):
            print('Invalid args'); return
    elif command == 'SEARCH':
        if len(args) != 1 or not args[0].strip():
            print('Invalid args'); return
        if args[0].startswith('--') and not args[0].lower().startswith('--author='):
            print('Invalid args'); return
        if args[0].lower().startswith('--author=') and not args[0].split('=', 1)[1].strip():
            print('Invalid args'); return
    elif args:
        print('Invalid args'); return

    if command == 'INIT': git.init(args[0])
    elif command == 'BRANCH': git.branch(args[0])
    elif command == 'SWITCH': git.switch(args[0])
    elif command == 'COMMIT': git.commit(args[0])
    elif command == 'LOG': git.log(args[0].split('=', 1)[1].lower() if args else None)
    elif command == 'PATH': git.path(*args)
    elif command == 'ANCESTORS': git.ancestors(args[0])
    elif command == 'SEARCH':
        if args[0].lower().startswith('--author='):
            git.search(args[0].split('=', 1)[1], author=True)
        else:
            git.search(args[0])
    elif command == 'MERGE': git.merge(args[0])
    elif command == 'DIFF':
        try:
            lines = diff_lines(*args)
        except (OSError, UnicodeError) as exc:
            print(f'Diff error: {exc}'); return
        print("Diff ('  ' unchanged, '- ' removed, '+ ' added):")
        for line in lines: print(line)
    elif command == 'BENCHMARK': benchmark()
    elif command == 'HELP':
        print('INIT <user> | BRANCH <name> | SWITCH <name> | COMMIT <message>')
        print('LOG [--sort-by=date|author] | PATH <hash1> <hash2> | ANCESTORS <hash>')
        print('SEARCH <keyword> | SEARCH --author=<name>')
        print('DIFF <file1> <file2> | MERGE <branch> | BENCHMARK | HELP | EXIT/QUIT')
        print('Quote arguments containing spaces, e.g. COMMIT "Add login feature"')


def main():
    """Interactive read/evaluate/print loop with persistent session state."""
    git = MiniGit()
    print('Welcome to Mini Git! Type HELP for commands; EXIT or QUIT to close.')
    while True:
        try:
            line = input('mini-git> ')
        except (EOFError, KeyboardInterrupt):
            print('\nGoodbye!'); break
        if line.strip().lower() in {'exit', 'quit'}:
            print('Goodbye!'); break
        command, args = parse_command(line)
        if command is not None:
            execute_command(git, command, args)


if __name__ == '__main__':
    main()
