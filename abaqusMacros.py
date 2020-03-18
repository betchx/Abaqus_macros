# -*- coding: mbcs -*-
# Do not delete the following import lines
from abaqus import *
from abaqusConstants import *
import __main__

#
# Note
#

###############
## extract

# 
# def UniaxialGaugeStress(odb, elset, comp = 'S11'):
# def TriaxialGaugeStress(odb, elset):

# def GetTargetFileName(fname="extract_targets.txt"):
# def GetSetsAndKey( fname ="target_sets_and_keys.txt" ):
# def GetElsets():
# def GetNsets():
# def getVar(key, pos = None):

# odbやmodelを選択
# def SelectOdb():          return session.odbs[SelectOdbKey()]
# def SelectOdbKey():
# def SelectModel():        return mdb.models[SelectModelKey()]
# def SelectModelKey():     
# def currentOdb():         return session.odbs[currentOdbKey()]
# def currentOdbKey():      return session.viewports[session.currentViewportName].odbDisplay.name



# 集合と出力対象のキーをファイルから取得する．
# def GetSetsAndKey( fname ="target_sets_and_keys.txt" ):

# Extract XY data from results
# def XYFromField(odb, sets, key, given_pos=None):

##############
## TempXY

# def TempKeys():
# def AddPrefix(pre):
# def Sum(newName=""):
# def RemoveAll():


def B_AddPrefixToTempXY():
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    pre = getInput('Enter Prefix')
    for xy in session.xyDataObjects.keys():
      if xy[0] == '_':
        #session.curves[xy].setValues(useDefault=False, legendLabel=pre+xy)
        session.xyDataObjects[xy].setValues(legendLabel=pre+xy)
        session.xyDataObjects.changeKey(xy, pre + xy)

def B_RemoveTempXYs():
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    for xy in session.xyDataObjects.keys():
      if xy[0] == '_':
        del session.xyDataObjects[xy]

def E_SumTempXY():
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    import extract
    targets = []
    for xy in session.xyDataObjects.keys():
      if xy[0] == '_':
        targets.append(session.xyDataObjects[xy])
    ans = sum(targets)
    newName = getInput('Enter Name')
    tmpName = ans.name
    session.xyDataObjects.changeKey(tmpName, newName)
    RemoveTempXYs()
    session.viewports[session.currentViewportName].odbDisplay.display.setValues(plotState=(UNDEFORMED, ))
    session.viewports[session.currentViewportName].setValues(displayedObject=extract.currentOdb())


def D_DeformAnimate():
  import visualization
  import xyPlot
  import displayGroupOdbToolset as dgo
  #Get User Input
  ans=getInput("Enter Scale Factor (default:100)")
  if ans=="":
    factor=100
  else:
    try:
      factor=int(ans)
    except ValueError:
      factor=100
  # Main
  session.viewports[session.currentViewportName].view.setValues(session.views['Iso'])
  session.viewports[session.currentViewportName].view.rotate(xAngle=-90, yAngle=0, zAngle=0,
      mode=MODEL)
  session.viewports[session.currentViewportName].odbDisplay.commonOptions.setValues(
      deformationScaling=UNIFORM, uniformScaleFactor=factor)
  session.viewports[session.currentViewportName].view.fitView()
  session.animationController.setValues(animationType=TIME_HISTORY, viewports=(
    'Viewport: 1', ))
  session.animationController.play(duration=UNLIMITED)


def E_ExtractStressHistoryFromFieldByElset():
  import visualization
  import xyPlot
  import displayGroupOdbToolset as dgo
  #from extract import SelectOdb, GetElsets, UniaxialGaugeStress
  import os.path
  import extract
  import tempXY
  odbkey = extract.SelectOdbKey()
  print odbkey
  odb = session.odbs[odbkey]
  basename = os.path.basename(odbkey)
  stem = os.path.splitext(basename)[0]
  keys = []
  elsets = extract.GetElsets()
  for elset in elsets:
    extract.XYFromField(odb, elset, "S11")
    res = tempXY.AddPrefix(elset)
    for k in res:
      keys.append(k)
  rpt = getInput("Enter basename of rpt filename",stem) + '.rpt'
  if rpt == '.rpt':
    return
  targets = []
  for key in keys:
    targets.append( session.xyDataObjects[key] )
  session.writeXYReport(fileName=rpt, appendMode=OFF, xyData=tuple(targets))

def checkPath():
  msg = ""
  import sys
  for p in sys.path:
    msg += p + "\n"
  getInput(msg)


