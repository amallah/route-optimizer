# route-optimizer


## Description

In May 2020, a friend and I were talking about an effort to deliver items to 120 parents in the area. The plan was to take a number of volunteer drivers and divide the list evenly and then ask the parents to deliver to their list.

Network optimization problems have always been interesting to me, since the days when GPS was a separate device you had to buy (or before that, you had to go to MapQuest and plot out your path and print it before you left the house) I was always trying to figure out the optimal way to get between two points and my friend had just delivered the ideal actual use case.

Randall Olson wrote an article 5 years earlier planning out the ideal way to visit the [ultimate US road trip](https://randalolson.com/2015/03/08/computing-the-optimal-road-trip-across-the-u-s/) and he used a genetic algorithm to optimize it. I thought that was a good application here. 

He wrote it as a [python notebook on git](https://github.com/rhiever/Data-Analysis-and-Machine-Learning-Projects/blob/master/optimal-road-trip/Computing%20the%20optimal%20road%20trip%20across%20the%20U.S..ipynb) so I quickly adapted it for this parental delivery mission.

### How it works

I highly recommend reading Dr. Olson's article, but here's my tldr of genetic algorithms in this specific context:

Each house is a gene. So, at the beginning, we randomly pick a bunch of houses for each driver. We then calculate the distance to time to drive between all those houses in the random order.




## Getting Started

### Dependencies

Use PIP to install these python libraries
* googlemaps
* itertools 
* numpy
* random
* dotenv

### Installing

You need 3 files:
drivers.tsv - the home address of each driver
waypoints.tsv - the home address of each recipient of items
.env - with a single environment variable GOOGLE_DISTANCE_MATRIX_KEY which is your [Google Distance Matrix API key](https://console.cloud.google.com/google/maps-apis/credentials)

I use google Distance Matrix API to precalculate the distances and time to drive for every pair of houses, this only has to be done once and is saved to a file called route_matrix.tsv. Subsequent runs read the file (if it exists). 120 addresses will generate almost 9000 calls, but as an experiment a single run is usually covered in the monthly billing credit. The scope of setting up Google Data Matrix API is beyond this readme.

### Executing program

Simply run optimize.py with the files in place, Every 1000 generations, it will output this
```
6206 Driver Garth, City, ST 22222: = 18 stops, 2:39:24
12110 Driver Court, Town, ST 12212: = 11 stops, 2:40:06
509 E Driver Ave, City, ST 12122: = 26 stops, 5:30:36
6006 Driver Place, City, ST 11111: = 13 stops, 2:00:50
5205 Driver Way, City, ST 11111: = 14 stops, 2:41:53
2105 Driver Court, Suburb, ST 11121: = 12 stops, 2:37:56
34 Driver Ct., Townville, ST 11111: = 14 stops, 2:33:18
8832 Driver Drive, City, ST 11111: = 15 stops, 2:37:32
24:21:35
```
We settled on optimizing total time as a priority and distributing the load as a lower weight

