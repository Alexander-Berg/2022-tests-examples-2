from zoo.pickup_points.production import project_config


if __name__ == '__main__':
    job = project_config.get_project_cluster().job()
    job.concat(
        job.table('//home/taxi_ml/production/pickup_points/candidates'),
        job.table('//home/taxi_ml/dev/pickup_points/candidates/points_final')
    ).put(
        project_config.CANDIDATES_TESTING_YT_PATH
    )
    job.run()
