import sys
import importlib

from databricks.connect import DatabricksSession
from laktory import models


# --------------------------------------------------------------------------- #
# Setup                                                                       #
# --------------------------------------------------------------------------- #

stack_filepath = "../stack.yaml"

spark = DatabricksSession.builder.clusterId("0927-192621-rw19bbt").getOrCreate()

udf_dirpath = "../workspacefiles/pipelines/"

node_name = None

# --------------------------------------------------------------------------- #
# Get Pipeline                                                                #
# --------------------------------------------------------------------------- #


with open(stack_filepath, "r") as fp:
    stack = models.Stack.model_validate_yaml(fp)

pl = stack.get_env("dev").resources.pipelines["pl-stocks-dlt"]

print(pl)


# --------------------------------------------------------------------------- #
# Read UDFs                                                                   #
# --------------------------------------------------------------------------- #

# Import User Defined Functions
udfs = []
sys.path.append(udf_dirpath)
for udf in pl.udfs:
    module = importlib.import_module(udf.module_name)
    udfs += [getattr(module, udf.function_name)]


# --------------------------------------------------------------------------- #
# Execute Pipeline                                                            #
# --------------------------------------------------------------------------- #

if node_name:
    pl.nodes_dict[node_name].execute(spark=spark, write_sink=False, udfs=udfs)
else:
    pl.execute(spark=spark, write_sinks=False, udfs=udfs)

# --------------------------------------------------------------------------- #
# Display Results                                                             #
# --------------------------------------------------------------------------- #

if node_name:
    df = pl.nodes_dict[node_name].output_df
else:
    df = pl.nodes[-1].output_df
df.laktory.display()
