#!/usr/bin/env python
# coding: utf-8

# Author: Matthew Forbes
# Date: May 12th, 2022
# ZEDZ Shipment Model for APP
# 
# The following code produces estimates for the total driving distance conducted by delivery vehicles in the City of Santa Monica. It also produces estimates on how these driving distances change when different ZEDZ policies are imposed, using the boundaries of the voluntary-ZEDZ that is currently being implemented. 
# 
# This model is based on "Application of an empirical multi-agent model for urban goods transport to analyze impacts of zero emission zones in The Netherlands" by Michiel de Bok, Lorant Tavasszy, and Sebastiaan Thoen: https://www.sciencedirect.com/science/article/pii/S0967070X19307383. The model contains three main parts: shipment synthesizer, tour formation, and network assignment.
# 
# The first part, shipment synthesizer, is tasked with generating a dataframe of possible shipments that could plausibly occur on an average day. This dataframe contains the following for each generated shipment:
# ● The name and location of the sender;
# ● The name and location of the receiver;
# ● The company that is conducting this shipment
# 
# The second section, tour formation, is concerned with estimating the number of shipments contained in a single shipment route and then grouping these shipments together (i.e. can multiple shipments be completed in a single tour of a shipment vehicle, and if so which shipments are likely to be grouped together).
# 
# The third section, network assignment, attempts to predict the potential routes that vehicles will take to complete these tours. These estimates are derived simply by mapping the shortest path from the sender location that connects all recipient locations.
# 
# Inputs (these need to be in your working directory)(author: Ryota Abe):
# - "consumer_nodes edited.csv"
# - "depot_nodes edited.csv"
# - "Entire Nodes.xlsx"
# - "consumer_nodes_new.csv"
# - "depot-x_arccs.xlsx" with x being 1 through 16
# 
# Outputs:
# - "FinalResults - status quo dist.xlsx"
#     -the total distance driven in meters by each company and in total under no policy
# - "FinalResults - mandatory ZEDZ dist.xlsx"
#     -the total distance driven in meters by each company and in total under a mandatory ZEDZ policy
# - "FinalResults - status quo tours.xlsx"
#     -the number of vehicle tours conducted by each company and in total under no policy
# - "FinalResults - mandatory ZEDZ tours.xlsx"
#     -the number of vehicle tours conducted by each company and in total under a mandatory ZEDZ policy
# - "FinalResults - status quo vehicles.xlsx"
#     -the distance driven by tour and vehicle under no policy
# - "FinalResults - mandatory ZEDZ vehicles.xlsx"
#     -the distance driven by tour and vehicle under a mandatory ZEDZ policy
# 
# *Model description taken from our APP report

# In[1]:


#Import Statements
import pandas as pd 
import numpy as np
import random


# In[2]:


#Import consumer nodes
consumer_nodes = pd.read_csv("consumer_nodes edited.csv")
consumer_nodes


# In[3]:


#import logistic nodes
logistic_nodes = pd.read_csv("depot_nodes edited.csv")
logistic_nodes


# In[4]:


#Import depot arcs
depot_1 = pd.read_excel("depot-1_arccs.xlsx")
depot_2 = pd.read_excel("depot-2_arcs.xlsx")
depot_3 = pd.read_excel("depot-3_arcs.xlsx")
depot_4 = pd.read_excel("depot-4_arccs.xlsx")
depot_5 = pd.read_excel("depot-5_arccs.xlsx")
depot_6 = pd.read_excel("depot-6_arccs.xlsx")
depot_7 = pd.read_excel("depot-7_arccs.xlsx")
depot_8 = pd.read_excel("depot-8_arccs.xlsx")
depot_9 = pd.read_excel("depot-9_arccs.xlsx")
depot_10 = pd.read_excel("depot-10_arccs.xlsx")
depot_11 = pd.read_excel("depot-11_arccs.xlsx")
depot_12 = pd.read_excel("depot-12_arccs.xlsx")
depot_13 = pd.read_excel("depot-13_arccs.xlsx")
depot_14 = pd.read_excel("depot-14_arccs.xlsx")
depot_15 = pd.read_excel("depot-15_arccs.xlsx")
depot_16 = pd.read_excel("depot-16_arccs.xlsx")


# In[5]:


#Merge depot dataframes together
depot_arcs = pd.concat([depot_1, depot_2, depot_3, depot_4, depot_5, depot_6, depot_7, depot_8, depot_9, depot_10, depot_11, depot_12, depot_13, depot_14, depot_15, depot_16])
depot_arcs


# In[6]:


#Import Entire Nodes dataset
entire_nodes = pd.read_excel("Entire Nodes.xlsx")
entire_nodes


# <font size="5">Part I: Shipment Synthesizer</font>

# In[1]:


#Part 1.1: Depot Proportions
#This part declares the proportions of shipments that originate from each logistic depot

depots = logistic_nodes["depot_id"]
depot_share = logistic_nodes["depot_share"]

#Share of shipments that originate from each company (data from APP report)
company_share = [0.38, 0.24, 0.21, 0.17]
company_names = ["USPS", "UPS", "Amazon Logistics", "FedEx"]

parcels_per_day = pd.read_csv("consumer_nodes_new.csv")
parcels_per_day = parcels_per_day["parcel_delivered(#/day)"].tolist()
parcels_per_day = [round(num) for num in parcels_per_day]


# In[9]:


#Part 1.2: Generate Shipments

#The list of consumer node IDs
consumer_ids = consumer_nodes["street_id"]

#Dataframe that will ultimately contain all shipment data
shipment_df = pd.DataFrame( columns = [ "Receiver", "Receiver_ID", "Receiver Lat", "Receiver Lon", "Receiver_ZEDZ", "Sender", "Sender_ID", "Sender Lat", "Sender Lon", "Sender_ZEDZ"])

#Inputs a consumer node, and outputs the appropriate depot based on the company share proportions and the nearest depots to the consumer node.
def which_sender(consumer_id):
    the_consumer = consumer_nodes.iloc[consumer_id]
    the_business = np.random.choice( company_names, 1, p = company_share)
    if the_business[0] == "USPS":
        return the_consumer["USPS_ID"]
    if the_business[0] == "UPS":
        return the_consumer["UPS_ID"]
    if the_business[0] == "Amazon Logistics":
        return the_consumer["Amazon_ID"]
    if the_business[0] == "FedEx":
        return the_consumer["FedEx_ID"]
    
#Copy of consumer_node Dataframe
num_shipments = consumer_nodes

#Combines consumer and depot node information into the shipment_df dataframe, and selects appropriate sender depot for shipment to each node.
for i in range(len(consumer_ids)):
    ship_per_node =  parcels_per_day[i]
    for j in range(ship_per_node):
        receiver = consumer_nodes.iloc[i]
        sender_id = which_sender(i)
        sender = logistic_nodes.loc[logistic_nodes["depot_id"] == sender_id]

        receiver_id = receiver["street_id"]
        receiver_lat = receiver["latitude"]
        receiver_lon = receiver["longitude"]
        receiver_name = receiver["street_address"]
        rec_ZEDZ = receiver["ZEDZ(inside =1)"]

        sender_name = sender.iloc[0]["logistics_company_name"]
        sender_lat = sender.iloc[0]["depot_latitude"]
        sender_lon = sender.iloc[0]["depot_longitude"]
        sen_ZEDZ = sender.iloc[0]["ZEDZ(inside =1)"]
    
        shipment_df.loc[len(shipment_df.index)] = [receiver_name, receiver_id, receiver_lat, receiver_lon, rec_ZEDZ, sender_name, sender_id, sender_lat, sender_lon, sen_ZEDZ]
    




#Calculates the distance between each consumer node and its depot
ship_dist = []
for i in range(shipment_df[shipment_df.columns[0]].count()):
    the_shipment = shipment_df.iloc[[i]]
    the_ship_id = the_shipment.iloc[0]["Receiver_ID"]
    the_depot_id = the_shipment.iloc[0]["Sender_ID"]
    #Get the Entire_nodes ID for the receiver
    rec_node = entire_nodes[entire_nodes['street_id'] == the_ship_id]
    receiver_entire_ID = rec_node.iloc[0]["ID"]
    #Get the Entire_nodes ID for the sender
    sen_node = entire_nodes[entire_nodes["depot_id"] == the_depot_id ]
    sender_entire_ID = sen_node.iloc[0]["ID"]

    
    poss_depo_arcs = depot_arcs[depot_arcs['origin_id'] == sender_entire_ID]
    the_arc = poss_depo_arcs[poss_depo_arcs['destination_id'] == receiver_entire_ID]
    the_arc_dist = the_arc.iloc[0]['Distance in meter']
    
    ship_dist.append(the_arc_dist)

#Adds distances to shipment_df
shipment_df["Distance"] = ship_dist
 
shipment_df


# <font size="5">Part II: Tour Formation + Part III: Network Assignment</font>
# 
# The Tour Formation section groups shipments together into "tours", which are groups of shipments that are completed by a single vehicle before having to return to the depot. The basis of this section comes from this Thoen et al. 2020 paper, which is also used in the de Bok paper: https://reader.elsevier.com/reader/sd/pii/S1366554520306402?token=94FFE679DDC95AB4588FD05E915EF54B466EA50544AAD164F8C79AFFB3D97B92F41DC853C84CBE6E1BFC66821C332BA8&originRegion=us-east-1&originCreation=20220214151704
# 
# This grouping is conducted in such a way that the tour is already arranged in an optimal way, also satisfying Part III.

