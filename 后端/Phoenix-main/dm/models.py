from django.db import models

# Create your models here.

# 红色参数
class PrimaryPara(models.Model):
    name = models.CharField(max_length=100)
    value = models.FloatField()
    minValue = models.FloatField()
    maxValue = models.FloatField()
    description = models.TextField(null=True, blank=True)
    rating = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'primary_para'

    def __str__(self):
        return self.name

# 蓝色参数
class SecondaryPara(models.Model):
    name = models.CharField(max_length=100)
    value = models.FloatField()
    minValue = models.FloatField()
    maxValue = models.FloatField()
    description = models.TextField(null=True, blank=True)
    rating = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'secondary_para'

    def __str__(self):
        return self.name

# benchmark_para
class PropsDM(models.Model):
    db = models.CharField(max_length=255, default='dameng')
    driver = models.CharField(max_length=255, default='dm.jdbc.driver.DmDriver')
    conn = models.CharField(max_length=255, default='jdbc:dm://localhost:5236')
    user = models.CharField(max_length=255, default='BENCHMARKSQL')
    password = models.CharField(max_length=255, default='123456789')
    warehouses = models.IntegerField(default=100)
    loadWorkers = models.IntegerField(default=100)
    terminals = models.IntegerField(default=200)
    runTxnsPerTerminal = models.IntegerField(default=0)
    runMins = models.IntegerField(default=1)
    limitTxnsPerMin = models.IntegerField(default=0)
    terminalWarehouseFixed = models.BooleanField(default=True)
    newOrderWeight = models.IntegerField(default=45)
    paymentWeight = models.IntegerField(default=43)
    orderStatusWeight = models.IntegerField(default=4)
    deliveryWeight = models.IntegerField(default=4)
    stockLevelWeight = models.IntegerField(default=4)

    class Meta:
        db_table = 'props_dm'

    def __str__(self):
        return f"{self.db} Configurations"

# hardware_para
class SystemParameter(models.Model):
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=100)
    minValue = models.CharField(max_length=100)
    maxValue = models.CharField(max_length=100)
    description = models.TextField()

    class Meta:
        db_table = 'hardware_para'

    def __str__(self):
        return self.name


# TPMC
class TpmC(models.Model):
    value = models.IntegerField()

    class Meta:
        db_table = 'tpmc'

    def __str__(self):
        return self.name

class ItemPara(models.Model):
    IS_ALGORITHM_UPDATE = models.CharField(max_length=10)
    IS_PAUSED = models.CharField(max_length=10)
    IS_STOPPED = models.CharField(max_length=10)
    Min1 = models.IntegerField()
    Min2 = models.IntegerField()
    Min3 = models.IntegerField()
    Min4 = models.IntegerField()
    Min5 = models.IntegerField()
    Min6 = models.IntegerField()
    Min7 = models.IntegerField()
    Min8 = models.IntegerField()
    Min9 = models.IntegerField()
    Min10 = models.IntegerField()

    class Meta:
        db_table = 'item_para'

    def __str__(self):
        return f"ConfigurationData({self.id})"



