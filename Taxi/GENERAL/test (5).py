from business_models import greenplum, hahn

def main():
  greenplum.replicate(yt_path='//home/taxi-analytics/anyamalkova/Activity_priority/Daily_by_udid', table_name='snb_taxi.anyamalkova_activity_priority_dash')
  greenplum('grant all on snb_taxi.anyamalkova_activity_priority_dash to "robot-sql-retention","robot-taxi-business","robot-tableau-15", anyamalkova')


if __name__ == '__main__':
    main()
    
