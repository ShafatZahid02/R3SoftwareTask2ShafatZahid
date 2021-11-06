import socket
import sys
import pygame._sdl2
from pygame._sdl2 import controller


class Gamepad:
    '''
    SDL2 controller converts native pygame joysticks into a GameController object standard with the SDL library.
    (https://wiki.libsdl.org/)
    Axis ranges therefore are between -32768 and 32767
    Trigger axis ranges are between 0 and 32767 (they never return a negative value)
    (https://wiki.libsdl.org/SDL_GameControllerGetAxis)
    Therefore we must clamp these values between -1 and 1
    '''

    JOYSTICK_AXIS_MAX = 32767  #Protected member
    JOYSTICK_AXIS_MIN = -32768  #Protected member
    connectedJoysticks = []  #Protected member

    def __init__(self):
        if not pygame.joystick.get_init():
            print("Initializing joystick...")
            pygame.joystick.init()
            self.connectedJoysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
            print("{} joysticks found and initialized.".format(pygame.joystick.get_count()))

        if not controller.get_init():
            #Find first joystick that can be initialized as a controller, set it as the primary and break
            print("Initializing joysticks as controller...")
            controller.init()
            for joystick in self.connectedJoysticks:
                if controller.is_controller(joystick.get_id()):
                    print("\tJoystick {} detected as controller.\n\t(Name: {})".format(joystick.get_id(), joystick.get_name()))
                    print("\tSetting as primary...")
                    self.primaryController = controller.Controller(joystick.get_id())
                    print("Done!")
                    break

    def getLeftY(self):
        pygame.event.get()
        raw_val = self.primaryController.get_axis(pygame.CONTROLLER_AXIS_LEFTY)
        return self.clampAxisRange(raw_val)

    def getRightY(self):
        pygame.event.get()
        raw_val = self.primaryController.get_axis(pygame.CONTROLLER_AXIS_RIGHTY)
        return self.clampAxisRange(raw_val)

    def clampAxisRange(self, val):
        #Figure out how 'wide' default axis range is
        defAxisRange = self.JOYSTICK_AXIS_MAX - self.JOYSTICK_AXIS_MIN

        #For clarity
        convertedRange = 1.0 - (-1.0)

        scaledValue = float(val - self.JOYSTICK_AXIS_MIN) / float(defAxisRange)
        scaledValue = -1.0 + (scaledValue * convertedRange)

        #Round scaledValue to 1 decimal place to counteract joystick drift and flip it so that up on the joystick is positive
        return -1.0 * round(scaledValue, 1)

class Rover:
    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    def connectToRover(self, host, port):
        self.sock.connect((host,port))
        #print("Success!")

    def calcByteArray(self, axisVals):
        '''
        Interpret and format stickAxes list into bytearray suitable for sending to the rover.
        NOTE: reversing of wheel direction due to the side of the rover it is on is handled by the rover itself!!!
        DATA FORMAT:
        i=0 : forward/backward control (0x0=forward, 0xff=backwards)
        i=1 : value 0-255 (speed)
        i=2 : forward/backward control (0x0=forward, 0xff=backwards)
        i=3 : value 0-255 (speed)
        '''

        returnVal = []
        for i in range(0,len(axisVals)):
            if axisVals[i] < 0:
                axisVals[i] *= -1 #convert negative value to positive
                returnVal.append(255) #assign 'r' character to denote negative input
            else:
                returnVal.append(0)
            returnVal.append(int(axisVals[i] * 255)) #Constrain input values between 0-255
        #print("FIXED? {}".format(returnVal))
        return bytearray(returnVal)

    def sendControlData(self, data):
        totalsent = 0
        while totalsent < len(data):
            sent = self.sock.send(data[totalsent:])
            if sent == 0:
                raise RuntimeError("Socket connection broken!")
            totalsent += sent

    def closeSocket(self):
        self.sock.close()


if __name__ == "__main__":
    IP = '127.0.0.1'
    PORT = 2002
    DEBUG = True  #Print axis position and bytearray on clientside

    try:
        myClient = Rover()
    except IOError:
        myClient.closeSocket()
        sys.exit(1)

    print("Attempting to connect to rover...")
    try:
        myClient.connectToRover(IP, PORT)
        print("Success! (TCP connection on {}:{})".format(IP, PORT))
    except ConnectionRefusedError:
        myClient.closeSocket()
        print("Could not connect to Rover. (Is the server running?)")
        sys.exit(1)

    Controller = Gamepad()
    clock = pygame.time.Clock()
    pygame.init()

    print("\nSending control data to Rover.\n...rove on, space buggy...")
    while True:

        axisList = [Controller.getLeftY(), Controller.getRightY()]
        axesAsBytes = myClient.calcByteArray(axisList)
        if DEBUG:
            print("X: {}, Y: {}\n{}".format(axisList[0], axisList[1], axesAsBytes))

        myClient.sendControlData(axesAsBytes)
        clock.tick(60) #Send updates 60 times per second
