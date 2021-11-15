import {useState, useEffect} from "react"
import {useEthers, useContractFunction} from "@usedapp/core"
import { constants, utils} from "ethers"
import FarmToken from "../chain-info/contracts/FarmToken.json"
import ERC20 from "../chain-info/contracts/MockERC20.json"
import networkMapping from "../chain-info/deployments/map.json"
// import {Contract} from "@ethersproject/contracts"
import {Contract} from '@usedapp/core/node_modules/@ethersproject/contracts'



export const useStakeToken = (tokenAddress: string)=>{

    const {chainId} = useEthers()
    const {abi} = FarmToken
    // const dappTokenAddress = chainId ? networkMapping[String(chainId)]['DappToken'][0] : constants.AddressZero
    const farmTokenAddress = chainId ? networkMapping[String(chainId)]["FarmToken"][0] : constants.AddressZero
    const farmTokenInterface = new utils.Interface(abi)
    const farmTokenContract = new Contract(farmTokenAddress,farmTokenInterface)

    const erc20ABI = ERC20.abi
    const erc20Interface = new utils.Interface(erc20ABI)
    const erc20Contract = new Contract(tokenAddress, erc20Interface)
    // approve
    // stake tokens

    const {send: approveErc20Send, state: approveErc20State} = 
        useContractFunction(erc20Contract, "approve", {
          transactionName: "approve ERC20 tranfer"

      })
      const approveAndStake = (amount:string)=>{
        setAmountToStake(amount)
        return approveErc20Send(farmTokenAddress,amount)
      }

      const {send: stakeSend, state: stakeState} =
         useContractFunction(farmTokenContract, "stakeTokens", {
             transactionName: "stake tokens"
         })

      const [amountToStake, setAmountToStake] = useState("0")

    //   const [state, setState] = useState(approveErc20State)

      useEffect(() => {
         
        if(approveErc20State.status === "Success"){
            stakeSend(amountToStake, tokenAddress)
        }
      }, [approveErc20State, amountToStake, tokenAddress, stakeSend])

      return {approveAndStake, approveErc20State}
}