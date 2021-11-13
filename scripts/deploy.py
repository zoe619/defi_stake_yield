from eth_account import account
from scripts.helpful_scripts import get_account, get_contract
from brownie import DappToken, FarmToken, network, config;
from web3 import Web3;
import yaml
import json
import os
import shutil

KEPT_BALANCE = Web3.toWei(100, "ether")

def deploy_token_farm_and_dapp_token(front_end_update=False):
    account = get_account()
    dapp_token = DappToken.deploy({"from":account})
    farm_token = FarmToken.deploy(dapp_token.address, {"from":account},
      publish_source=config['networks'][network.show_active()]['verify']
    )

    txn = dapp_token.transfer(farm_token.address, dapp_token.totalSupply() - KEPT_BALANCE,
     {"from":account})
    txn.wait(1)
    # dapp_tokens, weth_token, fau_tokens(act as dai)
    weth_token = get_contract("weth_token")
    fau_token = get_contract("fau_token")

    dict_of_allowed_tokens = {
        dapp_token: get_contract("dai_usd_price_feed"),
        fau_token: get_contract('dai_usd_price_feed'),
        weth_token: get_contract('eth_usd_price_feed')
    }
    add_allowed_tokens(farm_token, dict_of_allowed_tokens, account)
    if front_end_update:
       update_front_end()
    return farm_token, dapp_token

def add_allowed_tokens(farm_token, dict_of_allowed_tokens,account):
    for token in dict_of_allowed_tokens:
        add_txn = farm_token.addAllowedTokens(token.address, {"from":account})
        add_txn.wait(1)
        set_txn = farm_token.setPriceFeedContract(token.address,
         dict_of_allowed_tokens[token], {"from":account})
        set_txn.wait(1)
    return farm_token
        
def update_front_end():
    # send front end our build folder
    copy_front_end_folders("./build", "./front_end/src/chain-info")
    # sending the frontend our brownie_config in JSON format
    with open('brownie-config.yaml', 'r') as brownie_config:
        config_dict = yaml.load(brownie_config, Loader=yaml.FullLoader)
        with open('./front_end/src/brownie-config.json', 'w') as brownie_config_json:
            json.dump(config_dict, brownie_config_json)
        print("Front end updated!!")

def copy_front_end_folders(src, dest):
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(src, dest)

def main():
    deploy_token_farm_and_dapp_token(front_end_update=True);