# model training para
class TrainingConfiguration(models.Model):
    ADAPTIVE_NPLN_FLAG = models.FloatField()
    BDTA_SIZE = models.FloatField()
    BTR_SPLIT_MODE = models.FloatField()
    BUFFER = models.FloatField()
    BUFFER_POOLS = models.FloatField()
    CACHE_POOL_SIZE = models.FloatField()
    CASE_WHEN_CVT_IFUN = models.FloatField()
    CKPT_DIRTY_PAGES = models.FloatField()
    CKPT_FLUSH_PAGES = models.FloatField()
    CKPT_FLUSH_RATE = models.FloatField()
    CKPT_INTERVAL = models.FloatField()
    CKPT_RLOG_SIZE = models.FloatField()
    CKPT_WAIT_PAGES = models.FloatField()
    COMM_VALIDATE = models.FloatField()
    COMPLEX_VIEW_MERGING = models.FloatField()
    DECIMAL_FIX_STORAGE = models.FloatField()
    DICT_BUF_SIZE = models.FloatField()
    DIRECT_IO = models.FloatField()
    ENABLE_FREQROOTS = models.FloatField()
    ENABLE_HASH_JOIN = models.FloatField()
    ENABLE_INDEX_JOIN = models.FloatField()
    ENABLE_IN_VALUE_LIST_OPT = models.FloatField()
    ENABLE_MERGE_JOIN = models.FloatField()
    ENABLE_MONITOR = models.FloatField()
    ENHANCED_BEXP_TRANS_GEN = models.FloatField()
    FAST_POOL_PAGES = models.FloatField()
    FAST_RELEASE_SLOCK = models.FloatField()
    FAST_ROLL_PAGES = models.FloatField()
    FIRST_ROWS = models.FloatField()
    FORCE_FLUSH_PAGES = models.FloatField()
    GROUP_OPT_FLAG = models.FloatField()
    HAGR_BLK_SIZE = models.FloatField()
    HAGR_BUF_GLOBAL_SIZE = models.FloatField()
    HAGR_BUF_SIZE = models.FloatField()
    HASH_PLL_OPT_FLAG = models.FloatField()
    HIO_THR_GROUPS = models.FloatField()
    HJ_BUF_GLOBAL_SIZE = models.FloatField()
    HJ_BUF_SIZE = models.FloatField()
    HUGE_BUFFER = models.FloatField()
    HUGE_BUFFER_POOLS = models.FloatField()
    HUGE_MEMORY_PERCENTAGE = models.FloatField()
    INDEX_SKIP_SCAN_RATE = models.FloatField()
    IO_THR_GROUPS = models.FloatField()
    JOIN_HASH_SIZE = models.FloatField()
    LIKE_OPT_FLAG = models.FloatField()
    LOCK_DICT_OPT = models.FloatField()
    MEMORY_EXTENT_SIZE = models.FloatField()
    MEMORY_POOL = models.FloatField()
    MEMORY_TARGET = models.FloatField()
    MSG_COMPRESS_TYPE = models.FloatField()
    NBEXP_OPT_FLAG = models.FloatField()
    NONREFED_SUBQUERY_AS_CONST = models.FloatField()
    NOWAIT_WHEN_UNIQUE_CONFLICT = models.FloatField()
    OPTIMIZER_AGGR_GROUPBY_ELIM = models.FloatField()
    OUTER_CVT_INNER_PULL_UP_COND_FLAG = models.FloatField()
    PARALLEL_PURGE_FLAG = models.FloatField()
    PHC_MODE_ENFORCE = models.FloatField()
    PSEG_RECV = models.FloatField()
    PURGE_DEL_OPT = models.FloatField()
    PURGE_WAIT_TIME = models.FloatField()
    RECYCLE = models.FloatField()
    RECYCLE_POOLS = models.FloatField()
    REFED_SUBQ_CROSS_FLAG = models.FloatField()
    RLOG_BUF_SIZE = models.FloatField()
    RLOG_PARALLEL_ENABLE = models.FloatField()
    RLOG_POOL_SIZE = models.FloatField()
    SESS_POOL_SIZE = models.FloatField()
    SESS_POOL_TARGET = models.FloatField()
    SORT_BUF_SIZE = models.FloatField()
    SPEED_SEMI_JOIN_PLAN = models.FloatField()
    TRX_VIEW_SIZE = models.FloatField()
    UNDO_EXTENT_NUM = models.FloatField()
    UNDO_RETENTION = models.FloatField()
    UPD_DEL_OPT = models.FloatField()
    VIEW_FILTER_MERGING = models.FloatField()
    VM_MEM_HEAP = models.FloatField()
    VM_POOL_SIZE = models.FloatField()
    VM_POOL_TARGET = models.FloatField()
    WORKER_THREADS = models.FloatField()
    WORK_THRD_RESERVE_SIZE = models.FloatField()
    WORK_THRD_STACK_SIZE = models.FloatField()

    class Meta:
        db_table = 'training_configuration'

    def __str__(self):
        return f"ConfigurationData({self.id})"

class TrainingConfiguration_runMin1(models.Model):
    TPMC = models.FloatField()
    RECYCLE = models.FloatField()
    FAST_ROLL_PAGES = models.FloatField()
    HAGR_BUF_SIZE = models.FloatField()
    HJ_BLK_SIZE = models.FloatField()
    HUGE_BUFFER = models.FloatField()
    WORK_THRD_RESERVE_SIZE = models.FloatField()
    BUFFER = models.FloatField()
    SORT_BUF_SIZE = models.FloatField()
    HJ_BUF_GLOBAL_SIZE = models.FloatField()
    FAST_POOL_PAGES = models.FloatField()
    MEMORY_POOL = models.FloatField()
    MEMORY_TARGET = models.FloatField()
    HAGR_BUF_GLOBAL_SIZE = models.FloatField()
    MVCC_RETRY_TIMES = models.FloatField()

    class Meta:
        db_table = 'training_configuration_runMin1'

    def __str__(self):
        return f"ConfigurationData({self.id})"

