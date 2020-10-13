#!/usr/bin/env python3
import StargateNetwork.Helpers as StargateNetworkUtils
import sys
import functools

if __name__ == "__main__":

    R = range(0, 255)
    print('Start comparing all ip with ip decoded')
    for a in R:
        for b in R:
            for c in R:
                for d in R:
                    Ip = [a, b, c, d]
                    StargateAddress = StargateNetworkUtils.IpToStargateCode(Ip)
                    IPDecode = StargateNetworkUtils.StargateCodeToIp(
                        StargateAddress)
                    if(functools.reduce(lambda x, y: x and y, map(lambda a, b: a == b, Ip, IPDecode), True)):
                        pass
                    else:
                        print('Error for ip')
                        print(f'{Ip} -> {StargateAddress}')
                        print(f'{StargateAddress} -> {IPDecode}')
                        sys.exit(1)
    print('Converting all ip ok')
