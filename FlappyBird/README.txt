����װ��������


0.��װpython2.7.14��cocos2d��pycrypto��


1.ͨ��FlappyBirdServer/start_server.bat��������ˡ�

������˵����


0.�����������ͨ��log in��log out��ѡ���½��ע�ᡣ

1.�����¼��ע�����������Ҫ��Ϣ�����ok������Ϸ���������Ѷ�ѡ�����

2.Ŀǰ���������Ѷȣ�easy��medium��hard���û�ѡ�����Ѷȼ���ʼ��Ϸ��ÿ�����¿�ʼ��Ϸ��Ҫѡ���Ѷ�


3.����ͻ��˽���հ״����Դ���С����Ծ���ܿ����ˡ�



4.������Ϸ������ͨ����� restart�������¿�ʼ

5.������Ϸ������������ͼ����Բ鿴���а�

6.������Ͻ�log out���Է����������л��û�



������˵����

0.[�ͻ���]�߼�������flappy_bird\libĿ¼�¡�


1.[�ͻ���]��Դ�ļ���flappy_bird\dataĿ¼�¡�


2.[�����]������flappy_bird\FlappyBirdServerĿ¼�¡�




������ܹ���

0.ʹ��C/S�ܹ������ͻ���/�������ܹ�

1.�ͻ���������cocos��Ĺ������ƣ���û��ʹ��������е�MVC�ܹ�����������Ҳ�����˶Ը���������зֱ��װ�����ڲ�ͬ�ļ���ʵ��



��ʵ��ϸ�ڡ�

�ͻ��ˣ�

0.�ͻ�������cocos��Ĺ���ʵ���˵�½��ע�ᡢ�л��û����Ѷ�ѡ�񡢲鿴�ɼ����鿴���еȼ�����ģ�飬�ֱ��װΪcocos.Menu�����࣬ͬʱ���cocos�Ĺ��ܵľ����Զ�һЩ���������д��������д��EntryMenuItme��ʵ�ֿ�����������������EntryPswMenuItem

1.�޸���ԭ�����ɹܵ�����ײģ�͵ķ������µķ�������ѯ�鿴�ܵ���λ�ã���ά��һ���ܵ��Ķ��У���һ���ܵ���λ�ó�����Ļ���ʱ�����䵯�����У�ͬʱѹ��һ���µĹܵ�����������ײģ�ͼ�¼�ı������Ӷ����Գ������ɲ�ͬ�߶ȵĹܵ�

2.�ܵ��߶Ȳ���������ɷ���������һ���µĹܵ�����ʱ����߶�
3.�ñ���difficulty��¼�Ѷȣ�0=easy 1=medium 2=hard���ܵ��Ŀ�϶���ƶ��ٶȸ����ѶȽ��е�������ʽ�ֱ�Ϊ��
          pipeDistance = 120 - difficulty * 17 
    
      moveDistance = common.visibleSize["width"]/(2*60*(1-difficulty*0.13))

4.�ͻ��˳ɼ�������������˳ɼ����淽��ͬ

5.�ͻ���ÿ����Ϸ��ʼʱ�������������ɼ����ݣ�����������֯��ǰ�Ѷ���ǰʮ�ĳɼ����û�Ϊһ���������ͻ��ˣ��ͻ���Ҳ����ͬ������֯һ�����سɼ����������Ժ���Ϸ����ʱ�������а�

6.�û�ע��/��½��Ϣ��������ˣ������������ͳɼ��������� �� network.py ʵ��

7.���������ͨ�ŵ�ʱ����Ϣ����ʱ����json��ʽ����ġ�
���û��ڽ��е�½/ע������ǿ������ֵ䣬Ҳ���Ǽ�ֵ�Ե���ʽ��Ϊ�������塣

��½ʱ��send_data['signInAuthentication'] = signInInformation

ע��ʱ��send_data['signUpAuthentication'] = signUpInformation

��������ʱ��send_data['scoreRequest'] = scoreRequest

���������Ը���key֪���ͻ��˷�������Ϣ����



����ˣ�
ע���½�������֤�ͻظ������ճɼ������棬���ͻ��˷������гɼ�������Ϣ �� server.py ʵ��
�����ļ�Ϊsigninlist.json�����ڴ����û���Ϣ��scores_server.json�����ڴ洢�����û��ĳɼ�
signinlist.json�Ľṹ�������ģ�{"userInfo": [{"userName": "shenwzh", "password": "123456"}, {"userName": "yyy", "password": "yyy"}]}
һ����Ϊ'userInfo'��json�б����д��ţ��û��������룩��json�����û�shenwzh��yyy�ǿ����ߣ���Ϊ�����û�
scores_server.json�Ľṹ��[{"userName": "yyy", "scores": [{"difficulty": 0, "scores": [2, 2, 1, 10]}, {"difficulty": 1, "scores": [0, 1, 2]}, {"difficulty": 2, "scores": []}]}, {"userName": "shenwzh", "scores": [{"difficulty": 0, "scores": [0, 24]},{"difficulty": 1, "scores": [0]}, {"difficulty": 2, "scores": [8]}]}] 
һ��json�б��б��ÿ���û��ĳɼ���Ϣ�������磨�û������÷֣���json���󣬵÷�����һ��json�б���3���Ѷ��µ�ÿ�ε÷֡�
�ڷ���ˣ��յ����Կͻ��˵���Ϣ������key���лظ���
�磺keyΪ'signInAuthentication'ʱ��֪���ͻ����ڽ��е�½����������signInInformation��signinlist.json�ļ�������֤����signInInformation����signinlist.json�У��򷢻�sendData = {'authenResult':True}�����򷢻�sendData = {'authenResult':False}
ע�ᣬ���ɼ��Ȳ���Ҳ�����Ƶġ�

AES�ԳƼ��ܽ��ܣ��ͻ���&����˹���˽Կ����
AES128���ܽ��� �� myAES.py ʵ��
������socketͨ����Ϣ����֮ǰ����AES���ܣ�������Ϣ���� �� netstream.py ʵ��