
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
                monitor = {
                    'path': monitorXml.get('path'),
                    'server': monitorXml.get('server'),
                    'channel': monitorXml.get('channel'),
                }

                monitorFilter = monitorXml.get('filter')
                if monitorFilter != None:
                    monitor['filter'] = monitorFilter

                monitorPrefix = monitorXml.get('prefix')
                if monitorPrefix != None:
                    monitor['prefix'] = monitorPrefix

                self.__monitors.append(monitor)

            for serverXml in configurationXml.iter('server'):
                server = {
                    'url': serverXml.get('url'),
                    'team': serverXml.get('team'),
                    'username': serverXml.get('username'),
                    'name': serverXml.get('name'),
                }

                serverPassword = serverXml.get('password')
                if serverPassword != None:
                    server['password'] = serverPassword

                serverAskPassword = serverXml.get('ask-password-on-startup')
                if serverAskPassword != None:
                    server['ask-password-on-startup'] = (serverAskPassword.lower() == 'true')

                self.__servers[serverXml.get('name')] = server

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

            if 'filter' in monitor:
                monitorXml.set('filter', monitor['filter'])

            if 'prefix' in monitor:
                monitorXml.set('prefix', monitor['prefix'])

        for server in self.__servers:
            serverXml = ElementTree.SubElement(configurationXml, 'server')
            serverXml.set('url', server['url'])
            serverXml.set('team', server['team'])
            serverXml.set('username', server['username'])
            serverXml.set('name', server['name'])

            if 'password' in server:
                serverXml.set('password', server['password'])

            if 'ask-password-on-startup' in server:
                serverXml.set('ask-password-on-startup', server['ask-password-on-startup'])

        xml = ElementTree.ElementTree(configurationXml)
        xml.write(xmlFilePath)
