"""Print a reproducible candidate list; this does not decide rubric validity."""
import argparse
import json
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--base', default='a8b1a30', help='Excluded baseline; include descendants only')
parser.add_argument('--head', default='HEAD', help='The exact final submission revision')
args = parser.parse_args()

def git(*argv):
    return subprocess.check_output(['git', *argv], text=True, encoding='utf-8').strip()

base = git('rev-parse', args.base)
head = git('rev-parse', args.head)
subprocess.run(['git', 'merge-base', '--is-ancestor', base, head], check=True)
rows = []
for sha in git('rev-list', '--reverse', f'{base}..{head}').splitlines():
    paths = git('diff-tree', '--root', '--no-commit-id', '--name-only', '-r', sha).splitlines()
    rows.append({'sha': sha, 'message': git('show', '-s', '--format=%s', sha),
                 'paths': paths, 'has_file_changes': bool(paths),
                 'url': f'https://github.com/JiseongParkk/jswebsite/commit/{sha}'})
print(json.dumps({'excluded_baseline': base, 'included_head': head,
                  'candidate_count': len(rows), 'commits': rows,
                  'review_note': 'Inspect diffs and explicitly subtract invalid commits; count is not an automatic grading claim.'}, ensure_ascii=False, indent=2))
