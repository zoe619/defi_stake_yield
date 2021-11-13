from brownie import network, config, exceptions
from scripts.helpful_scripts import(
     LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account, get_contract, INITIAL_PRICE_FEED_VALUE,DECIMALS)
import  pytest
from scripts.deploy import deploy_token_farm_and_dapp_token

def test_set_price_feed_contract():
    # arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")

    account = get_account()
    non_owner_account = get_account(index=1)
    farm_token, dapp_token = deploy_token_farm_and_dapp_token()
    # act
    price_feed_address = get_contract("eth_usd_price_feed")
    farm_token.setPriceFeedContract(
        dapp_token.address, price_feed_address, {"from":account}
    )
    # assert
    assert farm_token.tokenPriceFeedMapping(dapp_token.address) == price_feed_address
    
    with pytest.raises(exceptions.VirtualMachineError):
        farm_token.setPriceFeedContract(
        dapp_token.address, price_feed_address, {"from":non_owner_account}
    )


def test_stake_tokens(amount_staked):
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    account = get_account()
    farm_token, dapp_token = deploy_token_farm_and_dapp_token()
    dapp_token.approve(farm_token.address,amount_staked, {"from":account})
    farm_token.stakeTokens(amount_staked, dapp_token.address, {"from":account})

    assert (
        farm_token.stakenBalance(dapp_token.address, account.address) == amount_staked
    )
    assert farm_token.uniqueTokensStaked(account.address) == 1
    assert farm_token.stakers(0) == account.address
    return farm_token, dapp_token

def test_issue_tokens(amount_staked):
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing")
    account = get_account()
    farm_token, dapp_token = test_stake_tokens(amount_staked)
    starting_balance = dapp_token.balanceOf(account.address)

    farm_token.issueTokens({"from":account})
    # we are staking 1 dapp_token which is = 1 eth
    # so we should get back 2000 dapp_token in rewards since 1 eth is 2000
    assert (
        dapp_token.balanceOf(account.address) == starting_balance + INITIAL_PRICE_FEED_VALUE
    )
   

def test_get_user_total_value_with_different_tokens(amount_staked, random_erc20):
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing!")
    account = get_account()
    farm_token, dapp_token = test_stake_tokens(amount_staked)
    # Act
    farm_token.addAllowedTokens(random_erc20.address, {"from": account})
    farm_token.setPriceFeedContract(
        random_erc20.address, get_contract("eth_usd_price_feed"), {"from": account}
    )
    random_erc20_stake_amount = amount_staked * 2
    random_erc20.approve(
        farm_token.address, random_erc20_stake_amount, {"from": account}
    )
    farm_token.stakeTokens(
        random_erc20_stake_amount, random_erc20.address, {"from": account}
    )
    # Assert
    total_value = farm_token.getUserTotalValue(account.address)
    assert total_value == INITIAL_PRICE_FEED_VALUE * 3

def test_get_token_value():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing!")
    token_farm, dapp_token = deploy_token_farm_and_dapp_token()
    # Act / Assert
    assert token_farm.getTokenValue(dapp_token.address) == (
        INITIAL_PRICE_FEED_VALUE,
        DECIMALS,
    )


def test_unstake_tokens(amount_staked):
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing!")
    account = get_account()
    token_farm, dapp_token = test_stake_tokens(amount_staked)
    # Act
    token_farm.unstakeTokens(dapp_token.address, {"from": account})
    assert dapp_token.balanceOf(account.address) == KEPT_BALANCE
    assert token_farm.stakingBalance(dapp_token.address, account.address) == 0
    assert token_farm.uniqueTokensStaked(account.address) == 0


def test_add_allowed_tokens():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing!")
    account = get_account()
    non_owner = get_account(index=1)
    token_farm, dapp_token = deploy_token_farm_and_dapp_token()
    # Act
    token_farm.addAllowedTokens(dapp_token.address, {"from": account})
    # Assert
    assert token_farm.allowedTokens(0) == dapp_token.address
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.addAllowedTokens(dapp_token.address, {"from": non_owner})
