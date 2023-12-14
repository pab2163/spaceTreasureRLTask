oneModelFreeSubject = function(alpha1, alpha2, itemp, elegibility, transitionContingency, totalTrials, rewardFrame, perseveration){
  # shuffle columns of reward frame, keeping pairs together (this is what happens for real participants)
  rewardFrame[,1:2] = sample(rewardFrame[,1:2])
  rewardFrame[,3:4] = sample(rewardFrame[,3:4])
  
  # Initialize output dataframe
  variableNames = c('trial', 'stage1Choice', 'stateStage2', 'stage1Q1', 'stage1Q2', 'stage2Q1', 'stage2Q2','stage2Q3','stage2Q4')
  subframe = data.frame(matrix(ncol = length(variableNames), nrow = totalTrials))
  colnames(subframe) = variableNames
  subframe$trial = 1:totalTrials

  # initialize Q matrix
  Q = data.frame(q1 = c(.5, .5, .5), q2 = c(.5, .5, .5))
  
  for (t in 1:totalTrials) {
    # Store current values from Q matrix into dataframe
    subframe$stage1Q1[t] = Q[1,1]
    subframe$stage1Q2[t] = Q[1,2]
    subframe$stage2Q1[t] = Q[2,1]
    subframe$stage2Q2[t] = Q[2,2]
    subframe$stage2Q3[t] = Q[3,1]
    subframe$stage2Q4[t] = Q[3,2]

    
    # factor in perseveration parameter
    if (t > 1){
      p = ifelse(subframe$stage1Choice[t-1] == 1, perseveration, -perseveration)
    }
    else{
      p = 0
    }
    
    #choose at stage 1 (softmax likelihood)
    numerator1 = exp(itemp*Q[1,1] + p) 
    denominator1 = exp(itemp*Q[1,1] + p) + exp(itemp*Q[1,2])
    subframe$smxL1[t]  = numerator1/denominator1
    subframe$stage1Choice[t] =  which.max(c(subframe$smxL1[t], runif(1)))
    
    # go to stage 2 based on transition contingency
    subframe$transitionStage2[t] = ifelse(runif(1) > transitionContingency, 'rare', 'common')
    subframe$stateStage2[t] = case_when(
      subframe$transitionStage2[t] == 'common' & subframe$stage1Choice[t] == 1 ~ 2,
      subframe$transitionStage2[t] == 'rare' & subframe$stage1Choice[t] == 1 ~ 3,
      subframe$transitionStage2[t] == 'common' & subframe$stage1Choice[t] == 2 ~ 3,
      subframe$transitionStage2[t] == 'rare' & subframe$stage1Choice[t] == 2 ~ 2)
    
    #choose at stage 2 (softmax lielihood)
    numerator2 = exp(itemp*Q[subframe$stateStage2[t],1]) 
    denominator2 =  exp(itemp*Q[subframe$stateStage2[t],1]) + exp(itemp*Q[subframe$stateStage2[t],2]) 
    subframe$smxL2[t] = numerator2/denominator2
    subframe$choiceStage2[t] =  which.max(c(subframe$smxL2[t], runif(1)))
    
    
    # update stage1 Q value based on stage2 choice (SARSA)
    rpeStage1 = Q[subframe$stateStage2[t],subframe$choiceStage2[t]]-Q[1,subframe$stage1Choice[t]]
    Q[1,subframe$stage1Choice[t]] = Q[1,subframe$stage1Choice[t]] + rpeStage1*alpha1
    
    # reward at stage 2
    subframe$rewardStage2[t] = case_when(
      subframe$stateStage2[t] == 2 & subframe$choiceStage2[t] == 1 ~ ifelse(rewardFrame[t,1] > runif(1), 1, 0),
      subframe$stateStage2[t] == 2 & subframe$choiceStage2[t] == 2 ~ ifelse(rewardFrame[t,2] > runif(1), 1, 0),
      subframe$stateStage2[t] == 3 & subframe$choiceStage2[t] == 1 ~ ifelse(rewardFrame[t,3] > runif(1), 1, 0),
      subframe$stateStage2[t] == 3 & subframe$choiceStage2[t] == 2 ~ ifelse(rewardFrame[t,4] > runif(1), 1, 0))
    
    # update stage2 Q (based on stage2 RPE)
    rpeStage2 = subframe$rewardStage2[t]-Q[subframe$stateStage2[t],subframe$choiceStage2[t]]
    Q[subframe$stateStage2[t],subframe$choiceStage2[t]] = Q[subframe$stateStage2[t],subframe$choiceStage2[t]] + alpha2*rpeStage2
    
    # update stage1 Q (based on stage2 RPE*elegibility)
    Q[1,subframe$stage1Choice[t]] = Q[1,subframe$stage1Choice[t]] + alpha1*rpeStage2*elegibility
    
    
    # Save useful into into dataframe
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
  # Return dataframe as list
  return(list(subframe))
}




