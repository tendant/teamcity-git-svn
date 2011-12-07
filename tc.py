#!/usr/bin/env python

import sys
import subprocess
import shlex
import re
import logging
import tempfile
import os
import ConfigParser

logging.basicConfig(level=logging.INFO)

if sys.version < '2.7':
    print 'You need at least Python 2.7+.'
    sys.exit(1)

config = ConfigParser.ConfigParser()
config_file = os.path.join(os.path.dirname(__file__), "tc.cfg")
logging.debug("Reading form configuration file %s.", config_file)
config.read(config_file)

tcc_jar = config.get("default", "tcc_jar")
tc_user = config.get("default", "tc_user")
tc_password = config.get("default", "tc_password")

tc_server = config.get("default", "tc_server")

builds = [build for build in config.sections() if build.lower() != "default"] 
build_mapping = {}
for build in builds:
    mapping = config.get(build, "mapping")
    build_mapping.update({build:mapping})

regex_sha1 = re.compile("([a-f0-9]{7,40})")

def parse_args(argv):
    for arg in argv:
        pass
        # print arg

def find_last_svn_sha1():
    '''
    find sha1 of last svn revision.
    '''
    # git_svn_info = shlex.split("git svn info")
    git_svn_url = shlex.split("git svn info --url")
    # git_svn_log_commit = shlex.split("git svn log --show-commit --oneline --limit=1")
    # find last svn commit in current history
    try:
        svn_url_result = subprocess.check_output(git_svn_url, stderr=subprocess.STDOUT)
        logging.debug("Result:\n%s", svn_url_result)
        svn_url = re.sub("\n", "", svn_url_result)
        logging.debug("svn url: ", svn_url)
        git_svn_log_commit_str = str.format('git log --grep="{0}" --oneline --max-count=1', svn_url)
        logging.debug("Shell for finding last svn commits: %s.", git_svn_log_commit_str)
        git_svn_log_commit = shlex.split(git_svn_log_commit_str)
        logging.debug("Finding last svn commits: %s", git_svn_log_commit)
        svn_info = subprocess.check_output(git_svn_log_commit)
        logging.debug("svn log info: %s", svn_info)
        m = re.findall(regex_sha1, svn_info)
        logging.info("SVN SHA1: %s", m)
        if m:
            if len(m) == 1:
                svn_sha1 = m[0]
                logging.info("Found SHA1:%s", svn_sha1)
                return svn_sha1
            else:
                logging.error("Please report error: Found more than one svn revision: %s", m)
        else:
            logging.error("SVN information is not found., Please make sure you are running this command under git-svn enabled repository.")
    except subprocess.CalledProcessError, e:
        logging.error("No git-svn information. Please make sure you are running this command under git-svn enabled repository.", e)

def find_git_commits(sha1_start, sha1_end="HEAD"):
    if not sha1_start:
        logging.warning("Please provide starting SHA1.")
        return
    git_rev_list = str.format("git rev-list {0}..{1}", sha1_start, sha1_end)
    logging.debug("Finding commits: %s", shlex.split(git_rev_list))
    try:
        list_output = subprocess.check_output(shlex.split(git_rev_list))
        logging.debug(list_output)
        commits = re.findall(regex_sha1, list_output)
        logging.info("Found commits:%s", commits)
        return commits
    except subprocess.CalledProcessError:
        logging.error("Failed getting revision list for %s..%s", sha1_start, sha1_end)

def find_commits_files(sha1_start, sha1_end="HEAD"):
    if not sha1_start:
        logging.warning("Please provide starting SHA1.")
        return
    git_diff_files = str.format("git diff --name-only {0}..{1}", sha1_start, sha1_end)
    logging.debug("Finding commits: %s", shlex.split(git_diff_files))
    try:
        file_list_output = subprocess.check_output(shlex.split(git_diff_files))
        logging.debug(file_list_output)
        # file_list = re.findall(r"^.+$", file_list_output, re.MULTILINE)
        logging.info("Found files:%s", file_list_output)
        return file_list_output
    except subprocess.CalledProcessError:
        logging.error("Failed getting file list for %s..%s", sha1_start, sha1_end)

def verify_commits(commits):
    logging.info("Verifying commits...")
    logging.info('xx')
    if (not commits) or len(commits) < 1:
        logging.warning("No commits to verify.")
        return False
    try:
        git_svn_dcommit_dry_run = shlex.split("git svn dcommit --dry-run")
        svn_commits = subprocess.check_output(git_svn_dcommit_dry_run)
        svn_commits_sha1 = re.findall(regex_sha1, svn_commits)
        logging.info("commits: %s", commits)
        logging.info("git svn commits: %s", svn_commits_sha1)
        if set(svn_commits_sha1) == set(commits):
            return True
        else:
            return False
    except subprocess.CalledProcessError, e:
        logging.error("Failed verifying commits. %s", e)
        logging.info("Possible reason: There are local changes in working directory, please commit or stash them before trying.")

