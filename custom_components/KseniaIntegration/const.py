"""Constants for the Ksenia Lares Alarm integration."""

DOMAIN = "ksenia_lares"
MANUFACTURER = "KSENIA"
DATA_COORDINATOR = "AlarmDataCoordinator"
DATA_PARTITIONS = "partitions"
DATA_ZONES = "zones"
DATA_SCENARIOS = "scenario"
DEFAULT_TIMEOUT = 10

# Partition Statuses
PARTITION_STATUS_DISARMED = "disarmed"
PARTITION_STATUS_ARMED = "armed"
PARTITION_STATUS_ARMED_IMMEDIATE = "armed_immediate"
PARTITION_STATUS_ARMING = "arming"
PARTITION_STATUS_PENDING = "pending"
PARTITION_STATUS_ALARM = "alarm"

# Zone Statuses
ZONE_STATUS_ALARM = "ALARM"
ZONE_STATUS_NORMAL = "NORMAL"
ZONE_STATUS_NOT_USED = "NOT_USED"
ZONE_BYPASS_ON = "bypass_on"
ZONE_BYPASS_OFF = "bypass_off"

# Configuration Options
CONF_PARTITION_AWAY = "partition_away"
CONF_PARTITION_HOME = "partition_home"
CONF_PARTITION_NIGHT = "partition_night"
CONF_SCENARIO_AWAY = "scenario_away"
CONF_SCENARIO_HOME = "scenario_home"
CONF_SCENARIO_NIGHT = "scenario_night"
CONF_SCENARIO_DISARM = "scenario_disarm"
PARTITION_STATUS_ARMED = "True"
PARTITION_STATUS_ARMED_IMMEDIATE = "armed_immediate"
PARTITION_STATUS_ARMING = "arming"
PARTITION_STATUS_DISARMED = "False"

# Zone status constants
ZONE_BYPASS_ON = "True"
ZONE_BYPASS_OFF = "False"
ZONE_STATUS_NOT_USED = "False"

# Configuration options
CONF_PARTITION_AWAY = "partition_away"
CONF_PARTITION_HOME = "partition_home"
CONF_PARTITION_NIGHT = "partition_night"
CONF_SCENARIO_AWAY = "scenario_away"
CONF_SCENARIO_HOME = "scenario_home"
CONF_SCENARIO_NIGHT = "scenario_night"
CONF_SCENARIO_DISARM = "scenario_disarm"
CONF_PIN = "pin"

# Alarm state constants
STATE_ALARM_ARMED_AWAY = "armed_away"
STATE_ALARM_ARMED_HOME = "armed_home"
STATE_ALARM_ARMED_NIGHT = "armed_night"
STATE_ALARM_ARMING = "arming"
STATE_ALARM_DISARMED = "disarmed"

# Scene
SCENE_ARM = "True"
SCENE_DISARM = "False"
SCENE_PARTIAL = "True"
