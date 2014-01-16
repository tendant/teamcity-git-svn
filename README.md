A simple script for git to work with Teamcity and subversion server.

Prerequisition
====

* tcc.jar 

> Download the tcc.jar from the "My Settings & Tools" > "TeamCity Tools" side panel > "Command Line Remote Run" to any directory.

> http://confluence.jetbrains.net/display/TW/Command+Line+Remote+Run+Tool

* Python 3

    If you have Python 2.7+, please check out branch "python-2.7" intead.

Configuraiton
====

* Copy tc.cfg.sample to tc.cfg, and update tcc_jar, tc_user, tc_password, tc_server in tc.cfg.

* Run below command.

    git config --global alias.tc \\!/home/neil/workspace/teamcity-git-svn/tc.py 

  Note: update file path, there is only one backslash before '!'

Usage
====

  Run below command in git-svn enabled respository.
 
    $ git tc
