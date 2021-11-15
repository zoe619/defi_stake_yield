/* eslint-disable spaced-comment */
/// <reference types="react-scripts" />
import { useEthers } from "@usedapp/core"
import helperConfig from '../helper-config.json'
import networkMapping from '../chain-info/deployments/map.json'
import { constants } from "ethers"
import browieConfig from "../brownie-config.json"
import dapp from "../dapp.png";
import weth from "../eth.png";
import dai from "../dai.png";
import {YourWallet } from "./yourWallet/YourWallet"

export type Token = {
  image: string,
  address: string,
  name: string
}


export const Main = () =>{
//    show tokens value from wallet
// Get the address of different token
// Get the balance of user wallet

  const {chainId} = useEthers()

  const networkName = chainId ? helperConfig[chainId] : "dev"

  const dappTokenAddress = chainId ? networkMapping[String(chainId)]['DappToken'][0] : constants.AddressZero
  const wethTokenAddress = chainId ? browieConfig['networks'][networkName]['weth_token'] : constants.AddressZero
  const fauTokenAddress = chainId ? browieConfig['networks'][networkName]['fau_token'] : constants.AddressZero
  
  const supportedTokens: Array<Token> = [
    {
      'image': dapp,
      'address': dappTokenAddress,
      'name': 'DAPP'
    },
    {
      'image':weth,
      'address':wethTokenAddress,
      'name': 'WETH'
    },
    {
      'image':dai,
      'address':fauTokenAddress,
      'name': 'DAI'
    }
  ]

  return (<YourWallet supportedTokens ={supportedTokens}/>)

}