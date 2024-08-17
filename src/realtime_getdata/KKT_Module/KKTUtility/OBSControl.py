import os.path
import sys
sys.path.append('../')
import time
from obswebsocket import obsws, requests
import logging


class OBSControl:
    def __init__(self):
        self._ws = None
        self.connected = False

    def connectOBSWebSocket(self, host = "localhost", port = 4444, password = "secret"):
        self._ws = obsws(host, port, password)
        self._ws.connect()
        self.connected = True
        logging.debug('OBS web socket connected')

        scenes = self._ws.call(requests.GetSceneList())
        print('Scenes:')
        for s in scenes.getScenes():
            name = s['name']
            print('\t'+name)

        sources = self._ws.call(requests.GetSourcesList()).getSources()
        print('Source:')
        for s in sources:
            source = s['name']
            print('\t'+ source)
            self._ws.call(requests.SetMute(source, True))

        self.connected = True

    def setRecordPath(self, dir , file_name):
        self._ws.call(requests.SetFilenameFormatting(file_name))
        self._ws.call(requests.SetRecordingFolder(dir))
        time.sleep(1)


    def startRecording(self):
        if self.connected:
            self._ws.call(requests.StartRecording())
            logging.debug("Start Video Recording")

    def stopRecording(self):
        path = None
        if self.connected:
            self._ws.call(requests.StopRecording())
            logging.debug("Stop Video Recording")
            outputs = self._ws.call(requests.ListOutputs()).getOutputs()
            for output in outputs:
                if output['name'] == 'simple_file_output':
                    path = output['settings']['path']
                    logging.debug('Record path : {}'.format(path))
                    break
        return path

    def pauseRecording(self):
        self._ws.call(requests.PauseRecording())
        logging.debug("Pause Recording")

    def resumeRecording(self):
        self._ws.call(requests.ResumeRecording())
        logging.debug("Resume Recording")

    def disconnectOBSWebSocket(self):
        if not self.connected:
            return
        self._ws.disconnect()
        self.connected = False
        logging.debug('OBS websocket disconnect')



def main():
    try:
        ws = OBSControl()

        ws.connectOBSWebSocket()

        ws.setRecordPath(r'C:\Users\eric.li\Desktop\Python\py_study\OBS_control\Record', 'test')

        ws.startRecording()

        time.sleep(5)

        ws.stopRecording()

        ws.disconnectOBSWebSocket()

        del ws

    except KeyboardInterrupt:
        pass



if __name__ == '__main__':
   main()
