# a={'a':1,'b':2}
# c={'c':3}
# b=[]
# b.append(a)
# b.append(c)
# print(b)
# a=[1,2,3]
# a.remove(2)
# print(a)
# a=1
# def dd():
#     global a
#     b=2
#     a =a+b
#
# if __name__ == "__main__":
#     dd()
#     print(a)
# a=[1,2,3]
# a.remove(1)
# print(a)
#import random
# # a={1:'A',2:'B',3:'C',4:'D'}
# # s = str(123)+a[1]
# # print(''.join(random.sample(s,5)))
# class Encryption:
#     """整形数字简单的一个加密/解密算法"""
#     def encryption(num):
#         """对数字进行加密解密处理每个数位上的数字变为与7乘积的个位数字，再把每个数位上的数字a变为10-a．"""
#         newNum=[]
#
#         for i in str(num):
#             if int(i):
#                 newNum.append(str(10-int(i)*7%10))
#             else:
#                 newNum.append(str(0))
#         newStr = ''.join(newNum)
#
#         if len(newStr)<3:
#             a = ''.join(random.sample('abcdefghkmnpqrstuvwxyzABCDEFGHGKMNOPQRSTUVWXYZ', 3-len(newStr)))
#             newStr = ''.join([a,newStr])
#         b =  random.choice('abcdefghkmnpqrstuvwxyzABCDEFGHGKMNOPQRSTUVWXYZ')
#         return ''.join([b,newStr])
#
# if __name__ == '__main__':
#     a=[]
#     for i in range(100):
#         a.append(Encryption.encryption(i))
#     print(a)
# import time
# start = time.clock()
# sum =0
# for i in range(10000):
#     sum=sum+i
# end = time.clock()
# print(end-start)
# from collections import Counter#统计出现的次数
# import os
# import re
# a= []
# # with open("C:/Users/HBin/Desktop/oj/日志/loggsNew.log") as f:
# #     for i in range(500):
# #         message = dict()
# #         s = re.sub('.+api/',"",f.readline())
# #         s = re.sub(' .+','',s)
# #         a.append(s)
# # print(Counter(a).most_common(3))
# # a = {'a':1,'b':2}
# # print(a.values())
# s = 'ww.bac.com'#match是从第一个位置匹配，search只要搜索到就行,sub是截取
# print(re.match('.w',s))