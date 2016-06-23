SRC= spikeM.py spikeMi.py X_demo.m M_spikeM.m M_spikeMfit.m
REST= README makefile sequence.dat


#interactive
demo: 	spikeMi.py
	python spikeMi.py
data:	spikeMi.py
	python spikeMi.py sequence.dat
run:	spikeM.py
	python spikeM.py  

fit:	X_demo.m
	matlab -r 'X_demo'


clean:
	\rm -r -f *.pyc output* *~ all.tar


all.tar: $(SRC) $(REST)
	tar cvf all.tar $(SRC) $(REST)
