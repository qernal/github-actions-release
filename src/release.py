from github import Github as g
from github.MainClass import Github
import semver
import os
import re
import tarfile

class release:
    gh = None
    config = dict()
    release = dict()

    # github action formatted output
    def output(self, type: str, message: str):
        if(type == "debug" or type == "warning" or type == "error"):
            print(f"::{type}::{message}")

            if type == "error":
                exit(1)
        else:
            print(message)

    # create release
    def create_release(self, repo_name: str, tag: str, name: str, message: str, draft: str, prerelease: bool):
        repo = self.gh.get_repo(repo_name)
        release = repo.create_git_release(tag, name, message, draft, prerelease)

        return release

    # get repo releases
    # def get_releases(self, repo_name, limit):
    #     releases = self.gh.get_repo(repo_name).get_releases()

    #     for release in releases:
    #         release.etag

    # match the last release from the repo
    # def match_tag(regex, tag):
    #     return re.match(regex, tag)

    # increment the tag
    # TODO: validate the semver check with semver valid
    def increment(tag: str, increment_type: str) -> str:
        ver = semver.VersionInfo.parse(tag)
        ver.next_version(increment_type)

        return ver.finalize_version()

    # validate all the defined assets are on disk
    def validate_assets(self, assets):
        asset_list = assets.split(',')

        for asset in asset_list:
            if(os.path.exists(asset) == False):
                self.output("error", f"Unable to find asset on disk; {asset}")

            self.output("debug", f"Found asset {asset} on disk")

    # upload assets into the release
    def upload_assets(self, release, assets, archive = False):
        asset_list = ','.split(assets)

        release = self.gh.get_repo(repo_name).get_release(release_id)

        if archive:
            with tarfile.open(output_filename, "w:gz") as tar:
                # loop through files and add
                tar.add(source_dir, arcname=os.path.basename(source_dir))

        # upload asset
        for asset in asset_list:
            release.upload_asset(asset)

    # loop through all releases and match the pattern (in desc order)
    def get_latest_release(self, repo_name: str, tag_pattern: str):
        releases = self.gh.get_repo(repo_name).get_releases()

        for release in releases:
            if re.match(tag_pattern, release.tag_name):
                return release.tag_name

        return None

    # main logic
    def run(self):
        # if auto increment is set, get last release
        latest = self.get_latest_release(self.config['arg_tag_pattern'])

        if latest == None:
            # no current release, use the tag
            self.release['tag'] = self.config['arg_tag']
        else:
            self.release['tag'] = self.increment(latest)
            # TODO: validate the output of increment against pattern

        # create release
        release = self.create_release(self.config['arg_repo_name'], self.release['tag'], )

        # upload assets
        self.upload_assets()

        # TODO: archive assets?
        # TODO: upload assets here
        print(b)

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
        self.config['arg_archive'] = os.environ.get('INPUT_ARCHIVE')
        self.config['arg_auto_increment'] = os.environ.get('INPUT_AUTO_INCREMENT')
        self.config['arg_owner'] = os.environ.get('INPUT_OWNER')
        self.config['arg_repo_name'] = os.environ.get('INPUT_REPO_NAME')

        # validate required config
        if self.config['arg_tag'] == None and self.config['arg_assets'] == None:
            self.output("error", "missing required fields tag or assets")
            exit(1)

        # make sure tag pattern was supplied
        if self.config['arg_tag_pattern'] != None and len(self.config['arg_tag_pattern']) > 0:
            try:
                re_pattern = self.config['arg_tag_pattern']
                re.compile(f'{re_pattern}')
            except re.error:
                self.output("error", "invalid tag pattern regex")
                exit(1)

        #

        # validate the assets
        self.validate_assets(self.config['arg_assets'])

        # connect to github
        self.gh = Github(os.environ.get('INPUT_TOKEN'))

        # run app
        self.run()

release()