#def CheckImport():
#  import tempXY
  #####
  #import extract
  #res = extract.GetElsets()
  #if res is None:
  #  getInput("None")
  #else:
  #  msg = ""
  #  for i in res:
  #    msg += i + "\n"
  #  getInput(msg)


def C_Precision4():
    import sketch
    mdb.models[0].sketches['__profile__'].sketchOptions.setValues(decimalPlaces=4)

def A_RotateX90Neg():
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    session.viewports[session.currentViewportName].view.rotate(xAngle=-90, yAngle=0, zAngle=0,
        mode=MODEL)


def E_SaveAllPlotAsXYXYForamt():
  import visualization
  import xyPlot
  import displayGroupOdbToolset as dgo
  import csv
  fname = getInput("Filename to output (csv format)")
  if fname.count('.') == 0:
    fname += '.csv'
  max_len = 0
  data_list = []
  header = []
  for key in session.xyDataObjects.keys():
    xy = session.xyDataObjects[key]
    data = xy.data
    n = len(data)
    if max_len < n:
      max_len = n
    data_list.append(data)
    header.append("X")
    header.append(xy.name)
  #
  with open(fname, "wb") as f:
    out = csv.writer(f)
    out.writerow(header)
    for i in range(max_len):
      res = []
      for data in data_list:
        if i < len(data):
          pair = data[i]
          res.append(str(pair[0]))
          res.append(str(pair[1]))
        else:
          res.append("")
          res.append("")
      out.writerow(res)

def E_SaveAllPlotAsTimeSerieseFormat():
  import visualization
  import xyPlot
  import displayGroupOdbToolset as dgo
  import csv
  fname = getInput("Filename to output (csv format)")
  if fname.count('.') == 0:
    fname += '.csv'
  max_len = 0
  data_list = []
  header = ["X"]
  lengths = []
  max_data = []
  for key in session.xyDataObjects.keys():
    xy = session.xyDataObjects[key]
    data = xy.data
    n = len(data)
    if max_len < n:
      max_len = n
      max_data = data
    data_list.append(data)
    header.append(xy.name)
  #
  with open(fname, "wb") as f:
    out = csv.writer(f)
    out.writerow(header)
    for i in range(max_len):
      res = []
      res.append(str(max_data[i][0]))
      for data in data_list:
        if i < len(data):
          pair = data[i]
          res.append(str(pair[1]))
        else:
          res.append("")
      out.writerow(res)