class TrainingConfiguration_runMin2(models.Model):
    TPMC = models.FloatField()
    RECYCLE = models.FloatField()
    FAST_ROLL_PAGES = models.FloatField()
    HAGR_BUF_SIZE = models.FloatField()
    HJ_BLK_SIZE = models.FloatField()
    HUGE_BUFFER = models.FloatField()
    WORK_THRD_RESERVE_SIZE = models.FloatField()
    BUFFER = models.FloatField()
    SORT_BUF_SIZE = models.FloatField()
    HJ_BUF_GLOBAL_SIZE = models.FloatField()
    FAST_POOL_PAGES = models.FloatField()
    MEMORY_POOL = models.FloatField()
    MEMORY_TARGET = models.FloatField()
    HAGR_BUF_GLOBAL_SIZE = models.FloatField()
    MVCC_RETRY_TIMES = models.FloatField()

    class Meta:
        db_table = 'training_configuration_runMin2'

    def __str__(self):
        return f"ConfigurationData({self.id})"

class TrainingConfiguration_runMin3(models.Model):
    TPMC = models.FloatField()
    RECYCLE = models.FloatField()
    FAST_ROLL_PAGES = models.FloatField()
    HAGR_BUF_SIZE = models.FloatField()
    HJ_BLK_SIZE = models.FloatField()
    HUGE_BUFFER = models.FloatField()
    WORK_THRD_RESERVE_SIZE = models.FloatField()
    BUFFER = models.FloatField()
    SORT_BUF_SIZE = models.FloatField()
    HJ_BUF_GLOBAL_SIZE = models.FloatField()
    FAST_POOL_PAGES = models.FloatField()
    MEMORY_POOL = models.FloatField()
    MEMORY_TARGET = models.FloatField()
    HAGR_BUF_GLOBAL_SIZE = models.FloatField()
    MVCC_RETRY_TIMES = models.FloatField()

    class Meta:
        db_table = 'training_configuration_runMin3'

    def __str__(self):
        return f"ConfigurationData({self.id})"

class TrainingConfiguration_runMin4(models.Model):
    TPMC = models.FloatField()
    RECYCLE = models.FloatField()
    FAST_ROLL_PAGES = models.FloatField()
    HAGR_BUF_SIZE = models.FloatField()
    HJ_BLK_SIZE = models.FloatField()
    HUGE_BUFFER = models.FloatField()
    WORK_THRD_RESERVE_SIZE = models.FloatField()
    BUFFER = models.FloatField()
    SORT_BUF_SIZE = models.FloatField()
    HJ_BUF_GLOBAL_SIZE = models.FloatField()
    FAST_POOL_PAGES = models.FloatField()
    MEMORY_POOL = models.FloatField()
    MEMORY_TARGET = models.FloatField()
    HAGR_BUF_GLOBAL_SIZE = models.FloatField()
    MVCC_RETRY_TIMES = models.FloatField()

    class Meta:
        db_table = 'training_configuration_runMin4'

    def __str__(self):
        return f"ConfigurationData({self.id})"

class TrainingConfiguration_runMin5(models.Model):
    TPMC = models.FloatField()
    RECYCLE = models.FloatField()
    FAST_ROLL_PAGES = models.FloatField()
    HAGR_BUF_SIZE = models.FloatField()
    HJ_BLK_SIZE = models.FloatField()
    HUGE_BUFFER = models.FloatField()
    WORK_THRD_RESERVE_SIZE = models.FloatField()
    BUFFER = models.FloatField()
    SORT_BUF_SIZE = models.FloatField()
    HJ_BUF_GLOBAL_SIZE = models.FloatField()
    FAST_POOL_PAGES = models.FloatField()
    MEMORY_POOL = models.FloatField()
    MEMORY_TARGET = models.FloatField()
    HAGR_BUF_GLOBAL_SIZE = models.FloatField()
    MVCC_RETRY_TIMES = models.FloatField()

    class Meta:
        db_table = 'training_configuration_runMin5'

    def __str__(self):
        return f"ConfigurationData({self.id})"

