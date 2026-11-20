import json
import os
import pandas as pd
import random
import time
import threading

from django.db import connection, transaction

import subprocess

# from django.middleware.csrf import get_token
# from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt

from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.conf import settings

from dm_constants import dm_metrics

from dm.models import PrimaryPara, SecondaryPara, SystemParameter, PropsDM, TpmC, TrainingConfiguration, ItemPara

from dm.models import (TrainingConfiguration_runMin1,
                       TrainingConfiguration_runMin2,
                       TrainingConfiguration_runMin3,
                       TrainingConfiguration_runMin4,
                       TrainingConfiguration_runMin5,
                       TrainingConfiguration_runMin6,
                       TrainingConfiguration_runMin7,
                       TrainingConfiguration_runMin8,
                       TrainingConfiguration_runMin9,
                       TrainingConfiguration_runMin10)

from dm.PropsRun import PropsTotalCommand

from dm.SMAC import SMAC_DM



# 操纵本地数据库   不要忘记using 'mysql'
def orm(request):
    
    return HttpResponse("数据库操作成功")

def isStopped(request):
    item_para = ItemPara.objects.using('mysql').all().get()
    item_para.IS_STOPPED = 'T'
    item_para.save()  # 需要保存更改
    return JsonResponse({'message': f'{item_para.IS_STOPPED}'}, status=200)
def isPaused(request):
    item_para = ItemPara.objects.using('mysql').all().get()
    item_para.IS_PAUSED = 'T'

    item_para.save()  # 需要保存更改

    return JsonResponse({'message': 'Paused successfully!'}, status=200)

def isContinue(request):
    item_para = ItemPara.objects.using('mysql').all().get()
    item_para.IS_PAUSED = 'F'

    item_para.save()  # 需要保存更改

    return JsonResponse({'message': 'Paused successfully!'}, status=200)

def isUpdate(request):
    item_para = ItemPara.objects.using('mysql').all().get()
    if item_para.IS_ALGORITHM_UPDATE == 'T':
        item_para.IS_ALGORITHM_UPDATE = 'F'
    else:
        item_para.IS_ALGORITHM_UPDATE = 'T'

    item_para.save()  # 需要保存更改

    return JsonResponse({'message': 'Paused successfully!'}, status=200)


def reSet_Stopped_And_Paused(request):
    item_para = ItemPara.objects.using('mysql').all().get()
    item_para.IS_PAUSED = 'F'
    item_para.IS_STOPPED = 'F'

    item_para.save()  # 需要保存更改

    return JsonResponse({'message': 'reset stop and pause'}, status=200)


# 算法部分 --------------------------------------------
def runSMAC():

    model = SMAC_DM(n_trials=10)
    model.SMAC()

    return "SMAC finish"

def Algorithm(request):
    # 启动后台线程
    thread = threading.Thread(target=runSMAC)
    thread.start()

    # 立即返回响应，不阻塞
    return JsonResponse({"status": "Algorithm start"})


# 达梦数据库状态总查询函数
def get_status_val(status_name):
    with connection.cursor() as cursor:
        cursor.execute(dm_metrics[status_name])
        row = cursor.fetchone()
    return row[0] if row else None