def M_CreateCouplingAtEndsOfBoltsRivets():
  # -- 下請け関数群
  # for debug
  def p(msg):
    usage="\n(Abort?)"
    res =  getWarningReply(msg+usage,(YES,NO))
    if res == YES:
      raise RuntimeError("Stop by User")
  # ---------------------------
  # select a list
  #  """header のメッセージのあとにtargetを番号付で列挙したものを提示し
  #    ユーザーから番号の入力を得て，それに対応する値を返す．
  #  """
  def QueryList(target, header):
    keys = target.keys()
    #p("keys")
    num = len(keys)
    #p("num:"+str(num))
    if num == 0:
      return None
    if num == 1:
      return keys[0]
    #p("msgs:")
    msgs = [ str(i)+":"+k for i, k in enumerate(keys)]
    res = getInput(header + ("\n" if header else "")+"Enter number\n" +"\n".join(msgs),"")
    if res == "":
      #p("first:"+keys[0])
      return keys[0]
    else:
      #p(res+":"+keys[int(res)])
      return keys[int(res)]
  # ---------------------------
  #  """ボルトやリベットを表す集合かどうかの判定を行う．
  #   return true if the Set has edges without any face or cell.
  #   """
  def isLineSet(target):
    e = len(target.edges)
    f = len(target.faces)
    c = len(target.cells)
    res = e > 0 and (f+c)<1
    p(str(e)+" edges\n"+str(f)+" faces\n"+str(c)+" cells\nresult:"+str(res))
    return res
  # ---------------------------
  #  """リベットエンドから孔径+誤差範囲内にあるフェイスを検索"""
  def getCylinder(v, e):
    center = v.pointOn[0]
    inside = e.pointOn[0]
    height = [ (a[0] - a[1])*0.1 for a in zip(inside, center) ]
    ch = zip(center, height)
    bottom = [ a[0] - a[1]/2.0 for a in ch]
    top = [a[0] + a[1] / 2.0 for a in ch]
    return (v, bottom, top)
  # ---------------------------
  # -- 設定 --
  # ---------------------------
  model_name = QueryList(mdb.models, "Which Model?")
  #p(model_name)
  # モデル
  model = mdb.models[model_name]
  root = model.rootAssembly
  #p("num of instances is "+str(len(root.instances)))
  if len(root.instances) == 0:
    getWarningReply("No Instance was found. Exit",(YES,))
    return None
  # インスタンスの確認
  #base = root.instances[instance_name]
  #p("GetSet("+str(len(root.allSets))+")")
  #k = root.allSets.keys()[16]
  #p(k)
  #res = isLineSet(root.allSets[k])
  #p(str(res))
  # セットの取得
  keys = root.allSets.keys()
  for k in keys:
    p(k)
  vals = [root.allSets[k] for k in keys]
  p("vals")
  isLine = [isLineSet(x) for x in vals]
  p("isLine")
  wire_sets = [x for x,y in zip(vals, isLine) if y]
  #wire_sets = [root.allSets[k] for k in root.allSets.keys() if isLineSet(root.allSets[k]) ]
  p("number of candidates is "+str(len(wire_sets)))
  set_name = QueryList(wire_sets,"Select target set of bolt/rivet")
  res = getInput("Diameter", "")
  if res == "":
    return None
  diameter = float(res)
  prefix = getInput("Enter prefix", "Bolt")
  p("Setting Finished")
  #
  # -- 基本的な準備 --
  #
  # アッセンブリと主たる対象のインスタンス
  # -- 対称となる点とエッジの選択 --
  # リベットのセットを取得
  rivets = root.sets[set_name]  # => Set
  # リベット端部の点のIDリストを取得. 二重に作成しないようにsetにして重複を取り除く
  #rivet_ends_ids = [x for e in rivets.edges for x in e.getVertices()] # flatted  [ int ]
  rivet_ends_ids = set([x for e in rivets.edges for x in e.getVertices()]) # set( int )
  # リベット端部頂点のリストを作成
  rivet_end_vertices = [base.vertices[i] for i in rivet_ends_ids] # => [ Vertix ]
  # リベット端部の点の座標リストを取得
  rivet_ends = [v.pointOn[0] for v in rivet_end_vertices] # => [ (float,float, float) ]
  # 孔径を取得
  radius = diameter * 0.51 # 誤差対策で若干大き目に
  #
  # -- Coupling 作成 --
  #
  # vertex cylinder pair
  cylinder = [getCylinder(v, base.edges[v.getEdges()[0] ]) for v in rivet_end_vertices]
  # cylinderから対象となる面とエッジの集合に変換
  vef = [ (v, root.edges.getByBoundingCylinder(b,t,radius), root.faces.getByBoundingCylinder(b,t,radius)) for v, b, t in cylinder]
  # 名前と面(エッジ）と点のリストを作成． setから名前が取得できないので，名前はここで作成する．
  # cylinder内に対象が見つからなかった場合は除外する．
  nsp = [ [prefix+str(v.index), root.Set(name=prefix+'-Hole'+str(v.index), edges=es, faces=fs), root.Set(name=prefix+'-End'+str(v.index), vertices=root.vertices.findAt(v.pointOn)) ] for v, es, fs in vef if len(es)+len(fs)>0 ]
  # カップリングを作成
  cps = [ model.Coupling(name=n, controlPoint=p, surface=s, influenceRadius=WHOLE_SURFACE, couplingType=KINEMATIC, localCsys=None, u1=ON, u2=ON, u3=ON, ur1=ON, ur2=ON, ur3=ON ) for n, s, p in nsp]


#
# 名前と面(エッジ）と点のリストを作成． setから名前が取得できないので，名前はここで作成する．
# OLD:  nsp = [ [prefix+str(v.index), root.Set(name=prefix+'-Hole'+str(v.index), edges=root.edges.getByBoundingCylinder(b,t,radius), faces=root.faces.getByBoundingCylinder(b,t,radius)), root.Set(name=prefix+'-End'+str(v.index), vertices=root.vertices.findAt(v.pointOn)) ] for v, b, t in cylinder]

# 防音壁の計算での応力範囲ステップを作成し選択する．
# 計算にはReturnステップが必要．

