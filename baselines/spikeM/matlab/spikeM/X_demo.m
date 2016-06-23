% $Author: Yasuko Matsubara 
% $Date: 2014-04-30

%% demo: fitting sequence "./sequence.dat"
%function[] = X_demo(T)
    addpath(genpath('.'));
    addpath(genpath('/home/bidisha/HashtagPopularity/spikeM/'));
    fn='./sequence.dat';
    % duration of sequence
    %T=24*4;
    % # of max iteration
    ITER=20;
    % daily periodicity (24hours)
    pfreq=24;


    dat=load(fn);
    T = dat(1:1);
    %length(dat);
    dat=dat(2:length(dat));
    disp(T);
    %old = length(dat);
    %dat=dat(1:T);
    outfn='output';
    wantPlot=0; % Yes!
    disp('===================================');
    disp('DEMO - fitting sample sequence');
    disp('-----------------------------------');
    disp(['- filename = ', fn]);
    disp(['- duration = ', num2str(T)]);
    disp(['- max iteration = ', num2str(ITER)]);
    disp('===================================');
    disp(' ');
    [RSE, params]=M_spikeMfit(T, dat, pfreq, outfn, ITER, wantPlot);

%end