# 返回达梦数据库16个状态指标
def dmStatus(request):
    dm_global_status_tps = get_status_val('dm_global_status_tps')
    dm_global_status_qps = get_status_val('dm_global_status_qps')
    dm_global_status_ips = get_status_val('dm_global_status_ips')
    dm_global_status_nioips = get_status_val('dm_global_status_nioips')
    dm_global_status_nio_ops = get_status_val('dm_global_status_nio_ops')
    dm_global_status_fio_ips = get_status_val('dm_global_status_fio_ips')
    dm_global_status_fio_ops = get_status_val('dm_global_status_fio_ops')
    dm_global_status_mem_used = get_status_val('dm_global_status_mem_used')
    dm_global_status_cpu_use_rate = get_status_val('dm_global_status_cpu_use_rate')
    dm_global_status_sessions = get_status_val('dm_global_status_sessions')
    dm_global_status_active_sessions = get_status_val('dm_global_status_active_sessions')
    dm_global_status_task_waiting = get_status_val('dm_global_status_task_waiting')
    dm_global_status_task_ready = get_status_val('dm_global_status_task_ready')
    dm_global_status_task_total_wait_time = get_status_val('dm_global_status_task_total_wait_time')
    dm_global_status_avg_wait_time = get_status_val('dm_global_status_avg_wait_time')
    dm_global_status_threads = get_status_val('dm_global_status_threads')

    data = {
        "dm_global_status_tps": dm_global_status_tps,
        "dm_global_status_qps": dm_global_status_qps,
        "dm_global_status_ips": dm_global_status_ips,
        "dm_global_status_nioips": dm_global_status_nioips,
        "dm_global_status_nio_ops": dm_global_status_nio_ops,
        "dm_global_status_fio_ips": dm_global_status_fio_ips,
        "dm_global_status_fio_ops": dm_global_status_fio_ops,
        "dm_global_status_mem_used": dm_global_status_mem_used,
        "dm_global_status_cpu_use_rate": dm_global_status_cpu_use_rate,
        "dm_global_status_sessions": dm_global_status_sessions,
        "dm_global_status_active_sessions": dm_global_status_active_sessions,
        "dm_global_status_task_waiting": dm_global_status_task_waiting,
        "dm_global_status_task_ready": dm_global_status_task_ready,
        "dm_global_status_task_total_wait_time": dm_global_status_task_total_wait_time,
        "dm_global_status_avg_wait_time": dm_global_status_avg_wait_time,
        "dm_global_status_threads": dm_global_status_threads
    }

    response = HttpResponse(json.dumps(data))

    response['Access-Control-Allow-Origin'] = '*'  # 其实加这一个响应参数就行
    response['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
    response['Access-Control-Max-Age'] = '1000'
    response['Access-Control-Allow-Headers'] = '*'

    return response

# 查询红色参数
def redPara(request):
    # 获取所有参数记录
    parameters = PrimaryPara.objects.using('mysql').all().values()
    # 将QuerySet转换为列表，因为QuerySet不是JSON可序列化的
    parameters_list = list(parameters)
    # 返回JSON响应
    return JsonResponse(parameters_list, safe=False)

# 查询蓝色参数
def bluePara(request):

    parameters = SecondaryPara.objects.using('mysql').all().values()

    parameters_list = list(parameters)

    return JsonResponse(parameters_list, safe=False)

# 查询benchmark参数
def benchmarkPara(request):

    parameters = PropsDM.objects.using('mysql').all().values()

    parameters_list = list(parameters)

    return JsonResponse(parameters_list, safe=False)

# # 查询dm.ini文件
def dmini(request):
    dmini = '\#DaMeng Database Server Configuration file\n\#this is comments\n\n\#file location of dm.ctl\n		CTL_PATH                        = /dmdata/data/DAMENG/dm.ctl           \#ctl file path\n		CTL_BAK_PATH                    = /dmdata/data/DAMENG/ctl_bak         \#dm.ctl backup path\n		CTL_BAK_NUM                     = 10                                          \#backup number of dm.ctl, allowed to keep one more backup file besides specified number.\n		SYSTEM_PATH                     = /dmdata/data/DAMENG                         \#system path\n		CONFIG_PATH                     = /dmdata/data/DAMENG                         \#config path\n		TEMP_PATH                       = /dmdata/data/DAMENG                         \#temporary file path\n		BAK_PATH                        = /dmdata/data/DAMENG/bak                 \#backup file path\n		DFS_PATH                        =                                             \#path of db_file in dfs\n		BCT_PATH                        = /dmdata/data/DAMENG                         \#BCT file path\n\n\#instance name\n		INSTANCE_NAME                   = DBSERVER                                    \#Instance name\n\n\#memory pool and buffer\n		MAX_OS_MEMORY                   = 100                   \#Maximum Percent Of OS Memory\n		MEMORY_POOL                     = 500                   \#Memory Pool Size In Megabyte\n		MEMORY_N_POOLS                  = 1                     \#Number of Memory Pool\n		MEMORY_TARGET                   = 15000                 \#Memory Share Pool Target Size In Megabyte\n		MEMORY_EXTENT_SIZE              = 32                    \#Memory Extent Size In Megabyte\n		MEMORY_LEAK_CHECK               = 0                     \#Memory Pool Leak Checking Flag\n		MEMORY_MAGIC_CHECK              = 1                     \#Memory Pool Magic Checking Flag\n		HUGEPAGE_THRESHOLD              = 16                    \#IF not zero, try using hugepage if allocating size >= threshold * 2M\n		MEMORY_BAK_POOL                 = 4                     \#Memory Backup Pool Size In Megabyte\n		HUGE_MEMORY_PERCENTAGE          = 50                    \#Maximum percent of HUGE buffer that can be allocated to work as common memory pool\n		HUGE_BUFFER                     = 80                    \#Initial Huge Buffer Size In Megabytes\n		HUGE_BUFFER_POOLS               = 4                     \#number of Huge buffer pools\n		BUFFER                          = 1000                  \#Initial System Buffer Size In Megabytes\n		BUFFER_POOLS                    = 19                    \#number of buffer pools\n		FAST_POOL_PAGES                 = 3000                  \#number of pages for fast pool\n		FAST_ROLL_PAGES                 = 1000                  \#number of pages for fast roll pages\n		KEEP                            = 8                     \#system KEEP buffer size in Megabytes\n		RECYCLE                         = 300                   \#system RECYCLE buffer size in Megabytes\n		RECYCLE_POOLS                   = 19                    \#Number of recycle buffer pools\n		ROLLSEG                         = 1                     \#system ROLLSEG buffer size in Megabytes\n		ROLLSEG_POOLS                   = 19                    \#Number of rollseg buffer pools\n		MULTI_PAGE_GET_NUM              = 1                     \#Maximum number of pages for each read of buffer\n		PRELOAD_SCAN_NUM                = 0                     \#The number of pages scanned continuously to start preload task\n		PRELOAD_EXTENT_NUM              = 0                     \#The number of clusters preloaded for the first time\n		SORT_BUF_SIZE                   = 20                    \#maximum sort buffer size in Megabytes\n		SORT_BLK_SIZE                   = 1                     \#maximum sort blk size in Megabytes\n		SORT_BUF_GLOBAL_SIZE            = 1000                  \#maximum global sort buffer size in Megabytes\n		SORT_FLAG                       = 1                     \#choose method of sort\n		HAGR_HASH_SIZE                  = 100000                \#hash table size for hagr\n		HJ_BUF_GLOBAL_SIZE              = 5000                  \#maximum hash buffer size for all hash join in Megabytes\n		HJ_BUF_SIZE                     = 500                   \#maximum hash buffer size for single hash join in Megabytes\n		HJ_BLK_SIZE                     = 2                     \#hash buffer size allocated each time for hash join in Megabytes\n		HAGR_BUF_GLOBAL_SIZE            = 5000                  \#maximum buffer size for all hagr in Megabytes\n		HAGR_BUF_SIZE                   = 500                   \#maximum buffer size for single hagr in Megabytes\n		HAGR_BLK_SIZE                   = 2                     \#buffer size allocated each time for hagr in Megabytes\n		MTAB_MEM_SIZE                   = 8                     \#memory table size in Kilobytes\n		FTAB_MEM_SIZE                   = 0                     \#file table package size in Kilobytes\n		MMT_GLOBAL_SIZE                 = 4000                  \#memory map table global size in megabytes\n		MMT_SIZE                        = 0                     \#memory map table size in megabytes\n		MMT_FLAG                        = 1                     \#ways of storing bdta data in memory map table\n		DICT_BUF_SIZE                   = 50                    \#dictionary buffer size in Megabytes\n		HFS_CACHE_SIZE                  = 160                   \#hfs cache size in Megabytes, used in huge horizon table for insert, update,delete\n		VM_STACK_SIZE                   = 256                   \#VM stack size in Kilobytes\n		VM_POOL_SIZE                    = 64                    \#VM pool size in Kilobytes\n		VM_POOL_TARGET                  = 16384                 \#VM pool target size in Kilobytes\n		SESS_POOL_SIZE                  = 64                    \#session pool size in Kilobytes\n		SESS_POOL_TARGET                = 16384                 \#session pool target size in Kilobytes\n		RT_HEAP_TARGET                  = 8192                  \#runtime heap target size in Kilobytes\n		VM_MEM_HEAP                     = 0                     \#Whether to allocate memory to VM from HEAP\n		RFIL_RECV_BUF_SIZE              = 16                    \#redo file recover buffer size in Megabytes\n		COLDATA_POOL_SIZE               = 0                     \#coldata pool size for each worker group\n		HAGR_DISTINCT_HASH_TABLE_SIZE   = 10000                 \#Size of hagr distinct hash table\n		CNNTB_HASH_TABLE_SIZE           = 100                   \#Size of hash table in connect-by operation\n		GLOBAL_RTREE_BUF_SIZE           = 100                   \#The total size of buffer for rtree\n		SINGLE_RTREE_BUF_SIZE           = 10                    \#The size of buffer for single rtree\n		SORT_OPT_SIZE                   = 0                     \#once max memory size of radix sort assist count array\n		TSORT_OPT                       = 1                     \#minimizing memory allocation during small rowset sorting if possible\n		DFS_BUF_FLUSH_OPT               = 0                     \#Whether to flush buffer page in opt mode for DFS storage\n		BIND_PLN_PERCENT                = 30                    \#Maximum percent of bind plan in plan cache pool\n		FBACK_HASH_SIZE                 = 10000                 \#hash table size for flashback function\n		XBOX_MEMORY_TARGET              = 1024                  \#Memory target size in Megabyte of XBOX system\n		LIKE_PATTERN_NUM                = 300                   \#The maximum length of like pattern-matching\n		MEM_POOL_EXTEND_MODE             = 7                     \#Memory pool extend policy\n\n\#thread\n		WORKER_THREADS                  = 16                    \#Number Of Worker Threads\n		TASK_THREADS                    = 16                    \#Number Of Task Threads\n		FAST_RW_LOCK                    = 1                     \#Fast Read Write Lock flag\n		SPIN_TIME                       = 4000                  \#Spin Time For Threads In Microseconds\n		WORK_THRD_STACK_SIZE            = 8192                  \#Worker Thread Stack Size In Kilobytes\n		WORK_THRD_RESERVE_SIZE          = 256                   \#Worker Thread Reserve Stack Size In Kilobytes\n		WORKER_CPU_PERCENT              = 0                     \#Percent of CPU number special for worker thread\n		NESTED_C_STYLE_COMMENT          = 0                     \#flag for C stype nested comment\n		STHD_FLAG                       = 0                     \#Whether to use SQL threads pool\n		STHD_GRP_NUM                    = 8                     \#The number of SQL thread groups\n		STHD_THREAD_NUM                 = 8                     \#The number of SQL threads initialized\n\n\#query\n		USE_PLN_POOL                    = 1                     \#Query Plan Reuse Mode, 0: Forbidden; 1:strictly reuse, 2:parsing reuse, 3:mixed parsing reuse\n		DYN_SQL_CAN_CACHE               = 1                     \#Dynamic SQL cache mode. 0: Forbidden; 1: Allowed if the USE_PLN_POOL is non-zero;\n		VPD_CAN_CACHE                   = 0                     \#VPD SQL cache mode. 0: Forbidden; 1: Allowed if the USE_PLN_POOL is non-zero;\n		RS_CAN_CACHE                    = 0                     \#Resultset cache mode. 0: Forbidden; 1: Allowed only if the USE_PLN_POOL is non-zero;\n		RS_CACHE_TABLES                 =                       \#Tables allowed to enable result set cache\n		RS_CACHE_MIN_TIME               = 0                     \#Least time for resultset to be cached\n		RS_BDTA_FLAG                    = 0                     \#Resultset mode. 0: row; 2: bdta;\n		RS_BDTA_BUF_SIZE                = 32                    \#Maximum size of message in Kilobytes for BDTA cursor, it\'s valid only if RS_BDTA_FLAG is set to 2\n		RS_TUPLE_NUM_LIMIT              = 2000                  \#Maximum number for resultset to be cached\n		RESULT_SET_LIMIT                = 10000                 \#Maximum Number Of  cached Resultsets\n		RESULT_SET_FOR_QUERY            = 0                     \#Whether to generate result set for non-query statement\n		SESSION_RESULT_SET_LIMIT        = 10000                 \#Maximum number of cached result sets for each session, 0 means unlimited\n		BUILD_FORWARD_RS                = 0                     \#Whether to generate result set for forward only cursor\n		MAX_OPT_N_TABLES                = 6                     \#Maximum Number Of Tables For Query Optimization\n		MAX_N_GRP_PUSH_DOWN             = 5                     \#Maximum Number Of Rels For Group push down Optimization\n		CNNTB_MAX_LEVEL                 = 20000                 \#Maximum Level Of Hierarchical Query\n		CTE_MAXRECURSION                = 100                   \#Maximum recursive Level Of Common Expression Table\n		CTE_OPT_FLAG                    = 1                     \#Optimize recursive with, 0: false, 1: convert refed subquery to invocation\n		BATCH_PARAM_OPT                 = 0                     \#optimize flag for DML with batch binded params\n		CLT_CONST_TO_PARAM              = 0                     \#Whether to convert constant to parameter\n		LIKE_OPT_FLAG                   = 127                   \#the optimized flag of LIKE expression\n		FILTER_PUSH_DOWN                = 2                     \#whether push down filter to base table\n		USE_MCLCT                       = 2                     \#mclct use flag for replace mgat\n		PHF_NTTS_OPT                    = 1                     \#phf ntts opt flag\n		MPP_MOTION_SYNC                 = 200                   \#mpp motion sync check number\n		UPD_DEL_OPT                     = 2                     \#update&delete opt flag, 0: false, 1: opt, 2: opt & ntts opt\n		ENABLE_INJECT_HINT              = 0                     \#enable inject hint\n		FETCH_PACKAGE_SIZE              = 512                   \#command fetch package size\n		UPD_QRY_LOCK_MODE               = 0                     \#lock mode of FOR UPDATE query\n		ENABLE_DIST_IN_SUBQUERY_OPT     = 0                     \#Whether to enable in-subquery optimization\n		MAX_OPT_N_OR_BEXPS              = 7                     \#maximum number of OR bool expressions for query optimization\n		USE_HAGR_FLAG                   = 0                     \#Whether to use HAGR operator when can\'t use SAGR operator\n		DTABLE_PULLUP_FLAG              = 1                     \#the flag of pulling up derived table\n		VIEW_PULLUP_FLAG                = 34                    \#the flag of pulling up view\n		GROUP_OPT_FLAG                  = 60                    \#the flag of opt group\n		FROM_OPT_FLAG                   = 0                     \#the flag of opt from\n		HAGR_PARALLEL_OPT_FLAG          = 4                     \#the flag of opt hagr in mpp or parallel\n		HAGR_DISTINCT_OPT_FLAG          = 2                     \#the flag of opt hagr distinct in mpp\n		REFED_EXISTS_OPT_FLAG           = 1                     \#Whether to optimize correlated exists-subquery into non-correlated in-subquery\n		REFED_OPS_SUBQUERY_OPT_FLAG     = 1                     \#Whether to optimize correlated op all/some/all-subquery into exists-subquery\n		HASH_PLL_OPT_FLAG               = 107                   \#the flag of cutting partitioned table when used hash join\n		PARTIAL_JOIN_EVALUATION_FLAG    = 1                     \#Whether to convert join type when upper operator is DISTINCT\n		USE_FK_REMOVE_TABLES_FLAG       = 1                     \#Whether to remove redundant join by taking advantage of foreign key constraint\n		USE_FJ_REMOVE_TABLE_FLAG        = 1                     \#Whether to remove redundant join by taking advantage of filter joining\n		SLCT_ERR_PROCESS_FLAG           = 0                     \#How to handle error when processing single row\n		MPP_HASH_LR_RATE                = 10                    \#The ratio of left child\'s cost to right child\'s cost of hash join in MPP environment that can influence the execution plan\n		LPQ_HASH_LR_RATE                = 30                    \#The ratio of left child\'s cost to right child\'s cost of hash join in LPQ environment that can influence the execution plan\n		USE_HTAB                        = 1                     \#Whether to use HTAB operator for the whole plan\n		SEL_ITEM_HTAB_FLAG              = 0                     \#Whether to use HTAB operator for correlated subquery in select items\n		OR_CVT_HTAB_FLAG                = 1                     \#Whether to use HTAB operator to optimizer or-expression\n		ENHANCED_SUBQ_MERGING           = 3                     \#Whether to use merging subquery opt\n		CASE_WHEN_CVT_IFUN              = 9                     \#Flag of converting subquery in case-when expression to IF operator\n		OR_NBEXP_CVT_CASE_WHEN_FLAG     = 0                     \#Whether to convert or-expression to case-when expression\n		NONCONST_OR_CVT_IN_LST_FLAG     = 0                     \#Whether to convert nonconst or-expression to in lst expression\n		OUTER_CVT_INNER_PULL_UP_COND_FLAG = 11                  \#Whether to pull up join condition when outer join converts to inner join\n		OPT_OR_FOR_HUGE_TABLE_FLAG      = 0                     \#Whether to use HFSEK to optimize or-expression for HUGE table\n		ORDER_BY_NULLS_FLAG             = 0                     \#Whether to place NULL values to the end of the result set when in ascending order\n		SUBQ_CVT_SPL_FLAG               = 1                     \#Flag of indicating how to convert correlated subquery\n		ENABLE_RQ_TO_SPL                = 1                     \#Whether to convert correlated subquery to SPOOL\n		MULTI_IN_CVT_EXISTS             = 1                     \#Whether to convert multi-column-in subquery to exists subquery\n		PRJT_REPLACE_NPAR               = 1                     \#Whether to replace NPAR tree in NSEL after projection\n		ENABLE_RQ_TO_INV                = 0                     \#Whether to convert correlated subquery to temporary function\n		SUBQ_EXP_CVT_FLAG               = 193                   \#whether convert refered subquery exp to non-refered subquery exp\n		USE_REFER_TAB_ONLY              = 0                     \#Whether to pull down correlated table only when dealing with correlated subquery\n		REFED_SUBQ_CROSS_FLAG           = 1                     \#Whether to replace hash join with cross join for correlated subquery\n		IN_LIST_AS_JOIN_KEY             = 0                     \#Whether to use in-list expression as join key\n		OUTER_JOIN_FLATING_FLAG         = 1                     \#Flag of indicating whether outer join will be flattened\n		TOP_ORDER_OPT_FLAG              = 5                     \#The flag of optimizing the query with the top clause and the order by clause\n		TOP_ORDER_ESTIMATE_CARD         = 300                   \#The estimated card of leaf node when optimize the query with the top clause and the order by clause\n		PLACE_GROUP_BY_FLAG             = 0                     \#The flag of optimizing the query with group_by and sfun by clause\n		TOP_DIS_HASH_FLAG               = 1                     \#Flag of disable hash join in TOP-N query\n		ENABLE_RQ_TO_NONREF_SPL         = 1                     \#Whether to convert correlated query to non-correlated query\n		ENABLE_CHOOSE_BY_ESTIMATE_FLAG  = 0                     \#Whether to choose different plan by estimating\n		OPTIMIZER_MODE                  = 1                     \#Optimizer_mode\n		NEW_MOTION                      = 1                     \#New Motion\n		LDIS_NEW_FOLD_FUN               = 0                     \#ldis use different fold fun with mdis\n		DYNAMIC_CALC_NODES              = 0                     \#different nodes of npln use different nubmer of calc sizes/threads\n		OPTIMIZER_MAX_PERM              = 7200                  \#Optimizer_max permutations\n		ENABLE_INDEX_FILTER             = 1                     \#enable index filter\n		OPTIMIZER_DYNAMIC_SAMPLING      = 0                     \#Dynamic sampling level\n		TABLE_STAT_FLAG                 = 0                     \#How to use stat of table\n		AUTO_STAT_OBJ                   = 0                     \#Flag of automatically collecting statistics and recording DML changing rows\n		MONITOR_MODIFICATIONS           = 0                     \#Flag of monitor statistics and recording DML modifications\n		MON_CHECK_INTERVAL              = 3600                  \#Server flush monitor modifications data to disk interval\n		NONREFED_SUBQUERY_AS_CONST      = 1                     \#Whether to convert non-correlated subquery to const\n		HASH_CMP_OPT_FLAG               = 0                     \#Flag of operators that enable optimization with static hash table\n		OUTER_OPT_NLO_FLAG              = 0                     \#Flag of enable index join for those whose right child is not base table\n		DISTINCT_USE_INDEX_SKIP         = 2                     \#Distinct whether to use index skip scan\n		USE_INDEX_SKIP_SCAN             = 0                     \#Whether to use index skip scan\n		INDEX_SKIP_SCAN_RATE            = 0.0025                \#Rate in index skip scan\n		SPEED_SEMI_JOIN_PLAN            = 9                     \#Flag of speeding up the generating process of semi join plan\n		COMPLEX_VIEW_MERGING            = 2                     \#Flag of merging complex view into query without complex view\n		HLSM_FLAG                       = 1                     \#Choose one method to realize hlsm operator\n		DEL_HP_OPT_FLAG                 = 0                     \#Optimize delete for horization partition table\n		OPTIMIZER_OR_NBEXP              = 29                    \#Flag of or-expression optimization method\n		NPLN_OR_MAX_NODE                = 20                    \#Max number of or-expression on join condition\n		CNNTB_OPT_FLAG                  = 193                   \#Optimize hierarchical query\n		ADAPTIVE_NPLN_FLAG              = 3                     \#Adaptive npln\n		MULTI_UPD_OPT_FLAG              = 1                     \#Optimize multi column update\n		MULTI_UPD_MAX_COL_NUM           = 128                   \#Max value of column counts when optimize multi column update\n		ENHANCE_BIND_PEEKING            = 0                     \#Enhanced bind peeking\n		NBEXP_OPT_FLAG                  = 7                     \#Whether to enable optimization for bool expressions\n		HAGR_HASH_ALGORITHM_FLAG        = 0                     \#HAGR hash algorithm choice\n		DIST_HASH_ALGORITHM_FLAG        = 0                     \#Distinct hash algorithm choice\n		UNPIVOT_OPT_FLAG                = 0                     \#Optimize UNPIVOT operator\n		VIEW_FILTER_MERGING             = 138                   \#Flag of merging view filter\n		ENABLE_PARTITION_WISE_OPT       = 1                     \#whether enable partition-wise optimization\n		OPT_MEM_CHECK                   = 0                     \#reduce search space when out of memory\n		ENABLE_JOIN_FACTORIZATION       = 1                     \#Whether to enable join factorization\n		EXPLAIN_SHOW_FACTOR             = 1                     \#factor of explain\n		ERROR_COMPATIBLE_FLAG           = 0                     \#enable/disable specified errors to be compatible with previous version\n		ENABLE_NEST_LOOP_JOIN_CACHE     = 0                     \#whether enable cache temporary result of nest loop join child\n		ENABLE_TABLE_EXP_REF_FLAG       = 1                     \#Whether allow table expression to reference brother tables\n		BIND_PARAM_OPT_FLAG             = 3                     \#flag of optimizer bind parameter\n		VIEW_OPT_FLAG                   = 1                     \#flag of optimize view\n		SORT_ADAPTIVE_FLAG              = 0                     \#sort buf adaptive\n		DPC_OPT_FLAG                    = 65535                 \#optimizer control for DPC\n		DPC_SYNC_STEP                   = 16                    \#dpc motion sync check step\n		DPC_SYNC_TOTAL                  = 0                     \#dpc motion sync check total\n		XBOX_DUMP_THRESHOLD             = 0                     \#The xbox_sys mem used threshold of dump xbox_msg\n		STMT_XBOX_REUSE                 = 1                     \#Xbox resuse flag on statement\n		XBOX_SHORT_MSG_SIZE             = 1024                  \#The xbox_sys short message threshold of dump xbox_msg\n		MAX_HEAP_SIZE                   = 0                     \#Maximum heap size in megabyte allowed to use during analysis phase\n		PLAN_OP_FLAG                    = 0                     \#flag of disabled plan operator\n		DUAL_ENABLE_SELECT              = 1                     \#Enable select dual/sysdual/sysdual2 in mount status. 0: no, 1: yes.\n		LOAD_BINDED_PLN                 = 0                     \#Whether to load binded plan\n		FORALL_OPT                      = 1                     \#Whether to optimize FORALL statements\n		HASH_OPT_FLAG                   = 1                     \#Flag of operators that enable optimization with hash table\n		SFUN_PUSH_DOWN_FLAG             = 1                     \#sfun push down flag\n		SKIP_CORRUPT_PAGE              = 0                    \#Policy for dealing with corrupt pages, 0: raise an error, 1: skip them\n		AUTO_GEN_PLAN                   = 0                     \#Maximum try times for iterating adaptive ini to generate pln; 0 means never try\n\n\#checkpoint\n		CKPT_RLOG_SIZE                  = 128                   \#Checkpoint Rlog Size, 0: Ignore; else: Generate With Redo Log Size\n		CKPT_DIRTY_PAGES                = 0                     \#Checkpoint Dirty Pages, 0: Ignore; else: Generate With Dirty Pages\n		CKPT_INTERVAL                   = 180                   \#Checkpoint Interval In Seconds\n		CKPT_FLUSH_RATE                 = 5.00                  \#Checkpoint Flush Rate(0.0-100.0)\n		CKPT_FLUSH_PAGES                = 1000                  \#Minimum number of flushed pages for checkpoints\n		CKPT_WAIT_PAGES                 = 1024                  \#Maximum number of pages flushed for checkpoints\n		FORCE_FLUSH_PAGES               = 8                     \#number of periodic flushed pages\n		ENABLE_CKPT_EVENT_TRIG          = 0                     \#Whether enable checkpoint event trigger, 0: disable; 1: enable\n\n\#IO\n		DIRECT_IO                       = 0                     \#Flag For Io Mode(Non-Windows Only), 0: Using File System Cache; 1: Without Using File System Cache\n		IO_THR_GROUPS                   = 8                     \#The Number Of Io Thread Groups(Non-Windows Only)\n		HIO_THR_GROUPS                  = 2                     \#The Number Of Huge Io Thread Groups(Non-Windows Only)\n		FIL_CHECK_INTERVAL              = 0                     \#Check file interval in Second,0 means no_check(Non-Windows Only)\n		FAST_EXTEND_WITH_DS             = 1                     \#How To Extend File\'s Size (Non-Windows Only), 0: Extend File With Hole; 1: Extend File With Disk Space\n		FIL_CHECK_MODE                  = 0                     \#Whether to halt when system file doesn\'t exist, 0:no_halt, 1:halt(Non-Windows Only)\n\n\#database\n		MAX_SESSIONS                    = 10000                 \#Maximum number of concurrent sessions\n		MAX_CONCURRENT_TRX              = 0                     \#Maximum number of concurrent transactions\n		CONCURRENT_TRX_MODE             = 0                     \#Concurrent transactions mode\n		CONCURRENT_DELAY                = 16                    \#Delay time in seconds for concurrent control\n		TRX_VIEW_SIZE                   = 512                   \#The buffer size of local transaction ids in TRX_VIEW\n		TRX_VIEW_MODE                   = 1                     \#The transaction view mode, 0: Active ids snap; 1: Recycled id array\n		TRX_CMTARR_SIZE                 = 10                    \#The size of transaction commitment status array in 1M\n		MAX_SESSION_STATEMENT           = 10000                 \#Maximum number of statement handles for each session\n		MAX_SESSION_MEMORY              = 0                     \#Maximum memory(In Megabytes) a single session can use\n		MAX_CONCURRENT_OLAP_QUERY       = 0                     \#Maximum number of concurrent OLAP queries\n		BIG_TABLE_THRESHHOLD            = 1000                  \#Threshold value of a big table in 10k\n		MAX_EP_SITES                    = 64                    \#Maximum number of EP sites for MPP\n		PORT_NUM                        = 5236                  \#Port number on which the database server will listen\n		LISTEN_IP                       =                       \#IP address from which the database server can accept\n		FAST_LOGIN                      = 0                     \#Whether to log information without login\n		DDL_AUTO_COMMIT                 = 1                     \#ddl auto commit mode, 0: not auto commit; 1: auto commit\n		COMPRESS_MODE                   = 0                     \#Default Compress Mode For Tables That Users Created, 0: Not Compress; 1: Compress\n		PK_WITH_CLUSTER                 = 0                     \#Default Flag For Primary Key With Cluster, 0: Non-Cluster; 1: Cluster\n		EXPR_N_LEVEL                    = 200                   \#Maximum nesting levels for expression\n		N_PARSE_LEVEL                   = 100                   \#Maximum nesting levels for parsing object\n		MAX_SQL_LEVEL                   = 500                   \#Maximum nesting levels of VM stack frame for sql\n		BDTA_SIZE                       = 300                   \#batch data processing size.SIZE OF BDTA(1-10000)\n		OLAP_FLAG                       = 2                     \#OLAP FLAG, 1 means enable olap\n		JOIN_HASH_SIZE                  = 500000                \#the hash table size for hash join\n		USE_DHASH_FLAG                  = 0                     \#use dhash flag: 0 means use static hash; 1,2,3 means use dynamic hash\n		HFILES_OPENED                   = 256                   \#maximum number of files can be opened at the same time for huge table\n		ISO_IGNORE                      = 0                     \#ignore isolation level flag\n		TEMP_SIZE                       = 10                    \#temporary file size  in Megabytes\n		TEMP_SPACE_LIMIT                = 0                     \#temp space limit in megabytes\n		FILE_TRACE                      = 0                     \#Whether to log operations of database files\n		COMM_TRACE                      = 0                     \#Whether to log warning information of communication\n		ERROR_TRACE                     = 0                     \#Whether to log error information, 1: NPAR ERROR\n		CACHE_POOL_SIZE                 = 100                   \#SQL buffer size in megabytes\n		PLN_DICT_HASH_THRESHOLD         = 20                    \#Threshold in megabytes for plan dictionary hash table creating\n		STAT_COLLECT_SIZE               = 10000                 \#minimum collect size in rows for statistics\n		STAT_ALL                        = 0                     \#if collect all the sub-tables of a partition table\n		PHC_MODE_ENFORCE                = 0                     \#join mode\n		ENABLE_HASH_JOIN                = 1                     \#enable hash join\n		ENABLE_INDEX_JOIN               = 1                     \#enable index join\n		ENABLE_MERGE_JOIN               = 1                     \#enable merge join\n		MPP_INDEX_JOIN_OPT_FLAG         = 1                     \#enhance index inner join in mpp\n		MPP_NLI_OPT_FLAG                = 1                     \#enhance nest loop inner join in mpp\n		MAX_PARALLEL_DEGREE             = 1                     \#Maximum degree of parallel query\n		PARALLEL_POLICY                 = 0                     \#Parallel policy\n		PARALLEL_THRD_NUM               = 10                    \#Thread number for parallel task\n		PARALLEL_MODE_COMMON_DEGREE     = 1                     \#the common degree of parallel query for parallel-mode\n		PUSH_SUBQ                       = 0                     \#Whether to push down semi join for correlated subquery\n		OPTIMIZER_AGGR_GROUPBY_ELIM     = 1                     \#Whether to attempt to eliminate group-by aggregations\n		UPD_TAB_INFO                    = 0                     \#Whether to update table info when startup\n		ENABLE_IN_VALUE_LIST_OPT        = 6                     \#Flag of optimization methods for in-list expression\n		ENHANCED_BEXP_TRANS_GEN         = 3                     \#Whether to enable enhanced transitive closure of boolean expressions\n		ENABLE_DIST_VIEW_UPDATE         = 0                     \#whether view with distinct can be updated\n		STAR_TRANSFORMATION_ENABLED     = 0                     \#Whether to enable star transformation for star join queries\n		MONITOR_INDEX_FLAG              = 0                     \#monitor index flag\n		AUTO_COMPILE_FLAG               = 1                     \#Whether to compile the invalid objects when loading\n		RAISE_CASE_NOT_FOUND            = 0                     \#Whether raise CASE_NOT_FOUND exception for no case item matched\n		FIRST_ROWS                      = 100                   \#maximum number of rows when first returned to clients\n		LIST_TABLE                      = 0                     \#Whether to convert tables to LIST tables when created\n		ENABLE_SPACELIMIT_CHECK         = 1                     \#flag for the space limit check, 0: disable 1: enable\n		BUILD_VERTICAL_PK_BTREE         = 0                     \#Whether to build physical B-tree for primary key on huge tables\n		BDTA_PACKAGE_COMPRESS           = 0                     \#Whether to compress BDTA packages\n		HFINS_PARALLEL_FLAG             = 0                     \#Flag of parallel policy for inserting on huge table\n		HFINS_MAX_THRD_NUM              = 100                   \#Maximum number of parallel threads that responsible for inserting on huge table\n		LINK_CONN_KEEP_TIME             = 15                    \#Max idle time in minute for DBLINK before being closed\n		DETERMIN_CACHE_SIZE             = 5                     \#deterministic function results cache size(M)\n		NTYPE_MAX_OBJ_NUM               = 1000000               \#Maximum number of objects and strings in composite data type\n		CTAB_SEL_WITH_CONS              = 0                     \#Whether to build constraints when creating table by query\n		HLDR_BUF_SIZE                   = 8                     \#HUGE table fast loader buffer size in Megabytes\n		HLDR_BUF_TOTAL_SIZE             = 4294967294            \#HUGE table fast loader buffer total size in Megabytes\n		HLDR_REPAIR_FLAG                = 0                     \#Flag of repairing huge table after exception, 0: NO 1: YES\n		HLDR_FORCE_COLUMN_STORAGE       = 1                     \#Whether force column storage for last section data, 0: NO 1: YES\n		HLDR_FORCE_COLUMN_STORAGE_PERCENT = 80                  \#Minimum percent of unfully section data for huge force column storage\n		HLDR_HOLD_RATE                  = 1.50                  \#THE minimum rate to hold hldr of column number(1-65535)\n		HLDR_MAX_RATE                   = 2                     \#THE minimum rate to create hldr of column number(2-65535)\n		HUGE_ACID                       = 0                     \#Flag of concurrent mechanism for HUGE tables\n		HUGE_STAT_MODE                  = 2                     \#Flag of default stat mode when create huge table, 0:NONE 1:NORMAL 2:ASYNCHRONOUS\n		HFS_CHECK_SUM                   = 1                     \#Whether to check sum val for hfs data\n		HBUF_DATA_MODE                  = 0                     \#Whether to uncompress and decrypt data before read into HUGE buffer\n		DBLINK_OPT_FLAG                 = 509                   \#optimize dblink query flag\n		ELOG_REPORT_LINK_SQL            = 0                     \#Whether to write the SQLs that sent to remote database by DBLINKs into error log file\n		DBLINK_LOB_LEN                  = 8                     \#BLOB/TEXT buffer size(KB) for dblink\n		FILL_COL_DESC_FLAG              = 0                     \#Whether to return columns description while database returns results\n		BTR_SPLIT_MODE                  = 1                     \#Split mode for BTREE leaf, 0: split half and half, 1: split at insert point\n		TS_RESERVED_EXTENTS             = 64                    \#Number of reserved extents for each tablespace when startup\n		TS_SAFE_FREE_EXTENTS            = 512                   \#Number of free extents which considered as safe value for each tablespace\n		TS_MAX_ID                       = 8192                  \#Maximum ID value for tablespaces in database\n		TS_FIL_MAX_ID                   = 255                   \#Maximum ID value for files in tablespace\n		DECIMAL_FIX_STORAGE             = 0                     \#Whether convert decimal data to fixed length storage\n		SAVEPOINT_LIMIT                 = 512                   \#The upper limit of savepoint in a transaction\n		SQL_SAFE_UPDATE_ROWS            = 0                     \#Maximum rows can be effected in an update&delete statement\n		ENABLE_HUGE_SECIND              = 1                     \#Whether support huge second index, 0: disable, 1: enable\n		TRXID_UNCOVERED                 = 0                     \#Whether disable scanning 2nd index only when pseudo column trxid used, 0: disable, 1: enable\n		LOB_MAX_INROW_LEN               = 900                   \#Max lob data inrow len\n		RS_PRE_FETCH                    = 0                     \#Whether enable result pre-fetch\n		DFS_PAGE_FLUSH_VALIDATE         = 1                     \#Whether enable validate page when flush in DDFS\n		GEN_SQL_MEM_RECLAIM             = 1                     \#Whether reclaim memory space after generating each SQL\'s plan\n		TIMER_TRIG_CHECK_INTERVAL       = 60                    \#Server check timer trigger interval\n		DFS_HUGE_SUPPORT                = 1                     \#Whether support huge table operation in DDFS\n		INNER_INDEX_DDL_SHOW            = 1                     \#Whether to show inner index ddl.\n		HP_STAT_SAMPLE_COUNT            = 50                    \#Max sample count when stating on horizon partitions\n		MAX_SEC_INDEX_SIZE              = 16384                 \#Maximum size of second index\n		ENHANCE_RECLAIM                 = 1                     \#Whether enhance class instances\n		ENABLE_PMEM                     = 0                     \#Whether allow to  use  persistent memory\n		HP_TAB_COUNT_PER_BP             = 1                     \#hash partition count per BP when use DEFAULT\n		SQC_GI_NUM_PER_TAB              = 1                     \#sqc_gi_num_per_tab\n		HP_DEF_LOCK_MODE                = 0                     \#Default lock mode for partition table. 0:lock root, 1: lock partitions\n		CODE_CONVERSE_MODE              = 1                     \#judge how dblink do with incomplete str bytes, 1 represents report err, 0 represents discard incomplete bytes\n		DBLINK_USER_AS_SCHEMA           = 1                     \#Whether use login name as default schema name for dblink\n		CTAB_MUST_PART                  = 0                     \#Whether to create partition user table\n		CTAB_WITH_LONG_ROW              = 0                     \#Default Flag of using long row for create table\n		TMP_DEL_OPT                     = 1                     \#delete opt flag for temporary table, 0: false, 1: opt\n		LOGIN_FAIL_TRIGGER              = 0                     \#Whether support trigger when login failed\n		INDEX_PARALLEL_FILL             = 0                     \#Enable index parallel fill rows\n		CIND_CHECK_DUP                  = 0                     \#Check index and unique constraint duplicates, 0: index same type and key is forbidden and ignore check unique constraint; 1: index same key is forbidden and check unique constraint\n		TSMV_RAFIL_SIZE                 = 64                    \#Max size(Mbytes) of temporary archive file for tablespace move on dpc\n		HUGE_ENABLE_DEL_UPD             = 1                     \#Whether huge table enable delete or update, 0: disable update/delete; 1: enable update/delete; 2: disable update; 3: disable delete\n		HUGE_DEFAULT_FILE_SIZE          = 64                    \#Default file size for huge table\n		HUGE_DEFAULT_SECTION_SIZE       = 65536                 \#Default section size for huge table\n		ENABLE_CS_CVT                   = 0                     \#the ifun cvt function, if opened,can convert str from one charset to another\n		HUGE_DEFAULT_FILE_INIT_SIZE     = 1                     \#Default file inital size for huge table\n		TSMV_WAIT_TIMEOUT               = 120                   \#Deadline(Second) for dpc_tsmv_lock_table_dict\n		STAT_OPT_FLAG                   = 0                     \#new way to implement stat\n		ALLOWED_CLIENT_VERSIONS         =                       \#Client version(s) allowed to connect\n		CSEK2_CHECK_LOCK                = 0                     \#Whether check lock when simple mpln doing csek2\n		DPC_DCT_REFRESH_POLICY          = 1                     \#DPC dct info refresh policy: with tick check or not\n		HANDLE_WARN_RATE                = 75                    \#handle used warning rate\n		CLOB_MAX_IFUN_LEN               = 20971520              \#Max length of source clob for ifun\n		MAX_UNCOMPRESS_RATIO            = 100                   \#Max uncompress ratio\n		MAX_UNCOMPRESS_LENGTH           = 1024                  \#Max uncompress length(MB)\n		ENET_SESS_CHECK_INTERVAL        = 10                    \#ENET check session interval when mp not in service\n		DPC_TABLESPACE_BALANCE          = 0                     \#Enable DPC load balance by tablespace\n		CYT_CHECK_FLAG                  = 0                     \#Whether check encrypt and decrypt\n		TS_FIL_USE_ABSOLUTE_PATH        = 0                     \#Data file must use absolute directory when creating tablespace or adding file\n		LIST_TABLE_BRANCH               = 0                     \#concurrent branch number when list_table open\n		LIST_TABLE_NON_BRANCH           = 0                     \#non-concurrent branch number when list_table open\n		DHASH3_MAX_CONFLICT             = 4                     \#Maximum conflict on each cell with dynamic hash3 table\n		DHASH3_SIZE_EXTEND_FACTOR       = 5                     \#Expansion factor when dynamically extending hash table\n		DB_FILE_NAME_CONVERT            =                       \#Patterns to map primary database files to standby database files\n		HFI_HP_MODE                     = 1                     \#Lock mode when hfi process partiton table.0:lock partitions,1:lock root\n		TRC_LOG_MODULE                  = ALL                   \#Trace log module config\n		DPC_GUP_SESS_TIMEOUT            = 180                   \#Deadline(Second) for sessions to disconnect from upgrade SP\n		TS_AUTO_EXTEND_SIZE             = 64                    \#The size to automatically extend for a tablespace\n		INI_SYNC                        = 1                     \#Whether sync ini parameter from primary node\n		TRUNC_CHECK_MODE                = 0                     \#How to check table truncate, 0:check by root table; 1:check by subpartition table; 2:check by index\n		PAGE_CHECK_POLICY               = 1                     \#Policy to choose when database page check failed, 0: IGNORE, 1:HALT\n		STAT_CACHE_FLAG                 = 1                     \#cache stat on sp\n		FAST_START_MTTR_TARGET          = 0                     \#The number of seconds the database takes to perform crash recovery of a single instance.\n		TSMV_FILE_COPY_PLL              = 1                     \#Parallel degree of file copying\n		TSMV_SEND_BUF_SIZE              = 4                     \#Send buffer size of tablespace moving in Mbytes\n		DEFAULT_FILLFACTOR              = 0                     \#default fillfactor value\n		SHADOW_CHECK_INTERVAL           = 60                    \#Raft shadow node archivelog thread check interval\n		PL_SQL_STRIP                    = 0                     \#Combination value for strip SQL from, 0:No, 1:PL, 2:PROC&FUNC, 4:PKG&OBJ, 8:TRIG\n		WM_CONCAT_LOB                   = 1                     \#Whether to return CLOB value for function wm_concat\n		CHECK_CONS_NAME                 = 1                     \#Whether to check the constraint name when create or rename a constraint\n		MAX_LINK_SESSIONS               = 10000                 \#Maximum number of DBLINK concurrent sessions\n		PKG_BUILD_WAIT_TIME             = 5                     \#Maximum waiting time in seconds for pkg build\n		PTX_ROLLBACK                    = 0                     \#Whether to support ptx rollback, 0:no, 1:yes\n		LOB_READ_LOCK                    = 1                     \#Whether to lock table when reading lob\n		DSC_QUOTA_RELOAD_INTERVAL       = 5                     \#The quota of tablespace reload interval in DSC. (1 ~ 60)\n		AUDIT_FLUSH_LEVEL               = 0                     \#Level to flush audit record, 0: flush by statement; 1: flush by transaction; 2: flush delay. default is 0\n		SUBSCRIBE_BUF_SIZE              = 8                     \#Buffer size in Mbytes for subscribe log\n		SUBSCRIBE_LOG_THRESHOLD         = 256                   \#Threshold in MBytes per second for subscribe log on source\n		VM_PINST_COUNT                  = 10                    \#How many package instances can be cached on stackframe\n		INSTRUCT_COMBINE                = 0                     \#Whether to combine instructions for some complex expressions\n		MAX_ESESSIONS                   = 100000                \#Maximum number of esessions, 0 means unlimited\n		PARALLEL_THRD_TARGET            = 0                     \#Maximum thread number for parallel task, 0 means unlimited\n		POOL_CLEAR_FLAG                 = 0                     \#free all memory when pool clear(1) or save extend blk in target(0)\n		PL_SQL_STRIP_VERSION            = 200                   \#Support version for PL_SQL_STRIP\n		IPV6_LSNR                       = 1                     \#Whether to listen to ipv6, 0: not listen, 1: listen\n		DBLINK_HEALTH_CHECK             = 1                     \#DBLINK connection health check, 0:no check, 1: lightweight check, 2: heavyweight check\n		BACKTRACE_REPORT                = 0                     \#Whether to trace backtrace when ptx rollback happen, 0:no, 1:yes\n		PTX_BI_PERCENTAGE                = 50                    \#Percentage of pages allocated from recycle pool for ptx bi register\n		GEO2_CONS_CHECK                  = 0                    \#Whether to check geom/geog column during constraint detection\n		LOCK_DICT_HASH_SIZE            = 1024                  \#Hash size for lock system\n		DEFAULT_HASHPARTMAP             = 1                     \#Default HASHPARTMAP value when create HASH partition table\n		ODCI_DEF_FETCH_NUM              = 300                   \#Set pipelined using func fetch num\n		DPC_RW                          = 0                     \#Whether enable DPC read/write separate, 0:false; 1:default leader; 2:default follower.\n		DPC_RWPERCENT                   = 100                   \#Read transaction percent of using standby instance when DPC read/write separate.\n		DPC_RW_SWITCH                   = 0                     \#Whether transaction read_policy can switch when DPC read/write separate, 0:false; 1:switch each sql; 2:switch each request.\n		ENABLE_FAST_REFCURSOR           = 1                     \#Whether to enable fast refcursor\n\n\#pre-load\n		LOAD_TABLE                      =                       \#need to pre-load table\n		LOAD_HTABLE                     =                       \#need to pre-load htable\n\n\#client cache\n		CLT_CACHE_TABLES                =                       \#Tables that can be cached in client\n\n\#redo log\n		RLOG_BUF_SIZE                   = 1024                  \#The Number Of Log Pages In One Log Buffer\n		RLOG_POOL_SIZE                  = 256                   \#Redo Log Pool Size In Megabyte\n		RLOG_PARALLEL_ENABLE            = 0                     \#Whether to enable database to write redo logs in parallel mode\n		RLOG_IGNORE_TABLE_SET           = 1                     \#Whether ignore table set\n		RLOG_APPEND_LOGIC               = 0                     \#Type of logic records in redo logs\n		RLOG_APPEND_SYSTAB_LOGIC        = 0                     \#Whether to write logic records of system tables in redo logs when RLOG_APPEND_LOGIC is set as 1\n		RLOG_SAFE_SPACE                 = 256                   \#Free redo log size in megabytes that can be considered as a save value\n		RLOG_RESERVE_THRESHOLD          = 0                     \#Redo subsystem try to keep the used space of online redo less than this target\n		RLOG_RESERVE_SIZE               = 8192                  \#Number of reserved redo log pages for each operation\n		RLOG_SEND_APPLY_MON             = 64                    \#Monitor recently send or apply rlog_buf info\n		RLOG_COMPRESS_LEVEL             = 0                     \#The redo compress level,value in [0,10],0:do not compress\n		RLOG_ENC_CMPR_THREAD            = 4                     \#The redo log thread number of encrypt and compress task,value in [1,64],default 4\n		RLOG_PKG_SEND_ECPR_ONLY         = 0                     \#Only send encrypted or compressed data to standby instance without original data\n		DFS_RLOG_SEND_POLICY            = 1                     \#DFS rlog send policy, 0: sync; 1:async\n		RLOG_HASH_NAME                  =                       \#The name of the hash algorithm used for Redo log\n		DPC_LOG_INTERVAL                = 0                     \#Only MP is valid, control MP broadcasts generating logs of specific DW type regularly, value range (0,86400), the unit is in seconds, and the value of 0 means not to generate\n		RLOG_PKG_SEND_NUM               = 1                     \#Need wait standby database\'s response message after the number of rlog packages were sent\n		RLOG_RAFT_NEED_WAIT             = 3                     \#Whether to wait for sending RAFT rlog package when standby database is accumulated\n		RLOG_RAFT_WAIT_TIME             = 1000                  \#Waiting time of sending RAFT rlog package when standby database is accumulated\n		RLOG_SYNC_MODE                  = 0                     \#Redo log sync mode for primary, 0: need suspend when sync failed; 1: no need suspend when sync failed.\n		LOG_FILE_POSTFIX_NAME           = log                   \#The postfix name of archive log file\n		RLOG_PKG_4K_CRC                 = 0                     \#Whether set crc for every 4k data of rpkg\n		RLOG_PKG_SEND_TIME              = 0                     \#Time to check async standby database\'s response in seconds, 0: not check\n		RLOG_LLOG_UPD_TO_DEL_INS        = 0                      \#While updating from one partition to another, logic log is update or delete+insert; 0: update, 1: delete+insert\n		RLOG_LLOG_COMPRESS            = 0                     \#Whether to compress logic log, 0: not compress, 1: compress\n		LOGMNR_PARSE_LOB               = 0                    \#Whether to parse LOB logic log using DBMS_LOGMNR, 0: FALSE, 1: TRUE\n\n\#redo redos\n		REDO_PWR_OPT                    = 1                     \#Whether to enable PWR optimization when system restarted after failure\n		REDO_IGNORE_DB_VERSION          = 0                     \#Whether to check database version while database is redoing logs\n		REDO_BUF_SIZE                   = 64                    \#The max buffer size of rlog redo In Megabyte\n		REDOS_BUF_SIZE                  = 1024                  \#The max buffer size of rlog redo for standby In Megabyte\n		REDOS_MAX_DELAY                 = 1800                  \#The permitted max delay for one rlog buf redo on standby In Second\n		REDOS_BUF_NUM                   = 4096                  \#The max apply rlog buffer num of standby\n		REDOS_PRE_LOAD                  = 0                     \#Number of pre-load apply rlog buffer for standby\n		REDOS_PARALLEL_NUM              = 1                     \#The parallel redo thread num\n		REDOS_ENABLE_SELECT             = 1                     \#Enable select for standby\n		REDOS_FILE_PATH_POLICY          = 0                     \#Data files\' path policy when standby instance applies CREATE TABLESPACE redo log. 0:use the same file name under system path, 1:use the same file path under the system path\n		REDOS_PAGE_CRC_CHECK            = 0                     \#Whether check page crc, 0:NO, 1:YES\n\n\#transaction\n		ISOLATION_LEVEL                 = 1                     \#Default Transaction Isolation Level, 1: Read Commited; 3: Serializable\n		DDL_WAIT_TIME                   = 10                    \#Maximum waiting time in seconds for DDLs\n		BLDR_WAIT_TIME                  = 10                    \#Maximum waiting time in seconds for BLDR\n		MPP_WAIT_TIME                   = 10                    \#Maximum waiting time in seconds for locks on MPP\n		FAST_RELEASE_SLOCK              = 1                     \#Whether to release share lock as soon as possible\n		SESS_CHECK_INTERVAL             = 3                     \#Interval time in seconds for checking status of sessions\n		LOCK_TID_MODE                   = 1                     \#Lock mode for select-for-update operation\n		LOCK_TID_UPGRADE                = 0                     \#Upgrade tid lock to X mode, 0:no, 1:yes\n		NOWAIT_WHEN_UNIQUE_CONFLICT     = 0                     \#Whether to return immediately when unique constraint violation conflict happens\n		UNDO_EXTENT_NUM                 = 4                     \#Number of initial undo extents for each worker thread\n		MAX_DE_TIMEOUT                  = 10                    \#Maximum external function wait time in Seconds\n		TRX_RLOG_WAIT_MODE              = 0                     \#Trx rlog wait mode\n		TRANSACTIONS                    = 75                    \#Maximum number of concurrent transactions\n		MVCC_RETRY_TIMES                = 5                     \#Maximum retry times while MVCC conflicts happen\n		MVCC_PAGE_OPT                   = 1                     \#Page visible optimize for MVCC\n		ENABLE_FLASHBACK                = 0                     \#Whether to enable flashback function\n		UNDO_RETENTION                  = 90.000                \#Maximum retention time in seconds for undo pages since relative transaction is committed\n		PARALLEL_PURGE_FLAG             = 0                     \#flag for parallel purge of undo logs\n		PURGE_WAIT_TIME                 = 500                   \#Maximum wait time in microseconds for purging undo pages\n		PSEG_RECV                       = 3                     \#Whether to rollback active transactions and purge committed transactions when system restarts after failure\n		ENABLE_IGNORE_PURGE_REC         = 2                     \#Whether to ignore purged records when returning -7120\n		ENABLE_TMP_TAB_ROLLBACK         = 1                     \#enable temp table rollback\n		ROLL_ON_ERR                     = 0                     \#Rollback mode on Error, 0: rollback current statement 1: rollback whole transaction\n		XA_TRX_IDLE_TIME                = 60                    \#Xa transaction idle time\n		XA_TRX_LIMIT                    = 1024                  \#Maximum number of Xa transaction\n		LOB_MVCC                        = 1                     \#Whether LOB access in MVCC mode\n		LOCK_DICT_OPT                   = 2                     \#lock dict optimize\n		TRX_DICT_LOCK_NUM               = 64                    \#Maximum ignorable dict lock number\n		DEADLOCK_CHECK_INTERVAL         = 1000                  \#Time interval of deadlock check\n		COMMIT_WRITE                    = IMMEDIATE,WAIT        \#wait means normal commit; nowait may speed up commit, but may not assure ACID,immediate,batch just support syntax parsing\n		DPC_2PC                         = 1                     \#enable two-phase commit for dpc, 0: disable, 1: enable, 2/3: use snap_seq cache, 5: use local cmt_seq, 6/7: use both snap_seq cache and local cmt_seq\n		SWITCH_CONN                     = 0                     \#switch connect flag\n		UNDO_BATCH_FAST                 = 0                     \#Whether to undo batch insert fast\n		FLDR_LOCK_RETRY_TIMES           = 0                     \#Maximum retry times while MVCC conflicts happen\n		DPC_TRX_TIMEOUT                 = 10                    \#Maximum trx waiting time in seconds for DPC\n		SESSION_READONLY                = 0                     \#session readonly parameter value\n		DSC_LBS_REVOKE_DELAY            = 0                     \#LBS revoke delay\n		SELECT_LOCK_MODE                = 0                     \#Whether to use operator lock mode\n		ENABLE_SEC_RPTR                 = 0                     \#Whether to append roll address in secondary index\n		FINS_UNDO_OPT                   = 1                     \#Whether to undo fast insert in optimal mode, 0:no, 1:yes\n		PLSQL_AUTO_COMMIT                = 0                     \#Whether to commit the transaction after each statement in plsql\n		TRX_VIEW_POLICY                 = 0                     \#Transactions view policy: 0: sqls in plsql will not refresh transactions view; 1: each sql in plsql will refresh transactions view\n		HP_DDL_LOCK_MODE                = 0                     \#DDL lock policy of horization partition table\n		ENABLE_ENCRYPT                  = 0                     \#Encrypt Mode For Communication, 0: Without Encryption; 1: SSL Encryption; 2: SSL Authentication; 3: GmSSL\n		CLIENT_UKEY                     = 0                     \#Client ukey, 0: all, active by Client; 1: Force client ukey Authentication\n		MIN_SSL_VERSION                 = 771                   \#SSL minimum version For Communication, For example, 0: all, 0x0301: TLSv1, 0x0302: TLSv1.1, 0x0303: TLSv1.2, 0x0304: TLSv1.3\n		ENABLE_UDP                      = 0                     \#Enable udp For Communication, 0: disable; 1: single; 2: multi\n		UDP_MAX_IDLE                    = 15                    \#Udp max waiting time in second\n		UDP_BTU_COUNT                   = 8                     \#Count of udp batch transfer units\n		ENABLE_IPC                      = 0                     \#Enable ipc for communication, 0: disable; 1: enable\n		AUDIT_FILE_FULL_MODE            = 1                     \#operation mode when audit file is full,1: delete old file; 2: no longer to write audit records\n		AUDIT_SPACE_LIMIT               = 8192                  \#audit space limit in Megabytes\n		AUDIT_MAX_FILE_SIZE             = 100                   \#maximum audit file size in Megabytes\n		AUDIT_IP_STYLE                  = 0                     \#IP style in audit record, 0: IP, 1: IP(hostname), default 0\n		MSG_COMPRESS_TYPE               = 2                     \#Flag of message compression mode\n		LDAP_HOST                       =                       \#LDAP Server ip\n		COMM_ENCRYPT_NAME               =                       \#Communication encrypt name, if it is null then the communication is not encrypted\n		COMM_VALIDATE                   = 1                     \#Whether to validate message\n		MESSAGE_CHECK                   = 0                     \#Whether to check message body\n		EXTERNAL_JFUN_PORT              = 6363                  \#DmAgent port for external java fun.\n		EXTERNAL_AP_PORT                = 4236                  \#DmAp port for external fun.\n		ENABLE_PL_SYNONYM               = 0                     \#Whether try to resolve PL object name by synonym.\n		FORCE_CERTIFICATE_ENCRYPTION    = 0                     \#Whether to encrypt login user name and password use certificate\n		REGEXP_MATCH_PATTERN            = 0                     \#Regular expression match pattern, 0: support non-greedy match; 1: only support greedy match\n		UNIX_SOCKET_PATHNAME            =                       \#Unix socket pathname.\n		TCP_ACK_TIMEOUT                 = 0                     \#TCP ack timeout value\n		RESOURCE_FLAG                   = 0                     \#Flag of user\'s resources, 1: reset session connecting time with second\n		AUTH_ENCRYPT_NAME               =                       \#User password encrypt name\n		IPV6_ZID_FLAG                   = 1                     \#To use the auto NIC-adaption of ipv6 link-local or not, 0: No; 1: Yes\n		IPV6_ZID                        =                       \#The NIC Zone id to use in connection\n		GRANT_SCHEMA                    = 0                     \#Whether to allow to grant to schema\n		EFC_USE_AP                      = 1                     \#Whether to use AP when call external cfun\n		PASSWORD_VERIFICATION           = 0                    \#Mode of password verification, 0: default, 1: replace\n\n\#compatibility\n		BACKSLASH_ESCAPE                = 0                     \#Escape Mode For Backslash, 0: Not Escape; 1: Escape\n		STR_LIKE_IGNORE_MATCH_END_SPACE = 1                     \#Whether to ignore end space of strings in like clause\n		CLOB_LIKE_MAX_LEN               = 10240                 \#Maximum length in kilobytes of CLOB data that can be filtered by like clause\n		EXCLUDE_DB_NAME                 =                       \#THE db names which DM7 server can exclude\n		MS_PARSE_PERMIT                 = 0                     \#Whether to support SQLSERVER\'s parse style\n		COMPATIBLE_MODE                 = 0                     \#Server compatible mode, 0:none, 1:SQL92, 2:Oracle, 3:MS SQL Server, 4:MySQL, 5:DM6, 6:Teradata, 7:PG\n		ORA_DATE_FMT                    = 0                     \#Whether support oracle date fmt: 0:No, 1:Yes\n		JSON_MODE                       = 0                     \#Json compatible mode, 0:Oracle, 1:PG, 2:MySQL\n		DATETIME_FMT_MODE               = 0                     \#Datetime fmt compatible mode, 0:none, 1:Oracle\n		DOUBLE_MODE                     = 0                     \#Calc double fold mode, 0:8bytes, 1:6bytes\n		CASE_COMPATIBLE_MODE            = 1                     \#Case compatible mode, 0:none, 1:Oracle(simple case), 2:Oracle(simple case new rule), 4:Oracle(bool case)\n		XA_COMPATIBLE_MODE              = 0                     \#XA compatible mode, 0:none, 1:Oracle\n		EXCLUDE_RESERVED_WORDS          =                       \#Reserved words to be exclude\n		COUNT_64BIT                     = 1                     \#Whether to set data type for COUNT as BIGINT\n		CALC_AS_DECIMAL                 = 0                     \#Whether integer CALC as decimal, 0: no, 1:only DIV, 2:all only has charactor, 3:all for digit\n		CMP_AS_DECIMAL                  = 0                     \#Whether integer compare as decimal, 0: no, 1:part, 2:all\n		CAST_VARCHAR_MODE               = 1                     \#Whether to convert illegal string to special pseudo value when converting string to integer\n		PL_SQLCODE_COMPATIBLE           = 0                     \#Whether to set SQLCODE in PL/SQL compatible with ORACLE as far as possible\n		LEGACY_SEQUENCE                 = 0                     \#Whether sequence in legacy mode, 0: no, 1:yes\n		DM6_TODATE_FMT                  = 0                     \#To Date\' HH fmt hour system, 0: 12(defalut) , 1: 24(DM6)\n		MILLISECOND_FMT                 = 1                     \#Whether To show TO_CHAR\' millisecond, 0: no, 1:yes\n		NLS_DATE_FORMAT                 =                       \#Date format string\n		NLS_TIME_FORMAT                 =                       \#Time format string\n		NLS_TIMESTAMP_FORMAT            =                       \#Timestamp format string\n		NLS_TIME_TZ_FORMAT              =                       \#Time_tz format string\n		NLS_TIMESTAMP_TZ_FORMAT         =                       \#Timestamp_tz format string\n		PK_MAP_TO_DIS                   = 0                     \#Whether map pk cols into distributed cols automatically\n		PROXY_PROTOCOL_MODE             = 0                     \#PROXY PROTOCOL mode, 0: close; 1: open\n		SPACE_COMPARE_MODE              = 0                     \#Whether to compare suffix space of strings, 0: default, 1: yes\n		DATETIME_FAST_RESTRICT          = 1                     \#Wherther To DATE\'s datetime with time.default:1. 1: No. 0: Yes.\n		BASE64_LINE_FLAG                = 1                     \#Whether base64 encode persection with line flag: CR and LF. default: 1. 1:YES. 2:NO.\n		MY_STRICT_TABLES                = 1                     \#Whether to set STRICT_XXX_TABLES in MYSQL compatible mode. default: 1. 1:YES. 0:NO.\n		IN_CONTAINER                    = 0                     \#judge if dm is run in container.default:0.\n		ENABLE_RLS                      = 0                     \#Whether enable rls\n		NVARCHAR_LENGTH_IN_CHAR         = 1                     \#Whether nchar/nvarchar convert to character/varchar(n char) 1:yes,0:no\n		PARAM_DOUBLE_TO_DEC             = 0                     \#Whether to convert double parameter to decimal, 0: disable, 1: enable with check, 2, enable without check\n		INSERT_COLUMN_MATCH             = 0                     \#Insert column match, 0: DM, 1: Aster, 2: PG\n		AUTO_INCREMENT_INCREMENT        = 1                     \#Increment for each insert in AUTO_INCREMENT column\n		AUTO_INCREMENT_OFFSET           = 1                     \#Offset for values in AUTO_INCREMENT column\n		NO_AUTO_VALUE_ON_ZERO           = 1                     \#Whether using default value when inserting 0\n		IFUN_DATETIME_MODE              = 0                     \#The definition of DATETIME in sys function, 0:DATETIME(6), 1:DATETIME(9)\n		CAST_DIGIT_MODE                 = 1                     \#Whether to convert stronger digit type to weak digit type col\n		VIEW_ACCESS_MODE                = 0                     \#View access mode, 0:DM, 1:Oracle\n		ENABLE_FULL_WIDTH               = 1                     \#Enable full-width characters. 0: no, 1: yes.\n		IFUN_LEN_OPT                    = 3                     \#How to adjust the ifun return string\'s length\n		FLOAT_MODE                      = 0                     \#FLOAT mode, 0:DM; 1:ORACLE\n		DECIMAL_ENHANCED                = 1                     \#Whether to enhance decimal calculate and storage\n		DOUBLE_TO_DEC_MASK              = 1                     \#Mask code used when casting double or float to decimal, 0: %g automaticly; 1: %e directly when %g choose %e;\n		ARG_VARCHAR_ADJUST              = 0                     \#Control whether to enlarge the length of the varchar type parameter,0: Not enlarge, 1: enlarge\n		CTI_SCORE_MODE                 = 1                     \#How to calculate context index score, 0: Simplified algorithm, get score only using key word frequence; 1: Complete algorithm, get score from whole data;\n		CASE_CONVERSION_ENHANCED         = 1                    \#Whether to enhanced case conversion and compare, 0: default, 1: enhanced\n		TIME_MODE                       = 1                     \#Parse the time type starting from: 0:hour, 1:year\n		DROP_CASCADE_VIEW               = 0                     \#Whether to drop cascade view while dropping table or view\n		NUMBER_MODE                     = 0                     \#NUMBER mode, 0:DM; 1:ORACLE\n		NLS_SORT_TYPE                   = 0                     \#Chinese sort type, 0:default 1:pinyin 2:stroke 3:radical 4:thai 5:korean 6:binary 7:ganzhi\n		BATCH_INSERT_ROWS               = 10                    \#Batch insert rows\n		INDEX_FINS_FLAG                = 0                    \#Flag of fast insert second index\n\n\#request trace\n		SVR_LOG_NAME                    = SLOG_ALL              \#Using which sql log sys in sqllog.ini\n		SVR_LOG                         = 0                     \#Whether the Sql Log sys Is open or close. 1:open, 0:close, 2:use switch and detail mode. 3:use not switch and simple mode.\n\n\#system trace\n		GDB_THREAD_INFO                 = 0                     \#Generate gdb thread info while dm_sys_halt. 1: yes; 0: no\n		TRACE_PATH                      =                       \#System trace path name\n		SVR_OUTPUT                      = 0                     \#Whether print at background\n		SVR_ELOG_FREQ                   = 0                     \#How to switch svr elog file. 0: by month. 1: by day, 2: by hour, 3, by limit\n		ENABLE_OSLOG                    = 0                     \#Whether to enable os log\n		LOG_IN_SHOW_DEBUG               = 2147483647            \#Whether record log info\n		TRC_LOG                         = 0                     \#Whether the trace Log sys Is open or close. 0:close, other: switch_mod*4 + asyn_flag*2 + 1(switch_mode: 0:no_switch;1:by num;2:by size;3:by interval).\n		ELOG_SWITCH_LIMIT               = 0                     \#The upper limit to switch elog\n		ELOG_ERR_ARR                    =                       \#dmerrs need to generate elog\n		DICT_COMPLETE_CHECK             = 0                     \#Whether to halt when get incomplete dict\n		ELOG_FLAG                       = 0                     \#whether elog file name is fixed . 0: not fixed. 1: fixed\n		SMALL_TABLE_THRESHOLD           = 2560                  \#The boundary between short tables and large tables\n		ELOG_LANGUAGE_FLAG              = 0                     \#elog_language_flag, 1:CN, 0:EN\n		CORE_DUMP_FLAG                  = 1                     \#Whether to dump some info before core\n\n\#ecs\n		ENABLE_ECS                      = 0                     \#Whether to enable elastic calc system\n		ECS_HB_INTERVAL                 = 60                    \#HB interval for elastic calc system\n		EP_GROUP_NAME                   = DMGROUP               \#Server group name as worker\n		AP_GROUP_NAME                   = DMGROUP               \#Server group name as cooperative worker\n		DCRS_IP                         = LOCALHOST             \#IP on which the dcrs server will listen\n		DCRS_PORT_NUM                   = 6236                  \#Port number on which the database dcrs will listen\n		AP_IP                           = LOCALHOST             \#The ap server IP for dcrs\n		AP_PORT_NUM                     = 0                     \#Port number on which the database ap will listen\n		AP_PARALLEL_DEGREE              = 10                    \#Maximum degree of parallel for ap\n		ENABLE_ECS_MSG_CHECK            = 0                     \#Whether to enable elastic check msg accumulate\n\n\#monitor\n		ENABLE_MONITOR                  = 1                     \#Whether to enable monitor\n		MONITOR_SQL_EXEC                = 0                     \#Whether to enable monitor sql execute\n		ENABLE_FREQROOTS                = 0                     \#Whether to collect pages that used frequently\n		MAX_FREQ_ROOTS                  = 200000                \#Maximum number of frequently used pages that will be collected\n		MIN_FREQ_CNT                    = 100000                \#Minimum access counts of page that will be collected as frequently used pages\n		LARGE_MEM_THRESHOLD             = 10000                 \#Large mem used threshold by k\n		ENABLE_MONITOR_DMSQL            = 1                     \#Flag of performance monitoring:sql or method exec time.0: NO. 1: YES.\n		ENABLE_TIMER_TRIG_LOG           = 0                     \#Whether to enable timer trigger log\n		IO_TIMEOUT                      = 300                   \#Maximum time in seconds that read from disk or write to disk\n		ENABLE_MONITOR_BP               = 1                     \#Whether to enable monitor bind param. 1: TRUE. 0:FALSE. default:1\n		LONG_EXEC_SQLS_CNT              = 1000                  \#Max row count of V$LONG_EXEC_SQLS\n		SYSTEM_LONG_EXEC_SQLS_CNT       = 300                   \#Max row count of V$SYSTEM_LONG_EXEC_SQLS\n		SQL_HISTORY_CNT                 = 10000                 \#Max row count of V$SQL_HISTORY\n		BP_ITEM_MAXSIZE                 = 50                    \#The maximum memory size of BINDDATA column on V$SQL_BINDDATA_HISTORY in Kbytes\n		MONITOR_SQL_PARSE               = 0                     \#Whether to enable monitor sql parse\n		RT_ERR_HISTORY_CNT              = 5000                  \#Max row count of V$RUNTIME_ERR_HISTORY\n		ENABLE_MONITOR_PLNHIST          = 0                     \#Whether to enable monitor sql plan history\n\n\#data watch\n		DW_MAX_SVR_WAIT_TIME            = 0                     \#Maximum time in seconds that server will wait for DMWATCHER to startup\n		DW_INACTIVE_INTERVAL            = 60                    \#Time in seconds that used to determine whether DMWATCHER exist\n		DW_PORT                         = 0                     \#Instance tcp port for watch2\n		ALTER_MODE_STATUS               = 1                     \#Whether to permit database user to alter database mode and status by SQLs, 1: yes, 0: no\n		ENABLE_OFFLINE_TS               = 1                     \#Whether tablespace can be offline\n		SESS_FREE_IN_SUSPEND            = 60                    \#Time in seconds for releasing all sessions in suspend mode after archive failed\n		SUSPEND_WORKER_TIMEOUT          = 180                   \#Suspend worker thread timeout in seconds\n		DW_CONSISTENCY_CHECK            = 0                     \#Whether to check consistency for standby database, 1: yes, 0: no\n		DW_ARCH_SPACE_CHECK             = 0                     \#Whether to check archive space for standby database, 1: yes, 0: no\n		DW_SUSPEND_TIME                 = 60                    \#The duration of SUSPEND status in seconds for async recovery, 0: not check.\n		DW_ARCH_HANG_CHECK              = 0                     \#Whether to check archive space for primary database, 1: yes, 0: no\n\n\#for context index\n		CTI_HASH_SIZE                   = 100000                \#the hash table size for context index query\n		CTI_HASH_BUF_SIZE               = 50                    \#the hash table cache size in Megabytes for context index query\n		USE_FORALL_ATTR                 = 0                     \#Whether to use cursor attributes of FORALL statements\n		ALTER_TABLE_OPT                 = 0                     \#Whether to optimize ALTER TABLE operation(add, modify or drop column)\n		USE_RDMA                        = 0                     \#Whether to use rdma\n\n\#configuration file\n		MAL_INI                         = 0                     \#dmmal.ini\n		ARCH_INI                        = 0                     \#dmarch.ini\n		REP_INI                         = 0                     \#dmrep.ini\n		LLOG_INI                        = 0                     \#dmllog.ini\n		TIMER_INI                       = 0                     \#dmtimer.ini\n		MPP_INI                         = 0                     \#dmmpp.ini\n		DFS_INI                         = 0                     \#dmdfs.ini\n		DSC_N_CTLS                      = 132096                \#Number Of LBS/GBS ctls\n		DSC_N_POOLS                     = 19                    \#Number Of LBS/GBS pools\n		DSC_USE_SBT                     = 1                     \#Use size balanced tree\n		DSC_TRX_CMT_LSN_SYNC            = 3                     \#Whether to adjust lsn when trx commit\n		DSC_ENABLE_MONITOR              = 1                     \#Whether to monitor request time\n		DSC_GBS_REVOKE_OPT              = 0                     \#Whether to optimize GBS revoke\n		DSC_TRX_VIEW_SYNC               = 1                     \#Whether to wait response after broadcast trx view to other ep\n		DSC_TRX_VIEW_BRO_INTERVAL       = 1000                  \#Time interval of trx view broadcast\n		DSC_REMOTE_READ_MODE            = 1                     \#PAGE remote read optimize mode\n		DSC_TRX_CMT_OPT                 = 0                     \#Whether to wait rlog file flush when trx commit in DSC\n		DSC_RESERVE_PERCENT             = 0.080                 \#Start ctl reserve percent\n		DSC_TABLESPACE_BALANCE          = 0                     \#Enable DSC load balance by tablespace\n		DSC_FREQ_INTERVAL               = 30                    \#High frequency conflict intervals\n		DSC_FREQ_CONFLICT               = 8                     \#High frequency conflict counts\n		DSC_FREQ_DELAY                  = 0                     \#High frequency conflict delay\n		DSC_INSERT_LOCK_ROWS            = 10                    \#Insert extra lock rows for DSC\n		DSC_CRASH_RECV_POLICY           = 0                     \#Policy of handling node crash\n		DSC_LBS_REVOKE_DELAY            = 0                     \#LBS revoke delay\n		DSC_REQUEST_TIMEOUT             = 3600                  \#DSC request timeout in seconds\n		DSC_SLOT_WAIT_TIMEOUT           = 600                   \#DSC request timeout in seconds\n\n\#other\n		IDLE_MEM_THRESHOLD              = 50                    \#minimum free memory warning size in Megabytes\n		IDLE_DISK_THRESHOLD             = 1000                  \#minimum free disk space warning size in Megabytes\n		IDLE_SESS_THRESHOLD             = 5                     \#minimum available session threshold value\n		ENABLE_PRISVC                   = 0                     \#Whether to enable priority service\n		HA_INST_CHECK_IP                =                       \#HA instance check IP\n		HA_INST_CHECK_PORT              = 65534                 \#HA instance check port\n		PWR_FLUSH_PAGES                 = 1000                  \#Make special PWR rrec when n pages flushed\n		REDO_UNTIL_LSN                  =                       \#redo until lsn\n		IGNORE_FILE_SYS_CHECK           = 1                     \#ignore file sys check while starup\n		FILE_SCAN_PERCENT               = 100.00                \#percent of data scanned when calculating file used space\n		STARTUP_CHECKPOINT              = 0                     \#checkpoint immediately when startup after redo\n		CHECK_SVR_VERSION               = 1                     \#Whether to check server version\n		ID_RECYCLE_FLAG                 = 0                     \#Enable ID recycle\n		ENABLE_DBLINK_TO_INV            = 0                     \#Whether to convert correlated subquery which has dblink to temporary function\n		ENABLE_BLOB_CMP_FLAG            = 1                     \#Whether BLOB/TEXT types are allowed to be compared;0:not allowed;1.allowed and text turn to char/varchar;2.allowed and char/varchar turn to text.\n		ENABLE_CREATE_BM_INDEX_FLAG     = 1                     \#Allow bitmap index to be created\n		CVIEW_STAR_WITH_PREFIX          = 1                     \#Whether append prefix for star item when create view\n		ENABLE_ADJUST_NLI_COST          = 1                     \#Whether adjust cost of nest loop inner join\n		ENABLE_SEQ_REUSE                = 0                     \#Whether allow reuse sequence expressions\n		RLS_CACHE_SIZE                  = 100000                \#Max number of objects for RLS cache.\n		ENABLE_ADJUST_DIST_COST         = 0                     \#Whether adjust cost of distinct\n		ID_RECYCLE_THRESHOLD            = 60                    \#ID recycle threshold\n		BAK_USE_AP                      = 1                     \#backup use assistant plus-in, 1:use AP; 2:not use AP. default 1.\n		BAK_DIRECT_IO                   = 0                     \#whether to enable direct io during backup\n		BAK_SAFE_CHECK                  = 1                     \#whether to check corrupt data during backup\n		BAK_TIMEOUT                     = 30                    \#Timeout interval of operations during backup\n		ENABLE_BCT                      = 0                     \#Whether to enable BCT\n		BCT_POOL_SIZE                   = 256                   \#BCT memory pool size in Megabytes\nADAPTIVE_NPLN_FLAG=3\nBDTA_SIZE=588\nBTR_SPLIT_MODE=1\nBUFFER=9780\nBUFFER_POOLS=38\nCACHE_POOL_SIZE=415\nCASE_WHEN_CVT_IFUN=7\nCKPT_DIRTY_PAGES=0\nCKPT_FLUSH_PAGES=1000\nCKPT_FLUSH_RATE=5\nCKPT_INTERVAL=180\nCKPT_RLOG_SIZE=128\nCKPT_WAIT_PAGES=1024\nCOMM_VALIDATE=0\nCOMPLEX_VIEW_MERGING=1\nDECIMAL_FIX_STORAGE=1\nDICT_BUF_SIZE=52\nDIRECT_IO=1\nENABLE_FREQROOTS=3\nENABLE_HASH_JOIN=0\nENABLE_INDEX_JOIN=1\nENABLE_IN_VALUE_LIST_OPT=6\nENABLE_MERGE_JOIN=1\nENABLE_MONITOR=0\nENHANCED_BEXP_TRANS_GEN=2\nFAST_POOL_PAGES=3282\nFAST_RELEASE_SLOCK=0\nFAST_ROLL_PAGES=1100\nFIRST_ROWS=108\nFORCE_FLUSH_PAGES=778\nGROUP_OPT_FLAG=3\nHAGR_BLK_SIZE=44\nHAGR_BUF_GLOBAL_SIZE=9073\nHAGR_BUF_SIZE=747\nHASH_PLL_OPT_FLAG=15\nHIO_THR_GROUPS=3\nHJ_BUF_GLOBAL_SIZE=49847\nHJ_BUF_SIZE=2561\nHUGE_BUFFER=218\nHUGE_BUFFER_POOLS=223\nHUGE_MEMORY_PERCENTAGE=88\nINDEX_SKIP_SCAN_RATE=0.6441145535483827\nIO_THR_GROUPS=47\nJOIN_HASH_SIZE=1346675\nLIKE_OPT_FLAG=32\nLOCK_DICT_OPT=0\nMEMORY_EXTENT_SIZE=6\nMEMORY_POOL=1237\nMEMORY_TARGET=15673\nMSG_COMPRESS_TYPE=1\nNBEXP_OPT_FLAG=7\nNONREFED_SUBQUERY_AS_CONST=1\nNOWAIT_WHEN_UNIQUE_CONFLICT=1\nOPTIMIZER_AGGR_GROUPBY_ELIM=0\nOUTER_CVT_INNER_PULL_UP_COND_FLAG=2\nPARALLEL_PURGE_FLAG=1\nPHC_MODE_ENFORCE=10\nPSEG_RECV=3\nPURGE_DEL_OPT=2\nPURGE_WAIT_TIME=500\nRECYCLE=107\nRECYCLE_POOLS=27\nREFED_SUBQ_CROSS_FLAG=0\nRLOG_BUF_SIZE=64\nRLOG_PARALLEL_ENABLE=1\nRLOG_POOL_SIZE=1623\nSESS_POOL_SIZE=484606\nSESS_POOL_TARGET=591386\nSORT_BUF_SIZE=1016\nSPEED_SEMI_JOIN_PLAN=11\nTRX_VIEW_SIZE=5926\nUNDO_EXTENT_NUM=736\nUNDO_RETENTION=869\nUPD_DEL_OPT=0\nVIEW_FILTER_MERGING=220\nVM_MEM_HEAP=1\nVM_POOL_SIZE=404\nVM_POOL_TARGET=18585\nWORKER_THREADS=6\nWORK_THRD_RESERVE_SIZE=225\nWORK_THRD_STACK_SIZE=7811\n'

    return JsonResponse({"dmini" : dmini})

# 查询硬件参数
def hardwarePara(request):
    # 获取所有参数记录
    parameters = SystemParameter.objects.using('mysql').all().values()

    parameters_list = list(parameters)

    return JsonResponse(parameters_list, safe=False)

# 查询第n轮tmpC值
@require_http_methods(["POST"])
def tmpC(request):
    data = json.loads(request.body)

    epoch = int(data.get('epoch'))

    tmpc = TpmC.objects.using('mysql').filter(id=epoch).first()

    if tmpc:
        # 如果找到匹配的记录
        response_data = {
            'tmpc': tmpc.value
        }
    else:
        # 如果没有找到匹配的记录
        response_data = {
            'error': 'No matching record found'
        }

    return JsonResponse(response_data)


# 查询第n轮dm数据库参数
@require_http_methods(["POST"])
def trainingPara(request):
    try:
        data = json.loads(request.body)
        epoch = data.get('epoch')

        # 根据 epoch 查找 TrainingConfiguration
        config = get_object_or_404(TrainingConfiguration.objects.using('mysql'), id=epoch)

        # 获取所有参数字段
        config_dict = config.__dict__

        result = []
        for field in config._meta.fields:
            if field.name != 'id':
                param_name = field.name
                param_value = getattr(config, param_name)

                # 查找 PrimaryPara 中的描述
                param_description = PrimaryPara.objects.using('mysql').filter(name=param_name).first()
                description = param_description.description if param_description else "No description available"

                result.append({
                    "name": param_name,
                    "value": param_value,
                    "description": description
                })

        return JsonResponse(result, safe=False)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except TrainingConfiguration.DoesNotExist:
        return JsonResponse({'error': 'Configuration not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid HTTP method'}, status=405)


# 根据run_mins，查看是否有更新训练数据，如果更新就返回数据字典
def TrainingData(request):
    # 查看是否更新
    item_para = ItemPara.objects.using('mysql').filter(id=1).get()
    is_update = item_para.IS_ALGORITHM_UPDATE

    if is_update == 'T':
        # 查看run_mins
        propsrun = PropsDM.objects.using('mysql').filter(id=1).get()
        run_mins = propsrun.runMins

        # 去对应的表获取最新数据
        training_class_name = f'TrainingConfiguration_runMin{run_mins}'   # 动态获取模型类
        training_class = globals()[training_class_name]

        last_traing_data = training_class.objects.using('mysql').latest('id')   # 最新一行训练数据

        print(last_traing_data)

        # 把last_traing_data改造一下

    else:
        return JsonResponse({'message' : 'no update'})



# 返回csrf-token
# @ensure_csrf_cookie
# def get_csrf_token(request):
#     csrf_token = get_token(request)
#     return JsonResponse({'csrfToken': csrf_token})

# 修改红色参数
@require_http_methods(["POST"])
# @csrf_exempt
def modifyRedPara(request):
    try:
        # 解析请求体中的JSON数据
        data = json.loads(request.body)

        # 获取数据
        name = data.get('name')
        value = float(data.get('value'))
        min_value = float(data.get('minValue'))
        max_value = float(data.get('maxValue'))
        description = data.get('description')

        # 查找并更新记录
        parameter, created = PrimaryPara.objects.using('mysql').update_or_create(
            name=name,
            defaults={'value': value, 'minValue': min_value, 'maxValue': max_value, 'description': description}
        )

        return JsonResponse({'message': 'Parameter updated successfully.'}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# 修改蓝色参数
@require_http_methods(["POST"])
# @csrf_exempt
def modifyBluePara(request):
    try:
        # 解析请求体中的JSON数据
        data = json.loads(request.body)

        # 获取数据
        name = data.get('name')
        value = float(data.get('value'))
        min_value = float(data.get('minValue'))
        max_value = float(data.get('maxValue'))
        description = data.get('description')

        # 查找并更新记录
        parameter, created = SecondaryPara.objects.using('mysql').update_or_create(
            name=name,
            defaults={'value': value, 'minValue': min_value, 'maxValue': max_value, 'description': description}
        )

        return JsonResponse({'message': 'Parameter updated successfully.'}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# 修改benchmark参数
@require_http_methods(["POST"])
# @csrf_exempt
def modifyBenchmarkPara(request):
    try:
        data = json.loads(request.body)
        props_dm = PropsDM.objects.using('mysql').get(id = 1)  # 更新 id=1 的记录
        props_dm.db = data.get('db', props_dm.db)
        props_dm.driver = data.get('driver', props_dm.driver)
        props_dm.conn = data.get('conn', props_dm.conn)
        props_dm.user = data.get('user', props_dm.user)
        props_dm.password = data.get('password', props_dm.password)
        props_dm.warehouses = data.get('warehouses', props_dm.warehouses)
        props_dm.loadWorkers = data.get('loadWorkers', props_dm.loadWorkers)
        props_dm.terminals = data.get('terminals', props_dm.terminals)
        props_dm.runTxnsPerTerminal = data.get('runTxnsPerTerminal', props_dm.runTxnsPerTerminal)
        props_dm.runMins = data.get('runMins', props_dm.runMins)
        props_dm.limitTxnsPerMin = data.get('limitTxnsPerMin', props_dm.limitTxnsPerMin)
        props_dm.terminalWarehouseFixed = data.get('terminalWarehouseFixed', props_dm.terminalWarehouseFixed)
        props_dm.newOrderWeight = data.get('newOrderWeight', props_dm.newOrderWeight)
        props_dm.paymentWeight = data.get('paymentWeight', props_dm.paymentWeight)
        props_dm.orderStatusWeight = data.get('orderStatusWeight', props_dm.orderStatusWeight)
        props_dm.deliveryWeight = data.get('deliveryWeight', props_dm.deliveryWeight)
        props_dm.stockLevelWeight = data.get('stockLevelWeight', props_dm.stockLevelWeight)
        props_dm.save()

        # 更新服务器props.dm或props_table.dm
        props = PropsDM.objects.using('mysql').get(id=1)  # 假设你要获取id为1的记录
        propsrun = PropsTotalCommand(props=props)
        propsrun.update()  # 更新props.dm和props_table.dm

        return JsonResponse({'status': 'success', 'message': 'Data updated successfully'}, status=200)
    except PropsDM.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Record not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

# 修改硬件参数
@require_http_methods(["POST"])
# @csrf_exempt
def modifyHardwarePara(request):
    try:
        # 解析请求体中的JSON数据
        data = json.loads(request.body)

        # 获取数据
        name = data.get('name')
        value = float(data.get('value'))
        min_value = float(data.get('minValue'))
        max_value = float(data.get('maxValue'))
        description = data.get('description')

        # 查找并更新记录
        parameter, created = SystemParameter.objects.using('mysql').update_or_create(
            name=name,
            defaults={'value': value, 'minValue': min_value, 'maxValue': max_value, 'description': description}
        )

        return JsonResponse({'message': 'Parameter updated successfully.'}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


# 创建表 & load数据 & 创建索引 & 压测
@require_http_methods(["POST"])
def runCommand(request):
    try:
        data = json.loads(request.body)
        run_type = data.get('run_type')

        props = PropsDM.objects.using('mysql').get(id=1)  # 假设你要获取id为1的记录
        propsrun = PropsTotalCommand(props=props)

        propsrun.run(run_type=run_type) # 运行对应指令

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# 压测
def runBenchMark(request):
    # 获取数据库中的配置
    props = PropsDM.objects.using('mysql').get(id=1)  # 假设你要获取id为1的记录

    # 原始字符串
    content = """db=dameng
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

    # 替换字符串中的内容
    content = content.replace("dameng", props.db)
    content = content.replace("dm.jdbc.driver.DmDriver", props.driver)
    content = content.replace("jdbc:dm://localhost:5236", props.conn)
    content = content.replace("BENCHMARKSQL", props.user)
    content = content.replace("123456789", props.password)
    content = content.replace("warehouses=100", f"warehouses={props.warehouses}")
    content = content.replace("loadWorkers=200", f"loadWorkers={props.loadWorkers}")
    content = content.replace("terminals=100", f"terminals={props.terminals}")
    content = content.replace("runTxnsPerTerminal=0", f"runTxnsPerTerminal={props.runTxnsPerTerminal}")
    content = content.replace("runMins=1", f"runMins={props.runMins}")
    content = content.replace("limitTxnsPerMin=0", f"limitTxnsPerMin={props.limitTxnsPerMin}")
    content = content.replace("terminalWarehouseFixed=true",
                              f"terminalWarehouseFixed={'true' if props.terminalWarehouseFixed else 'false'}")
    content = content.replace("newOrderWeight=45", f"newOrderWeight={props.newOrderWeight}")
    content = content.replace("paymentWeight=43", f"paymentWeight={props.paymentWeight}")
    content = content.replace("orderStatusWeight=4", f"orderStatusWeight={props.orderStatusWeight}")
    content = content.replace("deliveryWeight=4", f"deliveryWeight={props.deliveryWeight}")
    content = content.replace("stockLevelWeight=4", f"stockLevelWeight={props.stockLevelWeight}")

    with open("props.dm", "w") as file:
        file.write(content)

    result = subprocess.run(['cp', 'props.dm', '/home/dmdba/benchmarksql-5.0/run/props.dm'], check=True, text=True, capture_output=True)

    # 压测
    benchmark = 'su - dmdba -c "cd /home/dmdba/benchmarksql-5.0/run/ && ./runBenchmark.sh ./props.dm"' # -c前面是角色设置
    process = subprocess.Popen(benchmark, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    process.wait()
    # # 等待命令完成并获取输出
    # print(process.stdout.read())
    # print("-------------------")

    # ...wait for a minute

    # the other command

    return HttpResponse(f"{process.stdout.read()}")


def ChatRoom(request):
    return render(request, 'ChatRoom.html')