# In[10]:


#Tours without ZEDZ

UPS_tours = []
Amazon_tours = []
USPS_tours = []
FedEx_tours = []
#Our analysis found that diesel vehicles can carry 30 shipments before having to return to the depot
stops_per_vehicle = 30
max_dist = 20000000000

UPS_shipments = shipment_df.loc[shipment_df["Sender"] == "UPS"]
Amazon_shipments = shipment_df.loc[shipment_df["Sender"] == "Amazon Logistics"]
USPS_shipments = shipment_df.loc[shipment_df["Sender"] == "USPS"]
FedEx_shipments = shipment_df.loc[shipment_df["Sender"] == "FedEx"]

#Calculates the Euclidian distance between two locations
def calc_dist(A_lat, A_lon, B_lat, B_lon):
    dist = ((((A_lon - B_lon )**2) + ((A_lat - B_lat)**2) )**0.5)
    return dist

#Returns the actual driving distance between two locations
def calc_dist_nodes(A_ID, B_ID):
    #convert A_ID to its entire_node_ID
    A_node = entire_nodes[entire_nodes['street_id'] == A_ID]
    A_entire_ID = A_node.iloc[0]["ID"]
    
    #convert B_ID to its entire_node_ID
    B_node = entire_nodes[entire_nodes['street_id'] == B_ID]
    B_entire_ID = B_node.iloc[0]["ID"]
    
    poss_depo_arcs = depot_arcs[depot_arcs['origin_id'] == A_entire_ID]
    the_arc = poss_depo_arcs[poss_depo_arcs['destination_id'] == B_entire_ID]
    the_arc_dist = the_arc.iloc[0]['Distance in meter']
    return the_arc_dist

#The following functions generate a list of dataframes for each company.
#Each dataframe in these lists represent a single tour.
def UPS_tour_formation():
    remaining_shipments = pd.DataFrame.copy(UPS_shipments)
    tour_df = pd.DataFrame( columns = [ "Receiver", "Receiver_ID", "Receiver Lat", "Receiver Lon", "Receiver_ZEDZ", "Sender", "Sender_ID", "Sender Lat", "Sender Lon", "Sender_ZEDZ"])
    for i in range(remaining_shipments[remaining_shipments.columns[0]].count()):
        if len(remaining_shipments.index) == 0:
            break
        if len(tour_df) < stops_per_vehicle:
            if len(tour_df) == 0:
                the_shipment = remaining_shipments.iloc[:1]
                the_ship_id = the_shipment.iloc[0]["Receiver_ID"]
                remaining_shipments = remaining_shipments[remaining_shipments["Receiver_ID"] != the_ship_id]
                tour_df = pd.concat([tour_df, the_shipment], ignore_index = True)
                tour_df.reset_index()
            else:
                starting_lat = tour_df.iloc[0]["Receiver Lat"]
                starting_lon = tour_df.iloc[0]["Receiver Lon"]
                starting_ID = tour_df.iloc[0]["Receiver_ID"]
                min_dist = 1000000
                for k in range(len(remaining_shipments)):
                    q = remaining_shipments.iloc[[k]]
                    k_lat = q.iloc[0]["Receiver Lat"]
                    k_lon = q.iloc[0]["Receiver Lon"]
                    k_ID = q.iloc[0]["Receiver_ID"]
                    the_dist = calc_dist_nodes(starting_ID, k_ID)
                    if the_dist < min_dist:
                        the_chosen = q
                        min_dist = the_dist
                tour_df = pd.concat([tour_df, the_chosen], ignore_index = True)
                the_ship_id = the_chosen.iloc[0]["Receiver_ID"]
                remaining_shipments = remaining_shipments[remaining_shipments["Receiver_ID"] != the_ship_id]
                
        else:
            UPS_tours.append(tour_df)
            tour_df = pd.DataFrame( columns = [ "Receiver", "Receiver_ID", "Receiver Lat", "Receiver Lon", "Receiver_ZEDZ", "Sender", "Sender_ID", "Sender Lat", "Sender Lon", "Sender_ZEDZ"])
            if len(remaining_shipments.index) > 0:
                the_shipment = remaining_shipments.iloc[[0]]
                the_ship_id = the_shipment.iloc[0]["Receiver_ID"]
                remaining_shipments = remaining_shipments[remaining_shipments["Receiver_ID"] != the_ship_id]
                tour_df = pd.concat([tour_df, the_shipment], ignore_index = True)
    if len(tour_df.index) > 0:
        UPS_tours.append(tour_df)
        
def Amazon_tour_formation():
    remaining_shipments = pd.DataFrame.copy(Amazon_shipments)
    tour_df = pd.DataFrame( columns = [ "Receiver", "Receiver_ID", "Receiver Lat", "Receiver Lon", "Receiver_ZEDZ", "Sender", "Sender_ID", "Sender Lat", "Sender Lon", "Sender_ZEDZ"])
    for i in range(remaining_shipments[remaining_shipments.columns[0]].count()):
        if len(remaining_shipments.index) == 0:
            break
        if len(tour_df) < stops_per_vehicle:
            if len(tour_df) == 0:
                the_shipment = remaining_shipments.iloc[:1]
                the_ship_id = the_shipment.iloc[0]["Receiver_ID"]
                remaining_shipments = remaining_shipments[remaining_shipments["Receiver_ID"] != the_ship_id]
                tour_df = pd.concat([tour_df, the_shipment], ignore_index = True)
                tour_df.reset_index()
            else:
                starting_lat = tour_df.iloc[0]["Receiver Lat"]
                starting_lon = tour_df.iloc[0]["Receiver Lon"]
                starting_ID = tour_df.iloc[0]["Receiver_ID"]
                min_dist = 1000000
                for k in range(len(remaining_shipments)):
                    q = remaining_shipments.iloc[[k]]
                    k_lat = q.iloc[0]["Receiver Lat"]
                    k_lon = q.iloc[0]["Receiver Lon"]
                    k_ID = q.iloc[0]["Receiver_ID"]
                    the_dist = calc_dist_nodes(starting_ID, k_ID)
                    if the_dist < min_dist:
                        the_chosen = q
                        min_dist = the_dist
                tour_df = pd.concat([tour_df, the_chosen], ignore_index = True)
                the_ship_id = the_chosen.iloc[0]["Receiver_ID"]
                remaining_shipments = remaining_shipments[remaining_shipments["Receiver_ID"] != the_ship_id]
        else:
            Amazon_tours.append(tour_df)
            tour_df = pd.DataFrame( columns = [ "Receiver", "Receiver_ID", "Receiver Lat", "Receiver Lon", "Receiver_ZEDZ", "Sender", "Sender_ID", "Sender Lat", "Sender Lon", "Sender_ZEDZ"])
            the_shipment = remaining_shipments.iloc[[0]]
            the_ship_id = the_shipment.iloc[0]["Receiver_ID"]
            remaining_shipments = remaining_shipments[remaining_shipments["Receiver_ID"] != the_ship_id]
            tour_df = pd.concat([tour_df, the_shipment], ignore_index = True)
    Amazon_tours.append(tour_df)
    
def USPS_tour_formation():
    remaining_shipments = pd.DataFrame.copy(USPS_shipments)
    tour_df = pd.DataFrame( columns = [ "Receiver", "Receiver_ID", "Receiver Lat", "Receiver Lon", "Receiver_ZEDZ", "Sender", "Sender_ID", "Sender Lat", "Sender Lon", "Sender_ZEDZ"])
    for i in range(remaining_shipments[remaining_shipments.columns[0]].count()):
        if len(remaining_shipments.index) == 0:
            break
        if len(tour_df) < stops_per_vehicle:
            if len(tour_df) == 0:
                the_shipment = remaining_shipments.iloc[:1]
                the_ship_id = the_shipment.iloc[0]["Receiver_ID"]
                remaining_shipments = remaining_shipments[remaining_shipments["Receiver_ID"] != the_ship_id]
                tour_df = pd.concat([tour_df, the_shipment], ignore_index = True)
                tour_df.reset_index()
            else:
                starting_lat = tour_df.iloc[0]["Receiver Lat"]
                starting_lon = tour_df.iloc[0]["Receiver Lon"]
                starting_ID = tour_df.iloc[0]["Receiver_ID"]
                min_dist = 1000000
                for k in range(len(remaining_shipments)):
                    q = remaining_shipments.iloc[[k]]
                    k_lat = q.iloc[0]["Receiver Lat"]
                    k_lon = q.iloc[0]["Receiver Lon"]
                    k_ID = q.iloc[0]["Receiver_ID"]
                    the_dist = calc_dist_nodes(starting_ID, k_ID)
                    if the_dist < min_dist:
                        the_chosen = q
                        min_dist = the_dist
                tour_df = pd.concat([tour_df, the_chosen], ignore_index = True)
                the_ship_id = the_chosen.iloc[0]["Receiver_ID"]
                remaining_shipments = remaining_shipments[remaining_shipments["Receiver_ID"] != the_ship_id]
        else:
            USPS_tours.append(tour_df)
            tour_df = pd.DataFrame( columns = [ "Receiver", "Receiver_ID", "Receiver Lat", "Receiver Lon", "Receiver_ZEDZ", "Sender", "Sender_ID", "Sender Lat", "Sender Lon", "Sender_ZEDZ"])
            the_shipment = remaining_shipments.iloc[[0]]
            the_ship_id = the_shipment.iloc[0]["Receiver_ID"]
            remaining_shipments = remaining_shipments[remaining_shipments["Receiver_ID"] != the_ship_id]
            tour_df = pd.concat([tour_df, the_shipment], ignore_index = True)
    USPS_tours.append(tour_df)
    