def D_CreateRangeStepForNB():
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    #: ---- Creating Field Output From Frames ----
    #odbFullPath = 'D:/DATA/Projects/H27-NB/Separate/ana/RF2/RF2.odb'
    keys = session.odbs.keys()
    odbFullPath = keys[0]
    currentOdb = session.odbs[odbFullPath]
    frames_in_step_2=session.odbs[odbFullPath].steps['In2Out'].frames
    frames_in_step_3=session.odbs[odbFullPath].steps['Out2In'].frames
    s2f0_S=frames_in_step_2[-1].fieldOutputs['S']
    s3f0_S=frames_in_step_3[-1].fieldOutputs['S']
    tmpField_S = s3f0_S*-1+s2f0_S
    s2f0_U=frames_in_step_2[-1].fieldOutputs['U']
    s3f0_U=frames_in_step_3[-1].fieldOutputs['U']
    tmpField_U = s3f0_U*-1+s2f0_U
    scratchOdb = session.ScratchOdb(odb=currentOdb)
    sessionStep = scratchOdb.Step(name='Session Step',description='Step for Viewer non-persistent fields', domain=TIME, timePeriod=1.0)
    sessionLC = sessionStep.LoadCase(name='Range')
    reservedFrame = sessionStep.Frame(frameId=0, frameValue=0.0, description='Session Frame')
    sessionFrame = sessionStep.Frame(loadCase=sessionLC, description='Load Case: Range; Range by train wind load')
    sessionField = sessionFrame.FieldOutput(name='S', description='Stress components', field=tmpField_S)
    sessionField = sessionFrame.FieldOutput(name='U', description='Spatial displacement', field=tmpField_U)
    #: ---- End of Creating Field Output From Frames ----
    session.viewports[session.currentViewportName].odbDisplay.setFrame(step='Session Step', 
        frame=1)
    session.viewports[session.currentViewportName].odbDisplay.display.setValues(plotState=(
        CONTOURS_ON_UNDEF, ))
    session.viewports[session.currentViewportName].odbDisplay.setPrimaryVariable(
        variableLabel='S', outputPosition=INTEGRATION_POINT, refinement=(
        INVARIANT, 'Max. In-Plane Principal'), )


def B_Back2White():
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    session.graphicsOptions.setValues(backgroundStyle=SOLID, 
        backgroundColor='#FFFFFF')

#
def D_RemoveAllXY():
    import xyPlot
    for xy in session.xyDataObjects.keys():
      del session.xyDataObjects[xy]

# alias
def D_ClearAllXY():
  RemoveAllXY()

