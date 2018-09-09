# coding: utf-8

import sys
import random
import itertools
from functools import reduce

#
# 突然変異が・・良くないところで終わってしまう
# 突然変異は、今のままでは絶対にたたないフラグを全てたてる
# その代わりに、その周りのフラグをどこか落とす必要がある？
#

#スリザーリンクの設定
#数値は0 ~ 3の値を取りうる
#未記入をNoneで表す
#field = [
#	[3 , 2] ,
#	[2 , 3]
#]

field = [
	[3 , 3    , 3] ,
	[2 , None , 2]
]


#世代のサイズ（個体数）
generation_size = 20

#何世代まで実行するか
generation_max = 10000

#0か1をランダムで返す
def getRandom() :
	return random.randint(0 , 1)

#指定されたサイズのリストを作成
#OUT:中身は0,1をランダムに設定する
def makeRandomList( size ) :
	return [ getRandom() for _ in range(size)  ]

#染色体を生成する
#OUT:(横 , 縦)
def makeChromosome( f ):
	h_size = len(f)
	w_size = len(f[0])

	#横線
	#横線は、横に w_size ,縦に h_size+1 本引く可能性がある
	vertical = [
		makeRandomList( w_size ) for _ in range( h_size + 1 )
	]

	#縦線
	#縦線は、横に w_size+1 ,縦に h_size 本引く可能性がある
	horizontal = [
		makeRandomList( w_size + 1 ) for _ in range( h_size )
	]

	return (vertical , horizontal)


#場から評価の最高得点を計算する
#IN:設定
#OUT:最高得点値
def maxValue( f ) :
	#最高得点値は
	#正しい数値（数値の周りの線の数）の個数 * 10
	# + 正しい頂点（頂点の周りの線は0本または2本）の個数
	h_size = len(f)
	w_size = len(f[0])
	return (h_size * w_size) * 10 + (h_size + 1) * (w_size + 1)

#場と線から適切な値を計算する
#INPUTの線のイメージは下図
#   w1
#h1 f h2
#   w2
#
#OUT:評価値 0:OK -1:NG
def calculateValue(f , w1 , w2 , h1 , h2 ) :
	#引かれている線の合計数
	all = h1 + h2 + w1 + w2

	if f is None :
		return 0
	elif f == all :
		return 0
	else :
		return -1



#頂点の周りの線の数を集計する
#INPUT 
#(縦の頂点,横の頂点,横線リスト,縦線リスト）
#
#頂点と囲む線のイメージは下図
#      h1
#w1 (vh , vw)  w2
#      h2
#ただし、頂点が端の場合は線が存在しない
#
#OUT 線の合計数
def countVertex(vh , vw , vertical , horizontal) :
	h1 = 0 if vh == 0 else horizontal[vh - 1][vw]
	h2 = 0 if vh >= len(horizontal) else horizontal[vh][vw]
	w1 = 0 if vw == 0 else vertical[vh][vw - 1]
	w2 = 0 if vw >= len(vertical[0]) else vertical[vh][vw]

	return h1 + h2 + w1 + w2


#場と線から適切な値を計算する
#INPUT 
#(縦の頂点,横の頂点,横線リスト,縦線リスト）
#OUT:評価値 0:OK -1:NG
def calculateVertex(vh , vw , vertical , horizontal) :
	num = countVertex(vh , vw , vertical , horizontal)

	#評価は線の数が0または2であれば一筆書きとなる
	if num == 0 or num == 2 :
		return 0
	else :
		return -1


#染色体を評価する
#IN:(横 , 縦 , スリザーリンクの設定）
#OUT:評価値
def evaluate(vertical , horizontal , field) :
	h_size = len(field)
	w_size = len(field[0])
	maxv = maxValue(field)

	#評価は減点方式

	#各場の値に対して、
	#周辺の線が正しい本数となっているかどうかで評価する
	for h in range( h_size ) :
		for w in range( w_size ) :
			maxv += calculateValue(
				field[h][w] ,
				vertical[h][w] ,
				vertical[h + 1][w] ,
				horizontal[h][w] ,
				horizontal[h][w + 1] ,
			) * 10

	#次に各頂点に対して正しい本数（0または2）となっているか評価する
	for h in range( h_size + 1 ) :
		for w in range( w_size + 1 ) :
			maxv += calculateVertex(h , w , vertical , horizontal)

	return maxv


#ルーレットを行うための基礎データを作成
#IN:世代の染色体リスト
#OUT:世代の評価値の合計
def makeRoulette( g ) :
	#評価値の合計を取得
	return sum( age["value"] for age in g )


#ルーレット選択する
#IN(ルーレット , 染色体リスト）
#OUT:選択された染色体の番号
def selectRoulette(r , g) :
	#ルーレットから値を確定する
	randv = random.randint(1 , r)

	num = 0

	#確定された値に該当する番号を返す
	sumv = 0;
	for c in g :
		sumv += c["value"]

		#合計値が超えたところが選択値となる
		if randv <= sumv :
			break;

		num += 1;

	return num


#染色体の（縦、横）を交叉して返す
#IN:(線1,線2,分割場所)
#OUT:新しい線
def crossoverLine( l1 , l2 , n ) :
	height = len(l1)
	width = len(l1[0])

	#連結したリストを作成
	l1_linked = reduce(lambda a,b: a+b, l1,[])
	l2_linked = reduce(lambda a,b: a+b, l2,[])

	#新しく連結（分割位置は先頭側に含む）
	new_linked = l1_linked[:(n+1)] + l2_linked[(n+1):]

	#またリストに分解して返す
	new = [new_linked[i:i+width] for i in range(0 , width * height , width)]

	return new


