# -*- coding: mbcs -*-  シフトJIS
# Do not delete the following import lines
from abaqus import *
from abaqusConstants import *
import __main__

#######
# Prefixのルール
# A: 作業フォルダのマクロ用に予約（先頭に表示させるため）
# B: 使用頻度が高いものに使用する．
# C:
# Z: 普段使用しないもの．

def BA_RotateX90Neg():
    try:
      import extract
      extract.cvp().view.rotate(xAngle=-90, yAngle=0, zAngle=0, mode=MODEL)
    except Exception as e:
      print(e)
      raise

def BA_RotateZ180():
    import extract
    extract.cvp().view.rotate(xAngle=0, yAngle=0, zAngle=180, mode=MODEL)

def BB_Back2White():
    session.graphicsOptions.setValues(backgroundStyle=SOLID, backgroundColor='#FFFFFF')

def BB_Back2Gradation():
    session.graphicsOptions.setValues(backgroundStyle=GRADIENT,
        backgroundColor='#000054',
        backgroundBottomColor='#7A7A90')

def BB_Back2Original():
    session.graphicsOptions.setValues(backgroundStyle=GRADIENT,
        backgroundColor='#1B2D46',
        backgroundBottomColor='#A3B1C6')

def BD_View4Deform():
    session.View(name='User-4',
                 nearPlane=6508.9,
                 farPlane=15050,
                 width=7663.3,
                 height=4375.9,
                 projection=PARALLEL,
                 cameraPosition=(5878.1, 4197.6, 8612.1),
                 cameraUpVector=(-0.37389, 0.73454, -0.56626),
                 cameraTarget=(320.55, -214.08, -17.911),
                 viewOffsetX=0,
                 viewOffsetY=0,
                 autoFit=OFF)

#
def BP_RemoveAllXY():
    for xy in session.xyDataObjects.keys():
      del session.xyDataObjects[xy]

# alias
def BP_ClearAllXY():
  BP_RemoveAllXY()

def BT_AddPrefixToTempXYandReturn():
    import extract
    BT_AddPrefixToTempXY()
    session.viewports[session.currentViewportName].odbDisplay.display.setValues(plotState=(UNDEFORMED, ))
    session.viewports[session.currentViewportName].setValues(displayedObject=extract.currentOdb())

def BT_AddPrefixToTempXY():
    pre = getInput('Enter Prefix')
    for xy in session.xyDataObjects.keys():
      if xy[0] == '_':
        #session.curves[xy].setValues(useDefault=False, legendLabel=pre+xy)
        session.xyDataObjects[xy].setValues(legendLabel=pre+xy)
        session.xyDataObjects.changeKey(xy, pre + xy)

def BT_RemoveTempXYs():
    for xy in session.xyDataObjects.keys():
      if xy[0] == '_':
        del session.xyDataObjects[xy]

def C_Precision4():
    import sketch
    mdb.models[0].sketches['__profile__'].sketchOptions.setValues(decimalPlaces=4)

def C_ResultU3():
    session.viewports[session.currentViewportName].odbDisplay.setPrimaryVariable(
        variableLabel='U', outputPosition=NODAL, refinement=(COMPONENT, 'U3'))

def D_DeformAnimate():
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
  session.animationController.setValues(animationType=TIME_HISTORY, viewports=('Viewport: 1', ))
  session.animationController.play(duration=UNLIMITED)

def D_ColorSetting():
    session.viewports[session.currentViewportName].enableMultipleColors()
    session.viewports[session.currentViewportName].setColor(initialColor='#BDBDBD')
    cmap = session.viewports[session.currentViewportName].colorMappings['Material']
    cmap.updateOverrides(overrides={'FRP':(True, '#D08058', 'Default', '#D08058'),
        'STEEL': (True, '#999999', 'Default', '#999999')})
    session.viewports[session.currentViewportName].setColor(colorMapping=cmap)
    session.viewports[session.currentViewportName].disableMultipleColors()