#
# """ 集合FROMにある頂点から，集合TO内のもっとも近い頂点に接続するワイヤを作成する  """
def M_ConnectWireToClosest():
    import section
    import regionToolset
    import displayGroupMdbToolset as dgm
    import part
    import material
    import assembly
    import optimization
    import step
    import interaction
    import load
    import mesh
    import job
    import sketch
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    import connectorBehavior
    try:
      # マクロで保存したもの．
      #a = mdb.models['Model-1'].rootAssembly
      #v11 = a.instances['Track'].vertices
      #a.WirePolyLine(points=((v11[140], v11[251]), (v11[141], v11[145]), (v11[136], v11[252]), (v11[137], v11[146])), mergeType=IMPRINT, meshable=OFF)
      #
      #########
      # Assemblyの取得
      n = len(mdb.models.keys())
      print "Number of models is %d" % (n,)
      if n == 1:
        a = mdb.models.values()[0].rootAssembly
      else:
        keys = mdb.models.keys()
        msg = "\n".join([ "%d: %s" % (i , key[i]) for i in range(n)])
        res = getInput("Which model? input number\n"+msg)
        i = int(res) if res.isdigit() else 0
        if i < 0: i = 0
        if i >= num: i = num - 1
        a = mdb.models[keys[i]].rootAssembly
      print "Target model is %s" % (a.modelName, )
      ####
      # 必要なセットがあるかどうかのチェック
      #####
      # エッジ数の保存   (作成された集合の判定用）
      original_edge_count = len(a.edges)
      print "Original number of edges is %d" % original_edge_count
      #####
      # 対象頂点集合の取得
      def getSet(asm, key):
        if "." in key:
          i, n = key.split(".")
          if asm.instances.has_key(i):
            ins = asm.instances[i]
            if ins.sets.has_key(n):
              return asm.instances[i].sets[n]
        if asm.sets.has_key(key):
          return asm.sets[key]
        return None
      #
      if a.sets.has_key("FROM"):
        from_key = "FROM"
      else:
        from_key = getInput("起点となる集合名を指定してください")
      from_set = getSet(a, from_key)
      if from_set is None:
        print "エラー：アセンブリにワイヤ探索起点の集合「%s」が見つかりません．" % (from_key,)
        return
      origin = from_set.vertices
      print "Number of vertices in the %s set is %d" % (from_key, len(origin))
      #
      if a.sets.has_key("TO"):
        to_key = "TO"
      else:
        to_key = getInput("終点の候補となる集合名を指定してください")
      to_set = getSet(a, to_key)
      if to_set is None:
        print "エラー：アセンブリにワイヤ接続先候補頂点を含む集合「%s」が見つかりません．" % (to_key,)
        return
      dest = to_set.vertices
      print "Number of vertices in the %s set is %d" % (to_key, len(dest) )
      if a.sets.has_key("CONNECT_FROM_TO"):
        print "エラー： 作成したワイヤを保存する集合「CONNECT_FROM_TO」がすでに存在します．削除するか名前を変更して下さい．"
        return
      ####
      # 近接頂点の検索
      points = [v.pointOn[0] for v in origin]
      print "points were created such as (%g, %g, %g)" % points[0]
      coords = tuple(points)
      closest = dest.getClosest( coordinates=tuple(points), searchTolerance=1.0)
      print "closest was created"
      ####
      # ペアのタプルの作成
      pair = tuple( zip([ v for v in origin], [ closest[k][0] for k in closest.keys()] ))
      print "Vertices pair list was created."
      ####
      # ラインの作成
      print "Creating Wires."
      a.WirePolyLine(points=pair, mergeType=IMPRINT, meshable=OFF)
      print "Done."
      ####
      # 集合作成のためのエッジ集合数の再取得
      after_edge_count = len(a.edges)
      print "Number of edges after were creation is %d" % after_edge_count
      ####
      # エッジの差分を取得
      new_edge_count = after_edge_count - original_edge_count
      print "Number of created edges in new Wire is %d" % new_edge_count
      ####
      # エッジの集合を作成
      #    新たに作成されたフィーチャーのエッジは若い番号側に保存されるので，
      #  作成された数がわかれば対象を選定できる．
      a.Set(name="CONNECT_FROM_TO", edges=a.edges[0:(new_edge_count)])
      print "Created edges were saved in the new set of CONNECT_FROM_TO."
    except Exception as e:
      info  = sys.exc_info()
      c, ax, t = info
      #print type(c)
      #print type(ax)
      #print type(t)
      #print "exception class %s" % c
      #for x in dir(ax.message):
      #  print x
      #print type(ax.message)
      #print "Message:"
      print "Error:",ax.message
      #print unicode(ax.message, 'shift_jis')
      #print "Args:"
      #for x in ax.args:
      #  print x
      #print "exit"
      with open("MacroError.txt","wb") as f:
        f.write("Message:\n")
        f.write(ax.message)
        f.write("\nArgs:\n")
        for x in ax.args:
          f.write(x)
          f.write("\n")
      raise


def B_Back2Gradation():
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    session.graphicsOptions.setValues(backgroundStyle=GRADIENT,
        backgroundColor='#000054',
        backgroundBottomColor='#7A7A90')

def B_Back2Original():
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    session.graphicsOptions.setValues(backgroundStyle=GRADIENT,
        backgroundColor='#1B2D46',
        backgroundBottomColor='#A3B1C6')


def D_ColorSetting():
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    session.viewports[session.currentViewportName].enableMultipleColors()
    session.viewports[session.currentViewportName].setColor(initialColor='#BDBDBD')
    cmap = session.viewports[session.currentViewportName].colorMappings['Material']
    cmap.updateOverrides(overrides={'FRP':(True, '#D08058', 'Default', '#D08058'),
        'STEEL': (True, '#999999', 'Default', '#999999')})
    session.viewports[session.currentViewportName].setColor(colorMapping=cmap)
    session.viewports[session.currentViewportName].disableMultipleColors()


# 節点の結果を出力するマクロ
def X_NOT_YET_ExtractHistoryFromFieldByNset():
  import visualization
  import xyPlot
  import displayGroupOdbToolset as dgo
  #from extract import SelectOdb, GetElsets, UniaxialGaugeStress
  import os.path
  import extract
  import tempXY
  odbkey = extract.SelectOdbKey()
  print odbkey
  odb = session.odbs[odbkey]
  basename = os.path.basename(odbkey)
  stem = os.path.splitext(basename)[0]
  keys = []
  nsets = extract.GetNsets()
  for nset in nsets:
    print nset
    n = nset.find(' ')
    if ' ' in nset:
      arr = nset.split()
      set_name = arr[0]
      tags = arr[1:]
    else:
      set_name = nset
      tags = ['U1']
    for tag in tags:
      print set_name + ':' + tag
      extract.XYFromField(odb, set_name, tag, NODAL)
      res = tempXY.AddPrefix(set_name)
      for k in res:
        keys.append(k)
  rpt = getInput("Enter basename of rpt filename",stem)
  if rpt == None:
    print "rpt出力はキャンセルされました"
    return
  targets = []
  for key in keys:
    targets.append( session.xyDataObjects[key] )
  session.writeXYReport(fileName=rpt + '.rpt', appendMode=OFF, xyData=tuple(targets))

