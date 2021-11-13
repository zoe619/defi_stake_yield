//  SPDX-License-Identifier:MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

contract FarmToken is Ownable{
   
// stake tokens
// unstake tokens
// issue tokens
// add allowed tokens
// getethvalue

  address[] public allowedTokens;
//   mapping token address->staker address->amount
  mapping(address=>mapping(address=>uint256)) public stakenBalance;
  mapping(address=>uint256) public uniqueTokensStaked;
  address[] public stakers;
  IERC20 public dappToken;
  mapping(address=>address) public tokenPriceFeedMapping;

  constructor(address _dappToken) public{
      dappToken = IERC20(_dappToken);
  }

  function setPriceFeedContract(address _token, address _priceFeed) public onlyOwner{
    tokenPriceFeedMapping[_token] = _priceFeed;
  }

  function issueTokens() public onlyOwner{

     for(uint256 i = 0; i < stakers.length; i++){
         address recipient = stakers[i];

         uint256 userTotalValue = getUserTotalValue(recipient);
         dappToken.transfer(recipient, userTotalValue);
     }
  }

  function getUserTotalValue(address _user) public view returns(uint256){
     uint256 totalValue = 0;
     require(uniqueTokensStaked[_user] > 0 , "No tokens staked");

     for(uint256 i = 0; i < allowedTokens.length; i++){
         totalValue = totalValue + getUserSingleTokenValue(_user, allowedTokens[i]);
     }
     return totalValue;
     
  }

  function getUserSingleTokenValue(address _user, address _token) public view returns(uint256){

  
     if(uniqueTokensStaked[_user] <= 0){
         return 0;
     }
    //  price of token * stakenBalance[_token][_user]
    (uint256 price, uint256 decimals) =  getTokenValue(_token);
    return (stakenBalance[_token][_user] * price / (10 ** decimals));
  }

  function getTokenValue(address _token) public view returns(uint256,  uint256){
    //  priceFeedAddress
    address _priceFeed = tokenPriceFeedMapping[_token];
    AggregatorV3Interface priceFeed = AggregatorV3Interface(_priceFeed);
    (,int256 price,,,) = priceFeed.latestRoundData();
    uint256 decimals = uint256(priceFeed.decimals());

    return(uint256(price), decimals);
  }

  function stakeTokens(uint256 _amount, address _token) public{
      
      require(_amount > 0, "Amount must be greater than 0");
      require(tokenIsAllowed(_token), "Token is not allowed");
      IERC20(_token).transferFrom(msg.sender, address(this), _amount);
      updateUniqueTokensStaked(msg.sender, _token);
      stakenBalance[_token][msg.sender] = stakenBalance[_token][msg.sender] + _amount;
      if(uniqueTokensStaked[msg.sender] == 1){
          stakers.push(msg.sender);
      }
      
  }

  function unstakeTokens(address _token) public{

      uint256 balance = stakenBalance[_token][msg.sender];
      require(balance > 0, "Staked tokens balance is 0");
      IERC20(_token).transfer(msg.sender, balance);
      stakenBalance[_token][msg.sender] = 0;
      uniqueTokensStaked[msg.sender] = uniqueTokensStaked[msg.sender] - 1;
      

  }

  function updateUniqueTokensStaked(address _user, address _token) internal{
     if(stakenBalance[_token][_user] <= 0){
         uniqueTokensStaked[_user] = uniqueTokensStaked[_user] + 1;
     }
  }

  function addAllowedTokens(address _token) public onlyOwner{
     allowedTokens.push(_token);
  }


  function tokenIsAllowed(address _token) public returns(bool){
     
     for(uint256 i = 0; i < allowedTokens.length; i ++){
         if(allowedTokens[i] == _token){
             return true;
         }
     }
     return false;
  }
}