def D_LegendBack2White():
    session.viewports[session.currentViewportName].viewportAnnotationOptions.setValues(
        legendBackgroundStyle=MATCH, compass=OFF)

def D_CreateRangeStepForNB():
    # 防音壁の計算での応力範囲ステップを作成し選択する．
    # 計算にはReturnステップが必要．
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

# 集合からXYデータの結果を取得するマクロ
def E_ExtractXYFromField():
  try:
    import os.path
    import tempXY
    import extract
    #
    def SetNotFound(set_name):
      print("Warning: set " + set_name + " is not exist. Skipped")
    odbkey = extract.SelectOdbKey()
    print(odbkey)
    odb = session.odbs[odbkey]
    basename = os.path.basename(odbkey)
    stem = os.path.splitext(basename)[0]
    keys = []
    items = extract.GetSetsAndKey()
    for item in items:
      print(item)
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
        print(set_name + ':' + tag)
        extract.XYFromField(odb, set_name, tag)
        res = tempXY.AddPrefix(set_name)
        for k in res:
          keys.append(k)
    rpt = getInput("Enter basename of rpt filename",stem)
    if rpt == None:
      print("rpt出力はキャンセルされました")
      return
    targets = []
    for key in keys:
      targets.append( session.xyDataObjects[key] )
    session.writeXYReport(fileName=rpt + '.rpt', appendMode=OFF, xyData=tuple(targets))
  except Exception as e:
    print(e.message)
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
      print("Warnig: set " + set_name + " is not exist. Skipped")
    odbkey = extract.SelectOdbKey()
    print(odbkey)
    odb = session.odbs[odbkey]
    basename = os.path.basename(odbkey)
    stem = os.path.splitext(basename)[0]
    keys = []
    items = extract.GetSetsAndKey()
    for item in items:
      print(item)
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
        print(set_name + ':' + tag)
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
      print("rpt出力はキャンセルされました")
      return
    targets = []
    for key in keys:
      targets.append( session.xyDataObjects[key] )
    session.writeXYReport(fileName=rpt + '.rpt', appendMode=OFF, xyData=tuple(targets))
  except Exception as e:
    print(e.message)
    raise

def E_ExtractStressHistoryFromFieldByElset():
  import os.path
  import extract
  import tempXY
  from abaqus import session
  odbkey = extract.SelectOdbKey()
  print(odb_key)
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

def E_SaveAllPlotAsTimeSeriesFormat():
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

