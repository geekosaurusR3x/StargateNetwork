# helpers for translate ip to stargate glyph

def SequenceToListInt(s):
    lst = [int(item) for item in s.split('.')]
    return lst


def ListIntToSequence(l):
    return '.'.join(str(x) for x in l)


def ListNumbersToIntInBase(l, b):
    val = 0
    exp = len(l)-1
    for digit in l:
        val += digit*pow(b, exp)
        exp -= 1
    return val


def NumberToBase(n, b):
    b = int(b)
    if n == 0:
        return [0]
    digits = []
    while n:
        digits.append(n % b)
        n //= b
    return digits[::-1]


def IpToStargateCode(ip):
    IntIP = ListNumbersToIntInBase(ip, 256)
    ListGlyphes = NumberToBase(IntIP, 38)
    while len(ListGlyphes) < 7:
        ListGlyphes.insert(0, 0)
    ListGlyphes.pop(0)
    ListGlyphes.append(39)
    return ListGlyphes


def StargateCodeToIp(sc):
    sc = sc[:-1]
    maxintToShift = ListNumbersToIntInBase([38, 38, 38, 38, 38], 38)
    actualint = ListNumbersToIntInBase(sc, 38)
    sc.insert(0, 0 if (actualint <= maxintToShift) else 1)
    IntIP = ListNumbersToIntInBase(sc, 38)
    ListIP = NumberToBase(IntIP, 256)
    return ListIP
