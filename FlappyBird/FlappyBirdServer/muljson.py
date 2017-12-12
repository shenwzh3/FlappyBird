import json

file = open('signinlist.json','w')  
data1 = {"userName": "shenwzh","password": "123456"}
data2 = {"userName": "yyy","password": "yyy"}  
data = {}
data['userInfo']=[data1,data2]  
print(data)  
json.dump(data,file,ensure_ascii=False)  
file.close()  

file = open('signinlist.json','r')  
s = json.load(file)  
print s