def F_SelectModes():
  try:
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    import extract
    odb = extract.currentOdb()
    #odbName=session.viewports[session.currentViewportName].odbDisplay.name
    #session.odbData[odbName].setValues(activeFrames=(('Freq', ('1:15:7', )), ))
    modes = getInput("Input Mode numbers with space separated")
    if modes == '':
      return
    nm = odb.steps.values()[0].name
    #print nm
    #print modes
    lst = [ x for x in modes.split(' ') ]
    #print lst
    tpl = tuple(lst)
    #print tpl
    odbName=session.viewports[session.currentViewportName].odbDisplay.name
    session.odbData[odbName].setValues(activeFrames=((nm, tpl), ))
    #
  except Exception as e:
    print(e.message)
    raise

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
      print("Number of models is %d" % (n,))
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
      print("Target model is %s" % (a.modelName, ))
      ####
      # 必要なセットがあるかどうかのチェック
      #####
      # エッジ数の保存   (作成された集合の判定用）
      original_edge_count = len(a.edges)
      print("Original number of edges is %d" % original_edge_count)
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
        print("エラー：アセンブリにワイヤ探索起点の集合「%s」が見つかりません．" % (from_key,))
        return
      origin = from_set.vertices
      print("Number of vertices in the %s set is %d" % (from_key, len(origin)))
      #
      if a.sets.has_key("TO"):
        to_key = "TO"
      else:
        to_key = getInput("終点の候補となる集合名を指定してください")
      to_set = getSet(a, to_key)
      if to_set is None:
        print("エラー：アセンブリにワイヤ接続先候補頂点を含む集合「%s」が見つかりません．" % (to_key,))
        return
      dest = to_set.vertices
      print("Number of vertices in the %s set is %d" % (to_key, len(dest) ))
      if a.sets.has_key("CONNECT_FROM_TO"):
        print("エラー： 作成したワイヤを保存する集合「CONNECT_FROM_TO」がすでに存在します．削除するか名前を変更して下さい．")
        return
      ####
      # 近接頂点の検索
      points = [v.pointOn[0] for v in origin]
      print("points were created such as (%g, %g, %g)" % points[0])
      coords = tuple(points)
      closest = dest.getClosest( coordinates=tuple(points), searchTolerance=1.0)
      print("closest was created")
      ####
      # ペアのタプルの作成
      pair = tuple( zip([ v for v in origin], [ closest[k][0] for k in closest.keys()] ))
      print("Vertices pair list was created.")
      ####
      # ラインの作成
      print("Creating Wires.")
      a.WirePolyLine(points=pair, mergeType=IMPRINT, meshable=OFF)
      print("Done.")
      ####
      # 集合作成のためのエッジ集合数の再取得
      after_edge_count = len(a.edges)
      print("Number of edges after were creation is %d" % after_edge_count)
      ####
      # エッジの差分を取得
      new_edge_count = after_edge_count - original_edge_count
      print("Number of created edges in new Wire is %d" % new_edge_count)
      ####
      # エッジの集合を作成
      #    新たに作成されたフィーチャーのエッジは若い番号側に保存されるので，
      #  作成された数がわかれば対象を選定できる．
      a.Set(name="CONNECT_FROM_TO", edges=a.edges[0:(new_edge_count)])
      print("Created edges were saved in the new set of CONNECT_FROM_TO.")
    except Exception as e:
      info  = sys.exc_info()
      c, ax, t = info
      #print(type(c))
      #print(type(ax))
      #print(type(t))
      #print("exception class %s" % c)
      #for x in dir(ax.message):
      #  print(x)
      #print(type(ax.message))
      #print("Message:")
      print("Error:",ax.message)
      #print(unicode(ax.message, 'shift_jis'))
      #print("Args:")
      #for x in ax.args:
      #  print(x)
      #print("exit")
      with open("MacroError.txt","wb") as f:
        f.write("Message:\n")
        f.write(ax.message)
        f.write("\nArgs:\n")
        for x in ax.args:
          f.write(x)
          f.write("\n")
      raise

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
      fname = getInput('Setting File Name?','Assign.csv')
      #fname = 'MG-24_8'  # for debug
      if not os.path.isfile(fname):
        fname = fname + '.csv'
        if not os.path.isfile(fname):
          print("File is not found")
          return
      print('Open file:' + fname)
      with open(fname, "rb") as f:
        reader = csv.reader(f)
        for row in reader:
          model, part, set, sec, offset = row[0:5]
          if not model[0] == '#':
            print(row)
            p = mdb.models[model].parts[part]
            r = p.sets[set]
            p.SectionAssignment(region=r,
              sectionName=sec,
              offset=float(offset),
              offsetType=SINGLE_VALUE,
              offsetField='',
              thicknessAssignment=FROM_SECTION)
    except Exception as e:
      print(e.message)
      raise

