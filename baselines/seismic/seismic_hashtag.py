
# coding: utf-8

# In[1]:

from matplotlib.backends.backend_pdf import PdfPages
import sys
#import pandas as pd
import numpy as np
import networkx as nx
#import matplotlib.pyplot as plt
#import matplotlib.cm as cm
import operator
import time
import ast
import subprocess
from decimal import *
from collections import defaultdict
paths = ['../']
for p in paths:
        sys.path.insert(0, p)

from SRM.srm.db_manager import connect_to_db, execute_sql


# Dataset generation

# In[2]:

db_name, table = sys.argv[1], sys.argv[2]
cursor_mysql, conn = connect_to_db("10.5.18.69", "bidisha", "bidisha12")


# In[19]:


def plotGraph(prediction_dict):
    pp = PdfPages('SEISMIC80.pdf')
    for key in prediction_dict.keys():
        fig = plt.figure()
        xe = [x[0] for x in prediction_dict[key]]
        xp = [x[1] for x in prediction_dict[key]]
        plt.xlabel('time', fontsize=11)
        plt.ylabel('APE', fontsize=11)
        plt.title("id="+key, fontsize=12)
        plt.plot(xp, xe, color="g", marker=".")
        pp.savefig(fig)
    pp.close()
    
def calculateSeismic(end, filecsv):
    command = 'Rscript'
    path2script = 'seismic.R'
    # Build subprocess command
    cmd = [command, path2script]
    args = [str(end), filecsv]
    cmd = [command, path2script] + args
    x = subprocess.Popen(cmd,stdout=subprocess.PIPE).communicate()[0]
    print x
    (predTime, predicted) = x.split("\t")
    predTime = predTime.split(" ")
    predicted = predicted.split(" ")
    predTimeMod = []
    predictedMod = []
    for i in range(0, len(predTime)):
        if predicted[i] == "Inf":
            continue
        predTimeMod.append(int(Decimal(predTime[i])))
        predictedMod.append(float(predicted[i]))
    print predTimeMod,predictedMod 
    return (predTimeMod, predictedMod)


def mapeCalculate(hashtag, timesequence, prediction, t_original):
    Rinf = len(t_original)
    test_series = [float(t) for t in sys.argv[4].split(",")]
    t_original = [t[0] - t_original[0][0] for t in t_original]
    errorlist = {}
    index = 0 
    for t in test_series:
    	test = int(Rinf * t)
        t_test = t_original[test:]
        
	while index < len(timesequence) and timesequence[index]  < t_test[0]:
        	index += 1
    	index = index - 1
	apenew = 0
        for tp in t_test:
		apenew += float(abs(t_original.index(tp)+1 - prediction[index]) / (t_original.index(tp)+1))

	apenew = apenew / len(t_test)
	errorlist[t] = apenew
    return errorlist

# In[20]:

prediction_dict = defaultdict(list)
f = open(sys.argv[3])
count = 0
mape = {}
f_o = open(sys.argv[5],"w")
for hashtag in f:
    hashtagMod1 = '\"%'+hashtag.strip()+',%\"'
    hashtagMod2 = '\"%,'+hashtag.strip()+'%\"'
    hashtagMod3 = '\"'+hashtag.strip()+'\"'
    tweets = [(int(time.mktime(row[0].timetuple())), row[1]) for row in execute_sql("Select created_at,followers_Count     from %s.%s where (hashTags like %s OR hashTags like %s OR hashTags like %s)     order by created_at;", (db_name, table, hashtagMod1, hashtagMod2, hashtagMod3))]
    
    if len(tweets) < 20:
        continue
    count = count + 1
    f_i = open("seismic_train"+hashtag+".csv","w+")
    
    tweetCount = 20000
    for tweet in tweets:
	    tweetCount -= 1
            f_i.write(str(tweet[0]-tweets[0][0])+","+str(tweet[1])+"\n")
	    if tweetCount == 0:
		break
    f_i.close()
    (timeSeq, predicted) = calculateSeismic(tweets[-1][0] - tweets[0][0], "seismic_train"+hashtag+".csv")
    mape[hashtag]=mapeCalculate(hashtag, timeSeq, predicted, tweets)
    for key in mape[hashtag].keys():
        f_o.write(hashtag.strip() + "\t"+str(key)+ "\t" + str(mape[hashtag][key])+"\n")
    #f_o.write(hashtag + "\t"+key+ "\t" + str(mape[tweetid][key]))
f_o.close()

# In[22]:
'''
outlier_count = 0
weighted_sum = 0
f_o = open(sys.argv[5])
for tweetid in mape.keys():
    for key in mape[tweetid].keys():
	f_o.write(tweetid + "\t"+key+ "\t" + str(mape[tweetid][key]))
f_o.close()
'''