def M_AssignProperty():
    import section
    import regionToolset
    import displayGroupMdbToolset as dgm
    import part
    import material
    import assembly
    import optimization
    import step
    import interaction
    import load
    import mesh
    import job
    import sketch
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    import connectorBehavior
    import os.path
    import csv
    try:
      fname = getInput('Setting File Name?')
      #fname = 'MG-24_8'  # for debug
      if not os.path.isfile(fname):
        fname = fname + '.csv'
        if not os.path.isfile(fname):
          print "File is not found"
          return
      print 'Open file:' + fname
      with open(fname, "rb") as f:
        reader = csv.reader(f)
        for row in reader:
          model, part, set, sec, offset = row[0:5]
          if not model[0] == '#':
            print row
            p = mdb.models[model].parts[part]
            r = p.sets[set]
            p.SectionAssignment(region=r,
              sectionName=sec,
              offset=float(offset),
              offsetType=SINGLE_VALUE,
              offsetField='',
              thicknessAssignment=FROM_SECTION)
    except Exception as e:
      print e.message
      raise

def M_DumpPropertyAssignment():
    import section
    import regionToolset
    import displayGroupMdbToolset as dgm
    import part
    import material
    import assembly
    import optimization
    import step
    import interaction
    import load
    import mesh
    import job
    import sketch
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    import connectorBehavior
    import os.path
    import csv
    import extract
    model = extract.SelectModel()
    fname = model.name + '_section_assignments.csv'
    with open(fname, "wb") as f:
      writer = csv.writer(f)
      writer.writerow(["#model","Part","Set","Section","Offset"])
      for part in model.parts.values():
        print part.name
        for sec in part.sectionAssignments:
          print '   ' + sec.sectionName
          if not sec.suppressed:
            writer.writerow((model.name,part.name,sec.region[0],sec.sectionName, sec.offset, sec.offsetType))

def M_CreateShellSection():
    import section
    import regionToolset
    import displayGroupMdbToolset as dgm
    import part
    import material
    import assembly
    import optimization
    import step
    import interaction
    import load
    import mesh
    import job
    import sketch
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    import connectorBehavior
    import os.path
    import csv
    try:
      #fname = 'testshell'
      fname = getInput('Setting File Name?')
      if not os.path.isfile(fname):
        fname = fname + '.csv'
        if not os.path.isfile(fname):
          print "File is not found"
          return
      print 'read:'+ fname
      with open(fname, 'rb') as f:
        print 'opened'
        reader = csv.reader(f)
        print 'reader created'
        for row in reader:
          print row
          model, name, mat, thickness = row
          if not model[0] == '#':
            t=float(thickness)*0.001
            mdb.models[model].HomogeneousShellSection(name=name, 
              preIntegrate=OFF, material=mat, thicknessType=UNIFORM, 
              thickness=t, thicknessField='', idealization=NO_IDEALIZATION, 
              poissonDefinition=DEFAULT, thicknessModulus=None, temperature=GRADIENT, 
              useDensity=OFF, integrationRule=SIMPSON, numIntPts=5)
    except Exception as e:
      print e.message
      raise



def testGetVar():
  def test_eq(key, ans, pos=None):
    res = extract.getVar(key, pos)
    if res == ans:
      print 'OK (' + key + ')'
    else:
      print 'NG (' + key + ')'
      print 'expected:'
      print ans
      print 'but:'
      print res
  test_eq('Mises', (('S', INTEGRATION_POINT, ((INVARIANT, 'Mises'),)),),)
  test_eq('LE.Max. Principal', (('LE', INTEGRATION_POINT, ((INVARIANT, 'Max. Principal'),)),) )
  test_eq('S11', (('S', INTEGRATION_POINT, ((COMPONENT, 'S11'),)),) )
  test_eq('LE11', (('LE', INTEGRATION_POINT, ((COMPONENT, 'LE11'),)),) )
  test_eq('LE.LE11', (('LE', ELEMENT_NODAL, ((COMPONENT, 'LE11'),)),) , ELEMENT_NODAL)
  test_eq('UR1', (('UR', NODAL, ((COMPONENT, 'UR1'),)),) )
  test_eq('U1', (('U', NODAL, ((COMPONENT, 'U1'),)),) )
  test_eq('RF', (('RF', NODAL),) )


