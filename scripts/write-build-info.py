"""Record the version actually built by Actions, without committing build output."""
import json
import os
from pathlib import Path

public = Path('exampleSite/public')
if not (public / 'index.html').is_file():
    raise SystemExit('Hugo homepage is missing; cannot record a deployment.')
payload = {
    'commit': os.environ['GITHUB_SHA'],
    'branch': os.environ['GITHUB_REF_NAME'],
    'repository': os.environ['GITHUB_REPOSITORY'],
    'workflow': f"https://github.com/{os.environ['GITHUB_REPOSITORY']}/actions/runs/{os.environ['GITHUB_RUN_ID']}",
    'hugo': '0.167.0 extended',
}
(public / 'build-info.json').write_text(json.dumps(payload, indent=2) + chr(10), encoding='utf-8')
print(json.dumps(payload, indent=2))
