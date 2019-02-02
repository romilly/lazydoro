# Project journal for Lazydoro

## Saturday 02 February 2019

I didn't solder up cos I realised I can use a trinket m0, which will be smaller and cheaper.

And I can't solder today as I will get in Alice's way.

So today I'll carry on developing code, testing
1. with mocks
1. using the m0 express board

I will start by writing an e2e test script, and then build mocks that will allow copde to be
exercised by the script.

At the moment I am making the assumption that everything will be driven by an event loop with 
one-second ticks.
 
I'll need to mock
1. the Clock class
1. RGB LED
1. Buzzer and
1. ToF sensor.




## Thursday 31 January 2019

I've lost my code :(

Mu is great for beginners, but no version control!

Code is back, and working, and I have added a piezo buzzer: an LS03803 from CPC which
works off 3 v and is loud enough.

Tomorrow I will solder it onto a Perma-proto. It's shaping up to be a very nice project. 

## Monday 28 January 2019

I started the project and got the Adafruit ToF sensor working with an M0 Feather Express.




