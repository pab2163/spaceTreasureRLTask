data {
  int<lower=1> N;
  int<lower=1> T;
  int<lower=1, upper=T> Tsubj[N];
  int<lower=0, upper=1> missing[N,T];  // whether any data are missing on a given trial
  int<lower=1, upper=2> level1_choice[N,T];  // 1: left, 2: right
  int<lower=1, upper=4> level2_choice[N,T];  // 1-4: 1/2: commonly associated with level1=1, 3/4: commonly associated with level1=2
  int<lower=0, upper=1> reward[N,T];
}
transformed data {
}
parameters {
  // Declare all parameters as vectors for vectorizing
  // Hyper(group)-parameters
  vector[5] mu_pr;
  vector<lower=0>[5] sigma;

  // Subject-level raw parameters (for Matt trick)
  vector[N] beta1_pr;
  vector[N] beta2_pr;
  vector[N] pp_pr;
  vector[N] a3_pr;
  vector[N] lambda2_pr;
}
transformed parameters {
  // Transform subject-level raw parameters
  vector<lower=0>[N]         beta1;
  vector<lower=0>[N]         beta2;
  vector<lower=0,upper=5>[N] pp;
  vector<lower=0,upper=1>[N] a3;
  vector<lower=0,upper=1>[N] lambda2;

  for (i in 1:N) {
      beta1[i]  = exp( mu_pr[1] + sigma[1] * beta1_pr[i] );
      beta2[i]  = exp( mu_pr[2] + sigma[2] * beta2_pr[i] );
      pp[i]     = Phi_approx( mu_pr[3] + sigma[3] * pp_pr[i] ) * 5;
      a3[i]     = Phi_approx( mu_pr[4] + sigma[4] * a3_pr[i] );
      lambda2[i] = Phi_approx( mu_pr[5] + sigma[5] * lambda2_pr[i] );
  }
}
model {
  // Hyperparameters
  mu_pr  ~ normal(0, 1);
  sigma ~ normal(0, 0.2);

  // individual parameters
  beta1_pr  ~ normal(0, 1);
  beta2_pr  ~ normal(0, 1);
  pp_pr     ~ normal(0, 1);
  a3_pr     ~ normal(0, 1);
  lambda2_pr ~ normal(0, 1);

  for (i in 1:N) {
    // Define values
    vector[4] v_keys; // model-free stimulus values based on response keys alone
    real level1_prob_choice2; // Initialize prob. of choosing stim 2 (0 or 1) in level 1
    real level2_prob_choice2; // Initialize prob. of choosing stim 2 (0 or 1) in level 2
    int level1_choice_01;
    int level2_choice_01;

    // Initialize values
    v_keys = rep_vector(0.0, 4);

    for (t in 1:Tsubj[i])  {
      if (missing[i, t] == 0){
      // Prob of choosing stimulus 2 in ** Level 1 ** --> to be used on the next trial
      // level1_choice=1 --> -1, level1_choice=2 --> 1
      level1_choice_01 = level1_choice[i,t] - 1;  // convert 1,2 --> 0,1
      if(t == 1){
        level1_prob_choice2 = inv_logit( beta1[i]*(v_keys[2]-v_keys[1]));
      } else{
        level1_prob_choice2 = inv_logit( beta1[i]*(v_keys[2]-v_keys[1]) + pp[i]*(2*level1_choice[i,t-1] -3) );
      }
      level1_choice_01 ~ bernoulli( level1_prob_choice2 );  // level 1, prob. of choosing 2 in level 1


      // Prob of choosing stim 2 (2 from [1,2] OR 4 from [3,4]) in ** Level (step) 2 **
      level2_choice_01 = 1 - modulus(level2_choice[i,t], 2); // 1,3 --> 0; 2,4 --> 1
      level2_prob_choice2 = inv_logit( beta2[i]*( v_keys[4] - v_keys[3]));
      level2_choice_01 ~ bernoulli( level2_prob_choice2 );   // level 2, prob of choosing right option in level 2
      
      // update v_keys - level1 choices updated twice, once based on level1 presses and once based on level2
      v_keys[level1_choice[i,t]] += a3[i]*lambda2[i]*(reward[i,t] - v_keys[level1_choice[i,t]]);
      
      if (level2_choice[i,t] > 2) {
        v_keys[level2_choice[i,t]-2] += a3[i]*lambda2[i]*(reward[i,t] - v_keys[level2_choice[i,t]-2]);
        v_keys[level2_choice[i,t]] += a3[i]*(1-lambda2[i])*(reward[i,t] - v_keys[level2_choice[i,t]]);
      } else{
        v_keys[level2_choice[i,t]] += a3[i]*lambda2[i]*(reward[i,t] - v_keys[level2_choice[i,t]]);
        v_keys[level2_choice[i,t]+2] += a3[i]*(1-lambda2[i])*(reward[i,t] - v_keys[level2_choice[i,t]+2]);
      }
      }

    } // end of t loop
  } // end of i loop
}

generated quantities {
  // For group level parameters
  real<lower=0>         mu_beta1;
  real<lower=0>         mu_beta2;
  real<lower=0,upper=5> mu_pp;
  real<lower=0,upper=1> mu_a3;
  real<lower=0,upper=1> mu_lambda2;

  // For log likelihood calculation
  real log_lik[N];

  // For posterior predictive check
  real y_pred_step1[N,T];
  real y_pred_step2[N,T];

  // Set all posterior predictions to 0 (avoids NULL values)
  for (i in 1:N) {
    for (t in 1:T) {
      y_pred_step1[i,t] = -1;
      y_pred_step2[i,t] = -1;
    }
  }

  // Generate group level parameter values
  mu_beta1  = exp( mu_pr[1] );
  mu_beta2  = exp( mu_pr[2] );
  mu_pp     = Phi_approx( mu_pr[3] ) * 5;
  mu_a3     = Phi_approx( mu_pr[4] );
  mu_lambda2 = Phi_approx( mu_pr[5] );

  { // local section, this saves time and space
  for (i in 1:N) {
    // Define values
    vector[4] v_keys;
    real level1_prob_choice2; // prob of choosing stim 2 (0 or 1) in level 1
    real level2_prob_choice2; // prob of choosing stim 2 (0 or 1) in level 2
    int level1_choice_01;
    int level2_choice_01;

    // Initialize values
    v_keys = rep_vector(0.0, 4);
    log_lik[i] = 0;

    for (t in 1:Tsubj[i])  {
      if (missing[i, t] == 0){
      // Prob of choosing stimulus 2 in ** Level 1 ** --> to be used on the next trial
      // level1_choice=1 --> -1, level1_choice=2 --> 1
      level1_choice_01 = level1_choice[i,t] - 1;  // convert 1,2 --> 0,1
      if(t == 1){
        level1_prob_choice2 = inv_logit( beta1[i]*(v_keys[2]-v_keys[1]));
      } else{
        level1_prob_choice2 = inv_logit( beta1[i]*(v_keys[2]-v_keys[1]) + pp[i]*(2*level1_choice[i,t-1] -3) );
      }
      log_lik[i] += bernoulli_lpmf( level1_choice_01 | level1_prob_choice2 );

      // Prob of choosing stim 2 (2 from [1,2] OR 4 from [3,4]) in ** Level (step) 2 **
      level2_choice_01 = 1 - modulus(level2_choice[i,t], 2); // 1,3 --> 0; 2,4
      level2_prob_choice2 = inv_logit( beta2[i]*( v_keys[4] - v_keys[3] ) );
      log_lik[i] += bernoulli_lpmf( level2_choice_01 | level2_prob_choice2 );

      // generate posterior prediction for current trial
      y_pred_step1[i,t] = bernoulli_rng(level1_prob_choice2);
      y_pred_step2[i,t] = bernoulli_rng(level2_prob_choice2);

      // After observing the reward at Level 2...
      // update v_keys - level1 choices updated twice, once based on level1 presses and once based on level2
      v_keys[level1_choice[i,t]] += a3[i]*lambda2[i]*(reward[i,t] - v_keys[level1_choice[i,t]]);
      
      if (level2_choice[i,t] > 2) {
        // level1 key
        v_keys[level2_choice[i,t]-2] += a3[i]*lambda2[i]*(reward[i,t] - v_keys[level2_choice[i,t]-2]);
        // level2 key
        v_keys[level2_choice[i,t]] += a3[i]*(1-lambda2[i])*(reward[i,t] - v_keys[level2_choice[i,t]]);
        }
      else{
        // level1 key
        v_keys[level2_choice[i,t]] += a3[i]*lambda2[i]*(reward[i,t] - v_keys[level2_choice[i,t]]);
        // level2 key
        v_keys[level2_choice[i,t]+2] += a3[i]*(1-lambda2[i])*(reward[i,t] - v_keys[level2_choice[i,t]+2]);
        }
      }
      } // end of t loop
    } // end of i loop
  }
}
