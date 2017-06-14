
import os

class FileReader:
    __filePath = None
    __fileHandle = None
    __fileSeek = 0

    def __init__(self, filePath):
        self.__filePath = filePath
        fileHandle = open(filePath, "r")
        fileHandle.seek(0, 2) # seek to end
        self.__fileSeek = fileHandle.tell()
        self.__fileHandle = fileHandle

    def hasNewLines(self):
        fileHandle = self.__lazyLoadHandle()
        fileHandle.seek(0, 2) # seek to end
        currentFileSeek = fileHandle.tell()
        fileHandle.seek(self.__fileSeek, 0)
        return currentFileSeek > self.__fileSeek

    def fetchLine(self):
        fileHandle = self.__lazyLoadHandle()
        line = fileHandle.readline()
        self.__fileSeek = fileHandle.tell()
        return line

    def expire(self):
        if self.__fileHandle is not None:
            self.__fileHandle.close()
            self.__fileHandle = None

    def __lazyLoadHandle(self):
        if self.__fileHandle is None:
            self.__fileHandle = self.__createNewHandle()
        return self.__fileHandle

    def __createNewHandle(self):
        try:
            fileHandle = open(self.__filePath, 'r')
            fileHandle.seek(0, 2) # seek to end
            if fileHandle.tell() < self.__fileSeek:
                self.__fileSeek = 0
            fileHandle.seek(self.__fileSeek, 0)
            return fileHandle

        except FileNotFoundError as exception:
            self.__fileSeek = 0
            raise exception
