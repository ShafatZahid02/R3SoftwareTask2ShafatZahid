import socket

def formatData(data):
    '''
    Rover uses "tank drive" control scheme.
    (Each controller axis independently controls both motors on its respective side).
    Turning left is achieved by holding downwards on the left stick AND upwards on the right stick simultaneously.
    (Vice versa for turning right).

    Because of this, the data from the client only sends PWM speed for each SIDE of the rover, as well as their
    directions. (Forward/Reverse represented as 0 and 255 respectively).
    Therefore we must add a copy of each side's PWM speed byte to send to each individual motor.
    '''
    if len(data) != 4:
        return None  #Return None if we did not receive all 4 bytes from client
    else:
        outputList = []

        leftSideDirection = "r" if data[0] == 255 else "f"
        rightSideDirection = "r" if data[2] == 255 else "f"
        leftSidePWM = str(data[1])
        rightSidePWM = str(data[3])
        leftSideOutput = leftSideDirection + leftSidePWM
        rightSideOutput = rightSideDirection + rightSidePWM

        outputList.append(leftSideOutput)
        outputList.append(leftSideOutput)
        outputList.append(rightSideOutput)
        outputList.append(rightSideOutput)
        return outputList

def outputList(data):
    '''
    Loop through and print each list element individually.
    This function only avoids the ugly default python printing of string lists, namely the wrapping of each
    element in ' characters.
    '''
    outputString = ""
    for element in data:
        outputString += '['
        outputString += element
        outputString += ']'

    print(outputString)

TCP_IP='127.0.0.1'
TCP_PORT = 2002
BUFFER_SIZE=4

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
print("Listening...")
s.listen(1)

conn, addr= s.accept()
print("Connection address:", addr)
while True:
    data = conn.recv(BUFFER_SIZE)
    if not data:
        print("Stopped receiving data.")
        break
    formattedData = formatData(data)
    if formattedData is not None:
        outputList(formattedData)
    else:
        print("Data incorrectly formatted.")
print("Socket closed.")
conn.close()
