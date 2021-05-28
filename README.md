# github-actions-release
GitHub Actions: GH Release package


```bash
python3 ./release.py
```



# Github Actions: Release

![MIT licensed](https://img.shields.io/badge/license-MIT-blue.svg)

Github action to run release packages against a repository, this provides linting with the following features;

- Globbing files
- Auto increment semver
- Archive packages
- Mark as pre-release
- Dry run without release (for testing releases via non-release branches)

![alt text](gh_lint_example.png "GitHub Lint Example")

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

## Action parameters

| Parameter | Description | Required |
| ---- | ---- | ---- |
| `clippy_args` | Arguments for clippy configuration | N |
| `path_glob` | Glob for path finding (when a repository has multiple rust projects) | N |
| `git_ssh_key` | Base64 encoded SSH key used for cargo when private git repositories are specified | N |
| `threads` | Threads to run at once - for concurrency of functions used with `path_glob` (integer) | N |

Example;

```yaml
    steps:
      - uses: actions/checkout@v2
      - uses: qernal/github-actions-rust-clippy@v1.1
        with:
          args: "--verbose"
          path_glob: "**/src"
          git_ssh_key: "${{ secrets.base64_ssh_key }}" # Must be base64 encoded and a valid RSA key
```

## Manual runs

You can use the container without the context of the runner, and just run the container like so;

```bash
docker run --rm -v `pwd`:/github/workspace ghcr.io/qernal/gh-actions/rust-clippy-x86_64:latest
```

Replace the `pwd` with your workspace if you're not running from the current directory

## Development

```bash
INPUT_TAG=abc INPUT_TAG_PATTERN=abc INPUT_ASSETS="./" python3 ./src/release.py
```