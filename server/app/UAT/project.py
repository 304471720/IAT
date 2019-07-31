# -*-coding:utf-8-*-
from flask import Blueprint, jsonify, make_response, session, request
from app.tables.UAT import Project,Tree, GlobalValues, ProxyConfig, CaseLibs, CaseKeywords
from app.tables.User import users
from datetime import datetime
import os, hashlib, json, base64, binascii
from app import db, app

project = Blueprint('project', __name__)

def encrypt_name(name, salt=None, encryptlop=30):
  if not salt:
    salt = binascii.hexlify(os.urandom(32)).decode()  # length 32
  for i in range(encryptlop):
    name = hashlib.sha1(str(name + salt).encode('utf-8')).hexdigest()  # length 64
  return name

def addTreeNote(project_id, pid, name, type, user_id, index_id):
  '''
  :param project_id: 项目id
  :param pid: 父节点id
  :param name: 节点名称
  :param type: 节点属性:1.目录 2.用例 3.关键词目录 4.自定义关键词
  :param user_id: 用户id
  :return: 节点 id
  '''
  data = Tree(project_id, pid, name, type, user_id, index_id)
  db.session.add(data)
  db.session.commit()
  return data.id


@project.before_request
def is_login():  # 判断是否登录
    if not session.get("user_id"):
        # 重定向到登录页面
        return make_response(jsonify({'code': 99999, 'content': None, 'msg': u'请先登录!'}))


@project.route('/projectList', methods=['GET'])
def projectList():
  status = request.values.get("status")
  if not status:
    status = 3
  if status != 3:
    projectList = Project.query.filter(db.and_(Project.status == status)).order_by(
      db.desc(Project.add_time)).all()
  else:
    projectList = Project.query.order_by(
      db.desc(Project.add_time)).all()
  content = []
  if projectList:
    for item in projectList:
      # caseCount = Sample.query.filter(db.and_(Sample.project_id == item.id)).count()
      row_data = users.query.filter(db.and_(users.id == item.user_id)).first()
      username = ""
      if row_data:
        username = row_data.username
      content.append({
        "id": item.id,
        "name": item.name,
        "add_time": item.add_time.strftime('%Y-%m-%d %H:%M:%S'),
        "add_user": username,
        "count": 0,
        "status": item.status,
      })
  return make_response(jsonify({'code': 0, 'msg': '', 'content': content}))

@project.route('/addProject', methods=['POST'])
def addProject():
  user_id = session.get('user_id')
  name = request.json.get("name")
  try:
    data = Project(name, 1, user_id)
    db.session.add(data)
    db.session.commit()
    addTreeNote(data.id, 0, name, 1, user_id, 0)
    addTreeNote(data.id, 0, '自定义词库', 3, user_id, 1)
    return make_response(jsonify({'code': 0, 'content': None, 'msg': u'新建成功!'}))
  except Exception as e:
    print(e)
    return make_response(jsonify({'code': 10002, 'content': None, 'msg': u'新建失败!'}))

@project.route('/projectGlobalValues', methods=['GET'])
def projectGlobalValues():
  id = request.values.get("id")
  globalValuesData = GlobalValues.query.filter_by(project_id=id).order_by(db.asc(GlobalValues.add_time)).all()
  content = []
  if globalValuesData:
    for item in globalValuesData:
      content.append({
        "id": item.id,
        "key": item.key_name,
        "value": item.key_value,
        "valueType": item.value_type,
      })
  return make_response(jsonify({'code': 0, 'msg': '', 'content': content}))

@project.route('/addGlobalValues', methods=['POST'])
def addGlobalValues():
  user_id = session.get('user_id')
  keyName = request.json.get("keyName")
  keyValue = request.json.get("keyValue")
  projectId = request.json.get("projectId")
  valueType = request.json.get("valueType")
  try:
    rowData = GlobalValues.query.filter_by(key_name = keyName).first()
    if rowData:
      return make_response(jsonify({'code': 10002, 'content': None, 'msg': u'关键词名称重复!'}))
    data = GlobalValues(keyName, keyValue, projectId, user_id, valueType)
    db.session.add(data)
    db.session.commit()
    if valueType == 1:
      defaultData = GlobalValues(keyName, '', projectId, user_id, 2)
      db.session.add(defaultData)
      db.session.commit()
    if valueType == 2:
      defaultData = GlobalValues(keyName, '', projectId, user_id, 1)
      db.session.add(defaultData)
      db.session.commit()
    return make_response(jsonify({'code': 0, 'content': None, 'msg': u'新建成功!'}))
  except Exception as e:
    print(e)
    return make_response(jsonify({'code': 10002, 'content': None, 'msg': u'新建失败!'}))

