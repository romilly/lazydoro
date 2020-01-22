# Project journal for Lazydoro

## Monday 28 January 2019

I started the project and got the Adafruit ToF sensor working with an M0 Feather Express.




## Thursday 31 January 2019

I've lost my code :(

Mu is great for beginners, but no version control!

Code is back, and working, and I have added a piezo buzzer: an LS03803 from CPC which
works off 3 v and is loud enough.

Tomorrow I will solder it onto a Perma-proto. It's shaping up to be a very nice project. 

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


## Monday 04 February 2019

I've soldered the trinket. 

Here's the pinout![Trinket m0 pinout](resources/images/adafruit/trinket-m0/adafruit_products_Adafruit_Trinket_M0.png)


## Wednesday 13 March 2019

Wow - over a month since I last worked on the project! This should show how clearly I captured intent :)


## Tuesday 21 January 2020

Lots of work not captured in the journal.

I now have a working lazydoro with a Pi zero, a Pimoroni Blinkt! led array, a buzzer and an adafruit VL53L0X sensor.

It uses an adafruit bonnet.

![lazy-zero](resources/images/lazydoro/lazy-zero-cropped.jpg)

## Wednesday 22 January 2020

Today I plan to extend the code to show how much of each time period has elapsed.

I'll need to refactor.

1. Encapsulate the Colour that's sent to a Led
1. Add an *intensity* that goes from 1 to 8.
1. For Blinkt!, use that as an offset along the strip of LEDs.

When I get around to re-instating the feather version intensity will actually control the brightness of the LED.

