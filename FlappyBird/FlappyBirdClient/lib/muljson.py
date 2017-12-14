import json
import common

filename = common.get_filename('scores_client.json')
file = open(filename,'w')  
dif0 = {'difficulty':0,'scores':[1]}
dif1 = {'difficulty':1,'scores':[1]}
dif2 = {'difficulty':2,'scores':[1]}
diflst = [dif0,dif1,dif2]
data = {}
data['userName'] = 'yyy'
data['scores'] = diflst
datalst = []
datalst.append(data)
# print(data)  
json.dump(datalst,file,ensure_ascii=False)  
file.close()  

file = open(filename,'r')  
s = json.load(file)  
print s[0]['userName']

