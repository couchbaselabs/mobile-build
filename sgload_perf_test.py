#! /usr/bin/env python

# This is the Jenkins shell script for running an sgload based performance test

import collections
import os
import re
from libraries.utilities.generate_clusters_from_pool import generate_clusters_from_pool
from utilities.setup_ssh_tunnel import setup_tunnel
from utilities.setup_ssh_tunnel import get_remote_hosts_list

# A named tuple to hold all the environment variables (lightweight class without the boilerplate)
ScriptEnv = collections.namedtuple(
    'ScriptEnv',
    'remote_user pools_json',
)

RESOURCES_POOL_FILENAME="resources/pool.json"

def main():

    script_env = validate_environment()
    
    create_ansible_config(remote_user=script_env.remote_user)

    write_resources_pool_json(pools_json=script_env.pools_json)

    generate_clusters_from_pool(RESOURCES_POOL_FILENAME)
    
    maybe_setup_ssh_tunnel(script_env.remote_user)    

    set_influx_db_url()

    maybe_deploy_github_keys()

    maybe_install_deps()

    maybe_provision_cluster()

    run_sgload_perf_test()

def validate_environment():
    """
    Check for expected env variables
    """
    return ScriptEnv(
        remote_user=os.environ["REMOTE_USER"],
        pools_json=os.environ["POOLS_JSON"],
    )

def create_ansible_config(remote_user):
    # Read in ansible.cfg.example and replace "vagrant" -> remote_user and
    # write out result to ansible.cfg
    ansible_cfg_example = open("ansible.cfg.example").read()
    ansible_cfg = re.sub("vagrant", remote_user, ansible_cfg_example)
    f = open("ansible.cfg", "w")
    f.write(ansible_cfg)
    f.close()

def write_resources_pool_json(pools_json):
    with open(RESOURCES_POOL_FILENAME, "w") as file:
        file.write(pools_json)

def maybe_setup_ssh_tunnel(remote_user):

    # Only want to do this on AWS, where remote_user is centos
    if remote_user != "centos":
        return 

    remote_hosts_list = get_remote_hosts_list(RESOURCES_POOL_FILENAME)
    setup_tunnel(
        target_host="s61103cnt72.sc.couchbase.com",
        target_port="8086",
        remote_hosts_user=remote_user,
        remote_hosts=remote_hosts_list,
        remote_host_port="8086",
    )
    
def set_influx_db_url():
    pass

def maybe_deploy_github_keys():
    """
    # Enable building private sync-gateway-accel repo by making sure that 
    # the VM's have the private key that is registered with github as a 
    # deploy key on the sync-gateway-accel repo
    if [ "$SG_DEPLOY_TYPE" == "Source" ]; then
            echo $private_key_base64 | base64 -d > /tmp/private_key
        python libraries/utilities/install-gh-deploy-keys.py \
            --key-path=/tmp/private_key \
            --ssh-user=$REMOTE_USER 
    fi

    """
    pass

def maybe_install_deps():
    """
    # Install dependencies to the perf cluster
    if [ "$INSTALL_DEPS" == "true" ]; then
      python libraries/provision/install_deps.py
    fi

    """
    pass

def maybe_provision_cluster():
    """
    # Provision cluster
    if [ "$PROVISION_OR_RESET" == "Provision" ]; then
      echo "Provisioning cluster ..."
      if [ "$SG_DEPLOY_TYPE" == "Package" ]; then
        python libraries/provision/provision_cluster.py --server-version $COUCHBASE_SERVER_VERSION --sync-gateway-version $SYNC_GATEWAY_VERSION --sync-gateway-config-file $SYNC_GATEWAY_CONFIG_PATH
      else
        python libraries/provision/provision_cluster.py --server-version $COUCHBASE_SERVER_VERSION --sync-gateway-commit $SYNC_GATEWAY_COMMIT --sync-gateway-config-file $SYNC_GATEWAY_CONFIG_PATH
      fi
    else
      echo "Resetting cluster ..."
      python libraries/provision/reset_cluster.py --conf=$SYNC_GATEWAY_CONFIG_PATH
    fi

    if [ "$CB_COLLECT_INFO" == "true" ]; then
      CB_COLLECT_INFO_PARAM="--cb-collect-info"
    fi

    """
    pass

def run_sgload_perf_test():
    """
    if [ "$LOAD_GENERATOR" == "Gateload" ]; then
            echo "Starting performance tests"
            python testsuites/syncgateway/performance/run_gateload_perf_test.py --test-id 2 --number-pullers $GATELOAD_NUM_PULLERS --number-pushers $GATELOAD_NUM_PUSHERS $GATELOAD_CB_COLLECT_INFO_PARAM --doc-size $GATELOAD_DOC_SIZE --runtime-ms $GATELOAD_RUNTIME_MS --rampup-interval-ms $GATELOAD_RAMPUP_INTERVAL_MS
            echo "Finished performance tests"  
    else
        python testsuites/syncgateway/performance/run_sgload_perf_test.py gateload --createreaders --createwriters --numreaders $SGLOAD_NUM_READERS --numwriters $SGLOAD_NUM_WRITERS --numupdaters $SGLOAD_NUM_UPDATERS --numrevsperdoc $SGLOAD_NUM_REVS_PER_DOC --numdocs $SGLOAD_NUM_DOCS --numchannels $SGLOAD_NUM_CHANNELS --batchsize $SGLOAD_BATCH_SIZE --statsdendpoint localhost:8125 --statsdenabled --expvarprogressenabled --writerdelayms $SGLOAD_WRITER_DELAY_MS --loglevel $SGLOAD_LOG_LEVEL
    fi

    """
    pass 
    
if __name__ == "__main__":
    main()
    print("Done")








