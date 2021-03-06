# coding: utf-8
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from datetime import datetime
import webbrowser
import shutil
import glob
import csv
import os

#####  関数 #####
# ファイル移動
def move_file():
    global errorChk
    # エラーチェック値の初期化
    errorChk = 0
    try:
        dir_path = os.path.dirname(data_path)
        move_path = os.path.join(dir_path, move_fname)
        shutil.move(move_fname, move_path)
    except:
        # エラー通知
        messagebox.showerror("Error", "WinError 183")
        # ファイルの削除
        os.remove(move_fname)
        # エラーチェック値の代入
        errorChk = 1
            
# CSVへ書込み (各エネルギー値+計算時間)
def write_csv():
    # ファイル名取得
    file_name = os.path.splitext(os.path.basename(data_path))[0]
    # CSVへ書込み
    with open(csv_name,"a+") as datafile:
        writer = csv.writer(datafile, lineterminator="\n")
        writer.writerow([file_name] + te + zpe + ehgs + engine + status + [str(calc_time)])
        
# 計算開始時間の取得
def get_btime():
    global dt1
    # 検索文字列の行を抽出、単語要素に分割 
    time = data[finalnum].split()
    
    # GAMESS, Fireflyの判定
    if "GAMESS" in time:
        # 計算開始時間 (GAMESS)
        del time[0:5]
        time_begun = " ".join(time)
        dt1 = datetime.strptime(time_begun, "%b %d %H:%M:%S %Y")
    else:
        # 計算開始時間 (Firefly)
        time_begun = time[-2] + " " + time[-1]
        dt1 = datetime.strptime(time_begun, "%H:%M:%S %d-%b-%Y")

# 計算終了時間の取得(＆計算機と状態の取得)
def get_ttime():
    global dt2, engine, status
    # 検索文字列の行を抽出、単語要素に分割 
    time = data[finalnum].split()
    # 計算機と状態の取得
    engine = [str(time[2])]
    status = [str(time[4])]
    # ABNORMALLY表記の統一
    if status == ["-ABNORMALLY-"] :
        status = ["ABNORMALLY"]
    
    # GAMESS, Fireflyの判定
    if "GAMESS" in time:
        # 計算終了時間
        time_terminated = time[-4] + " " + time[-3] + " " + time[-2] + " " + time[-1]
        dt2 = datetime.strptime(time_terminated, "%b %d %H:%M:%S %Y")
    else:
        # 計算終了時間
        time_terminated = time[-2] + " " + time[-1]
        dt2 = datetime.strptime(time_terminated, "%H:%M:%S %d-%b-%Y")

# 計算時間の取得
def get_time():
    global search_word, calc_time, engine, status
    # 検索ワードの指定
    search_word = "BEGUN"
    # 検索ワードの行番号取得
    get_num()
    # 検索ワードの存在チェック
    if finalnum !=0:
        # 計算開始時間の取得
        get_btime()
    else:
        calc_time = None
        engine = status = ["None"]
        
    # 検索ワードの指定
    search_word = "TERMINATED"
    # 検索ワードの行番号取得
    get_num()
    # 検索ワードの存在チェック
    if finalnum !=0:
        # 計算終了時間の取得
        get_ttime()
        # 計算時間
        calc_time = dt2 - dt1
    else:
        calc_time = None
        engine = status = ["None"]
        
# 全エネルギー取得
def get_te():
    global te
    # 検索文字列の1行下を抽出, 単語要素に分割 
    te = data[finalnum+1].split()
    # 不要な要素を削除
    del te[0:3]

# ゼロ点エネルギー取得
def get_zpe():
    global zpe
    # 検索文字列の2行下を抽出, 単語要素に分割
    zpe = data[finalnum+2].split()
    # 不要な要素を削除
    del zpe[1:]

# E,H,G,S 補正値取得
def get_ehgs():
    global ehgs
    # 検索文字列の5行下を抽出, 単語要素に分割
    ehgs = data[finalnum+5].split()
    # 不要な要素を削除
    del ehgs[0]
    del ehgs[3:5]

# 検索ワードの行番号取得
def get_num():
    global finalnum
    # 行番号のリセット
    finalnum = 0
    for linenum, line in enumerate(data):
        if search_word in line:
            finalnum = linenum
            