def M_DumpPartSets():
  try:
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
    fname = model.name + '_part_sets.csv'
    with open(fname, "wb") as f:
      writer = csv.writer(f)
      writer.writerow(["#model","Part","Set"])
      for part in model.parts.values():
        print part.name
        for s in part.sets.keys():
          writer.writerow((model.name,part.name,s))
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
        print(part.name)
        for sec in part.sectionAssignments:
          print('   ' + sec.sectionName)
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
      fname = getInput('Setting File Name?','Prop.csv')
      if not os.path.isfile(fname):
        fname = fname + '.csv'
        if not os.path.isfile(fname):
          print("File is not found")
          return
      print('read:'+ fname)
      with open(fname, 'rb') as f:
        print('opened')
        reader = csv.reader(f)
        print('reader created')
        for row in reader:
          print(row)
          model, name, mat, thickness = row
          if not model[0] == '#':
            t=float(thickness)*0.001
            mdb.models[model].HomogeneousShellSection(name=name, 
              preIntegrate=OFF, material=mat, thicknessType=UNIFORM, 
              thickness=t, thicknessField='', idealization=NO_IDEALIZATION, 
              poissonDefinition=DEFAULT, thicknessModulus=None, temperature=GRADIENT, 
              useDensity=OFF, integrationRule=SIMPSON, numIntPts=5)
    except Exception as e:
      print(e.message)
      raise

