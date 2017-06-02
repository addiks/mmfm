mmfm - Mattermost File Monitor
===================================

A simple deamon that monitor's one or multiple files and post's all new lines to a Mattermost-Server to configured
channels or users. Handy tool if you want to monitor your error-log's and be alerted directly if some error happens.

## Set-Up

After you have cloned (and checked out) this repository, make sure to initialize the submodule(s).

Create a file like the one provided in "assets/configuration.sample.xml" somewhere, modify it's content to fit your
needs. You need one "monitor" entry per file you want to monitor and channel you want to post into. If you need to post
accross multiple mattermost-servers, create one "server" entry for every server you need to post onto. Make sure that
for every "server" attribute in the "monitor" entries there exists an "server" entry with the matching "name" attribute.
Run the python-script "mmfm.py" using the absolute path to the configuration file as the first (and only) parameter.
Make sure the user described in the configuration is already in all channels it is supposed to write into as it
currently cannot join channel's on it's own.

## Licence

This plugin is licenced under the GNU General Public Licence version 3.
If you do not know what that means, see the file 'LICENCE'.
