import subprocess

from django.http import HttpResponse

class PropsTotalCommand():
    def __init__(self, props):

        # props.dm || props_table.dm
        self.content = """db=dameng
        driver=dm.jdbc.driver.DmDriver
        conn=jdbc:dm://localhost:5236
        user=BENCHMARKSQL
        password=123456789

        warehouses=100
        loadWorkers=200
        #fileLocation=/data/tpccdata5000/
        terminals=100
        //To run specified transactions per terminal- runMins must equal zero
        runTxnsPerTerminal=0
        //To run for specified minutes- runTxnsPerTerminal must equal zero
        runMins=1
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

        // Directory name to create for collecting detailed result data.
        // Comment this out to suppress.
        //resultDirectory=my_result_%tY-%tm-%td_%tH%tM%tS
        //osCollectorScript=./misc/os_collector_linux.py
        //osCollectorInterval=1
        //osCollectorSSHAddr=user@dbhost
        //osCollectorDevices=net_eth0 blk_sda
        """
        self.props = props        # benchmark参数表

    def update(self):
        # 更新benchmark参数
        self.content = self.content.replace("warehouses=100", f"warehouses={self.props.warehouses}")
        self.content = self.content.replace("loadWorkers=200", f"loadWorkers={self.props.loadWorkers}")
        self.content = self.content.replace("terminals=100", f"terminals={self.props.terminals}")
        self.content = self.content.replace("runTxnsPerTerminal=0",
                                            f"runTxnsPerTerminal={self.props.runTxnsPerTerminal}")
        self.content = self.content.replace("runMins=1", f"runMins={self.props.runMins}")
        self.content = self.content.replace("limitTxnsPerMin=0", f"limitTxnsPerMin={self.props.limitTxnsPerMin}")
        self.content = self.content.replace("terminalWarehouseFixed=true",
                                            f"terminalWarehouseFixed={'true' if self.props.terminalWarehouseFixed else 'false'}")
        self.content = self.content.replace("newOrderWeight=45", f"newOrderWeight={self.props.newOrderWeight}")
        self.content = self.content.replace("paymentWeight=43", f"paymentWeight={self.props.paymentWeight}")
        self.content = self.content.replace("orderStatusWeight=4", f"orderStatusWeight={self.props.orderStatusWeight}")
        self.content = self.content.replace("deliveryWeight=4", f"deliveryWeight={self.props.deliveryWeight}")
        self.content = self.content.replace("stockLevelWeight=4", f"stockLevelWeight={self.props.stockLevelWeight}")

        # 替换props.dm ---------------------------------------------------------------
        with open("props.dm", "w") as file:
            file.write(self.content)

        subprocess.run(['cp', 'props.dm', '/home/dmdba/benchmarksql-5.0/run/props.dm'], check=True,
                       text=True,
                       capture_output=True)

        # 替换props_table.dm ----------------------------------------------------------
        self.content = self.content.replace("BENCHMARKSQL", "SYSDBA")
        self.content = self.content.replace("123456789", "SYSDBA")

        with open("props_table.dm", "w") as file:
            file.write(self.content)

        subprocess.run(['cp', 'props_table.dm', '/home/dmdba/benchmarksql-5.0/run/props_table.dm'], check=True,
                       text=True,
                       capture_output=True)

        return HttpResponse(f"Update successfully!")

    def run(self, run_type):

        if run_type == 'table':
            op = 'su - dmdba -c "cd /home/dmdba/benchmarksql-5.0/run/ && ./runSQL.sh ./props_table.dm ../sqlCreateTable.sql"'
        elif run_type == 'load':
            op = 'su - dmdba -c "cd /home/dmdba/benchmarksql-5.0/run/ && ./runLoader.sh ./props.dm"'
        elif run_type == 'index':
            op = 'su - dmdba -c "cd /home/dmdba/benchmarksql-5.0/run/ && ./runSQL.sh ./props.dm ../sqlCreateIndex.sql"'
        elif run_type == 'benchmark':
            op = 'su - dmdba -c "cd /home/dmdba/benchmarksql-5.0/run/ && ./runBenchmark.sh ./props.dm"'

        elif run_type == 'restart':
            op = 'su - dmdba -c "cd /home/dmdba/dmdbms/bin/DmServiceDAMENG/ && restart"'

        process = subprocess.Popen(op, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        process.communicate()

        return HttpResponse(f"{process.stdout.read()}")