def M_CreateCouplingAtEndsOfBoltsRivets():
 try:
  # -- 下請け関数群
  # for debug
  def p(msg):
    usage="\n(Abort?)"
    res =  getWarningReply(str(msg)+usage,(YES,NO))
    if res == YES:
      raise RuntimeError("Stop by User")
  # ---------------------------
  # select a list
  #  """header のメッセージのあとにtargetを番号付で列挙したものを提示し
  #    ユーザーから番号の入力を得て，それに対応する値を返す．
  #  """
  def QueryList(target, header):
    num = len(target)
    #p("num:"+str(num))
    if num == 0:
      return None
    if num == 1:
      return target[0]
    #p("msgs:")
    msgs = [ str(i)+":"+k for i, k in enumerate(target)]
    res = getInput(header + ("\n" if header else "")+"Enter number\n" +"\n".join(msgs),"")
    if res == "":
      #p("first:"+keys[0])
      return target[0]
    else:
      #p(res+":"+keys[int(res)])
      return target[int(res)]
  # ---------------------------
  #  """ボルトやリベットを表す集合かどうかの判定を行う．
  #   return true if the Set has edges without any face or cell.
  #   """
  def isLineSet(target):
    e = len(target.edges)
    f = len(target.faces)
    c = len(target.cells)
    res = e > 0 and (f+c)<1
    #p(str(e)+" edges\n"+str(f)+" faces\n"+str(c)+" cells\nresult:"+str(res))
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
  model_name = QueryList(mdb.models.keys(), "Which Model?")
  #p(model_name)
  # モデル
  model = mdb.models[model_name]
  root = model.rootAssembly
  #p("num of instances is "+str(len(root.instances)))
  if len(root.instances) == 0:
    getWarningReply("No Instance was found. Exit",(YES,))
    return None
  # セットの取得
  keys = root.allSets.keys()
  wire_set_keys = []
  for k in keys:
    st = root.allSets[k]
    if isLineSet(st):
      wire_set_keys.append(k)
  #p("number of candidates is "+str(len(wire_set_keys)))
  set_name = QueryList(wire_set_keys, "Select target set of bolt/rivet")
  res = getInput("Diameter", "")
  if res == "":
    return None
  diameter = float(res)
  # 孔径を取得
  radius = diameter * 0.51 # 誤差対策で若干大き目に
  #
  # 結果出力のPrefix
  prefix = getInput("Enter prefix", "Bolt")
  #p("Setting Finished")
  #
  # -- 基本的な準備 --
  #
  # アッセンブリと主たる対象のインスタンス
  # -- 対称となる点とエッジの選択 --
  # リベットのセットを取得
  rivets = root.sets[set_name]  # => Set
  # リベット端部の点を取得．複数のエッジで共有されている場合は対象外とする．
  targets = {}
  for e in rivets.edges:
    inst = e.instanceName
    for i in e.getVertices():
     if inst is None:
       v = root.vertices[i]
       key = str(i)
     else:
       v = root.instances[inst].vertices[i]
       key = inst + "." + str(i)
     if key in targets:
       targets[key] = None  # すでに存在すれば，中身を空に
     else:
       targets[key] = v #(v, e, v.pointOn, inst)
  for k in targets.keys():
    if targets[k] is None:
      del targets[k]
  #
  ins_names = root.instances.keys()
  # -- Coupling 作成 --
  #
  for key in targets:
    v = targets[key]
    xkey = key.replace(".","_")
    # 親の取得
    inst = v.instanceName
    parent = root if inst is None else root.instances[inst]
    # 接続するエッジを取得
    eid = v.getEdges()[0]
    e = parent.edges[eid]
    # 検索する円柱範囲を計算
    #c, b, t = getCylinder(v, e)
    center = v.pointOn[0]
    inside = e.pointOn[0]
    height = [ (a[0] - a[1])*0.1 for a in zip(inside, center) ]
    ch = zip(center, height)
    bottom = [ a[0] - a[1]/2.0 for a in ch]
    top = [a[0] + a[1] / 2.0 for a in ch]
    # cylinderから対象となる面とエッジの集合に変換  # 検索先はインスタンス限定．
    ss = None
    to_name = prefix + "-Hole-" + xkey
    for ins_name in ins_names:
      instance = root.instances[ins_name]
      # サーフェースが優先
      fs = instance.faces.getByBoundingCylinder(bottom, top, radius)
      if len(fs) > 0:
        ss = root.Set(name=to_name, faces=fs)
        break
      # なぜかエラーになるものがあるので，一旦無視
      #ed = instance.edges.getByBoundingCylinder(bottom, top, radius)
      #if len(ed) > 0:
      #  ss = root.Set(name=to_name, edges=ed)
      #  break
    # 見つかればカップリングを作成する．
    if not ss is None:
      # 接続元の  点の集合
      from_name = prefix + "-End-" + xkey
      # findAtでVerticesArrayにしないと集合が作成できない
      vs = parent.vertices.findAt(v.pointOn)
      ps = root.Set(name=from_name, vertices=vs)
      # カップリングを作成
      cp_name = prefix + "-" + xkey
      model.Coupling(name=cp_name, controlPoint=ps, surface=ss,
        influenceRadius=WHOLE_SURFACE, couplingType=KINEMATIC, localCsys=None,
        u1=ON, u2=ON, u3=ON, ur1=ON, ur2=ON, ur3=ON )
    #else:
    #  print(key + ": not found")
  print("Done")
 except Exception as e:
   info  = sys.exc_info()
   c, ax, t = info
   print("Error:",ax.message)

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
    import extract
    currentViewport = session.viewports[session.currentViewportName]
    modelName = currentViewport.displayedObject.modelName
    m = mdb.models[modelName]
    m.IProfile(name='Rail60kgSection', l=0.0778, h=0.174,
        b1=0.145, b2=0.065, t1=0.021, t2=0.045, t3=0.0165)
    m.BeamSection(name='Rail60kg',
        integration=DURING_ANALYSIS, poissonRatio=0.0,
        profile='Rail60kgSection', material='Steel', temperatureVar=LINEAR,
        consistentMassMatrix=False)

def O_AbsRainbow():
    session.Spectrum(name="AbsRaiwbow24", colors =('#FF0000', '#FF5C00', '#FFB900',
        '#E7FF00', '#8BFF00', '#2EFF00', '#00FF2E', '#00FF8B', '#00FFE7',
        '#00B9FF', '#005CFF', '#0000FF', '#0000FF', '#005CFF', '#00B9FF',
        '#00FFE7', '#00FF8B', '#00FF2E', '#2EFF00', '#8BFF00', '#E7FF00',
        '#FFB900', '#FF5C00', '#FF0000', ))
    session.Spectrum(name="AbsRainbow12", colors =('#FF0000', '#FFB900', '#E7FF00',
        '#2EFF00', '#00FFE7', '#0000FF', '#0000FF', '#00FFE7', '#2EFF00',
        '#E7FF00', '#FFB900', '#FF0000', ))

