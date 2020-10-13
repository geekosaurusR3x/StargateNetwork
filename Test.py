#!/usr/bin/env python3
import StargateNetwork.Helpers as StargateNetworkUtils

if __name__ == "__main__":
    Ip = StargateNetworkUtils.SequenceToListInt(input('Ip to convert : '))
    StargateAddress = StargateNetworkUtils.IpToStargateCode(Ip)
    IPDecode = StargateNetworkUtils.StargateCodeToIp(StargateAddress)
    print(f'{Ip} -> {StargateAddress}')
    print(f'{StargateAddress} -> {IPDecode}')
