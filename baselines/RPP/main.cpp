/* Pass the value of T as the first commandline argument followed by retweet timestamps as the arguments*/

#include "mic_model.h"
#include <fstream>
#include <iostream>
#include <string>
#include <cstdlib>
#include <sstream>


using namespace std;

//int training_time = 9000;

int main(int argc, char **argv )
{
	//int trainYear = 10;
	int training_time = atoi(argv[1]); //Second arg is training time T
	//cout<<"T="<< training_time<<"\n";	
	vector< vector<int> > citations;

	int cc;
	vector<int> citation;
	for(int i= 2; i< argc; i++)
	{
		cc = atoi(argv[i]);
		//cout<<cc<<"\n";
		if ( cc > 0 && cc <= training_time )
			citation.push_back( cc );
	}
	citations.push_back( citation );
	CMicModel model( training_time );
	
	for ( size_t ii = 0; ii < citations.size(); ++ii )
	{
		model.parameter_estimation(citations[ii]);
		cout << model.get_lambda() << "\t" << model.get_mu() << "\t" << model.get_sigma() << "\n";
		
	}
	
	return 0;
}