# 各エネルギー値+計算時間の取得~CSVへの書込み
def get_egs():
    global search_word, te, zpe, ehgs
    
    # 検索ワードの指定
    search_word = "ELECTRONIC ENERGY"
    # 検索ワードの行番号取得
    get_num()
    # 検索ワードの存在チェック
    if finalnum !=0:
        # 全エネルギー取得
        get_te()
    else:
        te = ["None"]

    # 検索ワードの指定
    search_word = "ZERO POINT ENERGY"
    # 検索ワードの行番号取得
    get_num()
    # 検索ワードの存在チェック
    if finalnum !=0:
        # ZPE取得
        get_zpe()
    else:
        zpe = ["None"]

    # 検索ワードの指定
    search_word = "KCAL/MOL  KCAL/MOL"
    # 検索ワードの行番号取得
    get_num()
    # 検索ワードの存在チェック
    if finalnum !=0:
        # E,H,G,S 補正値取得
        get_ehgs()
    else:
        ehgs = ["None", "None", "None", "None"]
        
    # 計算時間の取得
    get_time()

    # CSVへ書込み
    write_csv()

# outputファイルのリスト化
def output_list():
    global data
    with open(data_path,"r") as outfile:
        data = outfile.readlines()
        
# 熱化学データのCSV出力
def tmoc_fuc():
    global search_word, move_fname, csv_name
    try:
        # CSVファイル作成
        csv_name = os.path.splitext(os.path.basename(data_path))[0] + "_tmoct.csv"
        # CSV作成, 見出し追加
        with open(csv_name, "w+") as h:
            writer = csv.writer(h, lineterminator="\n")
            writer.writerow(["THERMOCHEMISTRY"])
            writer.writerow(["Name", "Energy", "ZPE", "E", "H", "G", "S", "Engine", "Status", "Time"])
            writer.writerow(["", "Hartree", "kcal/mol", "kcal/mol", "kcal/mol", "kcal/mol", "cal/mol-K", "", "", "day, H:M:S"])
        
        # outputファイルのリスト化
        output_list()
        # 各エネルギー値+計算時間の取得~CSVへの書込み
        get_egs()
    except:
        with open(csv_name, "a+") as h:
            writer = csv.writer(h, lineterminator="\n")
            writer.writerow(["NoData"])
        
# 熱化学データのCSV追加
def tmoc_add_fuc():
    global search_word, move_fname
    try:
        # outputファイルのリスト化
        output_list()
        
        # 各エネルギー値+計算時間の取得~CSVへの書込み
        get_egs()
    except:
        with open(csv_name, "a+") as h:
            writer = csv.writer(h, lineterminator="\n")
            writer.writerow(["NoData"])

# 熱化学データの取得(フォルダ指定)
def tmoc_ffuc(): 
    global data_path, move_fname
    dirPath = filedialog.askdirectory()
    
    # データが選択された場合
    if len(dirPath) != 0:
        #ファイル名の取得
        fileList = glob.glob(dirPath + "/*.out") + glob.glob(dirPath + "/*.gam") + glob.glob(dirPath + "/*.log")
        
        # リストが空の場合
        if not fileList:
            # エラー通知
            messagebox.showerror("Error", "No *.out, *.gam, *.log Files!!")
            
        else:
            # 一回目は、熱化学データのCSV作成
            data_path = fileList[0]
            tmoc_fuc()

            # 二回目以降は、CSVへ追加
            fileList = fileList[1:]
            for data_path in fileList:
                    tmoc_add_fuc()

            # CSVの移動
            move_fname = csv_name
            move_file()
            
            # CSV移動時にエラーがない場合
            if errorChk == 0:
                # 全てのタスクの終了を通知
                tk.messagebox.showinfo("Have fun!!", "Successfully!!")
    else:
        pass
        
# XYZ座標の出力
def get_xyz():
    global search_word, move_fname
    try:
        # outputファイルのリスト化
        output_list()
        # 検索ワードの指定
        search_word = "COORDINATES OF ALL ATOMS ARE (ANGS)"
        # 検索ワードの行番号取得
        get_num()
        
        # 検索ワードの存在チェック
        if finalnum !=0:
            # 検索文字列の3行目から最終行までリスト内要素を抽出
            words = data[(finalnum+3):]
            # 抽出データの書込み先を指定
            inp_name = os.path.splitext(os.path.basename(data_path))[0] + "_xyz.txt"
            datafile = open(inp_name,"w+")

            # ファイルへ書込み
            for line in words:
                # 最初の空行で処理を終了
                if line == "\n":
                    break
                else:
                    datafile.write(line)
            # ファイルを閉じる
            datafile.close()

            # inpファイルの移動
            move_fname = inp_name
            move_file()

            # 全てのタスクの終了を通知
            tk.messagebox.showinfo("Have fun!!", "Successfully!!")
        else:
            # エラー通知
            messagebox.showerror("Error", "No Coordinates!!")  
    except:
        # エラー通知
        messagebox.showerror("Error", "Error!!")

