A simple script for git to work with Teamcity and subversion server.

Prerequisition
====

* tcc.jar 

> Download the tcc.jar from the "My Settings & Tools" > "TeamCity Tools" side panel > "Command Line Remote Run" to any directory.

> http://confluence.jetbrains.net/display/TW/Command+Line+Remote+Run+Tool

* Python 2.7

Configuraiton
====

* Copy tc.cfg.sample to tc.cfg, and update tcc_jar, tc_user, tc_password, tc_server in tc.cfg.

* Update configure_mapping in tc.cfg.

    You should be able to find mapping configuration from "My Settings & Tools" > "TeamCity Tools" side panel > "Command Line Remote Run" in your teamcity server..

* Run below command.

    git config --global alias.tc \\!/home/neil/workspace/teamcity/util/tc.py 

  Note: update file path

Usage
====

  Run below command in git-svn enabled respository.
 
    $ git tc