def prompt_for_int(message, default=1, prompt="Please input:"):
    print message
    try:
        while True:
            choice=raw_input(prompt)
            if not choice: 
                choice = default
            else:
                choice = int(choice)
            return choice
    except KeyboardInterrupt as e:
        logging.warning("Wrong input. %s", e)
    except EOFError as e:
        logging.warning("Wrong input. %s", e)
    except Exception as e:
        logging.warning("Wrong input. %s", e)

def prompt_for_string(message, default="default", prompt="Please input:"):
    print message
    try:
        while True:
            choice=raw_input(prompt)
            if not choice:
                choice = default
            return choice
    except KeyboardInterrupt as e:
        logging.warning("Wrong input. %s", e)
    except EOFError as e:
        logging.warning("Wrong input. %s", e)
    except Exception as e:
        logging.warning("Wrong input. %s", e)

def teamcity_login(user, password):
    info_line = str.format("java -jar {0} info", tcc_jar)
    info_cmd = shlex.split(info_line)
    logging.info("teamcity info: %s", info_line)
    logging.debug("teamcity info: %s", info_cmd)
    info_result = subprocess.call(info_cmd)
    if info_result > 0:
        
        login_line = str.format("java -jar {0} login --host {1} --user {2} --password {3}", 
                                tcc_jar, tc_server, user, password)
        login_cmd = shlex.split(login_line)
        logging.info("teamcity login: %s", login_line)
        logging.debug("teamcity login: %s", login_cmd)
        result = subprocess.check_call(login_cmd)
        logging.debug(result)
        logging.info("Login successful.")
    else:
        logging.info("User has been logged in")

def submit_teamcity_build(files, choice, build_type):
    f = tempfile.NamedTemporaryFile(delete=False)
    logging.debug("Created temporary file: %s.", f.name)
    f.write(files)
    f.close()
    mapping_config = open('.teamcity-mappings.properties', 'w')
    logging.debug("Updating mapping file: %s, %s.", mapping_config.name, build_mapping.get(build_type))
    aaa = build_mapping.get(build_type)
    logging.debug(aaa)
    mapping_config.write(aaa)
    mapping_config.close()
    file_list = re.findall(r"^.+$", files, re.MULTILINE)
    teamcity_login(tc_user, tc_password)
    logging.info("Submitting files to teamcity: %s", file_list)
    teamcity_cmd_line = str.format('java -jar {0} run --host {1} -m "testing from command line" -c {2} --config-file {3} @{4}', tcc_jar, tc_server, build_type, mapping_config.name, f.name)
    logging.info("Running: %s", teamcity_cmd_line)
    teamcity_cmd = shlex.split(teamcity_cmd_line)
    logging.debug(teamcity_cmd)
    result = subprocess.check_call(teamcity_cmd)
    logging.info("Teamcity Result: %s", result)
    os.unlink(f.name)
    return result

def git_svn_dcommit(choice="s"):
    if choice == "C":
        logging.info("*** COMMITING to svn!")
        dcommit_cmd = shlex.split("git svn dcommit -n")
        logging.info("git svn dcommit SUCCESSFUL!")
    else:
        logging.info("--- Dry run git svn dcommit...")
        dcommit_cmd = shlex.split("git svn dcommit -n")
        logging.info("You are SAFE to commit now.")
    logging.debug(dcommit_cmd)
    result = subprocess.check_call(dcommit_cmd)
    logging.info("git svn dcommit result: %s", result)

if __name__ == "__main__":
    parse_args(sys.argv)
    sha1 = find_last_svn_sha1()
    if sha1:
        commits = find_git_commits(sha1)
        if not verify_commits(commits):
            logging.warning("Verify commits Failed.")
            exit(1)
        else:
            logging.info("Verify commits successful.")
        files = find_commits_files(sha1)
        file_list = re.findall(r"^.+$", files, re.MULTILINE)
        if len(file_list) < 1:
            print "No changes for submitting. Exiting..."
            exit(0)
        print "---Below files will be submitted to teamcity for build:---"
        for filename in  file_list:
          print "  ", filename, "\n"
        print "[s]. Submit to teamcity for build."
        print "[C]. Sumbit to teamcity for build and COMMIT to svn if it is successful."
        choice = prompt_for_string("Your choice[s, C], default [s].", default="s")
        if choice == "s":
            print "Submit to teamcity for build only."
        elif choice == "C":
            print "Submit to teamcity for build and commit to svn if it is successful. It takes time to wait for build."
        else:
            print "Not a valid choice. Exiting..."
            exit(2)
        for build in builds:
            print("[%s].For %s.", build, config.get(build, "name"))
        default_build = config.get("default", "build")
        prompt = str.format("Your choices[{0}], default [{1}]", builds, default_build)
        build_type = prompt_for_string(prompt, default=default_build)
        if build_type in build_mapping.keys():
            teamcity_login(tc_user, tc_password)
            build_result = submit_teamcity_build(files, choice, build_type)
            if build_result == 0:
                git_svn_dcommit(choice)
            else:
                logging.info("Bulid failed, please fix build issue and resubmit your commits. Check %s for more details", tc_server)
                exit(3)
        else:
            print "Not a valid choice. Exiting..."
            exit(4)
