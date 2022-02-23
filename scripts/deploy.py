from decimal import getcontext
from scripts.helpful_scripts import get_account, get_contract
from brownie import KCToken, TokenFarm, config, network
from web3 import Web3
import yaml, json, os, shutil

KEPT_BALANCE = Web3.toWei(100, "ether")


def deploy_token_farm_and_kc_token(front_end_update=False):
    account = get_account()
    kc_token = KCToken.deploy({"from": account})
    token_farm = TokenFarm.deploy(
        kc_token.address,
        {"from": account},
        publish_source=config["networks"][network.show_active()]["verify"],
    )
    txn = kc_token.transfer(
        token_farm.address, kc_token.totalSupply() - KEPT_BALANCE, {"from": account}
    )
    txn.wait(1)
    weth_token = get_contract("weth_token")
    fau_token = get_contract("fau_token")
    dict_of_allowed_tokens = {
        kc_token: get_contract("dai_usd_price_feed"),
        fau_token: get_contract("dai_usd_price_feed"),
        weth_token: get_contract("eth_usd_price_feed"),
    }
    add_allowed_tokens(token_farm, dict_of_allowed_tokens, account)
    if front_end_update:
        update_front_end()
    return token_farm, kc_token


def add_allowed_tokens(token_farm, dict_of_allowed_tokens, account):
    for token in dict_of_allowed_tokens:
        add_txn = token_farm.addAllowedTokens(token.address, {"from": account})
        add_txn.wait(1)
        set_txn = token_farm.setPriceFeedContract(
            token.address, dict_of_allowed_tokens[token], {"from": account}
        )
        set_txn.wait(1)
    return token_farm


def update_front_end():

    copy_folders_to_front_end("./build", "./front-end/src/chain-info")

    with open("brownie-config.yaml", "r") as brownie_config:
        config_dict = yaml.load(brownie_config, Loader=yaml.FullLoader)
        with open("./front-end/src/brownie-config.json", "w") as brownie_config_json:
            json.dump(config_dict, brownie_config_json)
    print("Front end updated!")


def copy_folders_to_front_end(src, dest):
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(src, dest)


def main():
    deploy_token_farm_and_kc_token(front_end_update=True)