# 集合からXYデータの結果を取得するマクロ
def E_ExtractXYFromField():
  try:
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    import os.path
    import tempXY
    import extract
    #
    def SetNotFound(set_name):
      print "Warnig: set " + set_name + " is not exist. Skipped"
    odbkey = extract.SelectOdbKey()
    print odbkey
    odb = session.odbs[odbkey]
    basename = os.path.basename(odbkey)
    stem = os.path.splitext(basename)[0]
    keys = []
    items = extract.GetSetsAndKey()
    for item in items:
      print item
      if ',' in item:
        arr = item.split(',')
        set_name = arr[0].strip()
        if set_name in odb.rootAssembly.elementSets.keys() or set_name in odb.rootAssembly.nodeSets.keys():
          tags = [x.strip() for x in arr[1:] ]
        else:
          SetNotFound(set_name)
          tags = [] # empty list ==> to skip XYFromField call.
      else:
        set_name = item
        if item in odb.rootAssembly.elementSets.keys():
          tags = ['S11']
        elif item in odb.rootAssembly.nodeSets.keys():
          tags = ['U']
        else:
          SetNotFound(set_name)
          tags = [] # empty list ==> to skip XYFromField call.
      for tag in tags:
        print set_name + ':' + tag
        extract.XYFromField(odb, set_name, tag)
        res = tempXY.AddPrefix(set_name)
        for k in res:
          keys.append(k)
    rpt = getInput("Enter basename of rpt filename",stem)
    if rpt == None:
      print "rpt出力はキャンセルされました"
      return
    targets = []
    for key in keys:
      targets.append( session.xyDataObjects[key] )
    session.writeXYReport(fileName=rpt + '.rpt', appendMode=OFF, xyData=tuple(targets))
  except Exception as e:
    print e.message
    raise


# 集合からXYデータの結果を取得するマクロ
def E_ExtractXYFromFieldWithSum():
  try:
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    import os.path
    import tempXY
    import extract
    #
    def SetNotFound(set_name):
      print "Warnig: set " + set_name + " is not exist. Skipped"
    odbkey = extract.SelectOdbKey()
    print odbkey
    odb = session.odbs[odbkey]
    basename = os.path.basename(odbkey)
    stem = os.path.splitext(basename)[0]
    keys = []
    items = extract.GetSetsAndKey()
    for item in items:
      print item
      if ',' in item:
        arr = item.split(',')
        set_name = arr[0].strip()
        if set_name in odb.rootAssembly.elementSets.keys() or set_name in odb.rootAssembly.nodeSets.keys():
          tags = [x.strip() for x in arr[1:] ]
        else:
          SetNotFound(set_name)
          tags = [] # empty list ==> to skip XYFromField call.
      else:
        set_name = item
        if item in odb.rootAssembly.elementSets.keys():
          tags = ['S11']
        elif item in odb.rootAssembly.nodeSets.keys():
          tags = ['U']
        else:
          SetNotFound(set_name)
          tags = [] # empty list ==> to skip XYFromField call.
      for tag in tags:
        print set_name + ':' + tag
        extract.XYFromField(odb, set_name, tag)
        #res = tempXY.AddPrefix(set_name)
        targets = []
        for xy in session.xyDataObjects.keys():
          if xy[0] == '_':
            targets.append(session.xyDataObjects[xy])
        res = sum(targets)
        session.xyDataObjects.changeKey(res.name, set_name)
        RemoveTempXYs()
        keys.append(set_name)
    rpt = getInput("Enter basename of rpt filename",stem)
    if rpt == None:
      print "rpt出力はキャンセルされました"
      return
    targets = []
    for key in keys:
      targets.append( session.xyDataObjects[key] )
    session.writeXYReport(fileName=rpt + '.rpt', appendMode=OFF, xyData=tuple(targets))
  except Exception as e:
    print e.message
    raise


def C_ResultU3():
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    session.viewports[session.currentViewportName].odbDisplay.setPrimaryVariable(
        variableLabel='U', outputPosition=NODAL, refinement=(COMPONENT, 'U3'))

