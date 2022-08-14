# tilt for k8s local dev - https://tilt.dev/

load('./TiltKnative', 'knative_install', 'knative_yaml')

knative_install()
knative_yaml('k8s/syft_task.yaml')

docker_build('task_dispatch',
             context='./images/task_dispatch',
             live_update=[
                sync('./images/task_dispatch/task_dispatch', '/home/app/task_dispatch/'),
             ]
)

docker_build('task_manager',
             context='./images/task_manager/',
             target="dev",
             live_update=[
                sync('images/task_manager/task_manager', '/home/app/task_manager/'),
             ]
)

docker_build('syft_task',
             context='./images/syft_task/',
             live_update=[
                sync('images/syft_task/syft_task', '/home/app/syft_task/'),
             ]
)

k8s_yaml(['k8s/task_manager.yaml', 'k8s/persistence.yaml', 
   'k8s/dev-tools.yaml','k8s/task_dispatcher.yaml'])

# services in prod
k8s_resource(workload='task-manager', port_forwards=8000)
k8s_resource(workload='celery-flower', port_forwards=5566)

# uneeded in prod
k8s_resource(workload='minio', port_forwards=9000)
k8s_resource(workload='minio', port_forwards=9001)
k8s_resource(workload='redis-commander', port_forwards='28081:8081')
k8s_resource(workload='mongo-express', port_forwards=8081)

# for vscode dev containers
# k8s_resource(workload='task-manager', port_forwards='172.17.0.1:5678:5678') # remote debug
# k8s_resource(workload='task-manager', port_forwards='172.17.0.1:18000:8000')
# k8s_resource(workload='celery-flower', port_forwards='172.17.0.1:15566:5566') # remote debug
# k8s_resource(workload='minio', port_forwards='172.17.0.1:19000:9000')
# k8s_resource(workload='redis', port_forwards='172.17.0.1:16379:6379')
# k8s_resource(workload='task-svc-syft', port_forwards='172.17.0.1:20000:8000')
