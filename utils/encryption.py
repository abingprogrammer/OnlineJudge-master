import random
class Course_code:
    """整形数字简单的一个加密/解密算法"""
    def encryption(num):
        """对数字进行加密解密处理每个数位上的数字变为与7乘积的个位数字，再把每个数位上的数字a变为10-a．"""
        newNum=[]

        for i in str(num):
            if int(i):
                newNum.append(str(10-int(i)*7%10))
            else:
                newNum.append(str(0))
        newStr = ''.join(newNum)

        if len(newStr)<3:
            a = ''.join(random.sample('abcdefghkmnpqrstuvwxyzABCDEFGHGKMNOPQRSTUVWXYZ', 3-len(newStr)))
            newStr = ''.join([a,newStr])
        b =  random.choice('abcdefghkmnpqrstuvwxyzABCDEFGHGKMNOPQRSTUVWXYZ')
        return ''.join([b,newStr])