def O_GotoRangeStep():
  import extract
  odb = extract.currentOdb()
  frame_id = len(odb.steps['Session Step'].frames) - 1
  extract.currentViewport().odbDisplay.setFrame(step='Session Step', frame=frame_id)

def O_PlotTrainLoad():
  try:
    import extract
    odb = extract.currentOdb()
    cvp = extract.cvp()
    a = odb.rootAssembly
    #
    start = float(getInput("列車スタート位置", "0.0"))
    speed = float(getInput("列車速度", "1.0"))
    num_car = int(getInput("何両編成？", "2"))
    #
    ra = "RAILA"
    if not ra in a.nodeSets.keys():
      ra = getInput("右側レール集合の名前は？","Rail-2")
      if not ra in a.nodeSets.keys():
        print("右側レールの集合 %s が見つかりません" % (ra,))
        return
    rail_a = a.nodeSets[ra]
    #
    rb = "RAILB"
    if not rb in a.nodeSets.keys():
      rb = getInput("左側レール集合の名前は？","Rail-1")
      if not rb in a.nodeSets.keys():
        print("左側レールの集合 %s が見つかりません" % (rb,))
        return
    rail_b = a.nodeSets[rb]
    #
    a_y = rail_a.nodes[0][0].coordinates[1]
    a_z = rail_a.nodes[0][0].coordinates[2]
    b_y = rail_b.nodes[0][0].coordinates[1]
    b_z = rail_b.nodes[0][0].coordinates[2]
    a_xs  = [ n.coordinates[0] for n in rail_a.nodes[0] ]
    b_xs  = [ n.coordinates[0] for n in rail_b.nodes[0] ]
    x_min = min( a_xs + b_xs )
    x_max = max( a_xs + b_xs )
    #
    od = cvp.odbDisplay
    ff = od.fieldFrame
    fs = od.fieldSteps[ff[0]]
    tm = fs[8][ff[1]]  # time in step
    #
    # 過去の矢印を消す
    for nm in odb.userData.annotations.keys():
      if nm[0:3] == "TL-":
        del odb.userData.annotations[nm]
    #
    origin = start + speed * tm
    axs = (2.5, 5.0, 20.0, 22.5)
    for car in range(num_car):
      for ax in range(4):
        x = origin - 25.0*car - axs[ax]
        if  x <= x_max and x >= x_min:
          plotLoadingArrow("TL-A-%d-%d" % (car+1, ax+1), x, a_y, a_z, 0.0, 0.0, 0.0, 0, 10, "P")
          plotLoadingArrow("TL-B-%d-%d" % (car+1, ax+1), x, b_y, b_z, 0.0, 0.0, 0.0, 0, 10, "P")
    #
  except Exception as e:
    print(e)
    raise

def O_PlotLoadArrowToNset():
  try:
    import extract
    odb = extract.currentOdb()
    #cvp = extract.cvp()
    a = odb.rootAssembly
    #
    setName = getInput("荷重矢印を記入する節点集合名")
    label = getInput("荷重ラベル（必要により荷重値に修正）", "P")
    alen = float(getInput("矢印の長さ","10"))
    #
    if not setName in a.nodeSets.keys():
      print("節点集合 %s が見つかりません" % (setName,))
      return
    targets = a.nodeSets[setName]
    #
    a_x = targets.nodes[0][0].coordinates[0]
    a_y = targets.nodes[0][0].coordinates[1]
    a_z = targets.nodes[0][0].coordinates[2]
    #
    # 過去の矢印を消す
    for nm in odb.userData.annotations.keys():
      if nm[0:3] == "CL-":
        del odb.userData.annotations[nm]
    #
    i = 0
    for nd in targets.nodes[0]:
      i = i + 1
      c = nd.coordinates
      plotLoadingArrow("CL-%d" % (i, ), c[0], c[1], c[2], 0.0, 0.0, 0.0, 0, alen, label)
    #
  except Exception as e:
    print(e)
    raise

