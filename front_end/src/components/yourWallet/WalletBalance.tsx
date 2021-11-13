import {Token} from '../Main'
import {useEthers, useTokenBalance} from '@usedapp/core'
import {formatUnits} from '@ethersproject/units'

interface WalletBalanceProps{
    token: Token
}
export const WalletBalance = ({token}:WalletBalanceProps)=>{
  const { address} = token
  const {account} = useEthers()
  const tokenBalance = useTokenBalance(address, account)
  
  const formattedTokenBalance:number = tokenBalance ? parseFloat(formatUnits(tokenBalance, 18)): 0

  return (<div>{formattedTokenBalance}</div>)
}