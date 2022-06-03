Pseudo-empirical data was created from the following information.
-Overall demographics of the City of Santa Monica
-Each intersection in the City of Santa Monica
-Per capita parcel delivery demand for the entire United States
-Depot information for major courier companies (Amazon, USPS, UPS, FedEX) in the vicinity of the City of Santa Monica
-Information on FleetDNA's US freight delivery vehicles by NREL

The address of each node was converted into latitude and longitude information using the GoogleMaps Geocoding API, which was used as the node data.

From the latitude and longitude information of each node, the arc (actual travel distance) between each depot and consumer was calculated to create the arc data.

As fo 02/09/2022, by Ryota Abe


Added a dummy variable that indicates the result of the ZEDZ internal and external judgment.
In addition, I created arcs for depots-1 through 9.
I continue work on creating arcs that covers depot-10 to 16.
As fo 02/23/2022, by Ryota Abe