def O_LiveLoadStress():
  import extract
  from textRepr import prettyPrint as pp

  def getRes(frame):
    fo = frame.fieldOutputs
    return (fo['S'], fo['U'])

  #: ---- Creating Field Output From Frames ----
  odb = extract.currentOdb()
  out = session.ScratchOdb(odb=odb)
  target_frames = odb.steps.values()[-1].frames
  base_frame = target_frames[0]
  (s0, u0) = getRes(base_frame)
  print('res')
  sessionStep = out.Step(name='LiveLoad', description='Reaction by Live Load', domain=TIME, timePeriod=1.0)
  for i in range(len(target_frames)):
    print('Frame:%03d' % i)
    (s1, u1) = getRes(target_frames[i])
    s  = 0.001*(s1-s0)   # kPa to MPa
    u  = (u1 - u0)*1000  # m to mm
    sessionLC = sessionStep.LoadCase(name='LL%03d' % i)
    sessionFrame = sessionStep.Frame(loadCase=sessionLC, description='Load Case: LL%03d; Restults by Live Load' % i)
    sessionField = sessionFrame.FieldOutput(name='S',    description='Stress components', field=s)
    sessionField = sessionFrame.FieldOutput(name='U',    description='Spatial displacement', field=u)

def O_LiveLoadResults():
  import extract
  from textRepr import prettyPrint as pp

  def getRes(frame):
    fo = frame.fieldOutputs
    return (fo['RF'], fo['RM'], fo['S'], fo['SF'], fo['SM'], fo['U'], fo['UR'])

  #: ---- Creating Field Output From Frames ----
  odb = extract.currentOdb()
  out = session.ScratchOdb(odb=odb)
  target_frames = odb.steps.values()[-1].frames
  base_frame = target_frames[0]
  (rf0, rm0, s0, sf0, sm0, u0, ur0) = getRes(base_frame)
  print('res')
  sessionStep = out.Step(name='LiveLoad', description='Reaction by Live Load', domain=TIME, timePeriod=1.0)
  for i in range(len(target_frames)):
    print('Frame:%03d' % i)
    (rf1, rm1, s1, sf1, sm1, u1, ur1) = getRes(target_frames[i])
    rf = rf1 - rf0
    rm = rm1 - rm0
    s  = 0.001*(s1-s0)   # kPa to MPa
    sf = sf1 - sf0
    sm = sm1 - sm0
    u  = (u1 - u0)*1000  # m to mm
    ur = ur1 - ur0
    sessionLC = sessionStep.LoadCase(name='LL%03d' % i)
    sessionFrame = sessionStep.Frame(loadCase=sessionLC, description='Load Case: LL%03d; Restults by Live Load' % i)
    sessionField = sessionFrame.FieldOutput(name='RF',   description='Reaction force', field=rf)
    sessionField = sessionFrame.FieldOutput(name='RM',   description='Reaction moment', field=rm)
    sessionField = sessionFrame.FieldOutput(name='S',    description='Stress components', field=s)
    sessionField = sessionFrame.FieldOutput(name='SF',   description='Section Forces', field=sf)
    sessionField = sessionFrame.FieldOutput(name='SM',   description='Section Moments', field=sm)
    sessionField = sessionFrame.FieldOutput(name='U',    description='Spatial displacement', field=u)
    sessionField = sessionFrame.FieldOutput(name='UR',   description='Rotational displacement', field=ur)

