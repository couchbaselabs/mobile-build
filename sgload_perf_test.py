#! /usr/bin/env python

# This is the Jenkins shell script for running an sgload based performance test



def main():

    validate_environment()
    
    create_ansible_config()

    write_resources_pool_json()

    generate_clusters_from_pool()

    setup_ssh_tunnel()

    set_influx_db_url()

    maybe_deploy_github_keys()

    maybe_install_deps()

    maybe_provision_cluster()

    run_sgload_perf_test()

def validate_environment():
    """
    Check for expected env variables
    """
    pass

def create_ansible_config():
    """
    ansible_config="ansible.cfg"
    echo "[defaults]" > $ansible_config
    echo "remote_user=$REMOTE_USER" >> $ansible_config
    """
    pass

def write_resources_pool_json():
    """
    pool_file="resources/pool.json"

    echo "Generating $pool_file ..."
    echo $POOLS_JSON > $pool_file
    cat $pool_file
    """
    pass

def generate_clusters_from_pool():
    """
    echo "Generating cluster configs from pool"
    python libraries/utilities/generate_clusters_from_pool.py
    cat $CLUSTER_CONFIG
    """
    pass

def setup_ssh_tunnel():
    """
    # If we are using a centos user, that means we are running on AWS.
    # When running on AWS we have to setup SSH port forwarding to expose
    # the grafana machine
    # Also, we need to make sure that the INFLUX target is localhost:8096 to
    # make sure the the stats are proxied over the tunnel
    if [ "$REMOTE_USER" == "centos" ]; then
            python utilities/setup_ssh_tunnel.py --target-host="s61103cnt72.sc.couchbase.com" --target-port="8086" --remote-hosts-user="$REMOTE_USER" --remote-hosts-file="$pool_file" --remote-host-port="8086"
            export INFLUX_URL="http://localhost:8086"
    else
            export INFLUX_URL="http://s61103cnt72.sc.couchbase.com:8086"
    fi

    """
    pass

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








