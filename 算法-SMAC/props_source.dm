db=dameng
driver=dm.jdbc.driver.DmDriver
conn=jdbc:dm://localhost:5236
user=BENCHMARKSQL
password=123456789

warehouses=100
loadWorkers=100
#fileLocation=/data/tpccdata5000/
terminals=200
//To run specified transactions per terminal- runMins must equal zero
runTxnsPerTerminal=0
//To run for specified minutes- runTxnsPerTerminal must equal zero
runMins=10
//Number of total transactions per minute
limitTxnsPerMin=0

//Set to true to run in 4.x compatible mode. Set to false to use the
//entire configured database evenly.
terminalWarehouseFixed=true

//The following five values must add up to 100
newOrderWeight=45
paymentWeight=43
orderStatusWeight=4
deliveryWeight=4
stockLevelWeight=4