def FedEx_tour_formation():
    remaining_shipments = pd.DataFrame.copy(FedEx_shipments)
    tour_df = pd.DataFrame( columns = [ "Receiver", "Receiver_ID", "Receiver Lat", "Receiver Lon", "Receiver_ZEDZ", "Sender", "Sender_ID", "Sender Lat", "Sender Lon", "Sender_ZEDZ"])
    for i in range(remaining_shipments[remaining_shipments.columns[0]].count()):
        if len(remaining_shipments.index) == 0:
            break
        if len(tour_df) < stops_per_vehicle:
            if len(tour_df) == 0:
                the_shipment = remaining_shipments.iloc[:1]
                the_ship_id = the_shipment.iloc[0]["Receiver_ID"]
                remaining_shipments = remaining_shipments[remaining_shipments["Receiver_ID"] != the_ship_id]
                tour_df = pd.concat([tour_df, the_shipment], ignore_index = True)
                tour_df.reset_index()
            else:
                starting_lat = tour_df.iloc[0]["Receiver Lat"]
                starting_lon = tour_df.iloc[0]["Receiver Lon"]
                starting_ID = tour_df.iloc[0]["Receiver_ID"]
                min_dist = 1000000
                for k in range(len(remaining_shipments)):
                    q = remaining_shipments.iloc[[k]]
                    k_lat = q.iloc[0]["Receiver Lat"]
                    k_lon = q.iloc[0]["Receiver Lon"]
                    k_ID = q.iloc[0]["Receiver_ID"]
                    the_dist = calc_dist_nodes(starting_ID, k_ID)
                    if the_dist < min_dist:
                        the_chosen = q
                        min_dist = the_dist
                tour_df = pd.concat([tour_df, the_chosen], ignore_index = True)
                the_ship_id = the_chosen.iloc[0]["Receiver_ID"]
                remaining_shipments = remaining_shipments[remaining_shipments["Receiver_ID"] != the_ship_id]
        else:
            FedEx_tours.append(tour_df)
            tour_df = pd.DataFrame( columns = [ "Receiver", "Receiver_ID", "Receiver Lat", "Receiver Lon", "Receiver_ZEDZ", "Sender", "Sender_ID", "Sender Lat", "Sender Lon", "Sender_ZEDZ"])
            the_shipment = remaining_shipments.iloc[[0]]
            the_ship_id = the_shipment.iloc[0]["Receiver_ID"]
            remaining_shipments = remaining_shipments[remaining_shipments["Receiver_ID"] != the_ship_id]
            tour_df = pd.concat([tour_df, the_shipment], ignore_index = True)
    FedEx_tours.append(tour_df)
    


UPS_tour_formation()
Amazon_tour_formation()
USPS_tour_formation()
FedEx_tour_formation()



# In[11]:


#Tours with ZEDZ policy
UPS_Ztours = []
Amazon_Ztours = []
USPS_Ztours = []
FedEx_Ztours = []
UPS_nZtours = []
Amazon_nZtours = []
USPS_nZtours = []
FedEx_nZtours = []
max_dist = 200

UPS_Zshipments = shipment_df.loc[shipment_df["Sender"] == "UPS"]
UPS_Zshipments =  UPS_Zshipments[(UPS_Zshipments["Receiver_ZEDZ"] == 1) | (UPS_Zshipments["Sender_ZEDZ"] == 1)]
Amazon_Zshipments = shipment_df.loc[shipment_df["Sender"] == "Amazon Logistics"]
Amazon_Zshipments = Amazon_Zshipments[(Amazon_Zshipments["Receiver_ZEDZ"] == 1) | (Amazon_Zshipments["Sender_ZEDZ"] == 1)]
USPS_Zshipments = shipment_df.loc[shipment_df["Sender"] == "USPS"]
USPS_Zshipments = USPS_Zshipments[(USPS_Zshipments["Receiver_ZEDZ"] == 1) | (USPS_Zshipments["Sender_ZEDZ"] == 1)]
FedEx_Zshipments = shipment_df.loc[shipment_df["Sender"] == "FedEx"]
FedEx_Zshipments = FedEx_Zshipments[(FedEx_Zshipments["Receiver_ZEDZ"] == 1) | (FedEx_Zshipments["Sender_ZEDZ"] == 1)]

UPS_nZshipments = shipment_df.loc[shipment_df["Sender"] == "UPS"]
UPS_nZshipments =  UPS_nZshipments[(UPS_nZshipments["Receiver_ZEDZ"] == 0)]
UPS_nZshipments = UPS_nZshipments[(UPS_nZshipments["Sender_ZEDZ"] == 0)]
Amazon_nZshipments = shipment_df.loc[shipment_df["Sender"] == "Amazon Logistics"]
Amazon_nZshipments = Amazon_nZshipments[(Amazon_nZshipments["Receiver_ZEDZ"] == 0)]
Amazon_nZshipments = Amazon_nZshipments[(Amazon_nZshipments["Sender_ZEDZ"] == 0)]
USPS_nZshipments = shipment_df.loc[shipment_df["Sender"] == "USPS"]
USPS_nZshipments = USPS_nZshipments[(USPS_nZshipments["Receiver_ZEDZ"] == 0)]
USPS_nZshipments = USPS_nZshipments[(USPS_nZshipments["Sender_ZEDZ"] == 0)]
FedEx_nZshipments = shipment_df.loc[shipment_df["Sender"] == "FedEx"]
FedEx_nZshipments = FedEx_nZshipments[(FedEx_nZshipments["Receiver_ZEDZ"] == 0)]
FedEx_nZshipments = FedEx_nZshipments[(FedEx_nZshipments["Sender_ZEDZ"] == 0)]

tour_df = pd.DataFrame( columns = [ "Receiver", "Receiver_ID", "Receiver Lat", "Receiver Lon", "Receiver_ZEDZ", "Sender", "Sender_ID", "Sender Lat", "Sender Lon", "Sender_ZEDZ"])
new_tour_df = pd.DataFrame.copy(tour_df)

#EV vehicles can do 33 stops from our analysis (mainly because they don't have to refuel as often)
stops_per_vehicle = 33


#The following functions generate a list of dataframes for each company and for whether the vehicle enters the ZEDZ zone.
#Each dataframe in these lists represent a single tour.
#Functions with "Z" are EVs that must enter the zone, and "nZ" do not
def UPS_Ztour_formation():
    remaining_shipments = pd.DataFrame.copy(UPS_Zshipments)
    tour_df = pd.DataFrame( columns = [ "Receiver", "Receiver_ID", "Receiver Lat", "Receiver Lon", "Receiver_ZEDZ", "Sender", "Sender_ID", "Sender Lat", "Sender Lon", "Sender_ZEDZ"])
    for i in range(remaining_shipments[remaining_shipments.columns[0]].count()):
        if len(remaining_shipments.index) == 0:
            break
        if len(tour_df) < stops_per_vehicle:
            if len(tour_df) == 0:
                the_shipment = remaining_shipments.iloc[:1]
                the_ship_id = the_shipment.iloc[0]["Receiver_ID"]
                remaining_shipments = remaining_shipments[remaining_shipments["Receiver_ID"] != the_ship_id]
                tour_df = pd.concat([tour_df, the_shipment], ignore_index = True)
                tour_df.reset_index()
            else:
                starting_lat = tour_df.iloc[0]["Receiver Lat"]
                starting_lon = tour_df.iloc[0]["Receiver Lon"]
                starting_ID = tour_df.iloc[0]["Receiver_ID"]
                min_dist = 1000000
                for k in range(len(remaining_shipments)):
                    q = remaining_shipments.iloc[[k]]
                    k_lat = q.iloc[0]["Receiver Lat"]
                    k_lon = q.iloc[0]["Receiver Lon"]
                    k_ID = q.iloc[0]["Receiver_ID"]
                    the_dist = calc_dist_nodes(starting_ID, k_ID)
                    if the_dist < min_dist:
                        the_chosen = q
                        min_dist = the_dist
                tour_df = pd.concat([tour_df, the_chosen], ignore_index = True)
                the_ship_id = the_chosen.iloc[0]["Receiver_ID"]
                remaining_shipments = remaining_shipments[remaining_shipments["Receiver_ID"] != the_ship_id]
        else:
            UPS_Ztours.append(tour_df)
            tour_df = pd.DataFrame( columns = [ "Receiver", "Receiver_ID", "Receiver Lat", "Receiver Lon", "Receiver_ZEDZ", "Sender", "Sender_ID", "Sender Lat", "Sender Lon", "Sender_ZEDZ"])
            the_shipment = remaining_shipments.iloc[[0]]
            the_ship_id = the_shipment.iloc[0]["Receiver_ID"]
            remaining_shipments = remaining_shipments[remaining_shipments["Receiver_ID"] != the_ship_id]
            tour_df = pd.concat([tour_df, the_shipment], ignore_index = True)
    UPS_Ztours.append(tour_df)
    