#染色体を交叉する
#IN:染色体１,染色体２
#OUT:新しい染色体
def crossover( c1 , c2 ) :
	v_height = len(c1["vertical"])
	v_width  = len(c1["vertical"][0])
	h_height = len(c1["horizontal"])
	h_width  = len(c1["horizontal"][0])

	#縦*横の配列の小さい方の数値を最大値とする
	maxv = min(v_height * v_width , h_height * h_width)

	#分割後の指定された番号は先頭側に含めるため、
	#0始まりの最大値 - 1 を範囲とする
	randv = random.randint(0 , maxv - 1)

	new_v = crossoverLine(c1["vertical"] , c2["vertical"] , randv)
	new_h = crossoverLine(c1["horizontal"] , c2["horizontal"] , randv)

	return {
		"vertical" : new_v ,
		"horizontal" : new_h ,
	}

#突然変異を作成する
#条件との整合性を確認して、
#問題のある線を変更した染色体を返す
#
#各頂点の周りの線の数を確認する
#1本の場合は足して調整する
#頂点の右の線を変更する
#
#IN 染色体 スリザーリンクの設定
#OUT 新しい隊染色体
def mutatePlus(c , field) : 
	new_v = c["vertical"]
	new_h = c["horizontal"]
	h_size = len(field)
	w_size = len(field[0])

	#各頂点に対する確認（横線）
	#横線の確認は、一番右は核にしてもできることがないため、
	#幅 - 1まで確認する
	for h in range( h_size + 1 ) :
		for w in range( w_size ) :
			num = countVertex(h , w , c["vertical"] , c["horizontal"])

			#print( "check" + str(num) )
			if num == 1 :
				#線が少ないので横線を足す
				new_h[h - 1][w - 1] = 1
				#print( "set1" )
			elif num == 3 :
				#線が多いので横線を消す
				new_h[h - 1][w - 1] = 0
				#print( "set0" )

	return {
		"vertical" : new_v ,
		"horizontal" : new_h ,
	}

#1行出力する(最後に改行される)
def printStrLn( str ) :
	print( str )

#1行出力する
def printStr( str ) :
	sys.stdout.write( str )

#場の１文字を出力する
def printStrField( f ):
	if f is None :
		printStr( "*" )
	else :
		printStr( str(f) )

#縦線を描画する
def printHorizontal(h , f) :
	w_size = len(h)
	for s in range(w_size) :
		r = h[s]
		if r == 1 :
			printStr( "|" )
		else :
			printStr( " " )
		if s < (w_size - 1) :
			printStrField( f[s] )

#横線を描画する
def printVertical( v ) :
	for r in v :
		printStr( " " )
		if r == 1 :
			printStr( "-" )
		else :
			printStr( " " )
	
#染色体を描画する
#IN:(横 , 縦 , スリザーリンク設定)
def printChromosome( v , h , f ) :
	#横線の縦サイズ-1分を交互に描画
	h_size = len(v) -1
	for s in range(h_size) :
		printVertical( v[s] )
		printStrLn("")
		printHorizontal( h[s] , f[s] )
		printStrLn("")

	#最後の横線を描画
	printVertical( v[h_size] )
	printStrLn("")


#メイン処理
def main () :

	print("start")
	print("##")

	#第1世代に染色体を作成
	generation = []
	for size in range( generation_size ) :
		v , h = makeChromosome( field ) 
		generation.append({
			"vertical" : v ,
			"horizontal" : h  ,
			"value" : evaluate(v , h  ,field)
		})

	#最高評価値
	maxv = maxValue(field)

	#世代を繰り返す
	for age in range( generation_max ) :
		print("##### age:%d #####" % (age + 1))

		#現在の世代の染色体を表示する
		num = 0
		for c in generation :
			print("##num:" + str(num))
			printChromosome( c["vertical"] , c["horizontal"] , field )
			print("value : " +  str( c["value"] ))
			print("##")
			num += 1

		#完全な評価の染色代が存在したら終わり
		ageMax = max( c["value"] for c in generation )

		if maxv == ageMax :
			print("Success")
			break

		#突然変異
		#染色体のバランスを改善した個体に変換する
		mutationNo = random.randint(1 , generation_size) - 1
		mutation = mutatePlus( generation[mutationNo] , field ) 
		mutation["value"] = evaluate(mutation["vertical"] , mutation["horizontal"]  ,field)

		#mutationCheck
		print("#mutationcheck start#")
		printChromosome( generation[mutationNo]["vertical"] , generation[mutationNo]["horizontal"] , field )
		printChromosome( mutation["vertical"] , mutation["horizontal"] , field )
		print("#mutationcheck end#")

		generation[mutationNo] = mutation

		#ルーレット選択で染色代を配合
		roulette = makeRoulette( generation )

		#作成する数は,最大で世代サイズ分
		newgeneration = []
		for _ in range( generation_size ) :
			#何番目の染色体を配合するか確定する
			c1 = selectRoulette(roulette , generation)
			c2 = selectRoulette(roulette , generation)

			#同じ染色体同士の場合は意味がないので次へ
			if c1 == c2 : continue

			#配合する
			print( "brend(%s) :%s + %s" % (str(roulette), str(c1),  str(c2)))
			new = crossover(generation[c1] , generation[c2])
			new["value"] = evaluate(new["vertical"] , new["horizontal"]  ,field)
			newgeneration.append( new )

		generation.extend( newgeneration )

		#淘汰(世代サイズを調整する)
		generationsort = sorted(generation, key=lambda c: c["value"] ,reverse=True)
		generation = generationsort[:generation_size]

	print("end")

main()

