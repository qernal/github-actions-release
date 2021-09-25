from github import Github as g
from github.MainClass import Github
from functools import partial
import semver
import os
import re
import tarfile
import string
import random

class release:
    gh = None
    config = dict()
    release = dict()
    workspace = "/github/workspace/"

    # validate if the config has a length
    def validate_config(self, name: str, value: str):
        if(value != None and len(value) > 0):
            return True
        else:
            self.workflow("error", "Missing field; " + name)
            return False

    # output of
    def output(self, name: str, value: str):
        print(f"::set-output name={name}::{value}")

    # github action formatted output
    # TODO: config to disable debug mode
    def workflow(self, type: str, message: str):
        if(type == "debug" or type == "warning" or type == "error"):
            print(f"::{type}::{message}")

            if type == "error":
                exit(1)
        else:
            print(message)

    # is pre-release
    def is_prerelease(self):
        if self.config['arg_prerelease'] == None:
            return False

        if len(self.config['arg_prerelease']) > 0 and self.config['arg_prerelease'].lower() == "true":
            return True

        return False

    # create release
    def create_release(self, repo_name: str, tag: str, name: str, message: str, prerelease: bool):
        # if we have no name defined, set it to be the tag
        if name == None:
            name = tag
        else:
            if len(name) < 1:
                name = tag

        # redefine to a blank message, None is not accepted
        if message == None:
            message = ""

        repo = self.gh.get_repo(repo_name)
        release = repo.create_git_release(tag, name, message, False, prerelease)
        self.output("tag", tag)

        return release

    # replace the regex closure
    # https://stackoverflow.com/questions/33634232/replace-named-group-in-regex-match
    def _regex_replace_closure(self, subgroup, replacement, m):
        if m.group(subgroup) not in [None, '']:
            start = m.start(subgroup)
            end = m.end(subgroup)
            return m.group()[:start] + replacement + m.group()[end:]

    # increment the tag
    # TODO: validate the semver check with semver valid
    def increment(self, tag: str, increment_type: str) -> str:
        self.workflow("debug", "tag; " + tag)

        matches = re.search(self.config['arg_tag_pattern'], tag)
        self.workflow('debug', "group-dict;" + matches['semver'])

        # TODO: handle regex replacement errors
        raw_ver = str(semver.VersionInfo.parse(matches['semver']).next_version(increment_type))
        ver = re.sub(self.config['arg_tag_pattern'], partial(self._regex_replace_closure, "semver", raw_ver), tag)

        self.workflow("debug", "final version; " + ver)
        return ver

    # validate all the defined assets are on disk
    def validate_assets(self, assets):
        asset_list = assets.split(',')

        for asset in asset_list:
            if(os.path.exists(self.workspace + asset) == False):
                self.workflow("error", f"Unable to find asset on disk; {asset}")

            self.workflow("debug", f"Found asset {asset} on disk")

    # split assets or return singular as dict
    def split_assets(self, assets: str) -> dict:
        if assets.find(',') > 0:
            return assets.split(',')
        else:
            return [assets]

    # generate an archive
    def generate_archive(self, asset: str, name: str = None) -> str:
        if name == None:
            filename_variant = ''.join(random.choice(string.ascii_letters) for i in range(5))
            output_filename = f"archive_{filename_variant}.tar.gz"
        else:
            output_filename = name + '.tar.gz'

        with tarfile.open(output_filename, "w:gz") as tar:
                tar.add(asset, arcname=os.path.basename(asset))

        return output_filename

    # upload assets into the release
    def upload_assets(self, repo_name: str, release: str, assets: str):
        asset_list = self.split_assets(assets)

        # upload asset
        for asset in asset_list:
            if os.path.isdir(self.workspace + asset):
                # generate archive for directories
                of = self.generate_archive(self.workspace + asset, asset)
                asset = of

            release.upload_asset(self.workspace + asset)

    # loop through all releases and match the pattern (in desc order)
    def get_latest_release(self, repo_name: str, tag_pattern: str):
        releases = self.gh.get_repo(repo_name).get_releases()

        for release in releases:
            if re.match(tag_pattern, release.tag_name):
                return release.tag_name

        return None

    # main logic
    def run(self):
        # if we're only getting last release, grab it and quit
        if self.config['arg_get_last_tag'] != None:
            latest = self.get_latest_release(self.config['arg_repo_name'], self.config['arg_tag_pattern'])

            if latest == None:
                self.output("tag", latest)

            print("-- Release skipped, output was last tag")
            return

        # if auto increment is set, get last release
        if self.config['arg_auto_increment'] != None:
            latest = self.get_latest_release(self.config['arg_repo_name'], self.config['arg_tag_pattern'])
            self.workflow("debug", latest)

            if latest == None:
                # no current release, use the tag
                self.release['tag'] = self.config['arg_tag']
            else:
                self.release['tag'] = self.increment(latest, "patch")
                # TODO: validate the output of increment against supplied pattern
                # self.config['arg_tag_pattern']
        else:
            # don't auto increment, just create release
            self.release['tag'] = self.config['arg_tag']

        # create release
        release = self.create_release(self.config['arg_repo_name'], self.release['tag'], self.config['arg_release_name'], self.config['arg_release_desc'], self.is_prerelease())

        # upload assets
        self.upload_assets(self.config['arg_repo_name'], release, self.config['arg_assets'])

        print("-- Release created")

    def __init__(self):
        # inputs
        self.config['base_dir'] = '/github/workspace'

        # config
        self.config['arg_tag'] = os.environ.get('INPUT_TAG')
        self.config['arg_tag_pattern'] = os.environ.get('INPUT_TAG_PATTERN')
        self.config['arg_release_name'] = os.environ.get('INPUT_RELEASE_NAME')
        self.config['arg_release_desc'] = os.environ.get('INPUT_RELEASE_DESCRIPTION')
        self.config['arg_prerelease'] = os.environ.get('INPUT_PRERELEASE')
        self.config['arg_assets'] = os.environ.get('INPUT_ASSETS')
        self.config['arg_auto_increment'] = os.environ.get('INPUT_AUTO_INCREMENT')
        self.config['arg_repo_name'] = os.environ.get('INPUT_REPO_NAME')
        self.config['arg_get_last_tag'] = os.environ.get('INPUT_GET_LAST_TAG')

        # validate required config
        if (not self.validate_config("tag", self.config['arg_tag']) and
            not self.validate_config("assets", self.config['arg_assets']) and
            not self.validate_config("repo name", self.config['arg_repo_name'])):
            self.workflow("error", "Missing required fields")
            exit(1)

        # make sure tag pattern was supplied
        if self.validate_config("tag pattern", self.config['arg_tag_pattern']):
            try:
                re_pattern = self.config['arg_tag_pattern']
                re.compile(f'{re_pattern}')
            except re.error:
                self.workflow("error", "invalid tag pattern regex")
                exit(1)

        # validate the assets
        self.validate_assets(self.config['arg_assets'])

        # connect to github
        self.gh = Github(os.environ.get('INPUT_TOKEN'))

        # run app
        self.run()

release()