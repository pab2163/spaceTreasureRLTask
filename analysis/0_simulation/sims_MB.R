library(tidyverse)
oneModelBasedSubject = function(alpha, itemp, transitionContingency, totalTrials, rewardFrame, perseveration){
  subframe = data.frame(trial = 1:totalTrials, stage1Choice = rep(NA, totalTrials), 
                        stateStage2 = rep(NA, totalTrials),
                        rewardStage2 = rep(NA, totalTrials),
                        smxL1 = rep(NA, totalTrials),
                        smxL2 = rep(NA, totalTrials),
                        transitionStage2 = rep(NA, totalTrials))
  
  #set.seed(id)
  rewHist = numeric(length = totalTrials)
  
  # Transition vector of rare/common transitions
  transition_vector = c(rep('rare', round(totalTrials*(1-transitionContingency))),
                        rep('common', round(totalTrials*(transitionContingency))))
  transition_vector = sample(transition_vector)
  
  # shuffle columns of reward frame, keeping pairs together (this is what happens for real participants)
  rewardFrame[,1:2] = sample(rewardFrame[,1:2])
  rewardFrame[,3:4] = sample(rewardFrame[,3:4])
  
  # if (runif(1) > 0.5) {
  #   rewardFrame[,1:4] = rev(rewardFrame[,1:4])
  # }
  
  
  Q = data.frame(q1 = c(.5, .5, .5), q2 = c(.5, .5, .5))
  
  probState2GivenChoose1 = .5
  probState2GivenChoose2 = .5
  probState3GivenChoose1 = .5
  probState3GivenChoose2 = .5
  
  for (t in 1:totalTrials) {
    # calculate stage1 q values
    Q[1,1] = probState2GivenChoose1*max(Q[2,]) + probState3GivenChoose1*max(Q[3,])
    Q[1,2] = probState2GivenChoose2*max(Q[2,]) + probState3GivenChoose2*max(Q[3,])
    
    #choose at stage 1, smxL1 = softmax likelihood of choosing option 1
    if (t > 1){
      p = ifelse(subframe$stage1Choice[t-1] == 1, perseveration, -perseveration)
    }
    else{
      p = 0
    }
    
    # Choose at stage 1 (softmax likelihoo)
    numerator1 = exp(itemp*Q[1,1] + p) 
    denominator1 = exp(itemp*Q[1,1] + p) + exp(itemp*Q[1,2])
    subframe$smxL1[t]  = numerator1/denominator1
    subframe$stage1Choice[t] =  which.max(c(subframe$smxL1[t], runif(1)))
    
    # go to stage 2 based on transition contingency
    subframe$transitionStage2[t] = transition_vector[t]#ifelse(runif(1) > transitionContingency, 'rare', 'common')
    subframe$stateStage2[t] = case_when(
      subframe$transitionStage2[t] == 'common' & subframe$stage1Choice[t] == 1 ~ 2,
      subframe$transitionStage2[t] == 'rare' & subframe$stage1Choice[t] == 1 ~ 3,
      subframe$transitionStage2[t] == 'common' & subframe$stage1Choice[t] == 2 ~ 3,
      subframe$transitionStage2[t] == 'rare' & subframe$stage1Choice[t] == 2 ~ 2)
    
    #choose at stage 2
    subframe$smxL2[t] = exp(itemp*Q[subframe$stateStage2[t],1]) / (exp(itemp*Q[subframe$stateStage2[t],1]) + exp(itemp*Q[subframe$stateStage2[t],2]))    
    subframe$choiceStage2[t] =  which.max(c(subframe$smxL2[t], runif(1)))
    
    # reward at stage 2
    subframe$rewardStage2[t] = case_when(
      subframe$stateStage2[t] == 2 & subframe$choiceStage2[t] == 1 ~ ifelse(rewardFrame[t,1] > runif(1), 1, 0),
      subframe$stateStage2[t] == 2 & subframe$choiceStage2[t] == 2 ~ ifelse(rewardFrame[t,2] > runif(1), 1, 0),
      subframe$stateStage2[t] == 3 & subframe$choiceStage2[t] == 1 ~ ifelse(rewardFrame[t,3] > runif(1), 1, 0),
      subframe$stateStage2[t] == 3 & subframe$choiceStage2[t] == 2 ~ ifelse(rewardFrame[t,4] > runif(1), 1, 0))

    # update stage2 Q (based on stage2 RPE)
    rpeStage2 = alpha*(subframe$rewardStage2[t]-Q[subframe$stateStage2[t],subframe$choiceStage2[t]])
    Q[subframe$stateStage2[t],subframe$choiceStage2[t]] = Q[subframe$stateStage2[t],subframe$choiceStage2[t]] + rpeStage2
    
    
    # update transition probabilities
    probState2GivenChoose1 = nrow(subset(subframe, stage1Choice == 1 & stateStage2 == 2))/nrow(subset(subframe, stage1Choice == 1))
    probState2GivenChoose2 = nrow(subset(subframe, stage1Choice == 2 & stateStage2 == 2))/nrow(subset(subframe, stage1Choice == 2))
    probState3GivenChoose1 = nrow(subset(subframe, stage1Choice == 1 & stateStage2 == 3))/nrow(subset(subframe, stage1Choice == 1))
    probState3GivenChoose2 = nrow(subset(subframe, stage1Choice == 2 & stateStage2 == 3))/nrow(subset(subframe, stage1Choice == 2))
    
    # replace NaNs if needed
    probState2GivenChoose1 = ifelse(is.nan(probState2GivenChoose1), .5, probState2GivenChoose1)
    probState2GivenChoose2 = ifelse(is.nan(probState2GivenChoose2), .5, probState2GivenChoose2)
    probState3GivenChoose1 = ifelse(is.nan(probState3GivenChoose1), .5, probState3GivenChoose1)
    probState3GivenChoose2 = ifelse(is.nan(probState3GivenChoose2), .5, probState3GivenChoose2)
    subframe$probState2GivenChoose1[t] = probState2GivenChoose1
    subframe$probState2GivenChoose2[t] = probState2GivenChoose2
    subframe$probState3GivenChoose1[t] = probState3GivenChoose1
    subframe$probState3GivenChoose2[t] = probState3GivenChoose2
    
    if (t > 1){
      subframe$prevReward[t] = subframe$rewardStage2[t-1]
      subframe$stay[t] = ifelse(subframe$stage1Choice[t] == subframe$stage1Choice[t-1], 1, 0)
      subframe$prevTransition[t] = subframe$transitionStage2[t-1]
    }
    else{
      subframe$prevReward[t] = NA
      subframe$stay[t] = NA
      subframe$prevTransition[t] = NA
    }
  }
  subframe$v1 = rewardFrame[,1]
  subframe$v2 = rewardFrame[,2]
  subframe$v3 = rewardFrame[,3]
  subframe$v4 = rewardFrame[,4]
  #print(probState2GivenChoose1)
  #print(probState2GivenChoose2)
  #print(probState3GivenChoose1)
  #print(probState3GivenChoose2)
  return(list(subframe))
}

