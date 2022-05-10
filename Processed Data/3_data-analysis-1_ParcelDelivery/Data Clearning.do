/*_//_//_//_//_//_//_//_//_//_//_//_//
  APP 2022
  Data Collection
  Fleet DNA: Commercial Fleet Vehicle Operating Data
//_//_//_//_//_//_//_//_//_//_//_//_*/

clear all
cap log close
set more off

cd "C:\Users\rabe8\OneDrive\ドキュメント\留学全般\14. APP\2) WINTER 298B-C Applied Policy Project Ⅱ\Data Collection\Vehicle Data\Freet DNA"


import delimited using "data_for_fleet_dna_composite_data.csv"

keep class_id voc_id type_id fuel_id drive_id absolute_time_duration_hrs speed_data_duration_hrs driving_data_duration_hrs non_recorded_time_hrs total_average_speed total_stops stops_per_mile average_stop_duration

*drop not last-mile delivery
drop if voc_id == 5
drop if voc_id == 7
drop if voc_id == 8
drop if voc_id == 10
drop if voc_id == 11
drop if voc_id == 13
drop if voc_id == 15

*drop not last-mile delivery related type
drop if type_id == 3
drop if type_id == 5
drop if type_id == 7
drop if type_id == 8
drop if type_id == 9
drop if type_id == 10
drop if type_id == 13
drop if type_id == 14
drop if type_id == 16
drop if type_id == 17
drop if type_id == 18
drop if type_id == 21
drop if type_id == 23
drop if type_id == 26
drop if type_id == 27
drop if type_id == 30
drop if type_id == 33
drop if type_id == 34
drop if type_id == 35
drop if type_id == 36
drop if type_id == 37

tab type_id
tab class_id
tab voc_id
tab drive_id
tab fuel_id

gen DVMT = speed_data_duration_hrs * total_average_speed
gen Zero_driving_hours = speed_data_duration_hrs - driving_data_duration_hrs

// DVMT Histgram
hist DVMT, title("All delivery") xtitle("DVMT(mile/day)") ytitle(Density) ///
saving("hist_dvmt_all.gph")
hist DVMT if voc_id == 4, title("Parcel delivery") xtitle("DVMT(mile/day)") ytitle(Density) ///
saving("hist_dvmt_parcel.gph")

// driving_data_duration Histgram
hist driving_data_duration_hrs, title("All delivery") xtitle("Driving Duration(hours)") ytitle(Density) ///
saving("hist_ddurat_all.gph")
hist driving_data_duration_hrs if voc_id == 4, title("Parcel delivery") xtitle("Driving Duration(hours)") ytitle(Density) ///
saving("hist_ddurat_parcel.gph")

// zero_driving_data_duration Histgram
hist Zero_driving_hours, title("All delivery") xtitle("Zero Driving Duration(hours)") ytitle(Density) ///
saving("hist_zddurat_all.gph")
hist driving_data_duration_hrs if voc_id == 4, title("Parcel delivery") xtitle("Zero Driving Duration(hours)") ytitle(Density) ///
saving("hist_zddurat_parcel.gph")

// Total Stops Histgram
hist total_stops, title("All delivery") xtitle("Total Stops") ytitle(Density) ///
saving("hist_tstops_all.gph")
hist total_stops if voc_id == 4, title("Parcel delivery") xtitle("Total Stops") ytitle(Density) ///
saving("hist_tstops_parcel.gph")

// Graph Combine
graph combine "hist_dvmt_all.gph" "hist_dvmt_parcel.gph" ///
"hist_ddurat_all.gph" "hist_ddurat_parcel.gph" ///
"hist_zddurat_all.gph" "hist_zddurat_parcel.gph" ///
"hist_tstops_all.gph" "hist_tstops_parcel.gph", ///
xsize(5) ysize(8) cols(2) saving("histgram")

tab voc_id, sum(DVMT)
tab voc_id, sum(driving_data_duration_hrs)
tab voc_id, sum(total_average_speed)
tab voc_id, sum(average_stop_duration)
tab voc_id, sum(total_stops)

drop if voc_id!=4
tab class_id, sum(DVMT)

/*

forvalues i = 1/5{
	qui summarize absolute_time_duration_hrs if class_id ==  `i'
	display `i' ",  " r(N) ",  " r(mean) ",  " r(sd)
}
*/

/*
forvalues i = 1/5{
	qui summarize speed_data_duration_hrs if class_id ==  `i'
	display `i' ", " r(N) ", " r(mean) ", " r(sd)
}
*/

export delimited using "Driving Characteristics of Last Mile Trucks", replace