#This variable is redefined since the vehicles are now diesel
stops_per_vehicle = 30

def UPS_nZtour_formation():
    remaining_shipments = pd.DataFrame.copy(UPS_nZshipments)
    tour_df = pd.DataFrame( columns = [ "Receiver", "Receiver_ID", "Receiver Lat", "Receiver Lon", "Receiver_ZEDZ", "Sender", "Sender_ID", "Sender Lat", "Sender Lon", "Sender_ZEDZ"])
    for i in range(remaining_shipments[remaining_shipments.columns[0]].count()):
        if len(remaining_shipments.index) == 0:
            break
        if len(tour_df) < stops_per_vehicle:
            if len(tour_df) == 0:
                the_shipment = remaining_shipments.iloc[:1]
                the_ship_id = the_shipment.iloc[0]["Receiver_ID"]
                remaining_shipments = remaining_shipments[remaining_shipments["Receiver_ID"] != the_ship_id]
                tour_df = pd.concat([tour_df, the_shipment], ignore_index = True)
                tour_df.reset_index()
            else:
                starting_lat = tour_df.iloc[0]["Receiver Lat"]
                starting_lon = tour_df.iloc[0]["Receiver Lon"]
                starting_ID = tour_df.iloc[0]["Receiver_ID"]
                min_dist = 1000000
                for k in range(len(remaining_shipments)):
                    q = remaining_shipments.iloc[[k]]
                    k_lat = q.iloc[0]["Receiver Lat"]
                    k_lon = q.iloc[0]["Receiver Lon"]
                    k_ID = q.iloc[0]["Receiver_ID"]
                    the_dist = calc_dist_nodes(starting_ID, k_ID)
                    if the_dist < min_dist:
                        the_chosen = q
                        min_dist = the_dist
                tour_df = pd.concat([tour_df, the_chosen], ignore_index = True)
                the_ship_id = the_chosen.iloc[0]["Receiver_ID"]
                remaining_shipments = remaining_shipments[remaining_shipments["Receiver_ID"] != the_ship_id]
        else:
            UPS_nZtours.append(tour_df)
            tour_df = pd.DataFrame( columns = [ "Receiver", "Receiver_ID", "Receiver Lat", "Receiver Lon", "Receiver_ZEDZ", "Sender", "Sender_ID", "Sender Lat", "Sender Lon", "Sender_ZEDZ"])
            the_shipment = remaining_shipments.iloc[[0]]
            the_ship_id = the_shipment.iloc[0]["Receiver_ID"]
            remaining_shipments = remaining_shipments[remaining_shipments["Receiver_ID"] != the_ship_id]
            tour_df = pd.concat([tour_df, the_shipment], ignore_index = True)
    UPS_nZtours.append(tour_df)
   
stops_per_vehicle = 33

def Amazon_Ztour_formation():
    remaining_shipments = pd.DataFrame.copy(Amazon_Zshipments)
    tour_df = pd.DataFrame( columns = [ "Receiver", "Receiver_ID", "Receiver Lat", "Receiver Lon", "Receiver_ZEDZ", "Sender", "Sender_ID", "Sender Lat", "Sender Lon", "Sender_ZEDZ"])
    for i in range(remaining_shipments[remaining_shipments.columns[0]].count()):
        if len(remaining_shipments.index) == 0:
            break
        if len(tour_df) < stops_per_vehicle:
            if len(tour_df) == 0:
                the_shipment = remaining_shipments.iloc[:1]
                the_ship_id = the_shipment.iloc[0]["Receiver_ID"]
                remaining_shipments = remaining_shipments[remaining_shipments["Receiver_ID"] != the_ship_id]
                tour_df = pd.concat([tour_df, the_shipment], ignore_index = True)
                tour_df.reset_index()
            else:
                starting_lat = tour_df.iloc[0]["Receiver Lat"]
                starting_lon = tour_df.iloc[0]["Receiver Lon"]
                starting_ID = tour_df.iloc[0]["Receiver_ID"]
                min_dist = 1000000
                for k in range(len(remaining_shipments)):
                    q = remaining_shipments.iloc[[k]]
                    k_lat = q.iloc[0]["Receiver Lat"]
                    k_lon = q.iloc[0]["Receiver Lon"]
                    k_ID = q.iloc[0]["Receiver_ID"]
                    the_dist = calc_dist_nodes(starting_ID, k_ID)
                    if the_dist < min_dist:
                        the_chosen = q
                        min_dist = the_dist
                tour_df = pd.concat([tour_df, the_chosen], ignore_index = True)
                the_ship_id = the_chosen.iloc[0]["Receiver_ID"]
                remaining_shipments = remaining_shipments[remaining_shipments["Receiver_ID"] != the_ship_id]
        else:
            Amazon_Ztours.append(tour_df)
            tour_df = pd.DataFrame( columns = [ "Receiver", "Receiver_ID", "Receiver Lat", "Receiver Lon", "Receiver_ZEDZ", "Sender", "Sender_ID", "Sender Lat", "Sender Lon", "Sender_ZEDZ"])
            the_shipment = remaining_shipments.iloc[[0]]
            the_ship_id = the_shipment.iloc[0]["Receiver_ID"]
            remaining_shipments = remaining_shipments[remaining_shipments["Receiver_ID"] != the_ship_id]
            tour_df = pd.concat([tour_df, the_shipment], ignore_index = True)
    Amazon_Ztours.append(tour_df)
   
stops_per_vehicle = 30

def Amazon_nZtour_formation():
    remaining_shipments = pd.DataFrame.copy(Amazon_nZshipments)
    tour_df = pd.DataFrame( columns = [ "Receiver", "Receiver_ID", "Receiver Lat", "Receiver Lon", "Receiver_ZEDZ", "Sender", "Sender_ID", "Sender Lat", "Sender Lon", "Sender_ZEDZ"])
    for i in range(remaining_shipments[remaining_shipments.columns[0]].count()):
        if len(remaining_shipments.index) == 0:
            break
        if len(tour_df) < stops_per_vehicle:
            if len(tour_df) == 0:
                the_shipment = remaining_shipments.iloc[:1]
                the_ship_id = the_shipment.iloc[0]["Receiver_ID"]
                remaining_shipments = remaining_shipments[remaining_shipments["Receiver_ID"] != the_ship_id]
                tour_df = pd.concat([tour_df, the_shipment], ignore_index = True)
                tour_df.reset_index()
            else:
                starting_lat = tour_df.iloc[0]["Receiver Lat"]
                starting_lon = tour_df.iloc[0]["Receiver Lon"]
                starting_ID = tour_df.iloc[0]["Receiver_ID"]
                min_dist = 1000000
                for k in range(len(remaining_shipments)):
                    q = remaining_shipments.iloc[[k]]
                    k_lat = q.iloc[0]["Receiver Lat"]
                    k_lon = q.iloc[0]["Receiver Lon"]
                    k_ID = q.iloc[0]["Receiver_ID"]
                    the_dist = calc_dist_nodes(starting_ID, k_ID)
                    if the_dist < min_dist:
                        the_chosen = q
                        min_dist = the_dist
                tour_df = pd.concat([tour_df, the_chosen], ignore_index = True)
                the_ship_id = the_chosen.iloc[0]["Receiver_ID"]
                remaining_shipments = remaining_shipments[remaining_shipments["Receiver_ID"] != the_ship_id]
        else:
            Amazon_nZtours.append(tour_df)
            tour_df = pd.DataFrame( columns = [ "Receiver", "Receiver_ID", "Receiver Lat", "Receiver Lon", "Receiver_ZEDZ", "Sender", "Sender_ID", "Sender Lat", "Sender Lon", "Sender_ZEDZ"])
            the_shipment = remaining_shipments.iloc[[0]]
            the_ship_id = the_shipment.iloc[0]["Receiver_ID"]
            remaining_shipments = remaining_shipments[remaining_shipments["Receiver_ID"] != the_ship_id]
            tour_df = pd.concat([tour_df, the_shipment], ignore_index = True)
    Amazon_nZtours.append(tour_df)
    
stops_per_vehicle = 33