@project.route('/deleteGlobalValues', methods=['POST'])
def deleteGlobalValues():
  id = request.json.get("id")
  try:
    rowData = GlobalValues.query.filter_by(id = id).first()
    if rowData:
      oldKeyName = rowData.key_name
      db.session.delete(rowData)
      db.session.commit()
      otherRowData = GlobalValues.query.filter_by(key_name=oldKeyName).first()
      if otherRowData:
        db.session.delete(otherRowData)
        db.session.commit()
      return make_response(jsonify({'code': 0, 'content': None, 'msg': u'删除成功!'}))
    else:
      return make_response(jsonify({'code': 10002, 'content': None, 'msg': u'删除失败!'}))
  except Exception as e:
    print(e)
    return make_response(jsonify({'code': 10002, 'content': None, 'msg': u'删除失败!'}))

@project.route('/updateGlobalValues', methods=['POST'])
def updateGlobalValues():
  id = request.json.get("id")
  keyName = request.json.get("keyName")
  keyValue = request.json.get("keyValue")
  rowData = GlobalValues.query.filter_by(id=id)
  if rowData.first():
    oldKeyName = rowData.first().key_name
    data = {
      'key_name': keyName,
      'key_value': keyValue,
    }
    rowData.update(data)
    db.session.commit()
    otherRowData = GlobalValues.query.filter_by(key_name = oldKeyName)
    if otherRowData.first():
      data = {
        'key_name': keyName,
      }
      otherRowData.update(data)
      db.session.commit()
  return make_response(jsonify({'code': 0, 'content': None, 'msg': u'操作成功'}))

@project.route('/uploadFile',methods=['POST'])
def uploadFile():
  upload_file = request.files["file"]
  if upload_file:
    fileHash = encrypt_name(upload_file.filename)
    fileType = upload_file.filename.split('.')[-1]
    fileName = fileHash + '.' + fileType
    fileDir = app.root_path +'/'+ app.config['UPLOAD_FILE_FOLDER']
    if not os.path.isdir(fileDir):
      os.makedirs(fileDir)
    upload_file.save(os.path.join(app.root_path, app.config['UPLOAD_FILE_FOLDER'], fileName))
    return make_response(jsonify({'code': 0, 'content':{'filePath':app.config['UPLOAD_FILE_FOLDER']+fileName}, 'msg': u'上传成功!'}))
  else:
    return make_response(jsonify({'code': 10002, 'content':None, 'msg': u'上传失败!'}))

@project.route('/addProxyConfig',methods=['POST'])
def addProxyConfig():
  user_id = session.get('user_id')
  proxyName = request.json.get("proxyName")
  browserType = request.json.get("browserType")
  filePath = request.json.get("filePath")
  proxyPath = request.json.get("proxyPath")
  try:
    path = ''
    if browserType == 1:
      path = filePath
    if browserType == 2:
      path = proxyPath
    data = ProxyConfig(proxyName, path, user_id, browserType)
    db.session.add(data)
    db.session.commit()
    return make_response(jsonify({'code': 0, 'content': None, 'msg': u'新建成功!'}))
  except Exception as e:
    print(e)
    return make_response(jsonify({'code': 10002, 'content': None, 'msg': u'新建失败!'}))

@project.route('/proxyConfigList', methods=['GET'])
def proxyConfigList():
  proxyConfigData = ProxyConfig.query.order_by(db.asc(ProxyConfig.add_time)).all()
  content = []
  if proxyConfigData:
    for item in proxyConfigData:
      row_data = users.query.filter(db.and_(users.id == item.user_id)).first()
      username = ""
      if row_data:
        username = row_data.username
      content.append({
        "id": item.id,
        "name": item.name,
        "path": item.path,
        "add_user": username,
        "add_time": item.add_time.strftime('%Y-%m-%d %H:%M:%S'),
        "Description": "",
        "browserType": item.browser_type,
      })
  return make_response(jsonify({'code': 0, 'msg': '', 'content': content}))

@project.route('/deleteProxyConfig', methods=['POST'])
def deleteProxyConfig():
  id = request.json.get("id")
  try:
    rowData = ProxyConfig.query.filter_by(id = id).first()
    if rowData:
      browserType = rowData.browser_type
      path = rowData.path
      db.session.delete(rowData)
      db.session.commit()
      if browserType == 1:
        os.remove('./app/'+path)
      return make_response(jsonify({'code': 0, 'content': None, 'msg': u'删除成功!'}))
    else:
      return make_response(jsonify({'code': 10002, 'content': None, 'msg': u'删除失败!'}))
  except Exception as e:
    print(e)
    return make_response(jsonify({'code': 10002, 'content': None, 'msg': u'删除失败!'}))

