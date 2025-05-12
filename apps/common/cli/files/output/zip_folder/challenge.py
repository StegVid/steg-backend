a= int(input())
arr=[]
for i in range(a):
    num=list(map(int,input().split()))
    if(num[0]==1):
        arr.append(num[1])
    elif(num[0]==2):
        c=0
        for i in range(len(arr)):
            if arr[i]==num[i]:
                c=1
                arr.pop(i)
        if c==0:
            print("-1")
    elif(num[0]==3):
        print(max(arr))
    elif(num[0]==4):
        print(min(arr))
