
from os.path import dirname
from _thread import start_new_thread
import os
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
            print("Usage: %s [CONFIG-FILE-PATH]" % argv[0])
            return

        configFilePath = argv[1]

        if not os.path.exists(configFilePath):
            print("File '%s' not found!" % configFilePath)
            return

        configuration = ConfigurationModel(configFilePath)

        self.__configuration = configuration

    def run(self):
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
                    print(channelModelCandidate.getName())
                    if channelModelCandidate.getName() == monitorData['channel']:
                        channelModel = channelModelCandidate
                        break

            if channelModel == None:
                for channelModelCandidate in teamModel.searchMoreChannels(monitorData['channel']):
                    print(channelModelCandidate.getName())
                    if channelModelCandidate.getName() == monitorData['channel']:
                        channelModel = channelModelCandidate
                        break

#            if channelModel == None:
#                for channelMember in teamModel.getChannelMembers():
#                    print(channelMember.getUser().getUserName())
#                    print(channelMember.getChannel().getName())
#                    if channelMember.getUser().getUserName() == monitorData['channel']:
#                        channelModel = channelMember.getChannel()

            if channelModel != None:
                channelModel.addUser(teamModel.getServer().getSelfUser())
                start_new_thread(self._monitorFile, (monitorData['path'], channelModel))

        while True:
            time.sleep(3600)

    def _monitorFile(self, filePath, channelModel):
        print("Monitoring %s" % filePath)
        fileHandle = open(filePath, 'r')
        fileHandle.seek(0, 2) # seek to end
        while True:
            line = fileHandle.readline()
            if len(line) > 0:
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
