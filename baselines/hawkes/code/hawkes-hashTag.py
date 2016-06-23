
# coding: utf-8

# In[1]:

import sys
import operator
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
from cvxpy import *
import math
import time
from math import exp, log
from math import pow
import subprocess
from collections import defaultdict
paths = ['../']
for p in paths:
        sys.path.insert(0, p)

from SRM.srm.db_manager import connect_to_db, execute_sql


# #initial values of these parameters are decided empherically 

# In[3]:

alpha = 0.004106219 
beta = 0.006362777 
gamma = 0.0007837629


# The hawkes process lambda(t) = mu + alpha * (sum (exp (-beta * t)))

# In[2]:

def hawkes(arrivals, beta):
    #t_train = data[:20]
    #arrivals = ','.join(str(t) for t in t_train)
    #initial values for alpha and mu
    initial = "0.01,0.01"
    
    command = 'Rscript'
    #path2script = 'hawkes_mod.R'
    path2script = 'hawkes.R'
    # Variable number of args in a list
    args = [arrivals,initial, beta]

    # Build subprocess command
    cmd = [command, path2script] + args

    x = subprocess.check_output(cmd, universal_newlines=True)
    #process the output
    params = x.split(" ")
    logLikelihood = float(params[0])
    alpha = float(params[1])
    mu = float(params[2])
    #print alpha, beta, mu
    return (logLikelihood, alpha, mu)


# In[3]:

def rate(t_0, mu, alpha, beta, t_train):
    sum_exp = 0
    for i in range(0, len(t_train)):
        sum_exp += exp(-beta * (t_0 - t_train[i]))
    return mu + alpha * sum_exp
        
def predictOld(alpha, beta, gamma, tp, T, t_train):
    n = len(t_train)
    first_term = (gamma / beta) * (exp(-beta* T) - exp(-beta * tp))
    sumterm = 0
    for i in range(0, n):
        sumterm += exp(-beta *(T - t_train[i])) - exp(-beta * (tp - t_train[i]))
    second_term = (alpha / beta) * sumterm
    return (n + first_term + second_term)

def predict(alpha, beta, mu, t_0, T, t_train):
    lambda_t0 = rate(t_0, mu, alpha, beta, t_train)
    first_part = (exp((alpha - beta)*(T - t_0)) - 1) * lambda_t0 /(alpha - beta)
    second_part = beta * mu * ((exp((alpha - beta) * (T - t_0)) - 1)/ (alpha - beta) - T + t_0 ) / (alpha - beta)
    return (first_part + second_part)

def mape(ta, tp):
    diff = 0.0
    n = len(ta)
    for i in range(n):
        diff+= math.fabs(float(ta[i]-tp[i]))/float(ta[i])
    #print diff
    return diff/n


# In[6]:

def plotGraph(prediction_dict):
    colors = cm.rainbow(np.linspace(0, 1, 256))
    for tweetid,c in zip(prediction_dict.keys(), colors):
        xp = [x[1] for x in prediction_dict[tweetid]]
        #xe = [x[1] for x in prediction_dict[tweetid]]
        xe = [ x[2] for x in prediction_dict[tweetid]]
        plt.xlabel('Actual', fontsize=11)
        plt.ylabel('prdicted', fontsize=11)
        plt.title("id="+tweetid, fontsize=12)
        plt.plot(xp, xe, color=c, marker='.')
    plt.show()


# In[13]:

prediction_dict = defaultdict(list)
f = open(sys.argv[1])
count = 0
for line in f:
#for ht in hashtaglist:   
    tokens = line.split("\t")
    tweetId = tokens[0]
    t_original = tokens[1].strip().split(",")
    length = min(20000, len(t_original))
    t_original = t_original[:length]
    
    t_original = [(int(t) - int(t_original[0])) for t in t_original]

    splitIndex = int(len(t_original) * float(sys.argv[2]))
    t_train, t_test = t_original[:splitIndex], t_original[splitIndex+1 : ]
    betaList = [0.05, 0.001]
    
    f_w = open(sys.argv[3],"w")
    for tt in t_train:
        f_w.write(str(tt)+"\n")
    f_w.close()
    
    logLikelihoodmin = -sys.maxint
    alphamax = 0.01
    mumax = 0.01
    for beta in betaList:
        try:
            (logLikelihood, alpha, mu) = hawkes(sys.argv[3], str(beta))
            if logLikelihood > loglikelihoodmin:
                logLikekihoodmin = logLikelihood
                alphamax = alpha
                mumax = mu
            count = count + 1
            #print logLikelihood, beta
        except:
            print "Fail Case", tweetId
	    if logLikelihoodmin == -sys.maxint :
            	continue
    N = len(t_train)
    T = t_train[-1]
        #expetcted number of retweets
    for tp in t_test:
            #ne = predictOld(alpha, beta, mu, tp, T, t_train)
            try:
                ne = predict(alpha, beta, mu, T, tp, t_train) + N
            except:
		print "Error in ", tweetId
		if tweetId in prediction_dict: del prediction_dict[tweetId]
                continue
            #print "expected :", ne
            if ne == -1: 
                continue
            if not prediction_dict.has_key(tweetId):
                prediction_dict[tweetId] = [(tp, t_original.index(tp)+1, ne)]
            else :
                prediction_dict[tweetId].append((tp, t_original.index(tp)+1, ne))
#print count

print prediction_dict
f.close()
# In[14]:

mape_dict = dict()
f_w = open(sys.argv[4],"w")
for tweetid in prediction_dict.keys():
        xp = [x[1] for x in prediction_dict[tweetid]]
        xe = [x[2] for x in prediction_dict[tweetid]]
        #print xp, xe
        if(len(xp)==0):
            continue
        mape_val = mape(xp, xe)
        f_w.write(tweetid+","+ str(mape_val))
        mape_dict[tweetid] = (mape_val, len(xp))

#print mape_dict[mape_dict.keys()[0]]
f_w.close()

# In[16]:

outlier_count = 0
weighted_sum = 0
for tweetid in mape_dict.keys():
    if mape_dict[tweetid][0] > 0.5 :
        outlier_count+=1
        #print "Outlier found id = %s, MAPE = %f"%(tweetid, mape_dict[tweetid][0])
        #continue
    weighted_sum+= mape_dict[tweetid][0]
    
print "Cumulative MAPE", float(weighted_sum)/len(mape_dict.keys())
#sum([x[1] for x in mape_dict.values()])
print "Number of outliers", outlier_count, "Total", len(mape_dict.keys())


# In[ ]:


#plotGraph(prediction_dict)
    #print len(prediction_dict[tweetid])