def USPS_Ztour_formation():
    remaining_shipments = pd.DataFrame.copy(USPS_Zshipments)
    tour_df = pd.DataFrame( columns = [ "Receiver", "Receiver_ID", "Receiver Lat", "Receiver Lon", "Receiver_ZEDZ", "Sender", "Sender_ID", "Sender Lat", "Sender Lon", "Sender_ZEDZ"])
    for i in range(remaining_shipments[remaining_shipments.columns[0]].count()):
        if len(remaining_shipments.index) == 0:
            break
        if len(tour_df) < stops_per_vehicle:
            if len(tour_df) == 0:
                the_shipment = remaining_shipments.iloc[:1]
                the_ship_id = the_shipment.iloc[0]["Receiver_ID"]
                remaining_shipments = remaining_shipments[remaining_shipments["Receiver_ID"] != the_ship_id]
                tour_df = pd.concat([tour_df, the_shipment], ignore_index = True)
                tour_df.reset_index()
            else:
                starting_lat = tour_df.iloc[0]["Receiver Lat"]
                starting_lon = tour_df.iloc[0]["Receiver Lon"]
                starting_ID = tour_df.iloc[0]["Receiver_ID"]
                min_dist = 1000000
                for k in range(len(remaining_shipments)):
                    q = remaining_shipments.iloc[[k]]
                    k_lat = q.iloc[0]["Receiver Lat"]
                    k_lon = q.iloc[0]["Receiver Lon"]
                    k_ID = q.iloc[0]["Receiver_ID"]
                    the_dist = calc_dist_nodes(starting_ID, k_ID)
                    if the_dist < min_dist:
                        the_chosen = q
                        min_dist = the_dist
                tour_df = pd.concat([tour_df, the_chosen], ignore_index = True)
                the_ship_id = the_chosen.iloc[0]["Receiver_ID"]
                remaining_shipments = remaining_shipments[remaining_shipments["Receiver_ID"] != the_ship_id]
        else:
            USPS_Ztours.append(tour_df)
            tour_df = pd.DataFrame( columns = [ "Receiver", "Receiver_ID", "Receiver Lat", "Receiver Lon", "Receiver_ZEDZ", "Sender", "Sender_ID", "Sender Lat", "Sender Lon", "Sender_ZEDZ"])
            the_shipment = remaining_shipments.iloc[[0]]
            the_ship_id = the_shipment.iloc[0]["Receiver_ID"]
            remaining_shipments = remaining_shipments[remaining_shipments["Receiver_ID"] != the_ship_id]
            tour_df = pd.concat([tour_df, the_shipment], ignore_index = True)
    USPS_Ztours.append(tour_df)
    
stops_per_vehicle = 30

def USPS_nZtour_formation():
    remaining_shipments = pd.DataFrame.copy(USPS_nZshipments)
    tour_df = pd.DataFrame( columns = [ "Receiver", "Receiver_ID", "Receiver Lat", "Receiver Lon", "Receiver_ZEDZ", "Sender", "Sender_ID", "Sender Lat", "Sender Lon", "Sender_ZEDZ"])
    new_tour_df = pd.DataFrame.copy(tour_df)
    for i in range(remaining_shipments[remaining_shipments.columns[0]].count()):
        if len(remaining_shipments.index) == 0:
            break
        if len(tour_df) < stops_per_vehicle:
            if len(tour_df) == 0:
                the_shipment = remaining_shipments.iloc[:1]
                the_ship_id = the_shipment.iloc[0]["Receiver_ID"]
                remaining_shipments = remaining_shipments[remaining_shipments["Receiver_ID"] != the_ship_id]
                tour_df = pd.concat([tour_df, the_shipment], ignore_index = True)
                tour_df.reset_index()
            else:
                starting_lat = tour_df.iloc[0]["Receiver Lat"]
                starting_lon = tour_df.iloc[0]["Receiver Lon"]
                starting_ID = tour_df.iloc[0]["Receiver_ID"]
                min_dist = 1000000
                for k in range(len(remaining_shipments)):
                    q = remaining_shipments.iloc[[k]]
                    k_lat = q.iloc[0]["Receiver Lat"]
                    k_lon = q.iloc[0]["Receiver Lon"]
                    k_ID = q.iloc[0]["Receiver_ID"]
                    the_dist = calc_dist_nodes(starting_ID, k_ID)
                    if the_dist < min_dist:
                        the_chosen = q
                        min_dist = the_dist
                tour_df = pd.concat([tour_df, the_chosen], ignore_index = True)
                the_ship_id = the_chosen.iloc[0]["Receiver_ID"]
                remaining_shipments = remaining_shipments[remaining_shipments["Receiver_ID"] != the_ship_id]
        else:
            USPS_nZtours.append(tour_df)
            tour_df = pd.DataFrame( columns = [ "Receiver", "Receiver_ID", "Receiver Lat", "Receiver Lon", "Receiver_ZEDZ", "Sender", "Sender_ID", "Sender Lat", "Sender Lon", "Sender_ZEDZ"])
            the_shipment = remaining_shipments.iloc[[0]]
            the_ship_id = the_shipment.iloc[0]["Receiver_ID"]
            remaining_shipments = remaining_shipments[remaining_shipments["Receiver_ID"] != the_ship_id]
            tour_df = pd.concat([tour_df, the_shipment], ignore_index = True)
    USPS_nZtours.append(tour_df)
    
stops_per_vehicle = 33    

def FedEx_Ztour_formation():
    remaining_shipments = pd.DataFrame.copy(FedEx_Zshipments)
    tour_df = pd.DataFrame(columns = [ "Receiver", "Receiver_ID", "Receiver Lat", "Receiver Lon", "Receiver_ZEDZ", "Sender", "Sender_ID", "Sender Lat", "Sender Lon", "Sender_ZEDZ"] )
    for i in range(remaining_shipments[remaining_shipments.columns[0]].count()):
        if len(remaining_shipments.index) == 0:
            break
        if (len(tour_df)) < stops_per_vehicle:
            if len(tour_df) == 0:
                the_shipment = remaining_shipments.iloc[:1]
                the_ship_id = the_shipment.iloc[0]["Receiver_ID"]
                remaining_shipments = remaining_shipments[remaining_shipments["Receiver_ID"] != the_ship_id]
                tour_df = pd.concat([tour_df, the_shipment], ignore_index = True)
                tour_df.reset_index()
            else:
                starting_lat = tour_df.iloc[0]["Receiver Lat"]
                starting_lon = tour_df.iloc[0]["Receiver Lon"]
                starting_ID = tour_df.iloc[0]["Receiver_ID"]
                min_dist = 1000000
                for k in range(len(remaining_shipments)):
                    q = remaining_shipments.iloc[[k]]
                    k_lat = q.iloc[0]["Receiver Lat"]
                    k_lon = q.iloc[0]["Receiver Lon"]
                    k_ID = q.iloc[0]["Receiver_ID"]
                    the_dist = calc_dist_nodes(starting_ID, k_ID)
                    if the_dist < min_dist:
                        the_chosen = q
                        min_dist = the_dist
                tour_df = pd.concat([tour_df, the_chosen], ignore_index = True)
                the_ship_id = the_chosen.iloc[0]["Receiver_ID"]
                remaining_shipments = remaining_shipments[remaining_shipments["Receiver_ID"] != the_ship_id]
        else:
            FedEx_Ztours.append(tour_df)
            tour_df = pd.DataFrame( columns = [ "Receiver", "Receiver_ID", "Receiver Lat", "Receiver Lon", "Receiver_ZEDZ", "Sender", "Sender_ID", "Sender Lat", "Sender Lon", "Sender_ZEDZ"])
            the_shipment = remaining_shipments.iloc[[0]]
            the_ship_id = the_shipment.iloc[0]["Receiver_ID"]
            remaining_shipments = remaining_shipments[remaining_shipments["Receiver_ID"] != the_ship_id]
            tour_df = pd.concat([tour_df, the_shipment], ignore_index = True)
    FedEx_Ztours.append(tour_df)
    
    
stops_per_vehicle = 30    
    
def FedEx_nZtour_formation():
    remaining_shipments = pd.DataFrame.copy(FedEx_nZshipments)
    tour_df = pd.DataFrame( columns = [ "Receiver", "Receiver_ID", "Receiver Lat", "Receiver Lon", "Receiver_ZEDZ", "Sender", "Sender_ID", "Sender Lat", "Sender Lon", "Sender_ZEDZ"])
    for i in range(remaining_shipments[remaining_shipments.columns[0]].count()):
        if len(remaining_shipments.index) == 0:
            break
        if len(tour_df) < stops_per_vehicle:
            if len(tour_df) == 0:
                the_shipment = remaining_shipments.iloc[:1]
                the_ship_id = the_shipment.iloc[0]["Receiver_ID"]
                remaining_shipments = remaining_shipments[remaining_shipments["Receiver_ID"] != the_ship_id]
                tour_df = pd.concat([tour_df, the_shipment], ignore_index = True)
                tour_df.reset_index()
            else:
                starting_lat = tour_df.iloc[0]["Receiver Lat"]
                starting_lon = tour_df.iloc[0]["Receiver Lon"]
                starting_ID = tour_df.iloc[0]["Receiver_ID"]
                min_dist = 1000000
                for k in range(len(remaining_shipments)):
                    q = remaining_shipments.iloc[[k]]
                    k_lat = q.iloc[0]["Receiver Lat"]
                    k_lon = q.iloc[0]["Receiver Lon"]
                    k_ID = q.iloc[0]["Receiver_ID"]
                    the_dist = calc_dist_nodes(starting_ID, k_ID)
                    if the_dist < min_dist:
                        the_chosen = q
                        min_dist = the_dist
                tour_df = pd.concat([tour_df, the_chosen], ignore_index = True)
                the_ship_id = the_chosen.iloc[0]["Receiver_ID"]
                remaining_shipments = remaining_shipments[remaining_shipments["Receiver_ID"] != the_ship_id]
        else:
            FedEx_nZtours.append(tour_df)
            tour_df = pd.DataFrame( columns = [ "Receiver", "Receiver_ID", "Receiver Lat", "Receiver Lon", "Receiver_ZEDZ", "Sender", "Sender_ID", "Sender Lat", "Sender Lon", "Sender_ZEDZ"])
            the_shipment = remaining_shipments.iloc[[0]]
            the_ship_id = the_shipment.iloc[0]["Receiver_ID"]
            remaining_shipments = remaining_shipments[remaining_shipments["Receiver_ID"] != the_ship_id]
            tour_df = pd.concat([tour_df, the_shipment], ignore_index = True)
    FedEx_nZtours.append(tour_df)
    

    
