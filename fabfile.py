import os

from fabric.api import env
from fabric.api import sudo
from fabric.api import prefix

from fabric.contrib.project import rsync_project
from fabric.context_managers import settings

from contextlib import contextmanager

env.hosts = []

env.serve_root = '/srv/www/django'
env.project_name = 'sitegen'
env.virtualenv_name = 'sitegenenv'

env.project_root = os.path.join(env.serve_root, env.project_name)
env.virtualenv_root = os.path.join(env.serve_root, env.virtualenv_name)
env.requirements_path = os.path.join(env.project_root, 'requirements.txt')

env.activate = 'source %s' % os.path.join(env.virtualenv_root, 'bin/activate')

@contextmanager
def activate_virtualenv():

    with prefix(env.activate):
        yield

def dev_env():
    env.hosts.append('wpy01.dev.microcosm.cc')

def prod_env():
    env.hosts.append('wpy01.microcosm.cc:2020')

def destroy_virtualenv():

    sudo('rm -rf %s' % env.virtualenv_root, user='django')

def create_virtualenv():

    sudo('virtualenv %s' % env.virtualenv_root, user='django')

def install_requirements():

    with activate_virtualenv():
        sudo('pip install -r %s' % env.requirements_path, user='django')

def collectstatic():

    with activate_virtualenv():
        sudo('python %s collectstatic --noinput' % os.path.join(env.project_root, 'manage.py'), user='django')

def rsync():

    rsync_project(
        env.serve_root,
        extra_opts='--exclude .git/ --exclude ENV/ --delete --rsync-path="sudo -u django rsync"'
    )

def start_service():

    sudo('service sitegen start', user='root')

def stop_service():

    sudo('service sitegen stop', user='root')

def restart_service():

    sudo('service sitegen restart', user='root')

def restart_memcached():

    sudo('service memcached restart', user='root')

def first_deploy():

    create_virtualenv()
    rsync()
    install_requirements()
    collectstatic()
    start_service()

def redeploy():

    # service may not be running, which will
    # stop the operation here if we don't set
    # warn_only=True
    with settings(warn_only=True):
        stop_service()
    rsync()
    install_requirements()
    collectstatic()
    start_service()