@project.route('/setProjectStatus', methods=['POST'])
def setProjectStatus():
  user_id = session.get('user_id')
  id = request.json.get("id")
  status = request.json.get("status")
  data = {'status': status}
  row_data = Project.query.filter(db.and_(Project.id == id))
  if row_data.first():
    row_data.update(data)
    db.session.commit()
    return make_response(jsonify({'code': 0, 'msg': 'sucess', 'content': []}))
  else:
    return make_response(jsonify({'code': 10001, 'msg': 'no such Project', 'content': []}))

@project.route('/getAllLibs')
def getAllLibs():
  status = request.values.get("status")
  if not status:
    libsData = CaseLibs.query.filter().order_by(
      db.desc(CaseLibs.add_time)).all()
  else:
    libsData = CaseLibs.query.filter(db.and_(CaseLibs.lib_type != 1,CaseLibs.status == status)).order_by(db.desc(CaseLibs.add_time)).all()
  content = []
  if libsData:
    for item in libsData:
      content.append({
        "id": item.id,
        "name": item.name,
        "add_time": item.add_time.strftime('%Y-%m-%d %H:%M:%S'),
      })
  return make_response(jsonify({'code': 0, 'content': content, 'msg': u''}))

@project.route('/getLibKeywords')
def getLibKeywords():
  id = request.values.get("id")
  results = CaseKeywords.query.filter(db.and_(CaseKeywords.lib_id == id)).order_by(db.asc(CaseKeywords.add_time)).all()
  content = []
  for keyword in results:
    content.append({
      'id': keyword.id,
      'name_en': keyword.name_en,
      'name_zh': keyword.name_zh,
      'shortdoc': keyword.shortdoc,
      'doc': keyword.doc,
      'args': keyword.args,
      'add_time': keyword.add_time.strftime('%Y-%m-%d %H:%M:%S'),
    })

  return make_response(jsonify({'code': 0, 'content': content, 'msg': u''}))

@project.route('/updateKeywords',methods=['POST'])
def updateKeywords():
  user_id = session.get('user_id')
  id = request.json.get("id")
  name_en = request.json.get("name_en")
  name_zh = request.json.get("name_zh")
  shortdoc = request.json.get("shortdoc")
  doc = request.json.get("doc")
  rowData = CaseKeywords.query.filter_by(id=id)
  if rowData.first():
    data = {
      'name_en': name_en,
      'name_zh': name_zh,
      'shortdoc': shortdoc,
      'doc': doc,
      'update_user': user_id,
    }
    rowData.update(data)
    db.session.commit()
    return make_response(jsonify({'code': 0, 'content': None, 'msg': u'操作成功'}))
  else:
    return make_response(jsonify({'code': 10002, 'content': None, 'msg': u'操作失败'}))

@project.route('/userList', methods=['GET'])
def userList():
  userDatas = users.query.filter_by(status = 1).order_by(db.asc(users.add_time)).all()
  content = []
  if userDatas:
    for item in userDatas:
      content.append({
        "id": item.id,
        "name": item.username,
        "email": item.email,
        "account_type": item.account_type,
        "status": item.status,
        "add_time": item.add_time.strftime('%Y-%m-%d %H:%M:%S'),
      })
  return make_response(jsonify({'code': 0, 'msg': '', 'content': content}))

def assertAdmin(user_id):
  row_data = users.query.filter(db.and_(users.id == user_id)).first()
  print(row_data.account_type)
  if row_data and row_data.account_type == 1:
    print('admin:',row_data.username,)
    return True
  else:
    print('error admin:', row_data.username, )
    return False

@project.route('/setUserStatus', methods=['POST'])
def setUserStatus():
  user_id = session.get('user_id')
  id = request.json.get("id")
  status = request.json.get("status")
  data = {'status': status}
  if not assertAdmin(user_id):
    return make_response(jsonify({'code': 10001, 'msg': '没有权限', 'content': []}))
  row_data = users.query.filter(db.and_(users.id == id))
  if row_data.first():
    row_data.update(data)
    db.session.commit()
    return make_response(jsonify({'code': 0, 'msg': 'sucess', 'content': []}))
  else:
    return make_response(jsonify({'code': 10001, 'msg': 'error', 'content': []}))

@project.route('/setUserType', methods=['POST'])
def setUserType():
  user_id = session.get('user_id')
  id = request.json.get("id")
  accountType = request.json.get("accountType")
  data = {'account_type': accountType}
  if not assertAdmin(user_id):
    return make_response(jsonify({'code': 10001, 'msg': '没有权限', 'content': []}))
  row_data = users.query.filter(db.and_(users.id == id))
  if row_data.first():
    row_data.update(data)
    db.session.commit()
    return make_response(jsonify({'code': 0, 'msg': 'sucess', 'content': []}))
  else:
    return make_response(jsonify({'code': 10001, 'msg': 'error', 'content': []}))