UPS_Ztour_formation()
UPS_nZtour_formation()
Amazon_Ztour_formation()
Amazon_nZtour_formation()
USPS_Ztour_formation()
USPS_nZtour_formation()
FedEx_Ztour_formation()
FedEx_nZtour_formation()


# In[13]:


#Calculate Distances
#This section calculates the total vehicle miles driven under each scenario, company, and type of vehicle.

#Status Quo - No ZEDZ
UPS_dist = 0
for i in range(len(UPS_tours)):
    the_tour = UPS_tours[i]
    for j in range(the_tour[the_tour.columns[0]].count()):
        if j == 0: 
            UPS_dist = UPS_dist + the_tour.iloc[0]["Distance"]
        else:
            start_id = the_tour.iloc[j-1]["Receiver_ID"]
            end_id = the_tour.iloc[j]["Receiver_ID"]
            UPS_dist = UPS_dist + calc_dist_nodes(start_id, end_id)
Amazon_dist = 0
for i in range(len(Amazon_tours)):
    the_tour = Amazon_tours[i]
    for j in range(the_tour[the_tour.columns[0]].count()):
        if j == 0: 
            Amazon_dist = Amazon_dist + the_tour.iloc[0]["Distance"]
        else:
            start_id = the_tour.iloc[j-1]["Receiver_ID"]
            end_id = the_tour.iloc[j]["Receiver_ID"]
            Amazon_dist = Amazon_dist + calc_dist_nodes(start_id, end_id)
USPS_dist = 0
for i in range(len(USPS_tours)):
    the_tour = USPS_tours[i]
    for j in range(the_tour[the_tour.columns[0]].count()):
        if j == 0: 
            USPS_dist = USPS_dist + the_tour.iloc[0]["Distance"]
        else:
            start_id = the_tour.iloc[j-1]["Receiver_ID"]
            end_id = the_tour.iloc[j]["Receiver_ID"]
            USPS_dist = USPS_dist + calc_dist_nodes(start_id, end_id)
FedEx_dist = 0
for i in range(len(FedEx_tours)):
    the_tour = FedEx_tours[i]
    for j in range(the_tour[the_tour.columns[0]].count()):
        if j == 0: 
            FedEx_dist = FedEx_dist + the_tour.iloc[0]["Distance"]
        else:
            start_id = the_tour.iloc[j-1]["Receiver_ID"]
            end_id = the_tour.iloc[j]["Receiver_ID"]
            FedEx_dist = FedEx_dist + calc_dist_nodes(start_id, end_id) 
    
total_dist_Status_Quo = UPS_dist + Amazon_dist + USPS_dist + FedEx_dist
    
    
#Mandatory ZEDZ
#Diesel Meters
UPS_nZ_dist = 0
for i in range(len(UPS_nZtours)):
    the_tour = UPS_nZtours[i]
    for j in range(the_tour[the_tour.columns[0]].count()):
        if j == 0: 
            UPS_nZ_dist = UPS_nZ_dist + the_tour.iloc[0]["Distance"]
        else:
            start_id = the_tour.iloc[j-1]["Receiver_ID"]
            end_id = the_tour.iloc[j]["Receiver_ID"]
            UPS_nZ_dist = UPS_nZ_dist + calc_dist_nodes(start_id, end_id)
Amazon_nZ_dist = 0
for i in range(len(Amazon_nZtours)):
    the_tour = Amazon_nZtours[i]
    for j in range(the_tour[the_tour.columns[0]].count()):
        if j == 0: 
            Amazon_nZ_dist = Amazon_nZ_dist + the_tour.iloc[0]["Distance"]
        else:
            start_id = the_tour.iloc[j-1]["Receiver_ID"]
            end_id = the_tour.iloc[j]["Receiver_ID"]
            Amazon_nZ_dist = Amazon_nZ_dist + calc_dist_nodes(start_id, end_id)
USPS_nZ_dist = 0
for i in range(len(USPS_nZtours)):
    the_tour = USPS_nZtours[i]
    for j in range(the_tour[the_tour.columns[0]].count()):
        if j == 0: 
            USPS_nZ_dist = USPS_nZ_dist + the_tour.iloc[0]["Distance"]
        else:
            start_id = the_tour.iloc[j-1]["Receiver_ID"]
            end_id = the_tour.iloc[j]["Receiver_ID"]
            USPS_nZ_dist = USPS_nZ_dist + calc_dist_nodes(start_id, end_id)
FedEx_nZ_dist = 0
for i in range(len(FedEx_nZtours)):
    the_tour = FedEx_nZtours[i]
    for j in range(the_tour[the_tour.columns[0]].count()):
        if j == 0: 
            FedEx_nZ_dist = FedEx_nZ_dist + the_tour.iloc[0]["Distance"]
        else:
            start_id = the_tour.iloc[j-1]["Receiver_ID"]
            end_id = the_tour.iloc[j]["Receiver_ID"]
            FedEx_nZ_dist = FedEx_nZ_dist + calc_dist_nodes(start_id, end_id)
    
total_dist_Man_Dies = FedEx_nZ_dist + USPS_nZ_dist + Amazon_nZ_dist + UPS_nZ_dist

#EV Meters
UPS_Z_dist = 0
for i in range(len(UPS_Ztours)):
    the_tour = UPS_Ztours[i]
    for j in range(the_tour[the_tour.columns[0]].count()):
        if j == 0: 
            UPS_Z_dist = UPS_Z_dist + the_tour.iloc[0]["Distance"]
        else:
            start_id = the_tour.iloc[j-1]["Receiver_ID"]
            end_id = the_tour.iloc[j]["Receiver_ID"]
            UPS_Z_dist = UPS_Z_dist + calc_dist_nodes(start_id, end_id)
Amazon_Z_dist = 0
for i in range(len(Amazon_Ztours)):
    the_tour = Amazon_Ztours[i]
    for j in range(the_tour[the_tour.columns[0]].count()):
        if j == 0: 
            Amazon_Z_dist = Amazon_Z_dist + the_tour.iloc[0]["Distance"]
        else:
            start_id = the_tour.iloc[j-1]["Receiver_ID"]
            end_id = the_tour.iloc[j]["Receiver_ID"]
            Amazon_Z_dist = Amazon_Z_dist + calc_dist_nodes(start_id, end_id)
USPS_Z_dist = 0
for i in range(len(USPS_Ztours)):
    the_tour = USPS_Ztours[i]
    for j in range(the_tour[the_tour.columns[0]].count()):
        if j == 0: 
            USPS_Z_dist = USPS_Z_dist + the_tour.iloc[0]["Distance"]
        else:
            start_id = the_tour.iloc[j-1]["Receiver_ID"]
            end_id = the_tour.iloc[j]["Receiver_ID"]
            USPS_Z_dist = USPS_Z_dist + calc_dist_nodes(start_id, end_id)
FedEx_Z_dist = 0
for i in range(len(FedEx_Ztours)):
    the_tour = FedEx_Ztours[i]
    for j in range(the_tour[the_tour.columns[0]].count()):
        if j == 0: 
            FedEx_Z_dist = FedEx_Z_dist + the_tour.iloc[0]["Distance"]
        else:
            start_id = the_tour.iloc[j-1]["Receiver_ID"]
            end_id = the_tour.iloc[j]["Receiver_ID"]
            FedEx_Z_dist = FedEx_Z_dist + calc_dist_nodes(start_id, end_id)
    
total_dist_Man_EV = UPS_Z_dist + Amazon_Z_dist + USPS_Z_dist + FedEx_Z_dist

total_dist_mandatory = total_dist_Man_Dies + total_dist_Man_EV


# In[14]:


#Calculate total tours

#Status Quo - No ZEDZ
UPS_tours_count = len(UPS_tours)

Amazon_tours_count = len(Amazon_tours)

USPS_tours_count = len(USPS_tours)

FedEx_tours_count = len(FedEx_tours)
    
total_tours_Status_Quo = UPS_tours_count + Amazon_tours_count + USPS_tours_count + FedEx_tours_count

#Mandatory ZEDZ
#Diesel tours
UPS_nZ_tours_count = len(UPS_nZtours)

Amazon_nZ_tours_count = len(Amazon_nZtours)

USPS_nZ_tours_count = len(USPS_nZtours)

FedEx_nZ_tours_count = len(FedEx_nZtours)

total_tours_Mand_Dies = UPS_nZ_tours_count + Amazon_nZ_tours_count + USPS_nZ_tours_count + FedEx_nZ_tours_count

#EV tours
UPS_Z_tours_count = len(UPS_Ztours) 

Amazon_Z_tours_count = len(Amazon_Ztours)

