import Leap, sys, time, socket, os, shutil 
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture

class MyLeapListener(Leap.Listener):
    def on_init(self, controller):
        self.alarm = 0

    def addVLCController(self, vlcContrl):
        self.vlcController = vlcContrl
        
    def on_connect(self, controller):
        print "Connected"
        controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE);
        controller.enable_gesture(Leap.Gesture.TYPE_KEY_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SCREEN_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SWIPE);

    def on_disconnect(self, controller):
        print "Disconnected"

    def on_exit(self, controller):
        print "Exited"

    def on_frame(self, controller):
        frame = controller.frame()

        if not frame.hands.empty:
            for gesture in frame.gestures():
                if gesture.type == Leap.Gesture.TYPE_SWIPE:
                    swipe = SwipeGesture(gesture)

                    if swipe.direction[0] > 0.5 and self.alarm < time.time():
                        self.alarm = time.time() + 1.00
                        print "Right: next song"
                        self.vlcController.send("next")
                    if swipe.direction[0] < -0.5 and self.alarm < time.time():
                        self.alarm = time.time() + 1.00
                        print "Left: previous song"
                        self.vlcController.send("prev")
                    if swipe.direction[1] > 0.5 and self.alarm < time.time():
                        self.alarm = time.time() + 1.00
                        print "Up: volume up"
                        self.vlcController.send("volup 2")
                    if swipe.direction[1] < -0.5 and self.alarm < time.time():
                        self.alarm = time.time() + 1.00
                        print "Down: volume down"
                        self.vlcController.send("voldown 2")

                if gesture.type == Leap.Gesture.TYPE_KEY_TAP and self.alarm < time.time():
                    self.alarm = time.time() + 1.00
                    self.vlcController.send("pause")
                    print "Key Tap: toggle pause"

                if gesture.type == Leap.Gesture.TYPE_SCREEN_TAP and self.alarm < time.time():
                    self.alarm = time.time() + 1.00
                    self.vlcController.send("pause")
                    print "Screen Tap: toggle pause"

class VLCController():
    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(0.5)
        self.socket.connect(("127.0.0.1",6666))
        print "connected to VLC"

    def send(self, command):
        self.socket.send("%s\r" % command)

    def changeSettings(self):
        filename = os.environ['APPDATA'] + "\\vlc\\vlcrc"
        filename2 = os.environ['APPDATA'] + "\\vlc\\vlcrc2"

        infile = open(filename, 'r')
        for line in infile:
            if "rc-host=127.0.0.1:6666" in line and "#" not in line:
                return
		infile.close()
        print "WARNING: this will change your VLC oldrc settings"
        answer = str(raw_input("Do you want to change your VLC settings so this will work? [Y/n]"))
        raw_input("close VLC first, press enter to continue")
        infile = open(filename, 'r')
        if answer == 'Y' or answer == '':
            print "correctanswer"
            outfile = open(filename2, 'w')
            for line in infile:
                if "[oldrc]" in line:
                    outfile.write(line)
                    outfile.write("rc-quiet=1\n")
                    outfile.write("rc-host=127.0.0.1:6666\n")
                elif "#extraintf=" in line:
                    outfile.write("extraintf=oldrc\n")
                else:
                    outfile.write(line)
        else:
            sys.exit(0)
        infile.close()
        outfile.close()
        shutil.move(filename2, filename)
        raw_input("Start VLC")
    
        
def main():
    print "swipe right for next song"
    print "swipe left for previous song"
    print "swipe up for volume up"
    print "swipe down for volume down"
    print "key/screen tap to toggle pause"
    print ""

    listener = MyLeapListener()
    vlcc = VLCController()
    vlcc.changeSettings()
    vlcc.connect()
    listener.addVLCController(vlcc)
    controller = Leap.Controller()

    controller.add_listener(listener)

    raw_input("Press enter to quit\n")
    controller.remove_listener(listener)

if __name__ == "__main__":
    main()