# XYZ座標の取得 (ファイル指定)
def xyz_fuc(): 
    global data_path
    typ = [("Output Files","*.out"), ("Output Files","*.gam"), ("Output Files","*.log"), ("All Files","*.*")]
    data_path = filedialog.askopenfilename(filetypes = typ)
    
    # データが選択された場合
    if len(data_path) != 0:
        # XYZ座標の出力
        get_xyz()
    else:
        pass

# $VECの出力
def get_vec():
    global search_word, move_fname
    try:
        # outputファイルのリスト化
        output_list()
        # 検索ワードの指定
        search_word = "$VEC"
        # 検索ワードの行番号取得
        get_num()
        
        # 検索ワードの存在チェック
        if finalnum !=0:
            # 検索文字列の行から最終行までリスト内要素を抽出
            words = data[(finalnum):]
            # 抽出データの書込み先を指定
            inp_name = os.path.splitext(os.path.basename(data_path))[0] + "_vec.txt"
            datafile = open(inp_name,"w+")
            # コメント追加
            datafile.write("##### INFORMATION ##############################################################\n"
                           + ".....\n" + "".join(data[(finalnum-3):(finalnum)]) +
                           "################################################################################\n\n" )
            # ファイルへ書込み
            for line in words:
                # キーワード一致で終了
                if line == " POPULATION ANALYSIS\n":
                    break
                else:
                    datafile.write(line)
            # ファイルを閉じる
            datafile.close()

            # inpファイルの移動
            move_fname = inp_name
            move_file()

            # 全てのタスクの終了を通知
            tk.messagebox.showinfo("Have fun!!", "Successfully!!")
        else:
            # エラー通知
            messagebox.showerror("Error", "No $VEC Groups!!")    
    except:
        # エラー通知
        messagebox.showerror("Error", "Error!!")

# $VECの取得 (ファイル指定)
def vec_fuc(): 
    global data_path
    typ = [("PUNCH Files","*.dat"), ("PUNCH Files","*.pun"), ("All Files","*.*")]
    data_path = filedialog.askopenfilename(filetypes = typ)
    
    # データが選択された場合
    if len(data_path) != 0:
        # $VECの出力
        get_vec()
    else:
        pass
        
# $HESSの出力
def get_hess():
    global search_word, move_fname
    try:
        # outputファイルのリスト化
        output_list()
        # 検索ワードの指定
        search_word = "$HESS"
        # 検索ワードの行番号取得
        get_num()
        
        # 検索ワードの存在チェック
        if finalnum !=0:
            # 検索文字列の行から最終行までリスト内要素を抽出
            words = data[(finalnum):]
            # 抽出データの書込み先を指定
            inp_name = os.path.splitext(os.path.basename(data_path))[0] + "_hess.txt"
            datafile = open(inp_name,"w+")
            # 近似ヘッセ行列の場合コメント追加
            if " CAUTION, APPROXIMATE HESSIAN!\n" in data[(finalnum-1)]:
                datafile.write("!Caution, Approximate Hessian\n\n" )
            else:
                pass
            # ファイルへ書込み
            for line in words:
                # キーワード一致で終了
                if line == " $END\n":
                    break
                else:
                    datafile.write(line)
            # 最後に$ENDを追加
            datafile.write(" $END\n")
            # ファイルを閉じる
            datafile.close()

            # inpファイルの移動
            move_fname = inp_name
            move_file()
            
            # 近似ヘッセ行列の場合通知
            if " CAUTION, APPROXIMATE HESSIAN!\n" in data[(finalnum-1)]:
                tk.messagebox.showwarning("Caution", "Approximate Hessian!!")
            else:
                tk.messagebox.showinfo("Have fun!!", "Successfully!!")
                
        else:
            # エラー通知
            messagebox.showerror("Error", "No $HESS Groups!!")         
    except:
        # エラー通知
        messagebox.showerror("Error", "Error!!")

