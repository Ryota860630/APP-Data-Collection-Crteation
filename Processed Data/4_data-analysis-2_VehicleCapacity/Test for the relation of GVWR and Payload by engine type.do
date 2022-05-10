/*_//_//_//_//_//_//_//_//_//_//_//_//
Test for significant difference between gross weight (GVWR)
 and Payload between ICEV and EV
//_//_//_//_//_//_//_//_//_//_//_//_*/

clear all
cap log close
set more off

cd "C:\Users\rabe8\OneDrive\ドキュメント\留学全般\14. APP\2) WINTER 298B-C Applied Policy Project Ⅱ\Data Collection\Vehicle Data"

import excel "Sample Vehicles.xlsx", sheet("sample vehicle list") firstrow clear
browse

tab Type, gen(type_id)
tab EngineType, gen(engine_id)

rename type_id1 type_cv
rename type_id2 type_ldt
rename type_id3 type_mdt
rename type_id4 type_sv

destring CargoCapacityft3, replace force

gen class=1 if GVWRlbs < 6000
replace class=2 if GVWRlbs >= 6000
replace class=3 if GVWRlbs >= 10000
replace class=4 if GVWRlbs >= 14000
replace class=5 if GVWRlbs >= 16000
replace class=6 if GVWRlbs >= 19500
replace class=7 if GVWRlbs >= 26000
replace class=8 if GVWRlbs >= 33000

rename engine_id1 engine_ev
drop engine_id2

reg Payloadlbs GVWRlbs if engine_ev==1
reg Payloadlbs GVWRlbs if engine_ev==0

ttesti 21 .7272206 .0550154 34 .837719 .7352556

tabulate class, sum(GVWRlbs)
tabulate class, sum(Payloadlbs)

iebaltab GVWRlbs Payloadlbs, ///
    grpvar(class) save("balancetable.xlsx") replace grpcodes 