# 節点の結果を出力するマクロ
def X_NOT_YET_ExtractHistoryFromFieldByNset():
  import os.path
  import extract
  import tempXY
  odbkey = extract.SelectOdbKey()
  print(odbkey)
  odb = session.odbs[odbkey]
  basename = os.path.basename(odbkey)
  stem = os.path.splitext(basename)[0]
  keys = []
  nsets = extract.GetNsets()
  for nset in nsets:
    print(nset)
    n = nset.find(' ')
    if ' ' in nset:
      arr = nset.split()
      set_name = arr[0]
      tags = arr[1:]
    else:
      set_name = nset
      tags = ['U1']
    for tag in tags:
      print(set_name + ':' + tag)
      extract.XYFromField(odb, set_name, tag, NODAL)
      res = tempXY.AddPrefix(set_name)
      for k in res:
        keys.append(k)
  rpt = getInput("Enter basename of rpt filename",stem)
  if rpt == None:
    print("rpt出力はキャンセルされました")
    return
  targets = []
  for key in keys:
    targets.append( session.xyDataObjects[key] )
  session.writeXYReport(fileName=rpt + '.rpt', appendMode=OFF, xyData=tuple(targets))

def Z_ModelVisualSetup():
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

def Z_TMP20201207_View4():
    session.View(name='User-4', nearPlane=68.038, farPlane=103.15, width=8.9694, 
        height=5.3688, projection=PARALLEL, cameraPosition=(45.302, -61.577, 
        26.875), cameraUpVector=(-0.4029, 0.4029, 0.82179), cameraTarget=(
        -14.612, -1.6631, 3.7516), viewOffsetX=0, viewOffsetY=0, autoFit=OFF)


def __template():
    try:
      pass
    except Exception as e:
      print(e)
      raise


def plotLoadingArrow(arrowName, x, y, z, dx, dy, dz, ox, oy, caption=""):
    import extract
    odb = extract.currentOdb()
    cvp = extract.cvp()
    ud = odb.userData
    if arrowName in ud.annotations.keys():
      del ud.annotations[arrowName]
    a = ud.Arrow(
        name=arrowName,
        startAnchor=(x, y, z),
        startPoint=(ox, oy),
        endAnchor=(x, y, z),
        color='#FF0000',
        lineThickness=THIN) # VERY_THIN, THIN, MEDIUM, THICK
    cvp.plotAnnotation(annotation=a)
    if caption != "":
      textName = arrowName+'_Cap'
      if textName in ud.annotations.keys():
        del ud.annotations[textName]
      t = ud.Text(
        name=textName,
        text=caption,
        offset=(ox, oy),
        anchor=(x + dx, y + dy, z + dz),
        referencePoint=BOTTOM_CENTER,
        justification=CENTER)
      cvp.plotAnnotation(annotation=t)

def testGetVar():
  def test_eq(key, ans, pos=None):
    import extract
    res = extract.getVar(key, pos)
    if res == ans:
      print('OK (' + key + ')')
    else:
      print('NG (' + key + ')')
      print('expected:')
      print(ans)
      print('but:')
      print(res)
  test_eq('Mises', (('S', INTEGRATION_POINT, ((INVARIANT, 'Mises'),)),),)
  test_eq('LE.Max. Principal', (('LE', INTEGRATION_POINT, ((INVARIANT, 'Max. Principal'),)),) )
  test_eq('S11', (('S', INTEGRATION_POINT, ((COMPONENT, 'S11'),)),) )
  test_eq('LE11', (('LE', INTEGRATION_POINT, ((COMPONENT, 'LE11'),)),) )
  test_eq('LE.LE11', (('LE', ELEMENT_NODAL, ((COMPONENT, 'LE11'),)),) , ELEMENT_NODAL)
  test_eq('UR1', (('UR', NODAL, ((COMPONENT, 'UR1'),)),) )
  test_eq('U1', (('U', NODAL, ((COMPONENT, 'U1'),)),) )
  test_eq('RF', (('RF', NODAL),) )

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




