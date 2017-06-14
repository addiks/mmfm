
from os.path import dirname
from _thread import start_new_thread
import os
import re
import time
import getpass

from .FileReader import FileReader
from .Model.ConfigurationModel import ConfigurationModel
from Mattermost.ServerModel import ServerModel

class Application:
    __assetPath = None
    __configuration = None # Model.ConfigurationModel
    __servers = {}
    __teamModels = {} # list(Mattermost.ServerLoggedInModel)

    def __init__(self, argv):
        assetPath = dirname(dirname(__file__)) + "/assets/"
        self.__assetPath = assetPath

        if len(argv) <= 1:
            raise Exception("Usage: %s [CONFIG-FILE-PATH]" % argv[0])

        configFilePath = argv[1]

        if not os.path.exists(configFilePath):
            raise Exception("File '%s' not found!" % configFilePath)

        configuration = ConfigurationModel(configFilePath)

        self.__configuration = configuration

    def run(self):
        # ConfigurationModel
        configuration = self.__configuration

        for monitorData in configuration.getMonitors():
            # Mattermost.TeamModel
            teamModel = self.getTeamModel(monitorData['server'])

            # Mattermost.ChannelModel
            channelModel = None

            # Mattermost.ServerLoggedInModel
            serverModel = teamModel.getServer()

            for channelModelCandidate in teamModel.getChannels():
                if channelModelCandidate.isDirectMessage():
                    remoteUser = channelModelCandidate.getDirectMessageRemoteUser()
                    if remoteUser != None and remoteUser.getUserName() == monitorData['channel']:
                        channelModel = channelModelCandidate
                else:
                    if channelModelCandidate.getName() == monitorData['channel']:
                        channelModel = channelModelCandidate
                        break

            if channelModel == None:
                for channelModelCandidate in teamModel.searchMoreChannels(monitorData['channel']):
                    if channelModelCandidate.getName() == monitorData['channel']:
                        channelModel = channelModelCandidate
                        break

            if channelModel == None:
                print("Could not find open channel for '%s'!" % monitorData['channel'])

            else:
                channelModel.addUser(teamModel.getServer().getSelfUser())
                lineFilter = None
                if "filter" in monitorData:
                    lineFilter = monitorData["filter"]
                linePrefix = None
                if "prefix" in monitorData:
                    linePrefix = monitorData["prefix"]
                start_new_thread(self._monitorFile, (
                    monitorData['path'],
                    channelModel,
                    lineFilter,
                    linePrefix
                ))

        while True:
            time.sleep(3600)

    def _monitorFile(self, filePath, channelModel, lineFilter=None, linePrefix=None):
        try:
            print("Monitoring %s" % filePath)
            monitor = FileReader(filePath)

            # default line handler: post line to mattermost channel
            lineHandler = channelModel.createPost

            # wrap the line-handler into a new one with a prefix
            if linePrefix != None:
                prePrefixLineHandler = lineHandler
                lineHandler = lambda line: prePrefixLineHandler(str(linePrefix) + line)

            # wrap the line-handler into a new one that filters
            if lineFilter != None:
                pattern = re.compile(lineFilter)
                preFilterLineHandler = lineHandler
                lineHandler = lambda line: self.__filterLineHandler(line, preFilterLineHandler, pattern)

            # main loop for this monitor
            while True:
                try:
                    while monitor.hasNewLines():

                        # handle all lines that are available right now
                        while monitor.hasNewLines():
                            line = monitor.fetchLine()
                            lineHandler(line)

                        # after handling a block of data,
                        # check after two seconds if there are more lines without closing file
                        time.sleep(2)

                except FileNotFoundError as exception:
                    print(exception)
                    print("Checking again in 10 seconds...")

                # no new lines in the last two seconds, close file and check again after ten seconds
                monitor.expire()
                time.sleep(10)

        except FileNotFoundError as exception:
            print(exception)

    def __filterLineHandler(self, line, innerLineHandler, pattern):
        if (pattern.search(line) != None):
            innerLineHandler(line)

    def getTeamModel(self, serverName):
        if serverName not in self.__teamModels:
            configuration = self.__configuration
            serverData = configuration.getServer(serverName)

            serverModel = ServerModel(serverData['url'])

            password = ""

            if 'password' in serverData:
                password = serverData['password']

            elif 'ask-password-on-startup' in serverData and serverData['ask-password-on-startup'] == True:
                print("Please enter password for server '%s' (%s)." % (serverData['name'], serverData['url']))
                password = getpass.getpass()

            # Mattermost.ServerLoggedInModel
            loggedInModel = serverModel.login(
                serverData['username'],
                password
            )

            # Mattermost.TeamModel
            teamModel = loggedInModel.getTeam(serverData['team'])

            self.__teamModels[serverName] = teamModel
        return self.__teamModels[serverName]

    def getAssetPath(self):
        return self.__assetPath

    def getServerModel(self, url):
        if url not in self.__servers:
            self.__servers[url] = ServerModel(url)
        return self.__servers[url]