class TrainingConfiguration_runMin6(models.Model):
    TPMC = models.FloatField()
    RECYCLE = models.FloatField()
    FAST_ROLL_PAGES = models.FloatField()
    HAGR_BUF_SIZE = models.FloatField()
    HJ_BLK_SIZE = models.FloatField()
    HUGE_BUFFER = models.FloatField()
    WORK_THRD_RESERVE_SIZE = models.FloatField()
    BUFFER = models.FloatField()
    SORT_BUF_SIZE = models.FloatField()
    HJ_BUF_GLOBAL_SIZE = models.FloatField()
    FAST_POOL_PAGES = models.FloatField()
    MEMORY_POOL = models.FloatField()
    MEMORY_TARGET = models.FloatField()
    HAGR_BUF_GLOBAL_SIZE = models.FloatField()
    MVCC_RETRY_TIMES = models.FloatField()

    class Meta:
        db_table = 'training_configuration_runMin6'

    def __str__(self):
        return f"ConfigurationData({self.id})"

class TrainingConfiguration_runMin7(models.Model):
    TPMC = models.FloatField()
    RECYCLE = models.FloatField()
    FAST_ROLL_PAGES = models.FloatField()
    HAGR_BUF_SIZE = models.FloatField()
    HJ_BLK_SIZE = models.FloatField()
    HUGE_BUFFER = models.FloatField()
    WORK_THRD_RESERVE_SIZE = models.FloatField()
    BUFFER = models.FloatField()
    SORT_BUF_SIZE = models.FloatField()
    HJ_BUF_GLOBAL_SIZE = models.FloatField()
    FAST_POOL_PAGES = models.FloatField()
    MEMORY_POOL = models.FloatField()
    MEMORY_TARGET = models.FloatField()
    HAGR_BUF_GLOBAL_SIZE = models.FloatField()
    MVCC_RETRY_TIMES = models.FloatField()

    class Meta:
        db_table = 'training_configuration_runMin7'

    def __str__(self):
        return f"ConfigurationData({self.id})"

class TrainingConfiguration_runMin8(models.Model):
    TPMC = models.FloatField()
    RECYCLE = models.FloatField()
    FAST_ROLL_PAGES = models.FloatField()
    HAGR_BUF_SIZE = models.FloatField()
    HJ_BLK_SIZE = models.FloatField()
    HUGE_BUFFER = models.FloatField()
    WORK_THRD_RESERVE_SIZE = models.FloatField()
    BUFFER = models.FloatField()
    SORT_BUF_SIZE = models.FloatField()
    HJ_BUF_GLOBAL_SIZE = models.FloatField()
    FAST_POOL_PAGES = models.FloatField()
    MEMORY_POOL = models.FloatField()
    MEMORY_TARGET = models.FloatField()
    HAGR_BUF_GLOBAL_SIZE = models.FloatField()
    MVCC_RETRY_TIMES = models.FloatField()

    class Meta:
        db_table = 'training_configuration_runMin8'

    def __str__(self):
        return f"ConfigurationData({self.id})"

class TrainingConfiguration_runMin9(models.Model):
    TPMC = models.FloatField()
    RECYCLE = models.FloatField()
    FAST_ROLL_PAGES = models.FloatField()
    HAGR_BUF_SIZE = models.FloatField()
    HJ_BLK_SIZE = models.FloatField()
    HUGE_BUFFER = models.FloatField()
    WORK_THRD_RESERVE_SIZE = models.FloatField()
    BUFFER = models.FloatField()
    SORT_BUF_SIZE = models.FloatField()
    HJ_BUF_GLOBAL_SIZE = models.FloatField()
    FAST_POOL_PAGES = models.FloatField()
    MEMORY_POOL = models.FloatField()
    MEMORY_TARGET = models.FloatField()
    HAGR_BUF_GLOBAL_SIZE = models.FloatField()
    MVCC_RETRY_TIMES = models.FloatField()

    class Meta:
        db_table = 'training_configuration_runMin9'

    def __str__(self):
        return f"ConfigurationData({self.id})"

class TrainingConfiguration_runMin10(models.Model):
    TPMC = models.FloatField()
    RECYCLE = models.FloatField()
    FAST_ROLL_PAGES = models.FloatField()
    HAGR_BUF_SIZE = models.FloatField()
    HJ_BLK_SIZE = models.FloatField()
    HUGE_BUFFER = models.FloatField()
    WORK_THRD_RESERVE_SIZE = models.FloatField()
    BUFFER = models.FloatField()
    SORT_BUF_SIZE = models.FloatField()
    HJ_BUF_GLOBAL_SIZE = models.FloatField()
    FAST_POOL_PAGES = models.FloatField()
    MEMORY_POOL = models.FloatField()
    MEMORY_TARGET = models.FloatField()
    HAGR_BUF_GLOBAL_SIZE = models.FloatField()
    MVCC_RETRY_TIMES = models.FloatField()

    class Meta:
        db_table = 'training_configuration_runMin10'

    def __str__(self):
        return f"ConfigurationData({self.id})"