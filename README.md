# Github Actions: Release

![MIT licensed](https://img.shields.io/badge/license-MIT-blue.svg)

Github action to run release packages against a repository, this provides release creation with the following features;

- List multiple assets and directores for auto-archiving
- Auto increment semver (with pattern matching on existing release naming)
- Mark as pre-release
- Dry run without release (for testing releases via non-release branches)

## Workflow configuration

To use this action, define it in your workflow;

```yaml
on: [push, pull_request]

jobs:
  lint:
    runs-on: self-hosted
    name: Lint package
    steps:
      - uses: actions/checkout@v2
      - uses: qernal/github-actions-release@v1.0
```

### Action parameters

| Parameter | Description | Default | Required | Values |
| ---- | ---- | ---- | ---- | ---- |
| `tag` | Tag to use, can be initial tag if `tag_pattern` is set | _no default_ | Y | String |
| `tag_pattern` | A regular expression of the pattern to use, e.g. `abc_v(?P<semver>([0-9]+)\.([0-9]+)\.([0-9]+))` - the pattern *must* include a `semver` group that matches a semantic versioning pattern otherwise the replacement will fail | _no default_ | N | String |
| `release_name` | Name of the release | _no default_ | N | String |
| `release_description` | Description of the release | _no default_ | N | String |
| `prerelease` | Mark as prerelease | false | N | boolean |
| `assets` | Comma separated list of assets, can be files or directory | _no default_ | Y | String, e.g. `file.yaml,file2.yaml,charts` |
| `auto_increment` | Auto increment | _no default_ | N | String, values are; `major`, `minor`, `patch` |
| `repo_name` | Name of the repository to create release on | Y | String |
| `token` | GitHub PAT Token to access/create release | _no default_ | Y | String |
| `dry_run` | _not yet implemeneted_ | False | N | Boolean |

Example;

```yaml
    steps:
      - uses: actions/checkout@v2
      - uses: qernal/github-actions-rust-release@v1.0
        with:
          tag: "abc_v1.0.0"
          tag_pattern: 'abc_v(?P<semver>([0-9]+)\.([0-9]+)\.([0-9]+))'
          token: "${{ secrets.github_token }}"
```

### Action output

| Output | Description |
| ---- | ---- |
| `tag` | Tag that was created during the release |

## Manual runs

You can use the container without the context of the runner, and just run the container like so;

```bash
docker run --rm -v `pwd`:/github/workspace ghcr.io/qernal/gh-actions/release-x86_64:main
```

Replace the `pwd` with your workspace if you're not running from the current directory

## Development

```bash
INPUT_TAG="abc_v1.0.0" INPUT_TAG_PATTERN="abc_v(?P<semver>([0-9]+)\.([0-9]+)\.([0-9]+))" INPUT_ASSETS="./example-assets" INPUT_AUTO_INCREMENT="minor" INPUT_REPO_NAME="my-user/releases-repo" INPUT_TOKEN="xxxx" python3 ./src/release.py
```