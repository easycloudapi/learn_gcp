"""
Ref: https://codelabs.developers.google.com/codelabs/pyspark-bigquery#1

# Submit The Dataproc Job
```shell
gcloud dataproc jobs submit pyspark --cluster ${CLUSTER_NAME} \
    --jars gs://spark-lib/bigquery/spark-bigquery-latest_2.12.jar \
    --driver-log-levels root=FATAL \
    pyspark_bq_show_dataproc.py
```
"""

# This script accompanies this codelab:
# https://codelabs.developers.google.com/codelabs/pyspark-bigquery/

# This script outputs subreddits counts for a given set of years and month
# This data comes from BigQuery via the dataset "fh-bigquery.reddit_comments"

# These allow us to create a schema for our data
from pyspark.sql.types import StructField, StructType, StringType, LongType

# A Spark Session is how we interact with Spark SQL to create Dataframes
from pyspark.sql import SparkSession

# This will help catch some PySpark errors
from py4j.protocol import Py4JJavaError

# Create a SparkSession under the name "reddit". Viewable via the Spark UI
spark = SparkSession.builder.appName("reddit").getOrCreate()

# Create a two column schema consisting of a string and a long integer
fields = [StructField("subreddit", StringType(), True),
          StructField("count", LongType(), True)]
schema = StructType(fields)

# Create an empty DataFrame. We will continuously union our output with this
subreddit_counts = spark.createDataFrame([], schema)

# Establish a set of years and months to iterate over
years = ['2017', '2018']
months = ['01', '02', '03', '04', '05', '06',
          '07', '08', '09', '10', '11', '12']

# Keep track of all tables accessed via the job
tables_read = []
for year in years:
    for month in months:

        # In the form of <project-id>.<dataset>.<table>
        table = f"fh-bigquery.reddit_posts.{year}_{month}"

        # If the table doesn't exist we will simply continue and not
        # log it into our "tables_read" list
        try:
            table_df = (spark.read.format('bigquery').option('table', table)
                        .load())
            tables_read.append(table)
        except Py4JJavaError as e:
            if f"Table {table} not found" in str(e):
                continue
            else:
                raise

        # We perform a group-by on subreddit, aggregating by the count and then
        # unioning the output to our base dataframe
        subreddit_counts = (
            table_df
            .groupBy("subreddit")
            .count()
            .union(subreddit_counts)
        )

print("The following list of tables will be accounted for in our analysis:")
for table in tables_read:
    print(table)

# From our base table, we perform a group-by, summing over the counts.
# We then rename the column and sort in descending order both for readability.
# show() will collect the table into memory output the table to std out.
(
    subreddit_counts
    .groupBy("subreddit")
    .sum("count")
    .withColumnRenamed("sum(count)", "count")
    .sort("count", ascending=False)
    .show()
)