# $HESSの取得 (ファイル指定)
def hess_fuc(): 
    global data_path
    typ = [("PUNCH Files","*.dat"), ("PUNCH Files","*.pun"), ("All Files","*.*")]
    data_path = filedialog.askopenfilename(filetypes = typ)
    
    # データが選択された場合
    if len(data_path) != 0:
        # $HESSの出力
        get_hess()
    else:
        pass

# 入力ファイルの取出し
def get_input():
    global move_fname
    # 抽出データの書込み先
    inp_name = os.path.splitext(os.path.basename(data_path))[0] + "_recv.inp"
    # outputファイルのリスト化
    output_list()
    try:
        # リストから検索文字列の行番号取得
        for linenum, line in enumerate(data):
            if "INPUT CARD>" in line:
                finalnum = linenum
                # 検索行を抽出 (＆不要なINPUT CARD>と空白を削除)
                words = data[finalnum].replace(" INPUT CARD>", "").rstrip() + '\n'
                with open(inp_name,"a+") as datafile:
                    # ファイルへ書込み
                    for line in words:
                            # 検索文字列がない行で処理を終了
                            if line == None:
                                break
                            else:
                                datafile.write(line)
        # 抽出データがあれば移動
        if os.path.exists(inp_name):
            # inpファイルの移動
            move_fname = inp_name
            move_file()
            # 全てのタスクの終了を通知
            tk.messagebox.showinfo("Have fun!!", "Successfully!!")
        else:
            # エラー通知
            messagebox.showerror("Error", "No Input Datas!!")
    except:
        # エラー通知
        messagebox.showerror("Error", "Error!!")
        
# 入力ファイルの取出し(ファイル指定)
def recv_fuc(): 
    global data_path
    typ = [("Output Files","*.out"), ("Output Files","*.gam"), ("Output Files","*.log"), ("All Files","*.*")]
    data_path = filedialog.askopenfilename(filetypes = typ)
    
    # データが選択された場合
    if len(data_path) != 0:
        # 入力ファイルの取出し
        get_input()
    else:
        pass

# HPへアクセス
def hp_web():
    hp_url = "http://pc-chem-basics.blog.jp/"
    webbrowser.open(hp_url)
    
# 配布ページへアクセス
def ttl_web():
    ttl_url = "http://pc-chem-basics.blog.jp/archives/24312314.html"
    webbrowser.open(ttl_url)
        
#####  GUI #####
# メイン画面
root = tk.Tk()
root.title("GAMARSS ver2.0.0")
root.resizable(width = False, height = False)

# フレーム
frame1 = ttk.Labelframe(root, text = "Output", padding = 10)
frame1.grid(row=0, column=1, padx = 15, pady = 15)

frame2 = ttk.Labelframe(root, text = "Punch", padding = 10)
frame2.grid(row=0, column=2, padx = 15, pady = 15)

# ボタン
recv_button = tk.Button(frame1, text = "RECV", command = recv_fuc)
recv_button.grid(row=0, column=0, padx = 5)

xyz_button = tk.Button(frame1, text = "XYX", command = xyz_fuc)
xyz_button.grid(row=0, column=1, padx = 5)

tmoc_button = tk.Button(frame1, text = "TMOC", command = tmoc_ffuc)
tmoc_button.grid(row=0, column=2, padx = 5)

vec_button = tk.Button(frame2, text = "VEC", command = vec_fuc)
vec_button.grid(row=0, column=0, padx = 5)

hess_button = tk.Button(frame2, text = "HESS", command = hess_fuc)
hess_button.grid(row=0, column=1, padx = 5)

# メニューバー
menubar = tk.Menu(root)
root.configure(menu = menubar)
# >File
filemenu = tk.Menu(menubar, tearoff = 0)
menubar.add_cascade(label = "File", menu = filemenu)
# --- セパレータ ---
filemenu.add_separator()
# File >Exit
filemenu.add_command(label = "Exit", command = lambda: root.destroy())
# >Help
helpmenu = tk.Menu(menubar, tearoff = 0)
menubar.add_cascade(label = "Help", menu = helpmenu)
# Help >Tutorials
helpmenu.add_command(label = "Tutorials", command = ttl_web)
# --- セパレータ ---
helpmenu.add_separator()
# Help >Website
helpmenu.add_command(label = "Website", command = hp_web)

# 画面維持
root.mainloop()