USPS_Z_tours_count = len(USPS_Ztours)

FedEx_Z_tours_count = len(FedEx_Ztours)

total_tours_Mand_EV = UPS_Z_tours_count  + Amazon_Z_tours_count + USPS_Z_tours_count + FedEx_Z_tours_count

total_tours_Mand = total_tours_Mand_Dies + total_tours_Mand_EV


# In[15]:


#Create dataframes of dist traveled

#status quo
status_quo = pd.DataFrame( columns = ["UPS_dist", "Amazon_dist", "USPS_dist", "FedEx_dist", "Total_dist" ])
status_quo["UPS_dist"] = [UPS_dist]
status_quo["Amazon_dist"] = [Amazon_dist]
status_quo["USPS_dist"] = [USPS_dist]
status_quo["FedEx_dist"] = [FedEx_dist]
status_quo["Total_dist"] = [total_dist_Status_Quo]


#mandatory ZEDZ
mandatory_ZEDZ = pd.DataFrame( columns = ["UPS_nZdist", "Amazon_nZdist", "USPS_nZdist", "FedEx_nZdist", "Total_nZdist", "UPS_Zdist", "Amazon_Zdist", "USPS_Zdist", "FedEx_Zdist", "Total_Zdist", "Total_dist" ])
mandatory_ZEDZ["UPS_nZdist"] = [UPS_nZ_dist]
mandatory_ZEDZ["Amazon_nZdist"] = [Amazon_nZ_dist]
mandatory_ZEDZ["USPS_nZdist"] = [USPS_nZ_dist]
mandatory_ZEDZ["FedEx_nZdist"] = [FedEx_nZ_dist]
mandatory_ZEDZ["Total_nZdist"] = [total_dist_Man_Dies]

mandatory_ZEDZ["UPS_Zdist"] = [UPS_Z_dist]
mandatory_ZEDZ["Amazon_Zdist"] = [Amazon_Z_dist]
mandatory_ZEDZ["USPS_Zdist"] = [USPS_Z_dist]
mandatory_ZEDZ["FedEx_Zdist"] = [FedEx_Z_dist]
mandatory_ZEDZ["Total_Zdist"] = [total_dist_Man_EV]

mandatory_ZEDZ["Total_dist"] = [total_dist_mandatory]

#Create dataframes of tours conducted
#status quo
status_quo_tours = pd.DataFrame( columns = ["UPS_tours", "Amazon_tours", "USPS_tours", "FedEx_tours", "Total_tours" ])
status_quo_tours["UPS_tours"] = [UPS_tours_count]
status_quo_tours["Amazon_tours"] = [Amazon_tours_count]
status_quo_tours["USPS_tours"] = [USPS_tours_count]
status_quo_tours["FedEx_tours"] = [FedEx_tours_count]
status_quo_tours["Total_tours"] = [total_tours_Status_Quo]

#mandatory ZEDZ
mandatory_ZEDZ_tours = pd.DataFrame( columns = ["UPS_nZ_tours", "Amazon_nZ_tours", "USPS_nZ_tours", "FedEx_nZ_tours", "Total_nZ_tours", "UPS_Z_tours", "Amazon_Z_tours", "USPS_Z_tours", "FedEx_Z_tours", "Total_Z_tours", "Total_tours" ])
mandatory_ZEDZ_tours["UPS_nZ_tours"] = [UPS_nZ_tours_count]
mandatory_ZEDZ_tours["Amazon_nZ_tours"] = [Amazon_nZ_tours_count]
mandatory_ZEDZ_tours["USPS_nZ_tours"] = [USPS_nZ_tours_count]
mandatory_ZEDZ_tours["FedEx_nZ_tours"] = [FedEx_nZ_tours_count]
mandatory_ZEDZ_tours["Total_nZ_tours"] = [total_tours_Mand_Dies]

mandatory_ZEDZ_tours["UPS_Z_tours"] = [UPS_Z_tours_count]
mandatory_ZEDZ_tours["Amazon_Z_tours"] = [Amazon_Z_tours_count]
mandatory_ZEDZ_tours["USPS_Z_tours"] = [USPS_Z_tours_count]
mandatory_ZEDZ_tours["FedEx_Z_tours"] = [FedEx_Z_tours_count]
mandatory_ZEDZ_tours["Total_Z_tours"] = [total_tours_Mand_EV]

mandatory_ZEDZ_tours["Total_tours"] = [total_tours_Mand]


# In[17]:


status_quo.to_excel('FinalResults - status quo dist.xlsx')


# In[18]:


mandatory_ZEDZ.to_excel('FinalResults - mandatory ZEDZ dist.xlsx')


# In[19]:


status_quo_tours.to_excel('FinalResults - status quo tours.xlsx')


# In[20]:


mandatory_ZEDZ_tours.to_excel('FinalResults - mandatory ZEDZ tours.xlsx')


# In[21]:


#Generate distance per tour
#status quo
status_quo_vehicles = pd.DataFrame(columns = ["Company", "Vehicle", "Tour", "Distance by tour" ])
company = []
vehicle = []
tour = []
Distance_tour = []
Distance_vehicle = []
vehicle_number = 1
tour_num = 0
j = 0
for i in range(len(UPS_tours)):
    tour_num += 1
    tour.append(tour_num)
    company.append("UPS")
    if j == 0:
        vehicle.append(vehicle_number)
        j = 1
    elif j == 1:
        j = 0
        vehicle.append(vehicle_number)
        if i != len(UPS_tours) - 1:
            vehicle_number += 1
    the_tour = UPS_tours[i]
    UPS_dist = 0
    for h in range(the_tour[the_tour.columns[0]].count()):
        if h == 0: 
            UPS_dist = UPS_dist + the_tour.iloc[0]["Distance"]
        else:
            start_id = the_tour.iloc[h-1]["Receiver_ID"]
            end_id = the_tour.iloc[h]["Receiver_ID"]
            UPS_dist = UPS_dist + calc_dist_nodes(start_id, end_id)
    Distance_tour.append(UPS_dist)
j = 0
vehicle_number += 1
for i in range(len(Amazon_tours)):
    tour_num += 1
    tour.append(tour_num)
    company.append("Amazon")
    if j == 0:
        vehicle.append(vehicle_number)
        j = 1
    elif j == 1:
        j = 0
        vehicle.append(vehicle_number)
        if i != len(Amazon_tours) - 1:
            vehicle_number += 1
    the_tour = Amazon_tours[i]
    Amazon_dist = 0
    for h in range(the_tour[the_tour.columns[0]].count()):
        if h == 0: 
            Amazon_dist = Amazon_dist + the_tour.iloc[0]["Distance"]
        else:
            start_id = the_tour.iloc[h-1]["Receiver_ID"]
            end_id = the_tour.iloc[h]["Receiver_ID"]
            Amazon_dist = Amazon_dist + calc_dist_nodes(start_id, end_id)
    Distance_tour.append(Amazon_dist)
    
j = 0
vehicle_number += 1
for i in range(len(USPS_tours)):
    tour_num += 1
    tour.append(tour_num)
    company.append("USPS")
    if j == 0:
        vehicle.append(vehicle_number)
        j = 1
    elif j == 1:
        j = 0
        vehicle.append(vehicle_number)
        if i != len(USPS_tours) - 1:
            vehicle_number += 1
    the_tour = USPS_tours[i]
    USPS_dist = 0
    for h in range(the_tour[the_tour.columns[0]].count()):
        if j == 0: 
            USPS_dist = USPS_dist + the_tour.iloc[0]["Distance"]
        else:
            start_id = the_tour.iloc[h-1]["Receiver_ID"]
            end_id = the_tour.iloc[h]["Receiver_ID"]
            USPS_dist = USPS_dist + calc_dist_nodes(start_id, end_id)
    Distance_tour.append(USPS_dist)

j = 0
vehicle_number += 1
for i in range(len(FedEx_tours)):
    tour_num += 1
    tour.append(tour_num)
    company.append("FedEx")
    if j == 0:
        vehicle.append(vehicle_number)
        j = 1
    elif j == 1:
        j = 0
        vehicle.append(vehicle_number)
        if i != len(FedEx_tours) - 1:
            vehicle_number += 1
    the_tour = FedEx_tours[i]
    FedEx_dist = 0
    for h in range(the_tour[the_tour.columns[0]].count()):
        if h == 0: 
            FedEx_dist = FedEx_dist + the_tour.iloc[0]["Distance"]
        else:
            start_id = the_tour.iloc[h-1]["Receiver_ID"]
            end_id = the_tour.iloc[h]["Receiver_ID"]
            FedEx_dist = FedEx_dist + calc_dist_nodes(start_id, end_id) 
    Distance_tour.append(FedEx_dist)

status_quo_vehicles["Company"] = company
status_quo_vehicles["Vehicle"] = vehicle
status_quo_vehicles["Tour"] = tour
status_quo_vehicles["Distance by tour"] = Distance_tour

temp = status_quo_vehicles.groupby(["Vehicle"]).sum()
temp = temp.rename(columns={"Distance by tour": "Distance by vehicle"})
temp = temp.drop(["Tour"], axis = 1)

status_quo_vehicles = pd.merge(status_quo_vehicles, temp, on = "Vehicle")