def D_LegendBack2White():
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    session.viewports[session.currentViewportName].viewportAnnotationOptions.setValues(
        legendBackgroundStyle=MATCH, compass=OFF)
    session.viewports[session.currentViewportName].odbDisplay.contourOptions.setValues(
        maxAutoCompute=OFF, maxValue=100000, minAutoCompute=OFF, 
        minValue=-20000, showMinLocation=ON, showMaxLocation=ON)


def A_Z_ModelVisualSetup():
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    session.graphicsOptions.setValues(backgroundStyle=SOLID, 
        backgroundColor='#FFFFFF')
    session.viewports[session.currentViewportName].viewportAnnotationOptions.setValues(triad=OFF, 
        legend=OFF, title=OFF, state=OFF, annotations=OFF, compass=OFF)
    session.viewports[session.currentViewportName].enableMultipleColors()
    session.viewports[session.currentViewportName].setColor(initialColor='#BDBDBD')
    cmap = session.viewports[session.currentViewportName].colorMappings['Material']
    cmap.updateOverrides(overrides={'RC_FCK30':(True, '#D6D6D6', 'Default', 
        '#D6D6D6'), 'STEEL':(True, '#777777', 'Default', '#777777')})
    session.viewports[session.currentViewportName].setColor(colorMapping=cmap)
    session.viewports[session.currentViewportName].disableMultipleColors()
    session.viewports[session.currentViewportName].odbDisplay.commonOptions.setValues(
        visibleEdges=FEATURE)

def M_SetupRailConnectors():
    import section
    import regionToolset
    import displayGroupMdbToolset as dgm
    import part
    import material
    import assembly
    import optimization
    import step
    import interaction
    import load
    import mesh
    import job
    import sketch
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    import connectorBehavior
    # 準備
    currentViewport = session.viewports[session.currentViewportName]
    modelName = currentViewport.displayedObject.modelName
    m = mdb.models[modelName]
    a = m.rootAssembly
    # 特性の作成
    # レール端部
    if not m.sections.has_key('RailEndSpring'):
      m.ConnectorSection(name='RailEndSpring', assembledType=BUSHING)
      elastic_0 = connectorBehavior.ConnectorElasticity(components=(1, 2, 3, 4, 5, 6), 
        table=((7000000.0, 110000000.0, 65500.0, 264800.0, 59400.0, 250400.0), ))
      m.sections['RailEndSpring'].setValues(behaviorOptions =( elastic_0, ) )
      m.sections['RailEndSpring'].behaviorOptions[0].ConnectorOptions( )
    # まくらぎレール間
    if not m.sections.has_key('Slipper2RailSpring'):
      m.ConnectorSection(name='Slipper2RailSpring', assembledType=BUSHING)
      elastic_1 = connectorBehavior.ConnectorElasticity(components=(1, 2, 3, 4, 5, 6),
        table=((35000.0, 110000000.0, 110000.0, 1324.0, 297.0, 1252.0), ))
      m.sections['Slipper2RailSpring'].setValues(behaviorOptions = (elastic_1, ) )
      m.sections['Slipper2RailSpring'].behaviorOptions[0].ConnectorOptions( )
    #割り当て
    if a.sets.has_key('RailEnds'):
      region=a.sets['RailEnds']
      csa = a.SectionAssignment(sectionName='RailEndSpring', region=region)
      a.ConnectorOrientation(region=csa.getSet(), localCsys1=a.datums[1])
    if a.sets.has_key('Slipper2Rail'):
      region=a.sets['Slipper2Rail']
      csa = a.SectionAssignment(sectionName='Slipper2RailSpring', region=region)
      a.ConnectorOrientation(region=csa.getSet(), localCsys1=a.datums[1])


def M_Rail60kg():
    import section
    import regionToolset
    import displayGroupMdbToolset as dgm
    import part
    import material
    import assembly
    import optimization
    import step
    import interaction
    import load
    import mesh
    import job
    import sketch
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    import connectorBehavior
    currentViewport = session.viewports[session.currentViewportName]
    modelName = currentViewport.displayedObject.modelName
    m = mdb.models[modelName]
    m.IProfile(name='Rail60kgSection', l=0.0778, h=0.174, 
        b1=0.145, b2=0.065, t1=0.021, t2=0.045, t3=0.0165)
    m.BeamSection(name='Rail60kg', 
        integration=DURING_ANALYSIS, poissonRatio=0.0, 
        profile='Rail60kgSection', material='Steel', temperatureVar=LINEAR, 
        consistentMassMatrix=False)




