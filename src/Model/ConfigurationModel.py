
import xml.etree.ElementTree as ElementTree
import os

class ConfigurationModel:
    __servers = {}
    __monitors = []
    __xmlFilePath = None

    def __init__(self, configurationPath):
        while len(configurationPath)>0 and configurationPath[-1] == '/':
            configurationPath = configurationPath[0:-1]
        self.__xmlFilePath = configurationPath
        self.__load()

    def getMonitors(self):
        return self.__monitors

    def getServer(self, serverName):
        if serverName in self.__servers:
            return self.__servers[serverName]

    ### INTERNALS - SAVE & LOAD

    def __load(self):
        xmlFilePath = self.__xmlFilePath

        if os.path.exists(xmlFilePath):
            with open(xmlFilePath, "r") as xmlFile:
                xmlData = xmlFile.read()
            configurationXml = ElementTree.fromstring(xmlData)

            for monitorXml in configurationXml.iter('monitor'):
                self.__monitors.append({
                    'path': monitorXml.get('path'),
                    'server': monitorXml.get('server'),
                    'channel': monitorXml.get('channel'),
                })

            for serverXml in configurationXml.iter('server'):
                self.__servers[serverXml.get('name')] = {
                    'url': serverXml.get('url'),
                    'team': serverXml.get('team'),
                    'username': serverXml.get('username'),
                    'password': serverXml.get('password'),
                    'name': serverXml.get('name'),
                }

    def __save(self):
        xmlFilePath = self.__xmlFilePath

        folderPath = os.path.dirname(xmlFilePath)

        if not os.path.exists(folderPath):
            os.makedirs(folderPath)

        configurationXml = ElementTree.Element('mmfm-config')

        for monitor in self.__monitors:
            monitorXml = ElementTree.SubElement(configurationXml, 'monitor')
            monitorXml.set('path', monitor['path'])
            monitorXml.set('server', monitor['server'])
            monitorXml.set('channel', monitor['channel'])

        for server in self.__servers:
            serverXml = ElementTree.SubElement(configurationXml, 'server')
            serverXml.set('url', server['url'])
            serverXml.set('team', server['team'])
            serverXml.set('username', server['username'])
            serverXml.set('password', server['password'])
            serverXml.set('name', server['name'])

        xml = ElementTree.ElementTree(configurationXml)
        xml.write(xmlFilePath)
