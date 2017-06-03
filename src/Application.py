
from os.path import dirname
from _thread import start_new_thread
import os
import re
import time

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
                    if remoteUser.getUserName() == monitorData['channel']:
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
        print("Monitoring %s" % filePath)
        fileHandle = open(filePath, 'r')
        fileHandle.seek(0, 2) # seek to end

        pattern = re.compile(lineFilter)

        while True:
            line = fileHandle.readline()
            if len(line) > 0:
                matches = True
                if lineFilter != None:
                    matches = (pattern.search(line) != None)
                if matches:
                    if linePrefix != None:
                        channelModel.createPost(str(linePrefix) + line)

                    else:
                        channelModel.createPost(line)
            else:
                time.sleep(3)

    def getTeamModel(self, serverName):
        if serverName not in self.__teamModels:
            configuration = self.__configuration
            serverData = configuration.getServer(serverName)

            serverModel = ServerModel(serverData['url'])

            # Mattermost.ServerLoggedInModel
            loggedInModel = serverModel.login(
                serverData['username'],
                serverData['password']
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
