import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


def engine():
    # When deployed to App Engine, the `SERVER_SOFTWARE` environment variable
    # will be set to 'Google App Engine/version'.
    if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'):
        # Connect using the unix socket located at
        # /cloudsql/cloudsql-connection-name.
        user = 'root'
        passwd = 'root'
        database = 'db_miapproval'
        instance_connection_name = 'mi-approval-sns:asia-south1:mysql-ma-test'

        connection_string = 'mysql+mysqldb://{}:{}@/{}?unix_socket=/cloudsql/{}'.format(
            user, passwd, database, instance_connection_name)

    # If the unix socket is unavailable, then try to connect using TCP. This
    # will work if you're running a local MySQL server or using the Cloud SQL
    # proxy, for example:
    #
    #   $ cloud_sql_proxy -instances=your-connection-name=tcp:3306
    #
    else:
        connection_string = 'mysql+pymysql://root:root@35.200.182.227:3306/db_miapproval'

    return create_engine(connection_string, isolation_level="READ COMMITTED")
