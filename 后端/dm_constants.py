dm_metrics = {
        "dm_global_status_tps": "select stat_val from sys.v$sysstat where name = 'transaction total count';",
        "dm_global_status_qps": "select stat_val from sys.v$sysstat where name = 'select statements';",
        "dm_global_status_ips": "select stat_val from sys.v$sysstat where name = 'insert statements';",
        "dm_global_status_nioips": "select stat_val from sys.v$sysstat where name = 'total bytes received from client';",
        "dm_global_status_nio_ops": "select stat_val from sys.v$sysstat where name = 'total bytes sent to client';",
        "dm_global_status_fio_ips": "select stat_val * page from sys.v$sysstat where name = 'physical read count';",
        "dm_global_status_fio_ops": "select stat_val * page from sys.v$sysstat where name = 'physical write count';",
        "dm_global_status_mem_used": "select stat_val from sys.v$sysstat where name = 'memory used bytes';",
        "dm_global_status_cpu_use_rate": "select stat_val from sys.v$sysstat where name = 'os DM database cpu rate';",
        "dm_global_status_sessions": "select count(1) from v$sessions;",
        "dm_global_status_active_sessions": "select count(1) from v$sessions where state = 'ACTIVE';",
        "dm_global_status_task_waiting": "select waiting from v$task_queue;",
        "dm_global_status_task_ready": "select ready from v$task_queue;",
        "dm_global_status_task_total_wait_time": "select total_wait_time from v$task_queue;",
        "dm_global_status_avg_wait_time": "select average_wait_time from v$task_queue;",
        "dm_global_status_threads": "select count(1) from sys.v$threads;"
    }