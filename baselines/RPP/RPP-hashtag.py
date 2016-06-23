
# coding: utf-8

# In[4]:

import sys
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import operator
import time
import ast
import math
import subprocess
from scipy.stats import norm
from collections import defaultdict
from collections import defaultdict
paths = ['../']
for p in paths:
        sys.path.insert(0, p)

from SRM.srm.db_manager import connect_to_db, execute_sql


# In[5]:

def param_estimate(t_train, T):
    """ For accurate calculation, use the last timestamp from t_train as T and the rest shall be passed as 
    commandline arguments to estimate parameters
    """
    t_args = "\t".join(str(x) for x in t_train[:-1])
    #print command_arg
    cmd = ['./RPP', str(T), t_args]

    res = subprocess.check_output(cmd, universal_newlines=True)
    #res = !./RPP  $T $t_args
    #print res
    l, mu, sigma = (float(x) for x in "".join(res).split('\t'))
    #print l, mu, sigma
    return l, mu, sigma

def predict(l, mu, sigma, T, nd, tp) :
    m = 10 # Prior bilief. Make sure m_m in mic_model.cpp has the same value
    try:
        f_tp = norm.cdf((math.log(tp) - mu)/sigma)
        norm.cdf(f_tp)    
        f_T = norm.cdf((math.log(T) - mu)/sigma)
        norm.cdf(f_T)
        cn = (m + nd)*math.exp((f_tp - f_T)*l) - m
        #print "Predicted", l, (f_tp - f_T)*l
    #print cn
    
        te = int(math.ceil(cn))
        return te
    except Exception as e:
    #    print e
        return -1
    
def mape(ta, tp):
    """Calculated MAPE for actual values ta and predicted values tp
    """
    diff = 0
    n = len(ta)
    for i in range(n):
        diff+= abs(ta[i]-tp[i])/float(ta[i])
    return diff/n


# In[3]:

#db_name, table = "srm", "BigBillionDay"
#cursor_mysql, conn = connect_to_db("localhost", "root", "root")


# In[23]:

prediction_dict = defaultdict(list)
#f = open("Data/timeseries_ICC.txt")
f = open(sys.argv[1])
count = 0
for line in f:
    tokens = line.split("\t")
    tweetId = tokens[0]
    
    #print tweetId
    t_original = tokens[1].strip().split(",")
    length = min(20000, len(t_original))
    t_original = [(int(t) - int(t_original[0])) + 1 for t in t_original]

    splitIndex = int(len(t_original) * float(sys.argv[2]))
    t_train, t_test = t_original[:splitIndex], t_original[splitIndex+1 : ]
    
    #Training 
    T = t_train[-1]
    #print t_train
    l=0
    mu=0
    sigma=0
    try:
    	l, mu, sigma = param_estimate(t_train, T)
        #print l
    except:
        print "Error", tweetId
        continue
    if math.isnan(l):
            print "Error L", tweetId
            continue
    #print "Training"
    #
    nd = len(t_train[:-1])
    
    for tp in t_test:
        
        te = predict(l, mu, sigma, T, nd, tp)
        if te == -1 : 
            print tweetId, tp
	    if tweetId in prediction_dict: del prediction_dict[tweetId]            
            break
        #print "Real", t_original.index(tp)+1
        if not prediction_dict.has_key(tweetId):
            prediction_dict[tweetId] = [(tp-T, t_original.index(tp)+1, te)]
        else :
            prediction_dict[tweetId].append((tp-T, t_original.index(tp)+1, te))
    count = count + 1
#print count


# In[24]:
f_w = open(sys.argv[3],"w")
mape_dict = dict()
for tweetid in prediction_dict.keys():
        xp = [x[1] for x in prediction_dict[tweetid]]
        xe = [x[2] for x in prediction_dict[tweetid]]
        mape_val = mape(xp, xe)
        f_w.write(tweetid.strip()+"\t"+str(mape_val)+"\n")
        mape_dict[tweetid] = (mape_val, len(xp))
f_w.close()

# In[26]:

outlier_count = 0
weighted_sum = 0
for tweetid in mape_dict.keys():
    if mape_dict[tweetid][0] > 0.5 :
        outlier_count+=1
    #if tweetid == "tech" or tweetid == "Samsung" or tweetid == 'FootballFeverwithCW' or tweetid == "2Rs" or tweetid == "INSubcontinent":
        #continue
        #print "Outlier found id = %s, MAPE = %f"%(tweetid, mape_dict[tweetid][0])
        #continue
    #if mape_dict[tweetid][0] > 1000 :
    #    continue
    weighted_sum+= mape_dict[tweetid][0]
    
    print int(weighted_sum), mape_dict[tweetid][0], tweetid
    #*mape_dict[tweetid][1]
print "\n\nCumulative MAPE", float(weighted_sum)/len(mape_dict.keys())
#sum([x[1] for x in mape_dict.values()])
print "Number of outliers", outlier_count, "Total", len(mape_dict.keys())

