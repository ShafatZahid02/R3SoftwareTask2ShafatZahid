# R3SoftwareTask2ShafatZahid
The output.py file recieves the controller input and formats the data into the requested format of 4 bytes
 Rover uses "tank drive" control scheme.
    (Each controller axis independently controls both motors on its respective side). Turns are possible through differential steering
    Turning left is achieved by holding downwards on the left stick AND upwards on the right stick simultaneously.
    (Vice versa for turning right).
    Because of this, the data from the client only sends PWM speed for each SIDE of the rover, as well as their
    directions. (Forward/Reverse represented as 'f' and 'r' respectively).
    Therefore we must add a copy of each side's PWM speed byte to send to each individual motor. Sends updates at a rate of 60 times/second.
    The input.py file takes in input from the controller. 
    SDL2 controller converts native pygame joysticks into a GameController object standard with the SDL library.
    (https://wiki.libsdl.org/)
    Axis ranges therefore are between -32768 and 32767.
    Trigger axis ranges are between 0 and 32767 (they never return a negative value).
    (https://wiki.libsdl.org/SDL_GameControllerGetAxis)
    Therefore we must clamp these values between -1 and 1, where values that are negative are returned positive.
    however with the 'r' character along next to it to denote negative input.
    The SDL2 controller library allows for the usage of multiple controllers without having to alter the input.py code
    


https://user-images.githubusercontent.com/73914750/138623347-fd9e7c4d-a441-4e5e-a658-7c403363b9fd.mp4

