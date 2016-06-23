sayHello <- function(){
   print('hello')
}

loglik  <- function(params, arrivals) {
	n = length(arrivals)
	#cat(arrivals)
	#cat("test")

	alpha_i <- params[1]
	beta_i	<- params[2]
	mu_i	<- params[3]
	#n <- 12
	term_1 <- -mu_i * arrivals[n]
	term_2 <- sum(alpha_i/beta_i * (exp( -beta_i * (arrivals[n] - arrivals)) - 1))
	Ai <- c(0,sapply(2:n, function(z) {
			sum(exp(-beta_i * (arrivals[z] - arrivals[1:(z-1)])))
		}))	
	term_3 <- sum(log(mu_i + alpha_i * Ai))
	return(-term_1- term_2 - term_3)	
}

loglikIter  <- function(params, arrivals, beta) {
	n = length(arrivals)
	#cat(arrivals)
	#cat("test")

	alpha_i <- params[1]
	beta_i	<- beta
	mu_i	<- params[2]
	#n <- 12
	term_1 <- -mu_i * arrivals[n]
	term_2 <- sum(alpha_i/beta_i * (exp( -beta_i * (arrivals[n] - arrivals)) - 1))
	Ai <- c(0,sapply(2:n, function(z) {
			sum(exp(-beta_i * (arrivals[z] - arrivals[1:(z-1)])))
		}))	
	term_3 <- sum(log(mu_i + alpha_i * Ai))
	return(-term_1- term_2 - term_3)	
}

# insert your values for (mu, alpha, beta) in par
# insert your times for data
#opt <- optim(par=c(1,2,0.1), fn=neg.loglik, data=c(0, 15, 36, 52, 104, 125, 154, 180, 232, 295, 717, 999))
#paste( c("alpha", "beta", "mu"), round(opt$par,2), sep="=")

#opt <- nlm(neg.loglik, c(1,2,0.1), hessian=TRUE, data=c(0, 15, 36, 52, 104, 125, 154, 180, 232, 295, 717, 999))
#print(opt)
#paste( c("alpha", "beta", "mu"), round(opt$par,2), sep="=")

#case1_solution1 <- optim(c(1,2,0.1), loglik, arrivals = c(0, 15, 36, 52, 104, 125, 154, 180, 232, 295, 717, 999), n = 12)
##paste( c("alpha", "beta", "mu"), round(case1_solution1$par,2), sep="=")

#case2_solution1 <- optim(c(0.001,0.0001,0.001), loglik, arrivals = c(0, 15, 36, 52, 104, 125, 154, 180, 232, 295, 717, 999), n = 12)
#paste( c("alpha", "beta", "mu"), round(case2_solution1$par,2), sep="=")

#case1_solution2 <- nlm(loglik, c(1, 2, 0.1), hessian = TRUE, arrivals = c(0, 19, 47, 218, 268, 346), n = 6)
#case1_solution2 <- nlm(loglik, c(1, 2, 0.1), hessian = TRUE, arrivals = c(0, 15, 36, 52, 104, 125, 154, 180, 232, 295, 717, 999), n = 12)
#case1_solution2 <- nlm(loglik, c(1, 2, 0.1), hessian = TRUE, 
#	arrivals = c(0,588,1180,1740,6205,13623,15587,16810,22455,26339,26511,75516,92892,92908,92920,93017,93082,93125,93226,93727,94263,94635,95054))
#paste( c("alpha", "beta", "mu"), round(case1_solution2$par,2), sep="=")
#print(case1_solution2)
options(warn=-1)
myArgs <- commandArgs(trailingOnly = TRUE)
#myArgs[1]
#myArrivals <- as.integer(unlist(strsplit(myArgs[1],",")))
myInitial <- as.double(unlist(strsplit(myArgs[2],",")))
betaInitial <- as.double(myArgs[3])

#case1_solution2 <- nlm(loglik, c(1, 2, 0.1), hessian = TRUE, 
#	arrivals = c(0,588,1180,1740,6205,13623,15587,16810,22455,26339,26511,75516,92892,92908,92920,93017,93082,93125,93226,93727,94263,94635,95054))
#myVector
#print(length(myVector))
#print(myArrivals)
myArrivals <- as.integer(scan(myArgs[1], what="", sep="\n"))
# (read.csv(myArgs[1]))
#print(myArrivals)
#print(myInitial)
#print(betaInitial)
case1_solution3 <- nlm(loglikIter, myInitial, hessian = TRUE, arrivals = myArrivals, beta = betaInitial)
#case1_solution3
#print(case1_solution3)
cat(case1_solution3$minimum)
cat(" ")
cat(case1_solution3$estimate)
#loglik(c())
#print(myArgs[1])
#
#args <- commandArgs(TRUE)
#eval(parse(text=args))
#a
#b