#Mandatory ZEDZ
mandatory_vehicles = pd.DataFrame(columns = ["Company", "Vehicle", "Tour", "Distance by tour", "EV" ])
company = []
vehicle = []
tour = []
Distance_tour = []
Distance_vehicle = []
EV = []
vehicle_number = 1
tour_num = 0
j = 0
for i in range(len(UPS_nZtours)):
    tour_num += 1
    tour.append(tour_num)
    EV.append(0)
    company.append("UPS")
    if j == 0:
        vehicle.append(vehicle_number)
        j = 1
    elif j == 1:
        j = 0
        vehicle.append(vehicle_number)
        if i != len(UPS_nZtours) - 1:
            vehicle_number += 1
    the_tour = UPS_nZtours[i]
    UPS_nZ_dist = 0
    for h in range(the_tour[the_tour.columns[0]].count()):
        if h == 0: 
            UPS_nZ_dist = UPS_nZ_dist + the_tour.iloc[0]["Distance"]
        else:
            start_id = the_tour.iloc[h-1]["Receiver_ID"]
            end_id = the_tour.iloc[h]["Receiver_ID"]
            UPS_nZ_dist = UPS_nZ_dist + calc_dist_nodes(start_id, end_id)
    Distance_tour.append(UPS_nZ_dist)
j = 0
vehicle_number += 1
for i in range(len(Amazon_nZtours)):
    tour_num += 1
    tour.append(tour_num)
    EV.append(0)
    company.append("Amazon")
    if j == 0:
        vehicle.append(vehicle_number)
        j = 1
    elif j == 1:
        j = 0
        vehicle.append(vehicle_number)
        if i != len(Amazon_nZtours) - 1:
            vehicle_number += 1
    the_tour = Amazon_nZtours[i]
    Amazon_nZ_dist = 0
    for h in range(the_tour[the_tour.columns[0]].count()):
        if h == 0: 
            Amazon_nZ_dist = Amazon_nZ_dist + the_tour.iloc[0]["Distance"]
        else:
            start_id = the_tour.iloc[h-1]["Receiver_ID"]
            end_id = the_tour.iloc[h]["Receiver_ID"]
            Amazon_nZ_dist = Amazon_nZ_dist + calc_dist_nodes(start_id, end_id)
    Distance_tour.append(Amazon_nZ_dist)
    
j = 0
vehicle_number += 1
for i in range(len(USPS_nZtours)):
    tour_num += 1
    tour.append(tour_num)
    EV.append(0)
    company.append("USPS")
    if j == 0:
        vehicle.append(vehicle_number)
        j = 1
    elif j == 1:
        j = 0
        vehicle.append(vehicle_number)
        if i != len(USPS_nZtours) - 1:
            vehicle_number += 1
    the_tour = USPS_nZtours[i]
    USPS_nZ_dist = 0 
    for h in range(the_tour[the_tour.columns[0]].count()):
        if h == 0: 
            USPS_nZ_dist = USPS_nZ_dist + the_tour.iloc[0]["Distance"]
        else:
            start_id = the_tour.iloc[h-1]["Receiver_ID"]
            end_id = the_tour.iloc[h]["Receiver_ID"]
            USPS_nZ_dist = USPS_nZ_dist + calc_dist_nodes(start_id, end_id)
    Distance_tour.append(USPS_nZ_dist)
    
j = 0
vehicle_number += 1
for i in range(len(FedEx_nZtours)):
    tour_num += 1
    tour.append(tour_num)
    EV.append(0)
    company.append("FedEx")
    if j == 0:
        vehicle.append(vehicle_number)
        j = 1
    elif j == 1:
        j = 0
        vehicle.append(vehicle_number)
        if i != len(FedEx_nZtours) - 1:
            vehicle_number += 1
    the_tour = FedEx_nZtours[i]
    FedEx_nZ_dist = 0 
    for h in range(the_tour[the_tour.columns[0]].count()):
        if h == 0: 
            FedEx_nZ_dist = FedEx_nZ_dist + the_tour.iloc[0]["Distance"]
        else:
            start_id = the_tour.iloc[h-1]["Receiver_ID"]
            end_id = the_tour.iloc[h]["Receiver_ID"]
            FedEx_nZ_dist = FedEx_nZ_dist + calc_dist_nodes(start_id, end_id)
    Distance_tour.append(FedEx_nZ_dist)
    
j = 0
vehicle_number += 1
for i in range(len(UPS_Ztours)):
    tour_num += 1
    tour.append(tour_num)
    company.append("UPS")
    EV.append(1)
    if j == 0:
        vehicle.append(vehicle_number)
        j = 1
    elif j == 1:
        j = 0
        vehicle.append(vehicle_number)
        if i != len(UPS_Ztours) - 1:
            vehicle_number += 1
    the_tour = UPS_Ztours[i]
    UPS_Z_dist = 0
    for h in range(the_tour[the_tour.columns[0]].count()):
        if h == 0: 
            UPS_Z_dist = UPS_Z_dist + the_tour.iloc[0]["Distance"]
        else:
            start_id = the_tour.iloc[h-1]["Receiver_ID"]
            end_id = the_tour.iloc[h]["Receiver_ID"]
            UPS_Z_dist = UPS_Z_dist + calc_dist_nodes(start_id, end_id)
    Distance_tour.append(UPS_Z_dist)
    
j = 0
vehicle_number += 1
for i in range(len(Amazon_Ztours)):
    tour_num += 1
    tour.append(tour_num)
    EV.append(1)
    company.append("Amazon")
    if j == 0:
        vehicle.append(vehicle_number)
        j = 1
    elif j == 1:
        j = 0
        vehicle.append(vehicle_number)
        if i != len(Amazon_Ztours) - 1:
            vehicle_number += 1
    the_tour = Amazon_Ztours[i]
    Amazon_Z_dist = 0
    for h in range(the_tour[the_tour.columns[0]].count()):
        if h == 0: 
            Amazon_Z_dist = Amazon_Z_dist + the_tour.iloc[0]["Distance"]
        else:
            start_id = the_tour.iloc[h-1]["Receiver_ID"]
            end_id = the_tour.iloc[h]["Receiver_ID"]
            Amazon_Z_dist = Amazon_Z_dist + calc_dist_nodes(start_id, end_id)
    Distance_tour.append(Amazon_Z_dist)

j = 0
vehicle_number += 1
for i in range(len(USPS_Ztours)):
    tour_num += 1
    tour.append(tour_num)
    company.append("USPS")
    EV.append(1)
    if j == 0:
        vehicle.append(vehicle_number)
        j = 1
    elif j == 1:
        j = 0
        vehicle.append(vehicle_number)
        if i != len(USPS_Ztours) - 1:
            vehicle_number += 1
    the_tour = USPS_Ztours[i]
    USPS_Z_dist = 0 
    for h in range(the_tour[the_tour.columns[0]].count()):
        if h == 0: 
            USPS_Z_dist = USPS_Z_dist + the_tour.iloc[0]["Distance"]
        else:
            start_id = the_tour.iloc[h-1]["Receiver_ID"]
            end_id = the_tour.iloc[h]["Receiver_ID"]
            USPS_Z_dist = USPS_Z_dist + calc_dist_nodes(start_id, end_id)
    Distance_tour.append(USPS_Z_dist)
    
j = 0
vehicle_number += 1
for i in range(len(FedEx_Ztours)):
    tour_num += 1
    tour.append(tour_num)
    EV.append(1)
    company.append("FedEx")
    if j == 0:
        vehicle.append(vehicle_number)
        j = 1
    elif j == 1:
        j = 0
        vehicle.append(vehicle_number)
        if i != len(FedEx_Ztours) - 1:
            vehicle_number += 1
    the_tour = FedEx_Ztours[i]
    FedEx_Z_dist = 0 
    for h in range(the_tour[the_tour.columns[0]].count()):
        if h == 0: 
            FedEx_Z_dist = FedEx_Z_dist + the_tour.iloc[0]["Distance"]
        else:
            start_id = the_tour.iloc[h-1]["Receiver_ID"]
            end_id = the_tour.iloc[h]["Receiver_ID"]
            FedEx_Z_dist = FedEx_Z_dist + calc_dist_nodes(start_id, end_id)
    Distance_tour.append(FedEx_Z_dist)
    
mandatory_vehicles["Company"] = company
mandatory_vehicles["Vehicle"] = vehicle
mandatory_vehicles["Tour"] = tour
mandatory_vehicles["Distance by tour"] = Distance_tour
mandatory_vehicles["EV"] = EV

temp = mandatory_vehicles.groupby(["Vehicle"]).sum()
temp = temp.rename(columns={"Distance by tour": "Distance by vehicle"})
temp = temp.drop(["Tour"], axis = 1)

mandatory_vehicles = pd.merge(mandatory_vehicles, temp, on = "Vehicle")

mandatory_vehicles = mandatory_vehicles.drop(["EV_y"], axis = 1)
mandatory_vehicles = mandatory_vehicles.rename(columns = {"EV_x": "EV"})


# In[24]:


status_quo_vehicles.to_excel("FinalResults - status quo vehicles.xlsx")


# In[25]:


mandatory_vehicles.to_excel("FinalResults - mandatory ZEDZ vehicles.xlsx")


# In[ ]:




